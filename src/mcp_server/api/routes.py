from fastapi import APIRouter, HTTPException, status, Request
from typing import List, Dict, Any, Optional
import uuid
import logging

from src.mcp_server.models.api_models import (
    AgentRegistrationRequest, AgentRegistrationResponse,
    AgentInfo, DiscoverAgentsResponse,
    PostEventRequest, PostEventResponse,
    ActionRequest, ActionResponse,
    ToolExecutionRequest, ToolExecutionResponse,
    ExecuteAgentRequest, ExecuteAgentResponse, # Added for /execute_agent endpoint
    StatusResponse,
    ManagedTaskState, # Added for task status response
    PromptRegistrationRequest, PromptRegistrationResponse,
    PromptResolutionRequest, PromptResolutionResponse
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# In-memory storage for registered agents and events (for now)
# In a real application, this would be a database or other persistent storage.
events_log: List[Dict[str, Any]] = [] # This can remain local if not shared across app instances or modules

MCP_SERVER_VERSION = "0.1.0-alpha" # Example version

@router.get("/status", response_model=StatusResponse)
async def get_status():
    """
    Returns the current status of the MCP server.
    """
    logger.info("GET /status request received")
    return StatusResponse(status="active", version=MCP_SERVER_VERSION)

@router.post("/register_agent", response_model=AgentRegistrationResponse, status_code=status.HTTP_201_CREATED)
async def register_agent(agent_data: AgentRegistrationRequest, request: Request):
    """
    Allows an agent to register itself with the server.
    Request Body: Agent ID, capabilities, endpoint for direct communication.
    Response: Confirmation or error.
    """
    logger.info(f"POST /register_agent request received for agent_id: {agent_data.agent_id}")
    current_registered_agents: Dict[str, AgentInfo] = request.app.state.registered_agents
    if agent_data.agent_id in current_registered_agents:
        logger.warning(f"Agent {agent_data.agent_id} already registered.")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Agent with ID '{agent_data.agent_id}' already registered."
        )
    
    agent_info = AgentInfo(
        agent_id=agent_data.agent_id,
        capabilities=agent_data.capabilities,
        endpoint=agent_data.endpoint
    )
    current_registered_agents[agent_data.agent_id] = agent_info
    logger.info(f"Agent {agent_data.agent_id} registered successfully.")
    return AgentRegistrationResponse(
        message="Agent registered successfully",
        agent_id=agent_data.agent_id
    )

@router.get("/discover_agents", response_model=DiscoverAgentsResponse)
async def discover_agents(request: Request):
    """
    Returns a list of currently registered agents and their capabilities.
    """
    logger.info("GET /discover_agents request received")
    current_registered_agents: Dict[str, AgentInfo] = request.app.state.registered_agents
    return DiscoverAgentsResponse(agents=list(current_registered_agents.values()))

@router.post("/post_event", response_model=PostEventResponse, status_code=status.HTTP_201_CREATED)
async def post_event(event_data: PostEventRequest, request: Request):
    """
    Allows agents or other systems to post events to the MCP server.
    Request Body: Event type, event data.
    Response: Confirmation.
    """
    event_id = uuid.uuid4()
    logger.info(f"POST /post_event request received. Event Type: {event_data.event_type}, Event ID: {event_id}")
    
    event_record = {
        "event_id": event_id,
        "event_type": event_data.event_type,
        "event_data": event_data.event_data
    }
    events_log.append(event_record) # Storing in-memory for now
    
    state_manager: StateManager = request.app.state.state_manager
    task_id = event_data.task_id

    if not task_id:
        logger.error(f"Event received without task_id in event_data: {event_data.event_data}")
        # Optionally, raise HTTPException or handle as a generic event not tied to a task
        # For now, we'll log and proceed, but the graph update will likely fail or do nothing.
        # Consider raising HTTPException(status_code=400, detail="task_id missing in event_data")
    else:
        logger.info(f"Event for task_id {task_id} will be processed by StateManager.")
        # Pass the agent's specific event_data to the graph.
        # The graph's nodes will need to be designed to interpret this event_input.
        updated_state = await state_manager.invoke_graph_update(task_id=str(task_id), event_input=event_data.event_data)
        if updated_state:
            logger.info(f"Task {task_id} updated by event. New status: {updated_state.status}, Step: {updated_state.current_step}")
        else:
            logger.warning(f"StateManager did not return an updated state for task {task_id} after event {event_data.event_type}, or task not found.")
    
    return PostEventResponse(
        message="Event posted successfully",
        event_id=event_id
    )

