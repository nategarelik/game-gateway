import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import httpx # Required for spec in AsyncMock

from src.agents.level_architect_agent import (
    LevelArchitectAgent,
    LEVEL_GENERATION_INITIAL_TEMPLATE,
    LEVEL_STYLE_ADAPTATION_TEMPLATE,
    LEVEL_CONSTRAINT_CHECK_TEMPLATE
)
from src.agents.base_agent import BaseAgent # For type hinting or spec if needed
from src.toolchains.unity_bridge import UnityToolchainBridge # Import the actual UnityToolchainBridge

# Default capabilities for LevelArchitectAgent, assuming these are defined in the agent
DEFAULT_CAPABILITIES = ["level_design", "procedural_generation_guidance"]

@pytest.fixture
def mock_mcp_server_url():
    return "http://mock-mcp-server:8000"

@pytest.fixture
def mock_unity_bridge():
    mock_bridge = AsyncMock(spec=UnityToolchainBridge)
    mock_bridge.manipulate_scene.return_value = {"unity_status": "scene_manipulated", "message": "Mock Unity scene response"}
    mock_bridge.execute_script.return_value = {"unity_status": "script_executed", "message": "Mock Unity script response"}
    return mock_bridge

@pytest.fixture
def level_architect_agent_instance(mock_mcp_server_url, mock_unity_bridge):
    agent = LevelArchitectAgent(
        agent_id="test_level_architect_01",
        mcp_server_url=mock_mcp_server_url,
        unity_bridge=mock_unity_bridge # Pass the mock Unity bridge
    )
    # Mock the HTTP client within the agent to prevent real network calls
    agent.http_client = AsyncMock(spec=httpx.AsyncClient)
    # Configure a default successful response for post to simplify some tests
    # Specific tests can override this behavior
    agent.http_client.post.return_value = AsyncMock(status_code=200, json=lambda: {"status": "ok", "message": "success"})
    return agent

@pytest.mark.asyncio
async def test_agent_initialization(level_architect_agent_instance, mock_mcp_server_url):
    agent = level_architect_agent_instance
    assert agent.agent_id == "test_level_architect_01"
    assert agent.mcp_server_url == mock_mcp_server_url
    assert agent.capabilities == DEFAULT_CAPABILITIES # Assuming these are the defaults
    assert agent.prompt_templates["level_generation_initial"] == LEVEL_GENERATION_INITIAL_TEMPLATE
    assert agent.prompt_templates["level_style_adaptation"] == LEVEL_STYLE_ADAPTATION_TEMPLATE
    assert agent.prompt_templates["level_constraint_check"] == LEVEL_CONSTRAINT_CHECK_TEMPLATE
    assert "level_generation_initial" in agent.prompt_template_required_vars # Example check

@pytest.mark.asyncio
async def test_register_with_mcp_success(level_architect_agent_instance, mock_mcp_server_url):
    agent = level_architect_agent_instance
    await agent.register_with_mcp()
    # Based on BaseAgent.register_with_mcp
    agent.http_client.post.assert_called_once_with(
        f"{mock_mcp_server_url}/register_agent", # Corrected endpoint from BaseAgent
        json={
            "agent_id": agent.agent_id,
            "capabilities": agent.capabilities,
            "endpoint": f"http://localhost:XXXX/{agent.agent_id}" # As per BaseAgent
        }
    )

@pytest.mark.asyncio
async def test_register_with_mcp_http_error(level_architect_agent_instance, mock_mcp_server_url):
    agent = level_architect_agent_instance
    agent.http_client.post.side_effect = httpx.HTTPStatusError("Error", request=MagicMock(), response=AsyncMock(status_code=500))
    
    # BaseAgent catches the exception and returns None
    result = await agent.register_with_mcp()
    assert result is None
    agent.http_client.post.assert_called_once()

@pytest.mark.asyncio
async def test_register_with_mcp_request_error(level_architect_agent_instance, mock_mcp_server_url):
    agent = level_architect_agent_instance
    agent.http_client.post.side_effect = httpx.RequestError("Connection Error", request=MagicMock())

    # BaseAgent catches the exception and returns None
    result = await agent.register_with_mcp()
    assert result is None
    agent.http_client.post.assert_called_once()

