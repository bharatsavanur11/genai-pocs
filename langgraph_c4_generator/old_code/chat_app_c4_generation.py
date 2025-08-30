import streamlit as st
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver
import json


# --- App Configuration --- #
st.set_page_config(page_title="C4 DSL Generator", layout="wide")
st.title("🧠 LangGraph-based Structurizr DSL Generator")

# --- State Schema --- #
class State():
    spec: str
    structured_info: dict
    missing_info: List[str]

# --- Input Box --- #
user_spec = st.text_area("Paste your system specification below:", height=300)

if "dsl_output" not in st.session_state:
    st.session_state.dsl_output = ""
if "missing_info" not in st.session_state:
    st.session_state.missing_info = []

# --- LLM Setup --- #
api_key="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"
llm = ChatOpenAI(temperature=0, api_key=api_key)

# --- Prompt Templates --- #
spec_analysis_prompt = PromptTemplate.from_template(
    """
    You are a system architect assistant. Extract the following structured details from the given system specification:

    - System name and context
    - Actors (users, external systems)
    - Containers (apps, APIs, DBs)
    - Key components in main containers
    - Technology stack
    - Relationships and dependencies
    - Non-functional requirements

    Return JSON with fields: system_name, description, actors (list of dict), containers (list of dict), components, technologies, relationships (list of dict), non_functionals.

    Specification:
    {spec}
    """
)

missing_info_prompt = PromptTemplate.from_template(
    """
    Given the following extracted information from a system specification, identify which of the following required fields are missing or incomplete:

    Required fields: system_name, description, actors, containers, components, technologies, relationships, non_functionals.

    Extracted JSON:
    {info}

    Return a Python list of missing or incomplete field names.
    """
)

json_extractor_chain = LLMChain(llm=llm, prompt=spec_analysis_prompt)
missing_info_chain = LLMChain(llm=llm, prompt=missing_info_prompt)

# --- Structurizr DSL Generator --- #
def generate_structurizr_dsl(data):
    dsl = ["workspace {", "\n  model {"]
    dsl.append(f"    user = person \"User\"")
    dsl.append(f"    {data['system_name'].lower().replace(' ', '_')} = softwareSystem \"{data['system_name']}\" \"{data['description']}\"")
    for actor in data.get("actors", []):
        dsl.append(f"    {actor['id']} = person \"{actor['name']}\" \"{actor['description']}\"")
    for container in data.get("containers", []):
        dsl.append(f"    {container['id']} = container {data['system_name'].lower().replace(' ', '_')} \"{container['name']}\" \"{container['description']}\" \"{container['technology']}\"")
    for rel in data.get("relationships", []):
        dsl.append(f"    {rel['source']} -> {rel['target']} \"{rel['description']}\"")
    dsl.append("  }\n")
    dsl.append("  views {")
    dsl.append(f"    systemContext {data['system_name'].lower().replace(' ', '_')} {{")
    dsl.append("      include *")
    dsl.append("      autolayout lr")
    dsl.append("    }")
    dsl.append(f"    container {data['system_name'].lower().replace(' ', '_')} {{")
    dsl.append("      include *")
    dsl.append("      autolayout lr")
    dsl.append("    }")
    dsl.append("    theme default")
    dsl.append("  }\n}")
    return "\n".join(dsl)

# --- LangGraph Memory and Flow Setup --- #
store = SqliteSaver("c4_sessions.db")

# Define nodes for LangGraph
def analyze_spec_node(state):
    if "structured_info" not in state or not state["structured_info"]:
        result = json_extractor_chain.run({"spec": state["spec"]})
        return {"structured_info": json.loads(result)}
    return {}

def check_missing_info_node(state):
    response = missing_info_chain.run({"info": json.dumps(state.get("structured_info", {}))})
    try:
        missing = json.loads(response)
        return {"missing_info": missing}
    except (json.JSONDecodeError, ValueError):
        return {"missing_info": []}

def prompt_user_for_missing_info(state):
    if state.get("missing_info"):
        st.warning(f"🚨 Missing fields detected: {', '.join(state['missing_info'])}. Please update your spec accordingly.")
    return {}

graph = StateGraph(State)
graph.add_node("analyze", analyze_spec_node)
graph.add_node("check_missing", check_missing_info_node)
graph.add_node("prompt_user", prompt_user_for_missing_info)
graph.add_edge("analyze", "check_missing")
graph.add_edge("check_missing", "prompt_user")
graph.set_entry_point("analyze")
graph.set_finish_point("prompt_user")
c4_flow = graph.compile()

# --- Handle User Input and Run Graph --- #
if st.button("Analyze and Generate DSL") and user_spec:
    result = c4_flow.invoke({"spec": user_spec})
    if not result.get("missing_info"):
        st.session_state.dsl_output = generate_structurizr_dsl(result["structured_info"])
        store.put("latest", result)
        st.success("✅ Specification analyzed and session saved!")
    else:
        st.session_state.dsl_output = ""

# --- DSL Display --- #
if st.session_state.dsl_output:
    st.subheader("🧩 Generated Structurizr DSL:")
    st.code(st.session_state.dsl_output, language="dsl")

    # --- Download Option --- #
    st.download_button("⬇️ Download DSL File", st.session_state.dsl_output, file_name="structurizr.dsl")

    # --- Mermaid Preview --- #
    st.subheader("🔍 Mermaid-style Preview")
    saved_result = store.get("latest")
    if saved_result and "structured_info" in saved_result:
        mermaid_code = "graph TD\n"
        for rel in saved_result["structured_info"].get("relationships", []):
            mermaid_code += f"  {rel['source']} -->|{rel['description']}| {rel['target']}\n"
        st.markdown(f"""
        ```mermaid
        {mermaid_code}
        ```
        """, unsafe_allow_html=True)

# --- Optional Reset --- #
if st.button("🔄 Reset"):
    st.session_state.dsl_output = ""
    st.session_state.missing_info = []
    store.clear()