@router.post("/request_action", response_model=ActionResponse, status_code=status.HTTP_202_ACCEPTED)
async def request_action(action_data: ActionRequest, request: Request):
    """
    Allows an entity to request an action from a specific agent.
    Request Body: Target Agent ID, action type, parameters.
    Response: Initial acknowledgement; actual result might be asynchronous.
    """
    request_id = uuid.uuid4()
    logger.info(f"POST /request_action request received for agent {action_data.target_agent_id}. Action: {action_data.action_type}. Request ID: {request_id}")
    
    current_registered_agents: Dict[str, AgentInfo] = request.app.state.registered_agents
    if action_data.target_agent_id not in current_registered_agents:
        logger.warning(f"Target agent {action_data.target_agent_id} not found for action request {request_id}.")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Target agent with ID '{action_data.target_agent_id}' not found."
        )
    
    logger.info(f"Action request {request_id} for agent {action_data.target_agent_id} will be dispatched (simulated). Task details will be managed by StateManager.")

    # The request_id can serve as the task_id for LangGraph
    task_id = str(request_id)

    initial_task_input = {
        "task_id": task_id, # Add task_id to the initial input
        "parameters": action_data.parameters or {},
        "action_type": action_data.action_type,
        "target_agent_id": action_data.target_agent_id,
        "original_request_id": str(request_id) # Keep track of original API request ID
    }
    
    try:
        logger.info(f"Initializing LangGraph task {task_id} with input: {initial_task_input}")
        state_manager: StateManager = request.app.state.state_manager
        initial_state = state_manager.initialize_task_graph(task_id=task_id, initial_input=initial_task_input)
        
        if not initial_state:
            logger.error(f"Failed to initialize LangGraph for task {task_id}.")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to initialize task processing."
            )

        logger.info(f"LangGraph task {task_id} initialized. Current state: {initial_state.status}, Step: {initial_state.current_step}")

        # Conceptually, invoke the graph. For this simple graph, it might run to completion.
        # In a real scenario, this might be an async call or just setup.
        # The current StateManager's invoke_graph_update will run the simple graph.
        logger.info(f"Invoking LangGraph task {task_id} for processing...")
        state_manager: StateManager = request.app.state.state_manager
        final_state = await state_manager.invoke_graph_update(task_id=task_id, event_input=initial_task_input) # Pass input again if needed by steps

        if final_state:
            logger.info(f"LangGraph task {task_id} processed. Final state: {final_state.status}, Step: {final_state.current_step}")
        else:
            # This might happen if the graph is designed to pause or if an error occurred during invocation
            logger.warning(f"LangGraph task {task_id} invocation did not return a final state immediately or an error occurred. Check logs.")
            # We still return accepted as the task was initiated. Status can be checked via /task_status
            
    except Exception as e:
        logger.error(f"Error during LangGraph processing for task {task_id}: {e}", exc_info=True)
        # Don't necessarily raise HTTPException here if the goal is to acknowledge the request
        # and let the background processing handle errors, logging them in the task state.
        # However, for initial setup, if init fails, it's an issue.
        # If invoke_graph_update fails, the task state should reflect it.
        # For now, if init fails, we raise. If invoke fails, we log and proceed.

    # The original ActionResponse is fine, as the processing is "asynchronous" from API perspective
    return ActionResponse(
        message="Action request received and task processing initiated.",
        request_id=request_id # This is also the task_id for LangGraph
    )

@router.get("/task_status/{task_id}", response_model=ManagedTaskState) # Optional removed as per model
async def get_task_status(task_id: str, request: Request):
    """
    Retrieves the current state of a managed task.
    """
    logger.info(f"GET /task_status request for task_id: {task_id}")
    state_manager: StateManager = request.app.state.state_manager
    task_state = state_manager.get_graph_state(task_id)
    if not task_state:
        logger.warning(f"Task with ID '{task_id}' not found or no state available.")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with ID '{task_id}' not found or no state available."
        )
    return task_state

