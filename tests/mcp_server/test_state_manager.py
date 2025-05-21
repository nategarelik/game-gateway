import pytest
import uuid
from typing import Dict, Any

from src.mcp_server.core.state_manager import StateManager
from src.mcp_server.models.managed_task_state import ManagedTaskState

@pytest.fixture
def state_manager() -> StateManager:
    """Fixture to provide a StateManager instance for tests."""
    return StateManager()

def test_initialize_task_graph(state_manager: StateManager):
    """
    Tests if the StateManager can initialize a new graph for a task.
    """
    task_id = str(uuid.uuid4())
    initial_input: Dict[str, Any] = {"action": "test_action", "data": {"value": 123}}
    
    initial_state = state_manager.initialize_task_graph(task_id=task_id, initial_input=initial_input)
    
    assert initial_state is not None
    assert isinstance(initial_state, ManagedTaskState)
    assert initial_state.task_id == task_id
    assert initial_state.status == "pending" # Should be the pristine state
    assert initial_state.current_step == "initial" # Should be the pristine state
    assert task_id in state_manager.graphs
    # After only initialization, get_graph_state should return None as no steps have run to populate the checkpointer
    retrieved_state_after_init = state_manager.get_graph_state(task_id)
    assert retrieved_state_after_init is None

def test_invoke_simple_graph_transitions_state(state_manager: StateManager):
    """
    Tests if a simple graph can be invoked and transitions through its states
    to completion.
    """
    task_id = str(uuid.uuid4())
    initial_input: Dict[str, Any] = {"action": "run_simple_workflow", "details": "test run"}
    
    # Initialize
    init_state = state_manager.initialize_task_graph(task_id=task_id, initial_input=initial_input)
    assert init_state is not None
    assert init_state.task_id == task_id
    
    # Invoke the graph
    # For the simple graph defined, this should run it to completion.
    final_state = state_manager.invoke_graph_update(task_id=task_id, event_input=initial_input)
    
    assert final_state is not None
    assert isinstance(final_state, ManagedTaskState)
    assert final_state.task_id == task_id
    assert final_state.status == "completed"
    assert final_state.current_step == "completed" # As per the _end_task_node
    assert len(final_state.history) > 1 # Should have at least start, process, end
    
    # Verify history entries (example check for one entry)
    assert any(entry["step"] == "start_task" for entry in final_state.history)
    assert any(entry["step"] == "process_request_initiated" for entry in final_state.history)
    assert any(entry["step"] == "end_task" for entry in final_state.history)

    # Check agent_responses based on the simple graph's behavior
    # The simple graph sets 'unknown_agent' if target_agent_id is not in initial_input
    # or uses the target_agent_id from initial_input.
    # For the provided initial_input, target_agent_id is not present.
    assert "unknown_agent" in final_state.agent_responses
    assert final_state.agent_responses["unknown_agent"]["status"] == "dispatched"
    # The simple graph uses 'unknown_agent' if target_agent_id is not in initial_input.
    # The value is {"status": "dispatched"}.
    assert "unknown_agent" in final_state.agent_responses
    assert final_state.agent_responses["unknown_agent"] == {"status": "dispatched"}

def test_get_graph_state_after_invocation(state_manager: StateManager):
    """
    Tests retrieving graph state after it has been invoked.
    """
    task_id = str(uuid.uuid4())
    initial_input: Dict[str, Any] = {"action": "get_state_test"}
    
    state_manager.initialize_task_graph(task_id=task_id, initial_input=initial_input)
    invoked_state = state_manager.invoke_graph_update(task_id=task_id, event_input=initial_input)
    
    assert invoked_state is not None
    
    retrieved_state = state_manager.get_graph_state(task_id)
    
    assert retrieved_state is not None
    assert retrieved_state.task_id == task_id
    assert retrieved_state.status == "completed" # Assuming simple graph runs to completion
    assert retrieved_state.current_step == "completed"
    assert retrieved_state.model_dump() == invoked_state.model_dump() # States should be identical

def test_get_graph_state_not_found(state_manager: StateManager):
    """
    Tests retrieving state for a non-existent task_id.
    """
    non_existent_task_id = "task_does_not_exist"
    retrieved_state = state_manager.get_graph_state(non_existent_task_id)
    assert retrieved_state is None

def test_invoke_graph_not_found(state_manager: StateManager):
    """
    Tests invoking a graph for a non-existent task_id.
    """
    non_existent_task_id = "task_does_not_exist_for_invoke"
    result_state = state_manager.invoke_graph_update(non_existent_task_id)
    assert result_state is None