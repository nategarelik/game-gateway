# tests/agents/test_pixel_forge_agent.py
import pytest
import asyncio
import os
from unittest.mock import AsyncMock, patch

# Ensure the src directory is in the Python path for imports
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from src.agents.pixel_forge_agent import PixelForgeAgent
from src.agents.base_agent import BaseAgent # For type hinting or comparison if needed
from src.toolchains.unity_bridge import UnityToolchainBridge # Import the actual UnityToolchainBridge

# Mock MCP Server URL for tests
MOCK_MCP_URL = "http://localhost:8000/mcp_mock"

@pytest.fixture
def mock_unity_bridge():
    mock_bridge = AsyncMock(spec=UnityToolchainBridge)
    mock_bridge.manipulate_scene.return_value = {"unity_status": "asset_placed", "message": "Mock Unity asset placement response"}
    return mock_bridge

@pytest.fixture
def pixel_forge_agent_instance(mock_unity_bridge):
    """Provides a PixelForgeAgent instance for testing."""
    agent = PixelForgeAgent(
        agent_id="test_pixel_forge_01",
        mcp_server_url=MOCK_MCP_URL,
        unity_bridge=mock_unity_bridge # Pass the mock Unity bridge
    )
    # Mock the HTTP client to prevent actual network calls during unit tests
    agent.http_client = AsyncMock()
    return agent

@pytest.mark.asyncio
async def test_pixel_forge_agent_initialization(pixel_forge_agent_instance: PixelForgeAgent):
    """Test that the PixelForgeAgent initializes correctly."""
    agent = pixel_forge_agent_instance
    assert agent.agent_id == "test_pixel_forge_01"
    assert agent.mcp_server_url == MOCK_MCP_URL
    assert "asset_generation_2d" in agent.capabilities
    assert "asset_generation_3d_placeholder" in agent.capabilities
    assert "asset_placement" in agent.capabilities # New capability
    assert isinstance(agent, BaseAgent)

@pytest.mark.asyncio
async def test_process_task_missing_fields(pixel_forge_agent_instance: PixelForgeAgent):
    """Test task processing when required fields are missing."""
    agent = pixel_forge_agent_instance
    task_details = {
        "task_id": "test_task_incomplete"
        # Missing type, asset_type, and prompt
    }
    
    # Mock post_event_to_mcp to check if it's called
    agent.post_event_to_mcp = AsyncMock()

    result = await agent.process_task(task_details)

    assert result["status"] == "error"
    assert result["task_id"] == "test_task_incomplete"
    assert "Unsupported task type" in result["message"] # Now checks for task_type first
    agent.post_event_to_mcp.assert_called_once()
    call_args = agent.post_event_to_mcp.call_args[1] # Get kwargs
    assert call_args['event_type'] == "agent_task_error"
    assert call_args['event_data']['task_id'] == "test_task_incomplete"

@pytest.mark.asyncio
async def test_process_task_generate_asset_success_placeholder(pixel_forge_agent_instance: PixelForgeAgent):
    """Test successful asset generation task processing (placeholder logic)."""
    agent = pixel_forge_agent_instance
    task_details = {
        "task_id": "test_task_valid_001",
        "type": "generate_asset",
        "asset_type": "image",
        "prompt": "A cute cat illustration",
        "style_guidelines": {"theme": "cartoonish"},
    }

    agent.post_event_to_mcp = AsyncMock() # Mock to check event posting

    # Since asset generation is a placeholder, we expect it to "succeed"
    # and post a completion event.
    with patch('asyncio.sleep', new_callable=AsyncMock) as mock_sleep: # Mock sleep to speed up test
        result = await agent.process_task(task_details)

    assert result["status"] == "completed"
    assert result["task_id"] == "test_task_valid_001"
    assert "result" in result
    assert result["result"]["type"] == "image"
    assert "asset_test_task_valid_001_image" in result["result"]["asset_id"]
    
    mock_sleep.assert_called_once_with(2) # Check that our placeholder sleep was called

    # Check for progress and completion events
    assert agent.post_event_to_mcp.call_count == 2
    progress_call = agent.post_event_to_mcp.call_args_list[0][1]
    completion_call = agent.post_event_to_mcp.call_args_list[1][1]

    assert progress_call['event_type'] == "pixel_forge_progress"
    assert progress_call['event_data']['status'] == "started"
    assert completion_call['event_type'] == "agent_task_completed"
    assert completion_call['event_data']['task_id'] == "test_task_valid_001"
    assert completion_call['event_data']['result']['asset_id'] == result["result"]["asset_id"]

@pytest.mark.asyncio
async def test_generate_image_placeholder(pixel_forge_agent_instance: PixelForgeAgent):
    """Test placeholder generate_image method."""
    agent = pixel_forge_agent_instance
    with patch('asyncio.sleep', new_callable=AsyncMock) as mock_sleep:
        result = await agent.generate_image("test prompt for image")
    assert result["status"] == "simulated_success"
    assert "direct_image" in result["path"]
    mock_sleep.assert_called_once_with(1)

@pytest.mark.asyncio
async def test_generate_texture_placeholder(pixel_forge_agent_instance: PixelForgeAgent):
    """Test placeholder generate_texture method."""
    agent = pixel_forge_agent_instance
    with patch('asyncio.sleep', new_callable=AsyncMock) as mock_sleep:
        result = await agent.generate_texture("test prompt for texture")
    assert result["status"] == "simulated_success"
    assert "direct_texture" in result["path"]
    mock_sleep.assert_called_once_with(1)