@router.post("/execute_agent", response_model=ExecuteAgentResponse, status_code=status.HTTP_200_OK)
async def execute_agent(agent_request: ExecuteAgentRequest, request: Request):
    """
    Allows an external system to request an agent to perform a task or execute a tool.
    This endpoint acts as a unified entry point for various agent-related operations.
    """
    task_id = agent_request.task_id
    agent_id_req = agent_request.agent_id
    parameters = agent_request.parameters

    logger.info(f"POST /execute_agent request received. Task ID: {task_id}, Agent ID: {agent_id_req}, Parameters: {parameters}")

    state_manager = request.app.state.state_manager
    registered_agents = request.app.state.registered_agents

    try:
        if agent_id_req in registered_agents:
            agent_info = registered_agents[agent_id_req]
            # For now, we'll simulate direct execution or pass to state manager
            # In a real scenario, this would involve calling the agent's endpoint
            # or triggering a specific agent workflow via the state manager.
            logger.info(f"Agent '{agent_id_req}' found. Simulating execution.")
            
            # This part needs to be aligned with how agents actually receive and process requests.
            # If agents have their own endpoints, the MCP would forward the request.
            # If agents are internal components, the state manager would orchestrate.
            
            # For now, let's assume the state manager can handle this as a task initiation
            # or a specific step within a task.
            initial_task_input = {
                "task_id": task_id,
                "agent_id": agent_id_req,
                "parameters": parameters,
                "action_type": "execute_agent_request" # A generic action type for this endpoint
            }
            
            # Initialize and invoke a new LangGraph instance for this task
            initial_state = state_manager.initialize_task_graph(task_id=task_id, initial_input=initial_task_input)
            if not initial_state:
                logger.error(f"Failed to initialize LangGraph for task {task_id} via /execute_agent.")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to initialize task processing for agent execution."
                )
            
            # Invoke the graph to process the request. The graph's nodes will determine
            # how the agent_id and parameters are handled (e.g., calling agent's endpoint,
            # triggering internal agent logic).
            final_state = await state_manager.invoke_graph_update(task_id=task_id, event_input=initial_task_input)

            if final_state and final_state.status == "completed":
                return ExecuteAgentResponse(
                    task_id=task_id,
                    status="success",
                    result={"message": f"Agent '{agent_id_req}' executed successfully.", "final_state": final_state.dict()}
                )
            else:
                # If the task is not immediately completed, or if it's still processing
                # or failed within the graph.
                error_message = f"Agent '{agent_id_req}' execution initiated, but task status is '{final_state.status if final_state else 'unknown'}'. Check /task_status/{task_id} for details."
                logger.warning(error_message)
                return ExecuteAgentResponse(
                    task_id=task_id,
                    status="processing" if final_state else "failed",
                    result={"message": error_message},
                    error={"code": "TASK_IN_PROGRESS_OR_FAILED", "message": error_message}
                )

        # Handle specific toolchain calls if they are not registered as agents
        # This part mirrors the logic from server_core.py's handle_api_request
        elif agent_id_req == "muse":
            # Assuming muse_bridge is accessible via app.state or a similar mechanism
            # For now, this is a placeholder. Actual implementation needs the bridge.
            # if request.app.state.muse_bridge is None: raise HTTPException(status_code=503, detail="Muse toolchain not available.")
            # muse_response = request.app.state.muse_bridge.send_command(...)
            logger.info("Muse toolchain call simulated.")
            return ExecuteAgentResponse(task_id=task_id, status="success", result={"message": "Muse toolchain call simulated."})

        elif agent_id_req == "retro_diffusion":
            logger.info("Retro Diffusion toolchain call simulated.")
            return ExecuteAgentResponse(task_id=task_id, status="success", result={"message": "Retro toolchain call simulated."})
        
        elif agent_id_req == "unity":
            logger.info("Unity toolchain call simulated.")
            return ExecuteAgentResponse(task_id=task_id, status="success", result={"message": "Unity toolchain call simulated."})

        else:
            logger.warning(f"Agent or toolchain '{agent_id_req}' not found.")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agent or toolchain with ID '{agent_id_req}' not found."
            )

    except HTTPException:
        raise # Re-raise FastAPI HTTPExceptions
    except Exception as e:
        logger.error(f"Error processing /execute_agent request for task {task_id}, agent {agent_id_req}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An internal server error occurred: {e}"
        )

