from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
import uuid

class ManagedTaskState(BaseModel):
    """
    Represents the state of a managed task within the LangGraph workflow.
    """
    task_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    current_step: str = "initial"
    status: str = "pending"  # e.g., "pending", "in_progress", "waiting_for_agent", "completed", "failed"
    history: List[Dict[str, Any]] = Field(default_factory=list)  # List of events or steps taken
    agent_responses: Dict[str, Any] = Field(default_factory=dict) # Stores responses from agents
    error_info: Optional[Dict[str, Any]] = None # Details if an error occurs

    class Config:
        arbitrary_types_allowed = True