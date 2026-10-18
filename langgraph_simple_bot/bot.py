"""Simple LangGraph chatbot: a single-node graph with in-memory conversation history."""
import os
import sys

from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, MessagesState, StateGraph

SYSTEM_PROMPT = "You are a helpful assistant. Answer concisely."


def build_graph(llm):
    def chatbot(state: MessagesState):
        reply = llm.invoke([SystemMessage(content=SYSTEM_PROMPT)] + state["messages"])
        return {"messages": [reply]}

    builder = StateGraph(MessagesState)
    builder.add_node("chatbot", chatbot)
    builder.add_edge(START, "chatbot")
    builder.add_edge("chatbot", END)
    # MemorySaver keeps history per thread_id, so the bot remembers earlier turns.
    return builder.compile(checkpointer=MemorySaver())


def main():
    if not os.getenv("OPENAI_API_KEY"):
        sys.exit("Set OPENAI_API_KEY before running.")
    graph = build_graph(ChatOpenAI(model=os.getenv("OPENAI_MODEL", "gpt-4o-mini")))
    config = {"configurable": {"thread_id": "cli"}}

    print("Bot ready. Type 'quit' to exit.")
    while True:
        try:
            user = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if user.lower() in {"quit", "exit"}:
            break
        if not user:
            continue
        result = graph.invoke({"messages": [("user", user)]}, config)
        print(f"Bot: {result['messages'][-1].content}")


if __name__ == "__main__":
    main()
