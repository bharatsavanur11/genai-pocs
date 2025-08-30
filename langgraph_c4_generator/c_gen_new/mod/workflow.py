from langgraph.graph import END, StateGraph

from .state import C4State
from .nodes import (
    parse_spec_node,
    validate_architecture_node,
    generate_context_dsl_node,
    generate_container_dsl_node,
    merge_context_and_container_node,
    generate_component_dsl_node,
    final_review_node,
)


def create_c4_workflow() -> StateGraph:
    workflow = StateGraph(C4State)

    workflow.add_node("parse_spec", parse_spec_node)
    workflow.add_node("validate_architecture", validate_architecture_node)
    workflow.add_node("generate_context_dsl", generate_context_dsl_node)
    workflow.add_node("final_review", final_review_node)

    workflow.set_entry_point("parse_spec")
    workflow.add_edge("parse_spec", "validate_architecture")
    workflow.add_edge("validate_architecture", "generate_context_dsl")
    workflow.add_edge("generate_context_dsl", "final_review")


    return workflow.compile()


