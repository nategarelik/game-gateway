import pytest
import json
from unittest.mock import patch, MagicMock

# Adjust import path based on your project structure.
# This assumes 'src' is in PYTHONPATH or tests are run from project root.
from src.mcp_server.server_core import app as flask_app, MCPServer, Agent

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    # MCPServer instance is now managed by mcp_server_mock_management (autouse=True fixture),
    # and get_mcp_server_instance() should be patched by it to return the correct mock.
    flask_app.config.update({"TESTING": True})
    yield flask_app

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture
def mock_mcp_server(app):
    """Returns the mocked MCPServer instance used by the app context."""
    # This relies on the patching done in the app fixture.
    # We need to get the instance that the app's routes will actually use.
    # After app() fixture has run, server_core.get_mcp_server_instance() will return the mocked one.
    return flask_app.extensions['mcp_server_instance_for_test'] # Assuming we store it like this

# A more robust way to get the mock_mcp_server if the above doesn't work:
@pytest.fixture(autouse=True) # Autouse to ensure it's available
def mcp_server_mock_management(monkeypatch):
    """Manages the MCPServer mock instance for tests."""
    mock_server = MagicMock(spec=MCPServer)
    mock_server.agents = {} # Initialize agents dict
    
    # Mock the handle_api_request method to behave like the original but on the mock instance
    # This allows us to spy on it or add specific side effects per test if needed,
    # while still testing the original logic if we don't override its side_effect.
    mock_server.handle_api_request = MagicMock(side_effect=lambda req_data: MCPServer.handle_api_request(mock_server, req_data))

    # This function will be called by the app to get the server instance
    def get_mocked_instance():
        return mock_server

    monkeypatch.setattr('src.mcp_server.server_core.get_mcp_server_instance', get_mocked_instance)
    return mock_server


def test_execute_agent_success(client, mcp_server_mock_management):
    """Test successful agent execution."""
    mock_agent_id = "test_agent"
    mock_task_id = "task_123"
    mock_request_params = {"param1": "value1"}
    mock_agent_response = {"status": "agent_success", "data": "agent_data"}

    # Setup the mock agent and its behavior
    mock_agent_instance = MagicMock(spec=Agent) # Use your actual Agent base class if available
    mock_agent_instance.handle_direct_request = MagicMock(return_value=mock_agent_response)
    mcp_server_mock_management.agents[mock_agent_id] = mock_agent_instance
    
    # Ensure handle_api_request will use the mocked agent
    # The mcp_server_mock_management fixture already sets up handle_api_request
    # to use the logic from MCPServer class but on the mock_server instance.

    response = client.post('/execute_agent',
                           json={
                               "task_id": mock_task_id,
                               "agent_id": mock_agent_id,
                               "parameters": mock_request_params
                           })

    assert response.status_code == 200
    response_data = response.get_json()
    assert response_data["task_id"] == mock_task_id
    assert response_data["status"] == "success"
    assert response_data["result"] == mock_agent_response
    assert response_data["error"] is None

    mock_agent_instance.handle_direct_request.assert_called_once_with(mock_request_params)
    # Verify that the server's handle_api_request was called
    mcp_server_mock_management.handle_api_request.assert_called_once()


def test_execute_agent_agent_not_found(client, mcp_server_mock_management):
    """Test agent not found error."""
    mock_task_id = "task_456"
    non_existent_agent_id = "non_existent_agent"

    # Ensure the agent is not in the mocked server's agents dictionary
    mcp_server_mock_management.agents = {}

    response = client.post('/execute_agent',
                           json={
                               "task_id": mock_task_id,
                               "agent_id": non_existent_agent_id,
                               "parameters": {}
                           })

    assert response.status_code == 404 # As per server_core.py logic
    response_data = response.get_json()
    assert response_data["task_id"] == mock_task_id
    assert response_data["status"] == "failed"
    assert response_data["result"] is None
    assert response_data["error"]["code"] == "AGENT_NOT_FOUND"
    assert non_existent_agent_id in response_data["error"]["message"]

def test_execute_agent_missing_task_id(client, mcp_server_mock_management):
    """Test error when task_id is missing."""
    response = client.post('/execute_agent',
                           json={
                               # "task_id": "missing",
                               "agent_id": "some_agent",
                               "parameters": {}
                           })
    
    assert response.status_code == 400 # As per server_core.py logic
    response_data = response.get_json()
    assert response_data["status"] == "failed"
    assert response_data["error"]["code"] == "INVALID_REQUEST"
    assert "Missing task_id" in response_data["error"]["message"]

def test_execute_agent_missing_agent_id(client, mcp_server_mock_management):
    """Test error when agent_id is missing."""
    response = client.post('/execute_agent',
                           json={
                               "task_id": "task_789",
                               # "agent_id": "missing",
                               "parameters": {}
                           })

    assert response.status_code == 400 # As per server_core.py logic
    response_data = response.get_json()
    assert response_data["status"] == "failed"
    assert response_data["error"]["code"] == "INVALID_REQUEST"
    assert "agent_id" in response_data["error"]["message"] # Check if 'agent_id' is mentioned in the error

def test_execute_agent_invalid_json(client, mcp_server_mock_management):
    """Test error when request body is not JSON."""
    response = client.post('/execute_agent',
                           data="not a json string",
                           content_type="text/plain")

    assert response.status_code == 400
    response_data = response.get_json()
    assert response_data["status"] == "failed"
    assert response_data["error"]["code"] == "INVALID_REQUEST"
    assert "Request content type must be application/json" in response_data["error"]["message"]

# (Optional) Placeholder for testing toolchain routes if needed
# def test_execute_agent_muse_toolchain(client, mcp_server_mock_management):
#     pass

# def test_execute_agent_retro_diffusion_toolchain(client, mcp_server_mock_management):
#     pass

# (Optional) Placeholder for testing agent's handle_direct_request error propagation
# def test_execute_agent_internal_agent_error(client, mcp_server_mock_management):
#     mock_agent_id = "error_agent"
#     mock_task_id = "task_err"
#     mock_request_params = {"param1": "value1"}

#     mock_agent_instance = MagicMock()
#     mock_agent_instance.handle_direct_request = MagicMock(side_effect=ValueError("Agent internal error"))
#     mcp_server_mock_management.agents[mock_agent_id] = mock_agent_instance
    
#     response = client.post('/execute_agent',
#                            json={
#                                "task_id": mock_task_id,
#                                "agent_id": mock_agent_id,
#                                "parameters": mock_request_params
#                            })

#     assert response.status_code == 500 # Or appropriate error code based on server handling
#     response_data = response.get_json()
#     assert response_data["status"] == "failed"
#     # Further assertions on the error structure based on how MCPServer wraps agent errors.
#     # The current MCPServer.handle_api_request wraps generic exceptions as EXECUTION_ERROR.
#     assert response_data["error"]["code"] == "EXECUTION_ERROR" 
#     assert "Agent internal error" in response_data["error"]["message"]