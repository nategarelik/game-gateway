# MCP Server State Management (LangGraph Integration)
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
import uuid
from typing import TypedDict, Optional, Dict, Any

from src.mcp_server.models.managed_task_state import ManagedTaskState

# Define the state structure for LangGraph
class GraphState(TypedDict):
    task_state: ManagedTaskState
    input_data: Optional[Dict[str, Any]] = None # Initial input for the task

class StateManager:
    """
    Manages LangGraph instances for ongoing tasks.
    """
    def __init__(self, registered_agents: Dict[str, Any]):
        """
        Initializes the StateManager with an in-memory graph store, checkpointer,
        and a reference to registered agents.
        """
        self.graphs: Dict[str, Any] = {} # Stores compiled graph instances (in-memory for now)
        self.checkpointer = MemorySaver() # In-memory checkpointer.
        self.registered_agents = registered_agents # Reference to the dictionary of registered agent instances

    def _create_new_graph_definition(self) -> StateGraph:
        """
        Defines the structure of a new LangGraph.
        This is a very basic graph for now.
        """
        graph_builder = StateGraph(GraphState)

        # Define nodes
        graph_builder.add_node("start_task", self._start_task_node)
        graph_builder.add_node("process_request", self._process_request_node)
        graph_builder.add_node("dispatch_to_agent", self._dispatch_to_agent_node)
        graph_builder.add_node("handle_agent_response", self._handle_agent_response_node)
        graph_builder.add_node("custom_end_node", self._end_task_node)

        # Define edges
        graph_builder.set_entry_point("start_task")
        graph_builder.add_edge("start_task", "process_request")
        graph_builder.add_edge("process_request", "dispatch_to_agent")
        graph_builder.add_edge("dispatch_to_agent", "handle_agent_response")
        graph_builder.add_edge("handle_agent_response", "custom_end_node")
        graph_builder.set_finish_point("custom_end_node")
        
        return graph_builder

    def _start_task_node(self, state: GraphState) -> GraphState:
        """
        Node to initialize the task state.
        """
        print(f"DEBUG: _start_task_node received state: {state}")
        # If 'task_state' is not in the state, it means this is the initial invocation
        # and the input is the raw initial_input_data.
        if 'task_state' not in state:
            # Create a new ManagedTaskState from the initial input
            initial_input_data = state.get('input_data', {})
            task_id = initial_input_data.get('original_request_id') # Assuming original_request_id is the task_id
            if not task_id:
                # Fallback if original_request_id is not present, though it should be.
                # This might indicate an issue in how initial_input is formed.
                print(f"ERROR: _start_task_node received initial state without task_id in input_data: {state}")
                # For now, let's generate a random one to avoid crashing, but this needs attention.
                task_id = str(uuid.uuid4())
            # Store target_agent_id and initial_parameters in the task_state
            target_agent_id_from_input = initial_input_data.get('target_agent_id')
            initial_params_from_input = initial_input_data.get('parameters')
            task_state = ManagedTaskState(
                task_id=task_id,
                target_agent_id=target_agent_id_from_input,
                initial_parameters=initial_params_from_input
            )
            print(f"DEBUG: _start_task_node created new task_state for task {task_id} with target_agent_id: {target_agent_id_from_input} and initial_parameters: {initial_params_from_input}.")
        else:
            task_state = state['task_state']
            # Ensure target_agent_id and initial_parameters are preserved or updated if necessary
            if not task_state.target_agent_id and state.get('input_data', {}).get('target_agent_id'):
                task_state.target_agent_id = state.get('input_data', {}).get('target_agent_id')
            if not task_state.initial_parameters and state.get('input_data', {}).get('parameters'):
                 task_state.initial_parameters = state.get('input_data', {}).get('parameters')


        task_state.current_step = "start_task"
        task_state.status = "in_progress"
        task_state.history.append({"step": "start_task", "message": "Task initiated."})
        print(f"Task {task_state.task_id}: Started.")
        return {"task_state": task_state}

    def _process_request_node(self, state: GraphState) -> GraphState:
        """
        Example processing node.
        """
        task_state = state['task_state']
        # input_data now consistently holds the latest input for the current step.
        current_input_data = state.get('input_data', {})

        task_state.current_step = "process_request"
        
        # Log the initial request or any subsequent event data
        log_message = f"Processing request. Input: {current_input_data}"
        task_state.history.append({
            "step": "process_request",
            "message": log_message,
            "data": current_input_data
        })

        # Example: If this node is meant to handle initial action requests
        action_type = current_input_data.get('action_type')
        target_agent_id = current_input_data.get('target_agent_id')

        if action_type and target_agent_id:
            task_state.history.append({
                "step": "initial_action_request",
                "message": f"Initial action '{action_type}' requested for agent '{target_agent_id}'."
            })
            # This is where you might decide to transition to dispatch_to_agent
            # For now, the graph directly transitions to dispatch_to_agent.


        print(f"Task {task_state.task_id}: In _process_request_node. Log: {log_message}")
        
        return {"task_state": task_state}

    async def _dispatch_to_agent_node(self, state: GraphState) -> GraphState:
        """
        Node to dispatch the task to a specialized agent and get its response.
        """
        task_state = state['task_state']
        # Retrieve target_agent_id from task_state
        target_agent_id = task_state.target_agent_id if task_state.target_agent_id else 'unknown_agent'
        current_event_input = state.get('input_data', {}) # This is the event data that triggered this step

        task_state.current_step = "dispatch_to_agent"
        task_state.history.append({
            "step": "dispatch_to_agent",
            "message": f"Attempting to dispatch task to agent: {target_agent_id}",
            "agent_id": target_agent_id,
            "action_type": current_event_input.get('action_type') # Action type from the event or original request
        })

        agent_instance = self.registered_agents.get(target_agent_id)
        if agent_instance:
            print(f"Task {task_state.task_id}: Dispatching to actual agent {target_agent_id}.")
            
            # Construct task_details_for_agent:
            # It needs the original parameters and the current event/action context.
            print(f"DEBUG: _dispatch_to_agent_node - task_state.initial_parameters: {task_state.initial_parameters}")
            task_details_for_agent = {
                "task_id": task_state.task_id,
                "parameters": task_state.initial_parameters or {}, # Original parameters
                "current_event": current_event_input # The event that led to this dispatch
            }
            # If the current_event_input contains an 'action_type' or 'status' that the agent
            # uses to determine its next step, it should be accessible here.
            # For example, if an LLM response is in current_event_input, agent needs it.

            try:
                # Call the agent's process_task method with the combined details
                agent_response = await agent_instance.process_task(task_details_for_agent)
                task_state.agent_responses[target_agent_id] = {
                    "status": "completed", # This might be overwritten by agent's actual response status
                    "details": agent_response
                }
                print(f"Task {task_state.task_id}: Received response from {target_agent_id}.")
                # The agent_response itself becomes the input_data for the _handle_agent_response_node
                return {"task_state": task_state, "input_data": agent_response}
            except Exception as e:
                error_msg = f"Error processing task by agent {target_agent_id}: {e}"
                print(f"Task {task_state.task_id}: {error_msg}")
                task_state.status = "error"
                task_state.history.append({"step": "dispatch_to_agent_error", "message": error_msg})
                task_state.agent_responses[target_agent_id] = {
                    "status": "failed",
                    "details": {"error": error_msg}
                }
                return {"task_state": task_state, "input_data": {"error": error_msg, "source_agent_id": target_agent_id}}
        else:
            error_msg = f"Agent {target_agent_id} not found in registered agents."
            print(f"Task {task_state.task_id}: {error_msg}")
            task_state.status = "error"
            task_state.history.append({"step": "dispatch_to_agent_error", "message": error_msg})
            task_state.agent_responses[target_agent_id] = {
                "status": "failed",
                "details": {"error": error_msg}
            }
            return {"task_state": task_state, "input_data": {"error": error_msg, "source_agent_id": target_agent_id}}

    def _handle_agent_response_node(self, state: GraphState) -> GraphState:
        """
        Node to handle the response received from a specialized agent.
        """
        task_state = state['task_state']
        # The 'input_data' at this stage would contain the agent's response
        agent_response_data = state.get('input_data', {})
        source_agent_id = agent_response_data.get("source_agent_id", "unknown_agent")
        event_type = agent_response_data.get("event_type", "unknown_event")

        task_state.current_step = "handle_agent_response"
        task_state.history.append({
            "step": "handle_agent_response",
            "message": f"Received response from agent: {source_agent_id}, Event: {event_type}",
            "agent_id": source_agent_id,
            "event_type": event_type,
            "data": agent_response_data
        })

        # Update agent_responses with the latest from this agent
        task_state.agent_responses[source_agent_id] = {
            "last_event_type": event_type,
            "status": agent_response_data.get("status", "processed"),
            "details": agent_response_data
        }

        # Update overall task status based on agent's reported status
        if agent_response_data.get("status") == "completed_successfully":
            task_state.status = "completed"
        elif agent_response_data.get("status") == "failed":
            task_state.status = "error"
        elif agent_response_data.get("status") == "in_progress":
            task_state.status = "in_progress" # Keep in progress if agent reports so

        print(f"Task {task_state.task_id}: Handled response from {source_agent_id}.")
        return {"task_state": task_state}

    def _end_task_node(self, state: GraphState) -> GraphState:
        """
        Node to mark the task as completed.
        """
        task_state = state['task_state']
        task_state.current_step = "completed"
        if task_state.status != "error": # Don't override error status if set by agent response
            task_state.status = "completed"
        task_state.history.append({"step": "end_task", "message": "Task processing finished."})
        print(f"Task {task_state.task_id}: Completed.")
        return {"task_state": task_state}

    def initialize_task_graph(self, task_id: Optional[str] = None, initial_input: Optional[Dict[str, Any]] = None) -> ManagedTaskState:
        """
        Initializes and compiles a new LangGraph instance for a task.
        Returns the initial state of the task.
        """
        initial_task_state = ManagedTaskState()
        if task_id:
            initial_task_state.task_id = task_id
        
        graph_definition = self._create_new_graph_definition()
        
        # Compile the graph with a checkpointer
        # For a stateful graph, we need to provide a checkpointer.
        # The checkpointer is responsible for saving and loading the state of the graph.
        compiled_graph = graph_definition.compile(checkpointer=self.checkpointer)
        self.graphs[initial_task_state.task_id] = compiled_graph
        
        print(f"Initialized graph for task: {initial_task_state.task_id}")
        
        # Return the initial state. The first invocation will run the graph and persist state.
        return initial_task_state


    async def invoke_graph_update(self, task_id: str, event_input: Optional[Dict[str, Any]] = None) -> Optional[ManagedTaskState]:
        """
        Invokes the graph with new input, advancing its state.
        'event_input' here is the data that will be passed to the next node in the graph.
        LangGraph's Pregel will merge this input with the existing state from the checkpointer.
        """
        if task_id not in self.graphs:
            print(f"Error: Graph for task_id {task_id} not found.")
            return None

        compiled_graph = self.graphs[task_id]
        thread_config = {"configurable": {"thread_id": task_id}}
        
        # The input to stream is the new data for the current invocation.
        # LangGraph's Pregel will merge this with the existing state from the checkpointer.
        # The nodes will receive the combined state.
        # We need to ensure that `event_input` is correctly placed into the `input_data`
        # field of the `GraphState` when it reaches the node.
        # For now, we'll pass `event_input` directly as the input to stream.
        # The nodes will need to be updated to correctly access this.
        
        # To ensure the nodes always receive a full GraphState, we need to construct it here.
        # Get the current state from the checkpointer.
        current_graph_state_snapshot = compiled_graph.get_state(thread_config)
        
        # Determine the starting state for the stream
        if current_graph_state_snapshot is None:
            print(f"No checkpoint found for task {task_id}. Assuming first invocation.")
            # For the very first invocation, the input to stream is the initial GraphState
            # This initial GraphState must contain 'task_state' and 'input_data'
            initial_task_state_for_graph = ManagedTaskState(task_id=task_id)
            stream_input: GraphState = {"task_state": initial_task_state_for_graph, "input_data": event_input or {}}
        else:
            # If a snapshot exists, use its values as the base and update input_data
            current_graph_values: GraphState = current_graph_state_snapshot.values
            current_graph_values['input_data'] = event_input or {} # Update with new event_input
            stream_input = current_graph_values
        
        # Stream events to process the graph until it suspends or finishes
        async for event in compiled_graph.astream(input=stream_input, config=thread_config):
            pass # Process the stream until completion

        # After the stream, the checkpointer has the latest state, retrieve it via the graph.
        final_state_snapshot = compiled_graph.get_state(thread_config) # Get state from the graph instance
        if final_state_snapshot:
            if hasattr(final_state_snapshot, 'values') and isinstance(final_state_snapshot.values, dict):
                final_graph_state: GraphState = final_state_snapshot.values
                return final_graph_state.get("task_state")
            else:
                print(f"Error: Final state snapshot for task {task_id} does not have expected 'values' dictionary structure.")
                return None
        return None


    def get_graph_state(self, task_id: str) -> Optional[ManagedTaskState]:
        """
        Retrieves the current state of a graph instance.
        """
        if task_id not in self.graphs:
            print(f"Error: Graph for task_id {task_id} not found for state retrieval.")
            return None
        
        compiled_graph = self.graphs[task_id]
        thread_config = {"configurable": {"thread_id": task_id}}
        state_snapshot = compiled_graph.get_state(thread_config) # Get state from the graph instance
        
        if state_snapshot:
            if hasattr(state_snapshot, 'values') and isinstance(state_snapshot.values, dict):
                graph_state: GraphState = state_snapshot.values
                return graph_state.get("task_state")
            else:
                print(f"Warning: Retrieved state snapshot for task_id {task_id} does not have 'values' as a dict or is structured unexpectedly.")
                if isinstance(state_snapshot, dict): # Fallback for direct dict state
                    return state_snapshot.get("task_state")
                return None
        else:
            print(f"Warning: No state found in checkpointer for task_id {task_id}.")
            # This might happen if the graph hasn't been invoked yet to store its initial state.
            # Or if the task_id is incorrect.
            return None

# Example Usage (for testing purposes, will be removed or moved to tests)
if __name__ == "__main__":
    manager = StateManager()
    
    # Initialize a task
    task_input = {"action": "generate_report", "data": {"report_type": "sales"}}
    initial_state = manager.initialize_task_graph(initial_input=task_input)
    
    if initial_state:
        print(f"\nInitial state for task {initial_state.task_id}:")
        print(initial_state.model_dump_json(indent=2))

        # Invoke the graph to run it (since it's simple, it will run to completion)
        print(f"\nInvoking graph for task {initial_state.task_id}...")
        final_task_state = manager.invoke_graph_update(initial_state.task_id)

        if final_task_state:
            print(f"\nFinal state for task {final_task_state.task_id} after invocation:")
            print(final_task_state.model_dump_json(indent=2))
        else:
            print(f"Could not get final state for task {initial_state.task_id}")
            
        # Retrieve state again
        retrieved_state = manager.get_graph_state(initial_state.task_id)
        if retrieved_state:
            print(f"\nRetrieved state for task {retrieved_state.task_id} (should be final):")
            print(retrieved_state.model_dump_json(indent=2))
    else:
        print("Failed to initialize task graph.")