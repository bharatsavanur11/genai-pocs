"""Streamlit chat UI for the investment banking assistant."""
import json
import os
import uuid

import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langchain_openai import ChatOpenAI

st.set_page_config(page_title="IB Assistant", page_icon="📈")
st.title("📈 Investment Banking Assistant")
st.caption("Educational analysis only, not investment advice.")

with st.sidebar:
    st.header("Settings")
    api_key = st.text_input("OpenAI API key", value=os.getenv("OPENAI_API_KEY", ""), type="password")
    model = st.text_input("Model", value=os.getenv("OPENAI_MODEL", "gpt-4o-mini"))
    sec_ua = st.text_input("SEC User-Agent", value=os.getenv("SEC_USER_AGENT", ""),
                           placeholder="Your Name you@email.com",
                           help="SEC requires contact info in the User-Agent for EDGAR requests.")
    if st.button("New conversation"):
        st.session_state.clear()
        st.rerun()
    st.markdown("**Try:**")
    examples = [
        "Compare AAPL, MSFT and GOOGL on EV/EBITDA and P/E",
        "Pull MSFT's last 5 years of financials from SEC and run a DCF at 9% WACC, 2.5% terminal growth",
        "Find recent 8-Ks mentioning 'tender offer' and summarise the deal terms",
        "How is RELIANCE trading on NSE, and what are its latest announcements?",
        "LBO: 100 EBITDA, 10x entry and exit, 60% debt, 8% growth. IRR?",
    ]
    for ex in examples:
        if st.button(ex, use_container_width=True):
            st.session_state["queued"] = ex

if not api_key:
    st.info("Enter your OpenAI API key in the sidebar to start.")
    st.stop()

# Must be set before edgar_tools is imported, since it reads the env var at import time.
if sec_ua:
    os.environ["SEC_USER_AGENT"] = sec_ua
os.environ["OPENAI_API_KEY"] = api_key


@st.cache_resource
def get_graph(model_name: str, key: str):
    from finance_bot import build_graph  # imported lazily so SEC_USER_AGENT is applied
    return build_graph(ChatOpenAI(model=model_name, api_key=key))


graph = get_graph(model, api_key)
st.session_state.setdefault("thread_id", str(uuid.uuid4()))
st.session_state.setdefault("history", [])  # [{"role", "content", "tools"}]


def render_tools(tools):
    for t in tools:
        with st.expander(f"🔧 {t['name']}({', '.join(f'{k}={v!r}' for k, v in t['args'].items())})"):
            try:
                st.json(json.loads(t["result"]))
            except (TypeError, ValueError):
                st.code(t["result"][:3000])


for m in st.session_state["history"]:
    with st.chat_message(m["role"]):
        render_tools(m.get("tools", []))
        st.markdown(m["content"])

prompt = st.chat_input("Ask about valuation, M&A, LBOs, filings...") or st.session_state.pop("queued", None)
if prompt:
    st.session_state["history"].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        config = {"configurable": {"thread_id": st.session_state["thread_id"]}}
        tools, pending, answer = [], {}, ""
        with st.status("Thinking...", expanded=False) as status:
            try:
                # "updates" streams each node's output, so tool calls show up as they happen.
                for update in graph.stream({"messages": [HumanMessage(prompt)]}, config, stream_mode="updates"):
                    for node_out in update.values():
                        for msg in node_out["messages"]:
                            if isinstance(msg, AIMessage):
                                for tc in msg.tool_calls:
                                    pending[tc["id"]] = tc
                                    status.update(label=f"Calling {tc['name']}...")
                                if not msg.tool_calls:
                                    answer = msg.content
                            elif isinstance(msg, ToolMessage):
                                tc = pending.get(msg.tool_call_id, {"name": msg.name, "args": {}})
                                tools.append({"name": tc["name"], "args": tc["args"], "result": str(msg.content)})
                status.update(label=f"Done ({len(tools)} tool calls)", state="complete")
            except Exception as e:  # surface API/network errors instead of a stack trace
                status.update(label="Error", state="error")
                answer = f"Something went wrong: `{type(e).__name__}: {e}`"
        render_tools(tools)
        st.markdown(answer)
    st.session_state["history"].append({"role": "assistant", "content": answer, "tools": tools})