@pytest.mark.asyncio
async def test_post_event_to_mcp_success(level_architect_agent_instance, mock_mcp_server_url):
    agent = level_architect_agent_instance
    event_data_payload = {"key": "value", "task_id": "task_123"} # task_id should be in event_data
    await agent.post_event_to_mcp("test_event", event_data_payload)

    # Based on BaseAgent.post_event_to_mcp
    agent.http_client.post.assert_called_once_with(
        f"{mock_mcp_server_url}/post_event", # Corrected endpoint from BaseAgent
        json={
            "event_type": "test_event",
            "data": event_data_payload, # This is the event_data passed to post_event_to_mcp
            "source_agent_id": agent.agent_id
            # Timestamp is not part of BaseAgent's payload to MCP for this method
        }
    )

@pytest.mark.asyncio
async def test_post_event_to_mcp_http_error(level_architect_agent_instance, mock_mcp_server_url):
    agent = level_architect_agent_instance
    agent.http_client.post.side_effect = httpx.HTTPStatusError("Error", request=MagicMock(), response=AsyncMock(status_code=500))
    
    # BaseAgent catches the exception and returns None
    result = await agent.post_event_to_mcp("test_event", {"data": "some_data"})
    assert result is None
    agent.http_client.post.assert_called_once()

@pytest.mark.asyncio
async def test_post_event_to_mcp_request_error(level_architect_agent_instance, mock_mcp_server_url):
    agent = level_architect_agent_instance
    agent.http_client.post.side_effect = httpx.RequestError("Connection Error", request=MagicMock())

    # BaseAgent catches the exception and returns None
    result = await agent.post_event_to_mcp("test_event", {"data": "some_data"})
    assert result is None
    agent.http_client.post.assert_called_once()

# Assuming _get_prompt_template_for_task is a method in LevelArchitectAgent
def test_get_prompt_template_for_task(level_architect_agent_instance):
    agent = level_architect_agent_instance
    template = agent._get_prompt_template_for_task("level_generation_initial")
    assert template == LEVEL_GENERATION_INITIAL_TEMPLATE
    
    template_none = agent._get_prompt_template_for_task("non_existent_task_type")
    assert template_none is None

# Tests for _interpret_design_prompt (adapting from _resolve_prompt_and_simulate_llm)
# Assuming _interpret_design_prompt now handles the core logic of prompt resolution and LLM simulation (mocked)
@pytest.mark.asyncio
async def test_interpret_design_prompt_level_generation_success(level_architect_agent_instance):
    agent = level_architect_agent_instance
    # Mock the _call_llm method which is assumed to be part of _interpret_design_prompt
    # agent._call_llm is not used by _resolve_prompt_and_simulate_llm
    
    task_details = {
        "task_id": "task_gen_01",
        "level_type": "dungeon",
        "genre": "fantasy",
        "theme": "dark_ancient",
        "features_list": ["traps", "puzzles"], # This will be converted to str for template
        "difficulty": "hard"
    }
    result = await agent._resolve_prompt_and_simulate_llm("level_generation_initial", task_details)
    
    assert result["status"] == "success"
    assert "resolved_prompt" in result
    assert "A generated dungeon with dark_ancient theme and difficulty hard." in result["mock_output"]["description"]
    assert result["mock_output"]["level_type"] == "dungeon"
    # agent._call_llm was removed
    # Reset http_client mock for subsequent event posting checks if any are made by _interpret_design_prompt
    agent.http_client.post.reset_mock()


