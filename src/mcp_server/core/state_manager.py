# MCP Server State Management (LangGraph Integration)
from typing import Dict, Any, Optional, TypedDict
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from src.mcp_server.models.managed_task_state import ManagedTaskState

# Define the state structure for LangGraph
class GraphState(TypedDict):
    task_state: ManagedTaskState
    input_data: Optional[Dict[str, Any]] = None # Initial input for the task

class StateManager:
    """
    Manages LangGraph instances for ongoing tasks.
    """
    def __init__(self):
        """
        Initializes the StateManager with an in-memory graph store and checkpointer.
        """
        self.graphs: Dict[str, Any] = {} # Stores compiled graph instances (in-memory for now)
        self.checkpointer = MemorySaver() # In-memory checkpointer. Error said 'InMemorySaver', but import is MemorySaver. Let's stick to MemorySaver.

    def _create_new_graph_definition(self) -> StateGraph:
        """
        Defines the structure of a new LangGraph.
        This is a very basic graph for now.
        """
        graph_builder = StateGraph(GraphState)

        # Define nodes
        graph_builder.add_node("start_task", self._start_task_node)
        graph_builder.add_node("process_request", self._process_request_node)
        # Define a custom end node, do not use the reserved END name directly with add_node
        graph_builder.add_node("custom_end_node", self._end_task_node)

        # Define edges
        graph_builder.set_entry_point("start_task")
        graph_builder.add_edge("start_task", "process_request")
        graph_builder.add_edge("process_request", "custom_end_node")
        graph_builder.set_finish_point("custom_end_node") # Correctly set the graph's finish point
        
        return graph_builder

    def _start_task_node(self, state: GraphState) -> GraphState:
        """
        Node to initialize the task state.
        """
        task_state = state['task_state']
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
        # input_data is the initial input to the graph for this task_id
        initial_graph_input = state.get('input_data', {})
        
        # event_input is the specific data passed to invoke_graph_update,
        # which in our case comes from the agent's /post_event
        # This is not directly part of the GraphState type definition but is implicitly passed
        # by how invoke_graph_update constructs `final_input_for_stream`.
        # The `input_data` field in GraphState is where `event_input` from `invoke_graph_update` lands.
        agent_event_data = initial_graph_input # event_input from invoke_graph_update lands here

        task_state.current_step = "process_request" # Or "processing_agent_event"
        
        log_message = f"Processing/Updating task based on input. Initial graph input: {initial_graph_input}"
        if agent_event_data and agent_event_data != initial_graph_input: # Check if it's different from the very first input
             log_message = f"Processing agent event. Event data: {agent_event_data}"
             # Store agent event details
             agent_id_reporting = agent_event_data.get("source_agent_id", "unknown_agent")
             event_type = agent_event_data.get("event_type", "unknown_event")
             task_state.history.append({
                "step": "agent_event_received",
                "agent_id": agent_id_reporting,
                "event_type": event_type,
                "data": agent_event_data,
                "message": f"Received event '{event_type}' from agent '{agent_id_reporting}'."
             })
             # Example: update agent_responses
             if "status" in agent_event_data: # Assuming agent sends a status in its event_data
                 task_state.agent_responses[agent_id_reporting] = {
                     "last_event_type": event_type,
                     "status": agent_event_data["status"],
                     "details": agent_event_data # Store full event data from agent
                 }
                 # Potentially update overall task_state.status based on agent's reported status
                 if agent_event_data["status"] == "completed_successfully":
                     task_state.status = "nearing_completion" # Or directly to "completed" if this is the final step
                 elif agent_event_data["status"] == "failed":
                     task_state.status = "error"


        else: # This is likely the first pass through this node after 'start_task'
            task_state.history.append({
                "step": "process_request_initiated",
                "message": f"Initial processing for action: {initial_graph_input.get('action_type', 'N/A')} for agent {initial_graph_input.get('target_agent_id', 'N/A')}"
            })
            # Simulate dispatch message
            task_state.agent_responses[initial_graph_input.get('target_agent_id', 'unknown_agent')] = {"status": "dispatched"}


        print(f"Task {task_state.task_id}: In _process_request_node. Log: {log_message}")
        
        return {"task_state": task_state}

    def _end_task_node(self, state: GraphState) -> GraphState:
        """
        Node to mark the task as completed.
        """
        task_state = state['task_state']
        task_state.current_step = "completed"
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

        # Initial invocation to set up the state
        thread_config = {"configurable": {"thread_id": initial_task_state.task_id}}
        
        # The initial input for the graph stream
        graph_input: GraphState = {"task_state": initial_task_state, "input_data": initial_input or {}}

        # Stream events to process the graph until it suspends or finishes
        # We are not processing the full stream here, just initializing
        # The actual processing will happen in invoke_graph_update
        # For initialization, we can just get the state after the first step if needed,
        # but LangGraph's MemorySaver handles the initial state persistence.
        
        # To get the initial state as LangGraph sees it after setup:
        # We can invoke it once to get it into the checkpointer
        # For this simple graph, it will run to completion if we just call stream.
        # Instead, we'll rely on get_graph_state to fetch the state which will be the initial state.
        
        # To ensure the graph is "known" to the checkpointer with its initial state:
        # self.checkpointer.put_state(thread_config, graph_input) # Removed: MemorySaver might not have put_state.
        # The initial state should be retrievable via get_graph_state after compilation
        # or the first invocation will establish it.
        # For a truly clean initial state before any node runs, the GraphState itself is the source.
        # The `get_graph_state` will fetch from checkpointer if available.
        # Let's ensure the graph_input is what we consider the initial state for the purpose of returning.
        # The first actual run of the graph will use this graph_input.
        
        # The `compile` step associates the checkpointer. The state isn't "in" the checkpointer
        # until the graph runs at least one step or is explicitly put (if supported).
        # For now, we will return the constructed initial_task_state.
        # The API contract is to return ManagedTaskState.
        # The `get_graph_state` after this might return None if no steps ran.
        # Let's invoke the first step to ensure it's in the checkpointer.
        
        # Do not run any stream events here. Just setup.
        # The first invocation will run the graph from its entry point.
        # The checkpointer is associated, but no state is in it until the graph runs.
        return initial_task_state # Return the pristine, "pending" state.


    def invoke_graph_update(self, task_id: str, event_input: Optional[Dict[str, Any]] = None) -> Optional[ManagedTaskState]:
        """
        Invokes the graph with new input, advancing its state.
        'event_input' here is conceptual for how an external event might feed data.
        In this simple graph, it's more about running it.
        """
        if task_id not in self.graphs:
            print(f"Error: Graph for task_id {task_id} not found.")
            return None

        compiled_graph = self.graphs[task_id]
        thread_config = {"configurable": {"thread_id": task_id}}
        
        # The input for the graph stream. For this simple graph, the 'input_data'
        # was set at initialization. If subsequent steps needed more specific inputs,
        # they would be passed here.
        # Get state from the graph instance itself
        current_graph_state_snapshot = compiled_graph.get_state(thread_config)
        
        graph_stream_input: GraphState
        if current_graph_state_snapshot is None:
            # First run, no checkpoint exists. Construct the initial GraphState.
            # The ManagedTaskState should be pristine (e.g., status "pending").
            # The event_input becomes the input_data for this first run.
            print(f"Task {task_id}: No checkpoint found, starting fresh.")
            initial_managed_state = ManagedTaskState(task_id=task_id) # Ensure task_id is set
            graph_stream_input = GraphState(task_state=initial_managed_state, input_data=event_input or {})
        else:
            # Resuming from a checkpoint. The `event_input` is for the next step(s).
            # LangGraph's stream will use the checkpointed state and pass `event_input` to the appropriate node.
            # However, the `input` to stream should be the new data, not the full state.
            # If the graph is designed for the entry node to receive the full GraphState,
            # and subsequent nodes to receive specific inputs, this needs careful handling.
            # For now, let's assume `event_input` is the data for the next step.
            # The `_start_task_node` expects a full GraphState. If we are resuming *at* start_task,
            # this is tricky. But `start_task` should only run once.
            # If resuming, the `input` to stream is the data for the *currently pending* node.
            # For simplicity, if resuming, we'll pass the event_input. LangGraph handles state.
            # The issue is if the `_start_task_node` is re-entered, it needs `task_state`.
            # This implies the `input` to `stream` should always be the full `GraphState` if the
            # nodes always expect it. Or, nodes must be designed to handle partial inputs.

            # Let's assume for now that if a checkpoint exists, LangGraph handles providing the
            # full state to the node, and `event_input` is merged or used as new data.
            # The `input` to `stream` is the new data for the *current* invocation, not the whole state.
            # The nodes themselves receive the full `GraphState` (merged by Pregel).
            # So, `event_input` is the correct thing to pass as `input` to `stream` when resuming.
            # The `KeyError` happens because the `state` argument to `_start_task_node` is `event_input`.
            # This means when `stream` starts from entry point, `input` becomes the initial `state`.
            # So, `input` must always be a valid `GraphState`.

            if not hasattr(current_graph_state_snapshot, 'values') or not isinstance(current_graph_state_snapshot.values, dict):
                print(f"Error: Current state snapshot for task {task_id} does not have expected 'values' dictionary structure.")
                return None
            current_graph_values: GraphState = current_graph_state_snapshot.values
            
            # Construct the input for the stream: take the checkpointed state and update its input_data part.
            graph_stream_input = current_graph_values.copy() # Make a copy to modify
            graph_stream_input['input_data'] = event_input or {}
            # Ensure task_state is present from the checkpoint
            if 'task_state' not in graph_stream_input:
                 print(f"Error: task_state missing from checkpoint for task {task_id} when resuming.")
                 # This case should ideally not happen if checkpointing is correct.
                 # Fallback to a new ManagedTaskState if absolutely necessary, though this indicates a problem.
                 graph_stream_input['task_state'] = ManagedTaskState(task_id=task_id, status="resuming_error")


        # The input to stream should be the full GraphState object.
        # If resuming, LangGraph uses the checkpointed state and merges the input.
        # If starting fresh, this input is the initial state.
        # The `_start_task_node` expects `task_state` to be in its input `state` dictionary.
        # So, `graph_stream_input` must be a valid `GraphState`.
        

        final_input_for_stream: GraphState
        if current_graph_state_snapshot is None:
            # First run for this thread_id, no checkpoint exists
            print(f"Task {task_id}: invoke_graph_update - No checkpoint, creating initial GraphState.")
            final_input_for_stream = GraphState(
                task_state=ManagedTaskState(task_id=task_id),
                input_data=event_input or {}
            )
        else:
            # Checkpoint exists. We need to provide a GraphState that LangGraph can use.
            # LangGraph will merge this with the checkpoint.
            # The `input` to stream is often just the new data for the pending node.
            # However, our nodes are written to expect the full GraphState dictionary.
            # If the graph is truly resuming at a node that expects the full state,
            # we need to construct it. If it expects partial input, this is different.
            # Given _start_task_node expects full GraphState, and it's an entry point,
            # this path (resuming at start_task) should ideally not happen if start_task completes.
            # If it *does* happen (e.g. graph was interrupted before start_task saved its state),
            # then providing a full GraphState is necessary.

            print(f"Task {task_id}: invoke_graph_update - Checkpoint found. Constructing GraphState for stream.")
            checkpoint_values = current_graph_state_snapshot.values
            
            # Ensure checkpoint_values is a dict, as expected for GraphState
            if not isinstance(checkpoint_values, dict):
                print(f"Error: Checkpoint values for task {task_id} is not a dict. Checkpoint: {checkpoint_values}")
                # Fallback to a fresh state if checkpoint is malformed
                final_input_for_stream = GraphState(
                    task_state=ManagedTaskState(task_id=task_id, status="error_bad_checkpoint"),
                    input_data=event_input or {}
                )
            else:
                # Use task_state from checkpoint, or a new one if not present (should be present)
                resumed_task_state = checkpoint_values.get('task_state')
                if not isinstance(resumed_task_state, ManagedTaskState):
                    print(f"Warning: task_state in checkpoint for task {task_id} is not ManagedTaskState or missing. Re-initializing.")
                    resumed_task_state = ManagedTaskState(task_id=task_id)
                
                # Prefer new event_input for input_data, fallback to checkpoint's input_data
                updated_input_data = event_input if event_input is not None else checkpoint_values.get('input_data', {})

                final_input_for_stream = GraphState(
                    task_state=resumed_task_state,
                    input_data=updated_input_data
                )

        final_state_values = None
        for event in compiled_graph.stream(input=final_input_for_stream, config=thread_config):
            # The `event` dictionary contains the latest state of the graph after each step.
            # The key is the node name, and the value is the output of that node.
            # The full state is updated in the checkpointer automatically.
            # We are interested in the final state after the stream completes.
            # The last event in the stream for a non-looping graph will be from the END node.
            # The state is accessible via `checkpointer.get_state(thread_config)`
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