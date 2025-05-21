import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient # For async client if needed, TestClient handles it for FastAPI
import uuid

# Assuming your FastAPI app instance is in src.mcp_server.main
# Adjust the import path if your app instance is located elsewhere.
from src.mcp_server.main import app
from src.mcp_server.api.routes import MCP_SERVER_VERSION, events_log

# Use TestClient for sending requests to the FastAPI application
client = TestClient(app)

# Clear in-memory stores before each test function for isolation
@pytest.fixture(autouse=True)
def clear_in_memory_stores(): # Removed 'request' as it's not used
    # Ensure app.state and app.state.registered_agents exist before clearing
    if hasattr(app, 'state'):
        if hasattr(app.state, 'registered_agents') and isinstance(app.state.registered_agents, dict):
            app.state.registered_agents.clear()
        else:
            # If app.state exists but registered_agents doesn't (e.g. startup not fully run for some reason), initialize it
            app.state.registered_agents = {}
    # else:
        # This case should ideally not be hit if TestClient(app) at module level works as expected.
        # If app.state itself doesn't exist, there's a more fundamental issue with app init for tests.
        # For now, we proceed assuming app.state will be created by TestClient.

    events_log.clear() # events_log is a module-level global in routes.py

def test_get_status():
    response = client.get("/api/v1/status")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "active"
    assert data["version"] == MCP_SERVER_VERSION
    assert "message" in data

def test_register_agent_success():
    agent_payload = {
        "agent_id": "test_agent_001",
        "capabilities": ["test_capability_1", "test_capability_2"],
        "endpoint": "http://localhost:8001/agent"
    }
    response = client.post("/api/v1/register_agent", json=agent_payload)
    assert response.status_code == 201
    data = response.json()
    assert data["message"] == "Agent registered successfully"
    assert data["agent_id"] == "test_agent_001"
    # Verify by discovering agents
    discover_response = client.get("/api/v1/discover_agents")
    assert discover_response.status_code == 200
    discovered_agents_data = discover_response.json()
    found_agent = None
    for agent_info in discovered_agents_data["agents"]:
        if agent_info["agent_id"] == "test_agent_001":
            found_agent = agent_info
            break
    assert found_agent is not None
    assert found_agent["capabilities"] == ["test_capability_1", "test_capability_2"]

def test_register_agent_already_exists():
    agent_payload = {
        "agent_id": "test_agent_002",
        "capabilities": ["test"],
        "endpoint": "http://localhost:8002/agent"
    }
    # First registration
    client.post("/api/v1/register_agent", json=agent_payload)
    
    # Attempt to register again
    response = client.post("/api/v1/register_agent", json=agent_payload)
    assert response.status_code == 409 # Conflict
    data = response.json()
    assert data["detail"] == "Agent with ID 'test_agent_002' already registered."

def test_discover_agents_empty():
    response = client.get("/api/v1/discover_agents")
    assert response.status_code == 200
    data = response.json()
    assert data["agents"] == []

def test_discover_agents_with_data():
    agent1_payload = {"agent_id": "agent1", "capabilities": ["c1"], "endpoint": "http://agent1"}
    agent2_payload = {"agent_id": "agent2", "capabilities": ["c2", "c3"], "endpoint": "http://agent2"}
    client.post("/api/v1/register_agent", json=agent1_payload)
    client.post("/api/v1/register_agent", json=agent2_payload)

    response = client.get("/api/v1/discover_agents")
    assert response.status_code == 200
    data = response.json()
    assert len(data["agents"]) == 2
    agent_ids_in_response = {agent["agent_id"] for agent in data["agents"]}
    assert "agent1" in agent_ids_in_response
    assert "agent2" in agent_ids_in_response

def test_post_event_success():
    event_payload = {
        "event_type": "game_state_update",
        "event_data": {"level": 5, "score": 1000}
    }
    response = client.post("/api/v1/post_event", json=event_payload)
    assert response.status_code == 201
    data = response.json()
    assert data["message"] == "Event posted successfully"
    assert "event_id" in data
    try:
        uuid.UUID(data["event_id"]) # Check if it's a valid UUID
    except ValueError:
        pytest.fail("event_id is not a valid UUID")
    
    assert len(events_log) == 1
    assert events_log[0]["event_type"] == "game_state_update"

def test_request_action_success():
    # First, register an agent
    agent_payload = {"agent_id": "action_agent_001", "capabilities": ["do_stuff"], "endpoint": "http://action_agent"}
    client.post("/api/v1/register_agent", json=agent_payload)

    action_payload = {
        "target_agent_id": "action_agent_001",
        "action_type": "perform_task_X",
        "parameters": {"param1": "value1"}
    }
    response = client.post("/api/v1/request_action", json=action_payload)
    assert response.status_code == 202 # Accepted
    data = response.json()
    assert data["message"] == "Action request received and task processing initiated."
    assert "request_id" in data
    try:
        uuid.UUID(data["request_id"])
    except ValueError:
        pytest.fail("request_id is not a valid UUID")

def test_request_action_agent_not_found():
    action_payload = {
        "target_agent_id": "non_existent_agent",
        "action_type": "perform_task_Y",
        "parameters": {}
    }
    response = client.post("/api/v1/request_action", json=action_payload)
    assert response.status_code == 404 # Should be 404 if agent not found, as per route logic
    data = response.json()
    assert data["detail"] == "Target agent with ID 'non_existent_agent' not found."

def test_execute_tool_on_agent_success():
    # Register an agent
    agent_payload = {"agent_id": "tool_agent_001", "capabilities": ["use_tool_A"], "endpoint": "http://tool_agent"}
    client.post("/api/v1/register_agent", json=agent_payload)

    tool_payload = {
        "target_agent_id": "tool_agent_001",
        "tool_name": "tool_A",
        "parameters": {"input": "data"}
    }
    response = client.post("/api/v1/execute_tool_on_agent", json=tool_payload)
    assert response.status_code == 202 # Accepted
    data = response.json()
    assert data["message"] == "Tool execution request received and acknowledged. Processing is asynchronous."
    assert "execution_id" in data
    try:
        uuid.UUID(data["execution_id"])
    except ValueError:
        pytest.fail("execution_id is not a valid UUID")

def test_execute_tool_on_agent_not_found():
    tool_payload = {
        "target_agent_id": "ghost_agent",
        "tool_name": "tool_B",
        "parameters": {}
    }
    response = client.post("/api/v1/execute_tool_on_agent", json=tool_payload)
    assert response.status_code == 404 # Not Found
    data = response.json()
    assert data["detail"] == "Target agent with ID 'ghost_agent' not found."

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "MCP Server is running. Visit /docs for API documentation."}