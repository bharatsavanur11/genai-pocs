from typing import Any, Dict, List, Optional, TypedDict
from langchain_core.pydantic_v1 import BaseModel, Field


class C4State(TypedDict):
    raw_spec: str
    systems: Optional[List[Dict[str, Any]]]
    containers: Optional[List[Dict[str, Any]]]
    components: Optional[List[Dict[str, Any]]]
    relationships: Optional[List[Dict[str, Any]]]
    external_systems: Optional[List[Dict[str, Any]]]
    missing_info: Optional[List[str]]
    summary: Optional[str]
    dsl_context: Optional[str]
    dsl_container: Optional[str]
    dsl_component: Optional[str]
    dsl_context_container: Optional[str]
    architecture_analysis: Optional[Dict[str, Any]]


class SystemInfo(BaseModel):
    name: str = Field(description="Name of the system")
    description: str = Field(description="Description of the system's purpose")
    technology: Optional[str] = Field(description="Technology stack if mentioned")
    tags: List[str] = Field(description="Relevant tags for categorization")


class ContainerInfo(BaseModel):
    name: str = Field(description="Name of the container")
    system: str = Field(description="System this container belongs to")
    description: str = Field(description="Description of the container's purpose")
    technology: Optional[str] = Field(description="Technology stack if mentioned")
    tags: List[str] = Field(description="Relevant tags for categorization")


class ComponentInfo(BaseModel):
    name: str = Field(description="Name of the component")
    container: str = Field(description="Container this component belongs to")
    description: str = Field(description="Description of the component's purpose")
    technology: Optional[str] = Field(description="Technology stack if mentioned")
    tags: List[str] = Field(description="Relevant tags for categorization")


class RelationshipInfo(BaseModel):
    source: str = Field(description="Source component/system/container")
    destination: str = Field(description="Destination component/system/container")
    description: str = Field(description="Nature of the interaction")
    technology: Optional[str] = Field(description="Protocol/technology if mentioned")
    relationship_type: str = Field(description="Type of relationship: uses, depends_on, communicates_with")


class ArchitectureAnalysis(BaseModel):
    systems: List[SystemInfo]
    containers: List[ContainerInfo]
    components: List[ComponentInfo]
    relationships: List[RelationshipInfo]
    external_systems: List[SystemInfo]
    missing_info: List[str]
    summary: str