@router.post("/execute_tool_on_agent", response_model=ToolExecutionResponse, status_code=status.HTTP_202_ACCEPTED)
async def execute_tool_on_agent(tool_request: ToolExecutionRequest, request: Request):
    """
    Allows requesting a specific tool execution on an agent.
    Request Body: Target Agent ID, tool name, parameters.
    Response: Initial acknowledgement.
    """
    execution_id = uuid.uuid4()
    logger.info(f"POST /execute_tool_on_agent request for agent {tool_request.target_agent_id}. Tool: {tool_request.tool_name}. Execution ID: {execution_id}")

    current_registered_agents: Dict[str, AgentInfo] = request.app.state.registered_agents
    if tool_request.target_agent_id not in current_registered_agents:
        logger.warning(f"Target agent {tool_request.target_agent_id} not found for tool execution request.")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Target agent with ID '{tool_request.target_agent_id}' not found."
        )

    # Similar to /request_action, this would involve:
    # 1. Validating if the agent has the tool/capability.
    # 2. Forwarding the request to the agent.
    # 3. Handling responses.
    # For now, log and acknowledge.
    initial_task_input = tool_request.parameters or {}
    initial_task_input["tool_name"] = tool_request.tool_name
    initial_task_input["target_agent_id"] = tool_request.target_agent_id
    initial_task_input["original_execution_id"] = str(execution_id) # Keep track of original API request ID

    # Initialize and invoke a new LangGraph instance for this task
    task_id = str(execution_id)
    
    try:
        logger.info(f"Initializing LangGraph task {task_id} for tool execution with input: {initial_task_input}")
        state_manager: StateManager = request.app.state.state_manager
        initial_state = state_manager.initialize_task_graph(task_id=task_id, initial_input=initial_task_input)
        
        if not initial_state:
            logger.error(f"Failed to initialize LangGraph for tool execution task {task_id}.")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to initialize tool execution task processing."
            )

        logger.info(f"LangGraph tool execution task {task_id} initialized. Current state: {initial_state.status}, Step: {initial_state.current_step}")

        # Invoke the graph to start processing the tool execution
        logger.info(f"Invoking LangGraph tool execution task {task_id} for processing...")
        final_state = await state_manager.invoke_graph_update(task_id=task_id, event_input=initial_task_input)

        if final_state:
            logger.info(f"LangGraph tool execution task {task_id} processed. Final state: {final_state.status}, Step: {final_state.current_step}")
        else:
            logger.warning(f"LangGraph tool execution task {task_id} invocation did not return a final state immediately or an error occurred. Check logs.")
            
    except Exception as e:
        logger.error(f"Error during LangGraph processing for tool execution task {task_id}: {e}", exc_info=True)
        # For now, if init fails, we raise. If invoke fails, we log and proceed.

    return ToolExecutionResponse(
        message="Tool execution request received and acknowledged. Processing is asynchronous.",
        execution_id=execution_id
    )

@router.post("/register_prompt", response_model=PromptRegistrationResponse, status_code=status.HTTP_201_CREATED)
async def register_prompt(prompt_data: PromptRegistrationRequest, request: Request):
    """
    Registers a new prompt template with the PromptRegistry.
    """
    logger.info(f"POST /register_prompt request received for prompt_key: {prompt_data.prompt_key}")
    prompt_registry = request.app.state.prompt_registry
    try:
        prompt_registry.register_prompt(
            prompt_name=prompt_data.prompt_key, # Changed from prompt_key to prompt_name
            template=prompt_data.template_string, # Changed from template_string to template
            required_variables=prompt_data.required_vars, # Changed from required_vars to required_variables
            # description is not a direct param of register_prompt, but could be stored if model is extended
            # For now, we map what the Pydantic model provides to what the method expects.
            # The Pydantic model PromptRegistrationRequest does not have agent_type.
            # So we call register_prompt with available mapped fields.
        )
        logger.info(f"Prompt '{prompt_data.prompt_key}' registered successfully.")
        return PromptRegistrationResponse(
            message="Prompt registered successfully",
            prompt_key=prompt_data.prompt_key
        )
    except ValueError as e:
        logger.error(f"Error registering prompt '{prompt_data.prompt_key}': {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error registering prompt '{prompt_data.prompt_key}': {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while registering the prompt."
        )

@router.post("/resolve_prompt", response_model=PromptResolutionResponse)
async def resolve_prompt(resolution_data: PromptResolutionRequest, request: Request):
    """
    Resolves a registered prompt template with the given variables.
    """
    logger.info(f"POST /resolve_prompt request received for prompt_key: {resolution_data.prompt_key}")
    prompt_registry = request.app.state.prompt_registry
    try:
        resolved_prompt = prompt_registry.resolve_prompt(
            prompt_name=resolution_data.prompt_key, # Changed from prompt_key to prompt_name
            variables=resolution_data.variables
        )
        logger.info(f"Prompt '{resolution_data.prompt_key}' resolved successfully.")
        return PromptResolutionResponse(
            prompt_key=resolution_data.prompt_key,
            resolved_prompt=resolved_prompt
        )
    except KeyError as e:
        logger.error(f"Error resolving prompt '{resolution_data.prompt_key}': Prompt not found. {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Prompt with key '{resolution_data.prompt_key}' not found."
        )
    except ValueError as e:
        logger.error(f"Error resolving prompt '{resolution_data.prompt_key}': {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error resolving prompt '{resolution_data.prompt_key}': {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while resolving the prompt."
        )