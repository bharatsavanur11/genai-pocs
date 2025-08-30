from langgraph.graph import StateGraph, END, START
from langchain_openai import ChatOpenAI
from typing import Dict, Any
import openai


##api_key="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"
# Define the state as a typed dictionary
class QAState(Dict[str, Any]):
    question: str
    answer: str | None
    valid: bool | None

# LLM node: answer the question
def answer_node(state: QAState) -> QAState:
    print("Answer Node:", state)
    llm = ChatOpenAI(model="gpt-3.5-turbo",api_key=api_key )
    question = state["question"]
    answer = llm.invoke(question).content  # Extract content directly
    return {"question": question, "answer": answer}

# Validation node: check if answer overwhelmingly supports Python's superiority

def validate_node(state: QAState) -> QAState:
    print("Validate Node: Checking if 'Python' is in answer:", state["answer"])
    if "Python" in state["answer"]:
        return {"valid": True}
    return {"valid": False}

# Validation node: check if answer convincingly argues Python's superiority
def validate_python_superiority(state: QAState) -> QAState:
    prompt = f"""
You are an expert programming language analyst. Given the following answer, determine if it convincingly argues that Python is overwhelmingly better than any other programming language. 
Respond with "Yes" or "No" and a brief justification.

Answer:
{state['answer']}

Is Python overwhelmingly better than any other language according to this answer?
"""
    client = openai.OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )

    content = response.choices[0].message.content.strip().lower()
    # Check if the response starts with "yes"
    if content.startswith("yes"):
        return {"valid": True}
    else:
        return {"valid": False}

# Correction node: rephrase the question
def correction_node(state: QAState) -> QAState:
    print("Correction Node:", state)
    question = state["question"] + " (Please mention Python in your answer.)"
    return {"question": question}

# Build the graph
graph = StateGraph(QAState)
graph.add_node("answer", answer_node)
graph.add_node("validate", validate_node)
graph.add_node("validate_python_superiority",validate_python_superiority)
graph.add_node("correction", correction_node)

# Define edges
graph.add_edge(START, "answer")
graph.add_edge("answer", "validate")
graph.add_conditional_edges(
    "validate",
    lambda state: "validate_python_superiority" if state.get("valid", False) else "correction"
)
# This block adds conditional edges from the "validate" node:
# If the answer is not valid (i.e., does not mention "Python"), the flow goes to the "correction" node.
# Otherwise, if the answer is valid, the workflow ends.
graph.add_conditional_edges(
     "validate_python_superiority",
    lambda state: "correction" if state.get("valid", False) else END,
    {
       "correction": "correction",
        END: END
    }
)
graph.add_edge("correction", "answer")

if __name__ == "__main__":
    initial_state = QAState({"question": "What is your favorite programming language?", "answer": None, "valid": None})
    print("Initial State:", initial_state)
    app = graph.compile()
    for step in app.stream(initial_state):
        print(step)