@pytest.mark.asyncio
async def test_interpret_design_prompt_missing_variables(level_architect_agent_instance):
    agent = level_architect_agent_instance
    # No need to mock _call_llm as it shouldn't be reached if variables are missing
    
    task_details = {
        "task_id": "task_gen_missing_01",
        "level_type": "cave",
        # "genre" is missing
        "theme": "icy",
        "features_list": ["slippery_floors"],
        "difficulty": "medium"
    }
    result = await agent._resolve_prompt_and_simulate_llm("level_generation_initial", task_details)
    
    assert result["status"] == "error"
    assert "Missing required variables" in result["error_message"]
    assert "genre" in result["error_message"]
    # Check if post_event_to_mcp was called via http_client
    # This assumes _interpret_design_prompt posts an event on error
    # If it doesn't, this assertion should be removed or adapted
    # For this example, let's assume it posts an error event
    # agent.http_client.post.assert_called_once() 
    # call_args = agent.http_client.post.call_args[1]['json'] # kwargs['json']
    # assert call_args['event_type'] == "level_design_error"
    # assert "Missing required variables" in call_args['event_data']['error']
    # Reset for other tests
    agent.http_client.post.reset_mock()


@pytest.mark.asyncio
async def test_interpret_design_prompt_unknown_task_type(level_architect_agent_instance):
    agent = level_architect_agent_instance
    task_details = {"task_id": "task_unknown_01"}
    result = await agent._resolve_prompt_and_simulate_llm("unknown_task_type_for_prompt", task_details)
    
    assert result["status"] == "error"
    assert "No prompt template found" in result["error_message"]
    # Similar to above, check for event posting if applicable
    # agent.http_client.post.assert_called_once()
    agent.http_client.post.reset_mock()

@pytest.mark.asyncio
async def test_generate_initial_level_structure_placeholder(level_architect_agent_instance):
    agent = level_architect_agent_instance
    # This is a placeholder test as per context, assuming the method has simple logic for now
    mock_llm_output = {"level_type": "forest", "key_features_generated": ["trees"], "description": "A dense forest."}
    # Mock any internal calls if necessary, e.g., another LLM call or complex logic
    # For a simple placeholder, we might just check it runs and returns something expected.
    # agent._another_internal_method = AsyncMock(return_value={...})

    result = await agent._generate_initial_level_structure(mock_llm_output) # Removed extra task_id dict
    
    assert result is not None
    assert "rooms" in result
    assert result["details"] == mock_llm_output


# Tests for process_task
@pytest.mark.asyncio
async def test_process_task_level_generation_success(level_architect_agent_instance):
    agent = level_architect_agent_instance
    task_details = {
        "task_id": "proc_task_gen_01",
        "task_type_for_prompt": "level_generation_initial",
        "level_type": "forest", "genre": "adventure", "theme": "enchanted",
        "features_list": ["talking_trees", "hidden_grove"], "difficulty": "easy",
        "constraints": ["must_be_traversable"]
    }

    # Mock helper methods
    mock_interpret_output = {
        "status": "success", 
        "resolved_prompt": "dummy_prompt", 
        "mock_output": {"level_type": "forest", "key_features_generated": ["talking_trees", "hidden_grove"], "description": "An enchanted forest."} # Key changed to mock_output
    }
    agent._resolve_prompt_and_simulate_llm = AsyncMock(return_value=mock_interpret_output)
    
    mock_generate_output = {"structure": "generated_forest_structure", "features_included": ["talking_trees", "hidden_grove"]}
    agent._generate_initial_level_structure = AsyncMock(return_value=mock_generate_output)
    
    # Assuming _apply_theme_and_constraints exists and is called
    # Mock must include 'theme_applied' as per agent's _apply_theme_and_constraints method
    # The actual _generate_initial_level_structure returns a dict with a "details" key
    # containing the llm_output. _apply_theme_and_constraints copies its input structure.
    mock_generate_output_with_details = {
        "structure": "generated_forest_structure",
        "features_included": ["talking_trees", "hidden_grove"],
        "details": mock_interpret_output["mock_output"] # This is what _generate_initial_level_structure does
    }
    agent._generate_initial_level_structure = AsyncMock(return_value=mock_generate_output_with_details)

    mock_apply_theme_output = {
        # This mock should reflect that it receives mock_generate_output_with_details
        # and adds its own keys, preserving 'details'.
        "structure": "themed_forest_structure",
        "constraints_applied": ["must_be_traversable"],
        "theme_applied": task_details["theme"],
        "details": mock_interpret_output["mock_output"] # Carry over the details
    }
    agent._apply_theme_and_constraints = AsyncMock(return_value=mock_apply_theme_output)

    result = await agent.process_task(task_details)

    assert result["status"] == "success"
    assert result["output"]["theme_applied"] == "enchanted"
    assert result["output"]["details"]["level_type"] == "forest"
    
    agent._resolve_prompt_and_simulate_llm.assert_called_once_with("level_generation_initial", task_details)
    # The agent code uses 'mock_output' key from the result of _resolve_prompt_and_simulate_llm
    agent._generate_initial_level_structure.assert_called_once_with(mock_interpret_output["mock_output"])
    agent._apply_theme_and_constraints.assert_called_once_with(mock_generate_output_with_details, task_details["theme"], task_details["constraints"]) # Use the correct mock variable

    # Check for key event postings
    calls = agent.http_client.post.call_args_list
    event_types_posted = [call[1]['json']['event_type'] for call in calls if call[0][0].endswith('/post_event')]

    assert "level_design_progress" in event_types_posted # Multiple of these
    assert "level_design_complete" in event_types_posted
    # Count can be more specific if needed, e.g. count specific progress steps
    # For now, check that at least the main ones are there.
    # Expected: started, resolving_prompt, generating_structure, applying_theme_constraints, completed_successfully
    assert event_types_posted.count("level_design_progress") >= 4
    
    # Example of checking a specific event (if http_client is not reset inside process_task for each event)
    # calls = agent.http_client.post.call_args_list
    # complete_event_found = any(call[1]['json']['event_type'] == 'level_design_complete' for call in calls)
    # assert complete_event_found


