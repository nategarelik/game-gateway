import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from src.agents.code_weaver_agent import CodeWeaverAgent
from src.toolchains.unity_bridge import UnityToolchainBridge # Import the actual UnityToolchainBridge

@pytest.fixture
def mock_mcp_server_url():
    return "http://mock-mcp-server.com"

@pytest.fixture
def mock_unity_bridge():
    mock_bridge = AsyncMock(spec=UnityToolchainBridge)
    mock_bridge.execute_script.return_value = {"unity_status": "script_executed", "message": "Mock Unity response"}
    return mock_bridge

@pytest.fixture
def code_weaver_agent(mock_mcp_server_url, mock_unity_bridge):
    agent = CodeWeaverAgent(
        agent_id="test_code_weaver",
        mcp_server_url=mock_mcp_server_url,
        unity_bridge=mock_unity_bridge
    )
    agent.post_event_to_mcp = AsyncMock() # Mock the MCP event posting
    return agent

@pytest.mark.asyncio
async def test_code_weaver_agent_initialization(code_weaver_agent, mock_unity_bridge):
    assert code_weaver_agent.agent_id == "test_code_weaver"
    assert code_weaver_agent.mcp_server_url == "http://mock-mcp-server.com"
    assert code_weaver_agent.unity_bridge == mock_unity_bridge
    assert "script_generation" in code_weaver_agent.capabilities
    assert "game_logic_implementation" in code_weaver_agent.capabilities

@pytest.mark.asyncio
async def test_generate_and_implement_script_success(code_weaver_agent, mock_unity_bridge):
    script_name = "TestScript"
    script_content = "public class TestScript : MonoBehaviour {}"
    script_path = "Assets/Scripts/TestScript.cs"

    result = await code_weaver_agent.generate_and_implement_script(script_name, script_content, script_path)

    mock_unity_bridge.execute_script.assert_awaited_once_with(script_content, script_path)
    assert result["status"] == "success"
    assert "unity_response" in result
    assert result["unity_response"]["unity_status"] == "script_executed"

@pytest.mark.asyncio
async def test_generate_and_implement_script_no_unity_bridge(mock_mcp_server_url):
    agent_no_bridge = CodeWeaverAgent(
        agent_id="test_no_bridge",
        mcp_server_url=mock_mcp_server_url,
        unity_bridge=None
    )
    agent_no_bridge.post_event_to_mcp = AsyncMock()

    script_name = "NoBridgeScript"
    script_content = "public class NoBridgeScript : MonoBehaviour {}"

    result = await agent_no_bridge.generate_and_implement_script(script_name, script_content)

    assert result["status"] == "error"
    assert "UnityToolchainBridge not available" in result["message"]

@pytest.mark.asyncio
async def test_generate_and_implement_script_unity_error(code_weaver_agent, mock_unity_bridge):
    mock_unity_bridge.execute_script.side_effect = Exception("Unity connection failed")

    script_name = "ErrorScript"
    script_content = "public class ErrorScript : MonoBehaviour {}"

    result = await code_weaver_agent.generate_and_implement_script(script_name, script_content)

    assert result["status"] == "error"
    assert "Unity connection failed" in result["message"]

@pytest.mark.asyncio
async def test_process_task_generate_script_success(code_weaver_agent):
    task_details = {
        "task_id": "task_001",
        "task_type": "generate_script",
        "script_name": "NewGameLogic",
        "script_content": "using UnityEngine; public class NewGameLogic : MonoBehaviour {}"
    }

    result = await code_weaver_agent.process_task(task_details)

    code_weaver_agent.post_event_to_mcp.assert_any_call(
        "code_weaver_progress", {"task_id": "task_001", "status": "started", "task_type": "generate_script"}
    )
    code_weaver_agent.post_event_to_mcp.assert_any_call(
        "code_weaver_complete", {"task_id": "task_001", "status": "completed_successfully", "result": result["output"]}
    )
    assert result["status"] == "success"
    assert "Script 'NewGameLogic' processed successfully." in result["message"]

@pytest.mark.asyncio
async def test_process_task_missing_fields(code_weaver_agent):
    task_details = {
        "task_id": "task_002",
        "task_type": "generate_script",
        "script_name": "MissingContent"
        # script_content is missing
    }

    result = await code_weaver_agent.process_task(task_details)

    code_weaver_agent.post_event_to_mcp.assert_any_call(
        "code_weaver_error", {"task_id": "task_002", "status": "failed", "error": "Missing 'script_name' or 'script_content' for script generation/modification task."}
    )
    assert result["status"] == "failure"
    assert "Missing 'script_name' or 'script_content'" in result["message"]

@pytest.mark.asyncio
async def test_process_task_unsupported_type(code_weaver_agent):
    task_details = {
        "task_id": "task_003",
        "task_type": "unsupported_task",
        "script_name": "SomeScript",
        "script_content": "Some content"
    }

    result = await code_weaver_agent.process_task(task_details)

    code_weaver_agent.post_event_to_mcp.assert_any_call(
        "code_weaver_error", {"task_id": "task_003", "status": "failed", "error": "Unsupported task type: unsupported_task"}
    )
    assert result["status"] == "failure"
    assert "Unsupported task type" in result["message"]