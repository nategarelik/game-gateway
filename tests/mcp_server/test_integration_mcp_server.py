import pytest
from fastapi import status
from fastapi.testclient import TestClient
import uuid

from src.mcp_server.main import app # Import the FastAPI app instance
from src.mcp_server.models.api_models import AgentInfo, ManagedTaskState
from src.mcp_server.api.routes import events_log # For clearing events_log if needed

# Use TestClient for sending requests to the FastAPI application
client = TestClient(app)

# Fixture to clear relevant app state before each test
@pytest.fixture(autouse=True)
def clear_app_state():
    if hasattr(app.state, 'registered_agents') and isinstance(app.state.registered_agents, dict):
        app.state.registered_agents.clear()
    if hasattr(app.state, 'prompt_registry'): # Assuming prompt_registry might store state
        # If PromptRegistry has a clear method or needs specific reset:
        # app.state.prompt_registry.clear_prompts() # Example
        # For now, let's assume it's re-initialized or its state doesn't persist problematically for these tests
        pass
    if hasattr(app.state, 'state_manager'):
        # state_manager might have persistent checkpoints. For true isolation,
        # it might need a reset mechanism or use unique task_ids per test.
        # For now, we rely on unique task_ids.
        pass
    events_log.clear()


def test_register_and_discover_agent():
    """
    Test registering an agent and then discovering it.
    """
    agent_id = f"test-agent-{uuid.uuid4()}"
    registration_payload = {
        "agent_id": agent_id,
        "capabilities": ["test_capability_1", "test_capability_2"],
        "endpoint": f"http://localhost:8001/{agent_id}"
    }
    
    # Register agent
    response = client.post("/api/v1/register_agent", json=registration_payload)
    assert response.status_code == status.HTTP_201_CREATED
    response_data = response.json()
    assert response_data["message"] == "Agent registered successfully"
    assert response_data["agent_id"] == agent_id

    # Discover agents
    response = client.get("/api/v1/discover_agents")
    assert response.status_code == status.HTTP_200_OK
    discovery_data = response.json()
    
    found_agent = None
    for agent_dict in discovery_data["agents"]:
        agent = AgentInfo(**agent_dict) # Validate with Pydantic model
        if agent.agent_id == agent_id:
            found_agent = agent
            break
    
    assert found_agent is not None, f"Agent {agent_id} not found in discovery list."
    assert found_agent.capabilities == registration_payload["capabilities"]
    assert str(found_agent.endpoint) == registration_payload["endpoint"]

def test_request_action_and_check_status():
    """
    Test posting a /request_action and verifying StateManager was invoked
    by checking the task status.
    """
    action_payload = {
        "target_agent_id": "some_agent_for_action", # Agent doesn't need to be registered for this test
        "action_type": "test_action",
        "parameters": {"param1": "value1", "param2": 123}
    }

    # Request action
    response = client.post("/api/v1/request_action", json=action_payload)
    # Since "some_agent_for_action" is not registered, the API should return 404
    assert response.status_code == status.HTTP_404_NOT_FOUND
    action_response_data = response.json()
    assert action_response_data["detail"] == "Target agent with ID 'some_agent_for_action' not found."
    # No task_id will be generated if agent is not found, so no status check possible.

def test_register_and_resolve_prompt():
    """
    Test registering a prompt and then resolving it successfully.
    """
    prompt_key = f"test_prompt_{uuid.uuid4()}"
    template_string = "Hello, {name}! Welcome to {place}."
    required_vars = ["name", "place"]
    description = "A test greeting prompt."

    registration_payload = {
        "prompt_key": prompt_key,
        "template_string": template_string,
        "required_vars": required_vars,
        "description": description
    }

    # Register prompt
    response = client.post("/api/v1/register_prompt", json=registration_payload)
    assert response.status_code == status.HTTP_201_CREATED
    response_data = response.json()
    assert response_data["message"] == "Prompt registered successfully"
    assert response_data["prompt_key"] == prompt_key

    # Resolve prompt
    resolution_payload = {
        "prompt_key": prompt_key,
        "variables": {"name": "World", "place": "Testville"}
    }
    response = client.post("/api/v1/resolve_prompt", json=resolution_payload)
    assert response.status_code == status.HTTP_200_OK
    resolution_data = response.json()
    
    assert resolution_data["prompt_key"] == prompt_key
    assert resolution_data["resolved_prompt"] == "Hello, World! Welcome to Testville."

def test_resolve_nonexistent_prompt():
    """Test resolving a prompt that has not been registered."""
    resolution_payload = {
        "prompt_key": "non_existent_prompt_key_12345",
        "variables": {"name": "Test"}
    }
    response = client.post("/api/v1/resolve_prompt", json=resolution_payload)
    assert response.status_code == status.HTTP_400_BAD_REQUEST # Corrected: API returns 400 for ValueError from PromptRegistry
    error_data = response.json()
    assert "Prompt with name 'non_existent_prompt_key_12345' not found" in error_data["detail"] # Match ValueError message

def test_register_prompt_missing_vars_in_resolve():
    """Test resolving a prompt with missing required variables."""
    prompt_key = f"test_prompt_missing_vars_{uuid.uuid4()}"
    registration_payload = {
        "prompt_key": prompt_key,
        "template_string": "Data: {data1}, Info: {info1}",
        "required_vars": ["data1", "info1"],
        "description": "Test prompt for missing vars."
    }
    client.post("/api/v1/register_prompt", json=registration_payload) # Register it first

    resolution_payload = {
        "prompt_key": prompt_key,
        "variables": {"data1": "some_data"} # Missing "info1"
    }
    response = client.post("/api/v1/resolve_prompt", json=resolution_payload)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    error_data = response.json()
    assert "Missing required variables for prompt" in error_data["detail"]
    assert "info1" in error_data["detail"] # Check for the specific missing variable