from langgraph.graph import StateGraph, END, START
from langchain_openai import ChatOpenAI
from typing import Dict, Any

# Define the state as a typed dictionary
class QAState(Dict[str, Any]):
    question: str
    answer: str | None
    valid: bool | None

# LLM node: answer the question
def answer_node(state: QAState) -> QAState:
    print("Answer Node:", state)
    llm = ChatOpenAI(model="gpt-3.5-turbo", api_key="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")
    question = state["question"]
    answer = llm.invoke(question).content  # Extract content directly
    return {"question": question, "answer": answer}

# Validation node: check if answer contains a keyword
def validate_node(state: QAState) -> QAState:
    print("Validate Node: Checking if 'Python' is in answer:", state["answer"])
    if "Python" in state["answer"]:
        return {"valid": True}
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
graph.add_node("correction", correction_node)

# Define edges
graph.add_edge(START, "answer")
graph.add_edge("answer", "validate")
graph.add_conditional_edges(
    "validate",
    lambda state: "correction" if not state.get("valid", False) else END,
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