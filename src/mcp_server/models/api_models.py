from pydantic import BaseModel, HttpUrl
from typing import List, Dict, Any, Optional # Keep this one
import uuid
from .managed_task_state import ManagedTaskState # Import ManagedTaskState

class AgentRegistrationRequest(BaseModel):
    agent_id: str
    capabilities: List[str]
    endpoint: HttpUrl # Using HttpUrl for validation

class AgentRegistrationResponse(BaseModel):
    message: str
    agent_id: str

class AgentInfo(BaseModel):
    agent_id: str
    capabilities: List[str]
    endpoint: HttpUrl

class DiscoverAgentsResponse(BaseModel):
    agents: List[AgentInfo]

class PostEventRequest(BaseModel):
    event_type: str
    event_data: Dict[str, Any]
    task_id: Optional[str] = None # Add task_id as an optional field

class PostEventResponse(BaseModel):
    message: str
    event_id: uuid.UUID

class ActionRequest(BaseModel):
    target_agent_id: str
    action_type: str
    parameters: Dict[str, Any]

class ActionResponse(BaseModel):
    message: str
    request_id: uuid.UUID

class ToolExecutionRequest(BaseModel):
    target_agent_id: str
    tool_name: str
    parameters: Dict[str, Any]

class ToolExecutionResponse(BaseModel):
    message: str
    execution_id: uuid.UUID

class ExecuteAgentRequest(BaseModel):
    task_id: str
    agent_id: str
    parameters: Dict[str, Any] = {}

class ExecuteAgentResponse(BaseModel):
    task_id: str
    status: str # "success" or "failed"
    result: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None

class StatusResponse(BaseModel):
    status: str
    version: str
    message: str = "MCP Server is operational"
class PromptRegistrationRequest(BaseModel):
    prompt_key: str
    template_string: str
    required_vars: Optional[List[str]] = None
    description: Optional[str] = None

class PromptRegistrationResponse(BaseModel):
    message: str
    prompt_key: str

class PromptResolutionRequest(BaseModel):
    prompt_key: str
    variables: Dict[str, Any]

class PromptResolutionResponse(BaseModel):
    prompt_key: str
    resolved_prompt: str