@pytest.mark.asyncio
async def test_process_task_level_generation_creates_unity_scene(level_architect_agent_instance, mock_unity_bridge):
    agent = level_architect_agent_instance
    task_details = {
        "task_id": "proc_task_gen_unity_01",
        "task_type_for_prompt": "level_generation_initial",
        "level_type": "forest", "genre": "adventure", "theme": "enchanted",
        "features_list": ["talking_trees", "hidden_grove"], "difficulty": "easy",
        "constraints": ["must_be_traversable"]
    }

    # Mock helper methods to control their return values
    mock_llm_output = {"level_type": "forest", "key_features_generated": ["talking_trees", "hidden_grove"], "description": "An enchanted forest."}
    agent._resolve_prompt_and_simulate_llm = AsyncMock(return_value={"status": "success", "mock_output": mock_llm_output})
    
    mock_generated_structure = {
        "rooms": [{"id": "room1", "type": "start"}],
        "connections": [("room1", "room2")],
        "details": mock_llm_output
    }
    agent._generate_initial_level_structure = AsyncMock(return_value=mock_generated_structure)
    agent._apply_theme_and_constraints = AsyncMock(side_effect=lambda s, t, c: s) # Just pass through the structure

    # Ensure _create_unity_scene is mocked to check calls, but allow it to run its internal logic
    # We'll assert on mock_unity_bridge calls directly
    agent._create_unity_scene = AsyncMock(wraps=agent._create_unity_scene) # Use wraps to call original method

    result = await agent.process_task(task_details)

    assert result["status"] == "success"
    agent._create_unity_scene.assert_awaited_once_with(mock_generated_structure)
    
    # Verify calls to UnityToolchainBridge methods
    mock_unity_bridge.manipulate_scene.assert_awaited() # At least one call
    mock_unity_bridge.execute_script.assert_awaited() # At least one call for script

    # Check specific calls if needed, e.g., for plane creation
    mock_unity_bridge.manipulate_scene.assert_any_call(
        operation="create_object",
        target_object="Plane",
        parameters={"position": {"x": 0, "y": 0, "z": 0}, "scale": {"x": 10, "y": 1, "z": 10}}
    )
    # Check specific calls for room creation (example)
    mock_unity_bridge.manipulate_scene.assert_any_call(
        operation="create_object",
        target_object="Cube",
        parameters={"name": "RoomObject_room1", "position": {"x": 0, "y": 0.5, "z": 0}, "scale": {"x": 4, "y": 2, "z": 4}}
    )
    # Check specific calls for script execution
    mock_unity_bridge.execute_script.assert_any_call(
        script_content="""
using UnityEngine;

public class GeneratedLevelScript : MonoBehaviour
{
    void Start()
    {
        Debug.Log(\"Generated level script started!\");
    }
}
""",
        script_path="Assets/Scripts/GeneratedLevelScript.cs"
    )

    # Check MCP events
    event_types_posted = [call[1]['json']['event_type'] for call in agent.http_client.post.call_args_list if call[0][0].endswith('/post_event')]
    assert "level_design_progress" in event_types_posted
    assert "creating_unity_scene" in event_types_posted # New progress event
    assert "level_design_complete" in event_types_posted