@pytest.mark.asyncio
async def test_generate_model_placeholder_placeholder(pixel_forge_agent_instance: PixelForgeAgent):
    """Test placeholder generate_model_placeholder method."""
    agent = pixel_forge_agent_instance
    with patch('asyncio.sleep', new_callable=AsyncMock) as mock_sleep:
        result = await agent.generate_model_placeholder("test prompt for model")
    assert result["status"] == "simulated_success"
    assert "direct_model" in result["path"]
    assert result["path"].endswith(".obj")
    mock_sleep.assert_called_once_with(1)

@pytest.mark.asyncio
async def test_place_asset_in_unity_success(pixel_forge_agent_instance: PixelForgeAgent, mock_unity_bridge):
    agent = pixel_forge_agent_instance
    asset_name = "Cube"
    position = {"x": 1, "y": 2, "z": 3}
    rotation = {"x": 0, "y": 45, "z": 0}
    scale = {"x": 2, "y": 2, "z": 2}

    result = await agent.place_asset_in_unity(asset_name, position, rotation, scale)

    mock_unity_bridge.manipulate_scene.assert_awaited_once_with(
        operation="create_object",
        target_object=asset_name,
        parameters={"position": position, "rotation": rotation, "scale": scale}
    )
    assert result["status"] == "success"
    assert "Asset 'Cube' placed." in result["message"]
    assert "unity_response" in result

@pytest.mark.asyncio
async def test_place_asset_in_unity_no_unity_bridge(pixel_forge_agent_instance):
    agent = pixel_forge_agent_instance
    agent.unity_bridge = None # Simulate no bridge

    result = await agent.place_asset_in_unity("Sphere", {"x": 0, "y": 0, "z": 0}, {"x": 0, "y": 0, "z": 0}, {"x": 1, "y": 1, "z": 1})
    assert result["status"] == "error"
    assert "UnityToolchainBridge not available" in result["message"]

@pytest.mark.asyncio
async def test_place_asset_in_unity_unity_error(pixel_forge_agent_instance, mock_unity_bridge):
    mock_unity_bridge.manipulate_scene.side_effect = Exception("Unity API error")
    agent = pixel_forge_agent_instance

    result = await agent.place_asset_in_unity("Cylinder", {"x": 0, "y": 0, "z": 0}, {"x": 0, "y": 0, "z": 0}, {"x": 1, "y": 1, "z": 1})
    assert result["status"] == "error"
    assert "Unity API error" in result["message"]

@pytest.mark.asyncio
async def test_process_task_place_asset_success(pixel_forge_agent_instance: PixelForgeAgent):
    agent = pixel_forge_agent_instance
    task_details = {
        "task_id": "test_place_task_001",
        "type": "place_asset",
        "asset_name": "TreePrefab",
        "position": {"x": 10, "y": 0, "z": 10},
        "rotation": {"x": 0, "y": 90, "z": 0},
        "scale": {"x": 1.5, "y": 1.5, "z": 1.5}
    }

    agent.place_asset_in_unity = AsyncMock(return_value={"status": "success", "message": "Mock placed", "unity_response": {}})

    result = await agent.process_task(task_details)

    agent.place_asset_in_unity.assert_awaited_once_with(
        task_details["asset_name"],
        task_details["position"],
        task_details["rotation"],
        task_details["scale"]
    )
    # Check for progress and completion events
    assert agent.post_event_to_mcp.call_count == 2
    progress_call = agent.post_event_to_mcp.call_args_list[0][1]
    completion_call = agent.post_event_to_mcp.call_args_list[1][1]

    assert progress_call['event_type'] == "pixel_forge_progress"
    assert progress_call['event_data']['status'] == "started"
    assert completion_call['event_type'] == "agent_task_completed"
    assert completion_call['event_data']['task_id'] == "test_place_task_001"
    assert completion_call['event_data']['result']['status'] == "success"
    assert "Asset 'TreePrefab' placed successfully." in completion_call['event_data']['message']

    assert result["status"] == "completed"
    assert "Asset 'TreePrefab' placed successfully." in result["message"]

@pytest.mark.asyncio
async def test_process_task_place_asset_missing_fields(pixel_forge_agent_instance: PixelForgeAgent):
    agent = pixel_forge_agent_instance
    task_details = {
        "task_id": "test_place_task_002",
        "type": "place_asset",
        "asset_name": "RockPrefab"
        # position is missing
    }

    result = await agent.process_task(task_details)

    assert result["status"] == "error"
    assert "Missing required fields in task_details (task_id, asset_name, position) for place_asset task." in result["message"]
    agent.place_asset_in_unity.assert_not_awaited()
    # Check for progress and error events
    assert agent.post_event_to_mcp.call_count == 2
    progress_call = agent.post_event_to_mcp.call_args_list[0][1]
    error_call = agent.post_event_to_mcp.call_args_list[1][1]

    assert progress_call['event_type'] == "pixel_forge_progress"
    assert progress_call['event_data']['status'] == "started"
    assert error_call['event_type'] == "agent_task_error"
    assert error_call['event_data']['task_id'] == "test_place_task_002"
    assert "Missing required fields" in error_call['event_data']['error']

# Example of how to run tests with pytest:
# Ensure pytest and pytest-asyncio are installed:
# pip install pytest pytest-asyncio
# Then run from the root directory of the project:
# pytest tests/agents/test_pixel_forge_agent.py