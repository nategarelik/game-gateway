from typing import TypedDict, List, Dict, Any
from pydantic import BaseModel

# Using Pydantic for robust data validation, though TypedDict is also an option
# For LangGraph, the state is often a TypedDict.
# We can define a Pydantic model for internal use and FastAPI,
# and ensure compatibility or conversion if LangGraph strictly needs TypedDict.

class GameDevState(TypedDict, total=False):
    """
    State object that tracks the current state of the game development process.
    Using TypedDict as it's commonly used with LangGraph.
    `total=False` makes all fields optional by default.
    """
    project_metadata: Dict[str, Any]
    assets: Dict[str, Any] # e.g., {"characters": [...], "environments": [...]}
    current_tasks: List[str]
    completed_tasks: List[str]
    agent_outputs: List[Dict[str, Any]] # To store outputs from agents
    # Add other relevant state fields as needed

class GameDevStatePydantic(BaseModel):
    """
    Pydantic version of the game development state for API validation etc.
    """
    project_metadata: Dict[str, Any] = {}
    assets: Dict[str, Any] = {}
    current_tasks: List[str] = []
    completed_tasks: List[str] = []
    agent_outputs: List[Dict[str, Any]] = []

    class Config:
        extra = "allow" # Allow extra fields not explicitly defined

# Example of a more specific asset type
class CharacterAsset(BaseModel):
    name: str
    description: str
    attributes: Dict[str, Any] = {}
    # ... other character-specific fields

# Placeholder for now, actual state fields will evolve.