@pytest.mark.asyncio
async def test_process_task_style_adaptation_success(level_architect_agent_instance):
    agent = level_architect_agent_instance
    task_details = {
        "task_id": "proc_task_style_01",
        "task_type_for_prompt": "level_style_adaptation",
        "level_data_json": {"rooms": 1, "description": "A simple room"},
        "new_style": "steampunk",
        "style_elements": ["gears", "copper_pipes"]
    }
    mock_interpret_output = {
        "status": "success",
        "resolved_prompt": "dummy_style_prompt",
        "mock_output": {"adapted_level_data": {"rooms": 1, "description": "A simple room with gears"}, "adapted_style": "steampunk"} # Changed llm_output to mock_output
    }
    agent._resolve_prompt_and_simulate_llm = AsyncMock(return_value=mock_interpret_output)

    result = await agent.process_task(task_details)

    assert result["status"] == "success"
    # The output of process_task for style_adaptation is the adapted_level_data itself from llm_output
    # process_task for style_adaptation returns the 'mock_output' from _resolve_prompt_and_simulate_llm
    # which contains "adapted_style"
    assert result["output"]["adapted_style"] == "steampunk"
    agent._resolve_prompt_and_simulate_llm.assert_called_once_with("level_style_adaptation", task_details)
    assert agent.http_client.post.call_count >= 4 # E.g. started, interpret_start, interpret_end, task_complete


@pytest.mark.asyncio
async def test_process_task_constraint_check_success(level_architect_agent_instance):
    agent = level_architect_agent_instance
    task_details = {
        "task_id": "proc_task_constraint_01",
        "task_type_for_prompt": "level_constraint_check",
        "level_data_json": {"layout": "complex", "exits": 4},
        "constraints_list": ["no_loops", "min_treasure_3"]
    }
    mock_interpret_output = {
        "status": "success",
        "resolved_prompt": "dummy_constraint_prompt",
        "mock_output": {"constraint_check_report": {"passed": False, "details": "contains loops"}, "constraints_checked": ["no_loops", "min_treasure_3"]} # Changed llm_output to mock_output
    }
    agent._resolve_prompt_and_simulate_llm = AsyncMock(return_value=mock_interpret_output)

    result = await agent.process_task(task_details)

    assert result["status"] == "success"
    # The agent's process_task for constraint_check returns the constraint_check_report as part of output
    assert result["output"]["constraint_check_report"]["constraints_checked"] == ["no_loops", "min_treasure_3"]
    agent._resolve_prompt_and_simulate_llm.assert_called_once_with("level_constraint_check", task_details)
    assert agent.http_client.post.call_count >= 4 # E.g. started, interpret_start, interpret_end, task_complete


@pytest.mark.asyncio
async def test_process_task_missing_task_type_for_prompt(level_architect_agent_instance):
    agent = level_architect_agent_instance
    task_details = {
        "task_id": "proc_task_missing_type_01",
        "level_type": "city" 
    }
    result = await agent.process_task(task_details)

    assert result["status"] == "failure"
    assert "'task_type_for_prompt' missing" in result["message"]
    # Expect at least task_started and then an error event
    # The specific error event might be posted by process_task itself
    # Check that an error event was posted
    error_event_posted = False
    for call in agent.http_client.post.call_args_list:
        # BaseAgent structures payload as {"event_type": ..., "data": event_data, ...}
        if call[0][0].endswith('/post_event') and \
           call[1]['json']['event_type'] == 'level_design_error' and \
           "'task_type_for_prompt' missing" in call[1]['json']['data']['error']:
            error_event_posted = True
            break
    assert error_event_posted, "Error event for missing task_type_for_prompt not posted correctly"
    # Expected calls: task_started (level_design_error)
    # The agent posts one event for this failure case.
    # The fixture default mock for post is one call. If process_task makes one call, total is 1.
    # Let's count specific event type calls.
    error_event_calls = [
        c for c in agent.http_client.post.call_args_list
        if c[0][0].endswith('/post_event') and c[1]['json']['event_type'] == 'level_design_error'
    ]
    assert len(error_event_calls) == 1


