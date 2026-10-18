"""Investment-banking assistant: LangGraph ReAct-style loop with finance tools."""
import os
import sys

from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from edgar_tools import EDGAR_TOOLS
from finance_tools import FINANCE_TOOLS
from nse_tools import NSE_TOOLS

ALL_TOOLS = FINANCE_TOOLS + EDGAR_TOOLS + NSE_TOOLS

SYSTEM_PROMPT = """You are an investment banking analyst assistant covering M&A, LBOs, \
valuation (DCF, comps, precedents) and capital-markets strategy.
- Use SEC EDGAR tools to ground answers in filings (10-K, 8-K, S-1, merger proxies) and cite the filing URL.
- For DCF/LBO inputs, prefer reported figures from get_sec_financials over estimates.
- For Indian companies use the NSE tools (symbols like RELIANCE, TCS). For multiples/fundamentals use the yfinance tools with a '.NS' suffix (RELIANCE.NS). Amounts are in INR (1 crore = 10 million, 1 lakh = 100 thousand); never mix currencies in a comparison without saying so.
- Use tools for market data and every calculation; never do arithmetic or invent figures yourself.
- State assumptions, method, then conclusion, and flag key risks.
- This is educational analysis, not licensed investment advice."""


def build_graph(llm):
    llm_with_tools = llm.bind_tools(ALL_TOOLS)

    def assistant(state: MessagesState):
        return {"messages": [llm_with_tools.invoke([SystemMessage(content=SYSTEM_PROMPT)] + state["messages"])]}

    builder = StateGraph(MessagesState)
    builder.add_node("assistant", assistant)
    builder.add_node("tools", ToolNode(ALL_TOOLS))
    builder.add_edge(START, "assistant")
    builder.add_conditional_edges("assistant", tools_condition)  # tool call -> tools, else END
    builder.add_edge("tools", "assistant")
    return builder.compile(checkpointer=MemorySaver())


def main():
    if not os.getenv("OPENAI_API_KEY"):
        sys.exit("Set OPENAI_API_KEY before running.")
    graph = build_graph(ChatOpenAI(model=os.getenv("OPENAI_MODEL", "gpt-4o-mini")))
    config = {"configurable": {"thread_id": "cli"}}
    print("Finance bot ready. Type 'quit' to exit.")
    while True:
        try:
            user = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if user.lower() in {"quit", "exit"}:
            break
        if user:
            result = graph.invoke({"messages": [("user", user)]}, config)
            print(f"Bot: {result['messages'][-1].content}")


if __name__ == "__main__":
    main()