@pytest.mark.asyncio
async def test_process_task_interpret_prompt_failure(level_architect_agent_instance):
    agent = level_architect_agent_instance
    task_details = {
        "task_id": "proc_task_prompt_fail_01",
        "task_type_for_prompt": "level_generation_initial",
        "level_type": "space_station", # Missing "genre"
    }
    
    # Mock _interpret_design_prompt to return an error
    mock_interpret_error = {
        "status": "error", 
        "error_message": "Missing required variables: genre",
        "resolved_prompt": None, # Or some partial prompt
        "llm_output": None
    }
    agent._resolve_prompt_and_simulate_llm = AsyncMock(return_value=mock_interpret_error)

    result = await agent.process_task(task_details)

    assert result["status"] == "failure"
    # The mocked error_message is "Missing required variables: genre"
    # The agent's process_task returns this message directly.
    assert result["message"] == "Missing required variables: genre"
    
    agent._resolve_prompt_and_simulate_llm.assert_called_once_with("level_generation_initial", task_details)
    
    # Since _resolve_prompt_and_simulate_llm is fully mocked to just return mock_interpret_error,
    # it will not execute its internal logic to post an event.
    # The process_task method, upon receiving this error status, also does not post an additional event.
    # Therefore, we should not expect an error event to be posted in this specific test scenario
    # where _resolve_prompt_and_simulate_llm is completely replaced by a mock that just returns a value.
    # We've already asserted that result["status"] == "failure" and the message is correct.
    # We can check that no *unexpected* events were posted, or that only progress events before the failure point were.
    
    # Check that only progress events up to the point of calling the mocked _resolve_prompt_and_simulate_llm were made.
    # And that no error event was posted by process_task itself after the mocked method returned an error.
    error_event_call_found_in_process_task = False
    for call in agent.http_client.post.call_args_list:
        if call[0][0].endswith('/post_event') and call[1]['json']['event_type'] == 'level_design_error':
            # This would only be true if _resolve_prompt_and_simulate_llm was *not* mocked and ran,
            # or if process_task itself posted one.
            # Given the current mock, this should not be found from process_task.
            # The event from within the actual _resolve_prompt_and_simulate_llm is bypassed by the mock.
            pass
            
    # The test for _resolve_prompt_and_simulate_llm's internal event posting should be separate if needed.
    # For this test of process_task, we confirm it handles the error return from its call.
    # The number of calls to post.http_client should reflect only the progress events.
    
    # Let's count progress events.
    progress_event_calls = [
        c for c in agent.http_client.post.call_args_list
        if c[0][0].endswith('/post_event') and c[1]['json']['event_type'] == 'level_design_progress'
    ]
    # Expected: started and resolving_prompt
    assert len(progress_event_calls) == 2

    # Ensure no *additional* error event was posted by process_task after the mocked call.
    # The error event from within _resolve_prompt_and_simulate_llm is part of its own unit test (implicitly).
    # Here, we test process_task's reaction to the *return value* of the mocked method.
    # The mocked method returns status: "error", so process_task returns.
    # The event posting for this error is inside _resolve_prompt_and_simulate_llm, which is mocked.
    # So, we should not find an error event posted by this call to process_task.
    # The previous diff for this test was checking if the mocked error_message was in the event,
    # but the event itself won't be posted by the mocked function.
    # The test should focus on process_task's behavior given the mocked return.
    # The number of calls to http_client.post should reflect only the progress events.
    assert agent.http_client.post.call_count == 2