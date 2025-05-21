# Level Architect Agent Documentation

:start_line:3
-------
## Overview

The `LevelArchitectAgent` ([`src/agents/level_architect_agent.py`](src/agents/level_architect_agent.py:0)) is a specialized agent within the ecosystem responsible for generating, modifying, and directly creating virtual environment structures and world maps within the Unity Editor.

Its core capabilities, as registered with the MCP Server, include:

*   `level_design`: Creating initial level layouts and structures based on high-level prompts.
*   `procedural_generation_guidance`: Providing guidance or parameters for procedural content generation systems.
*   `scene_creation`: Directly manipulating the Unity Editor to create and populate scenes.
*   `world_mapping`: Contributing to the construction of larger world maps.

Key responsibilities involve interpreting design requirements (via simulated LLM interaction), generating level structures, applying themes and constraints, and translating these designs into concrete Unity Editor actions. It reports progress and results back to the MCP Server.

## Architecture

The `LevelArchitectAgent` inherits from the `BaseAgent` ([`src/agents/base_agent.py`](src/agents/base_agent.py:0)), providing foundational capabilities for interacting with the MCP Server, including registration and event posting.

:start_line:18
-------
Key internal methods:

*   `__init__(self, agent_id: str, mcp_server_url: str, unity_bridge=None, level_design_tool_config: dict = None)`: Initializes the agent with a unique ID, the MCP server URL, an instance of `UnityToolchainBridge` for direct Unity interaction, a dictionary for external tool configuration, and loads predefined prompt templates. It also stores required variables for each template.
*   `_get_prompt_template_for_task(self, task_type: str) -> str | None`: Retrieves a specific prompt template string based on the provided task type from the agent's internal `prompt_templates` dictionary.
*   `_resolve_prompt_and_simulate_llm(self, task_type: str, task_details: dict) -> dict`: Selects the appropriate prompt template using `task_type`, formats it using variables from `task_details` (checking for missing required variables), logs the resolved prompt, and returns a simulated LLM output based on the `task_type`. This method includes basic behavior enforcement and error handling for prompt formatting.
*   `_interpret_design_prompt(self, prompt: str, context: dict) -> dict`: **(Legacy Placeholder)** This method is a placeholder for interpreting natural language prompts and is not actively used in the current `process_task` workflow, which relies on structured `task_details` and simulated LLM output.
*   `_generate_initial_level_structure(self, design_goals: dict) -> dict`: Generates an initial level structure based on the `design_goals` dictionary, which is derived from the simulated LLM output. It includes basic logic to add rooms and connections, and incorporates features listed in `key_features_generated`.
*   `_apply_theme_and_constraints(self, level_structure: dict, theme: str, constraints: list) -> dict`: Modifies the level structure based on a specified `theme` and a list of `constraints`.
*   `_interact_with_external_tool(self, tool_name: str, tool_input: dict) -> dict`: **(Deprecated/Placeholder)** This method previously simulated interaction with external tools. Its functionality is now largely superseded by direct interaction with the `UnityToolchainBridge` via `_create_unity_scene`.
*   `_create_unity_scene(self, level_structure: dict) -> dict`: **NEW**. This crucial method translates the generated `level_structure` into concrete commands for the Unity Editor using the `UnityToolchainBridge`. It can create objects (e.g., planes, cubes for rooms) and execute C# scripts within Unity.
*   `process_task(self, task_details: dict) -> dict`: The main entry point for tasks assigned to the agent via the MCP Server. It requires `"task_type_for_prompt"` in `task_details`. It orchestrates the workflow: posting a "started" event, resolving the prompt and simulating LLM output, performing task-specific processing (`_generate_initial_level_structure`, `_apply_theme_and_constraints`, or handling style adaptation/constraint check outputs), and crucially, calling `_create_unity_scene` to apply changes in Unity. It posts progress events, and finally posts a "complete" or "error" event. It returns a dictionary indicating status, message, and output data.
*   `start_and_register(self)`: Handles agent startup and registers the agent with the configured MCP server by calling the `register_with_mcp` method inherited from `BaseAgent`.

## Configuration

The `LevelArchitectAgent` is configured upon instantiation:

```python
from src.agents.level_architect_agent import LevelArchitectAgent

# Replace with actual MCP server URL if running with a server
# For this example, the agent will attempt to post events, which will fail
# unless an MCP server is running at this URL.
mcp_url = "http://localhost:8000"
agent_id = "level_architect_001"

:start_line:32
-------
# Instantiate the agent
agent = LevelArchitectAgent(
    agent_id=agent_id,
    mcp_server_url=mcp_url,
    unity_bridge=None, # In a real scenario, this would be an instantiated UnityToolchainBridge
    level_design_tool_config={
        "example_generator": {"api_key": "mock_key", "endpoint": "mock_url"}
        # Add configuration for actual external tools here
    }
)
```

*   `agent_id` (str): A unique identifier for this agent instance.
*   `mcp_server_url` (str): The URL of the MCP Server the agent should connect to.
*   `unity_bridge` (UnityToolchainBridge, optional): An instance of the `UnityToolchainBridge` for direct interaction with the Unity Editor. This is typically provided by the MCP Server during agent instantiation.
*   `level_design_tool_config` (dict, optional): A dictionary containing configuration parameters for any external level design tools the agent might interact with (now largely superseded by `unity_bridge`). Defaults to an empty dictionary if not provided.

## Usage

Tasks are assigned to the `LevelArchitectAgent` indirectly via the MCP Server's task management system. A request is typically sent to the MCP's `/request_action` endpoint, specifying the `LevelArchitectAgent`'s ID and the required `task_details`. The MCP then triggers the agent's `process_task` method with these details.

The `process_task` method expects a `task_details` dictionary as input. This dictionary **must** include:

*   `"task_id"` (str): The unique identifier for the task, typically provided by the MCP.
*   `"task_type_for_prompt"` (str): Specifies which prompt template and processing logic to use (e.g., `"level_generation_initial"`, `"level_style_adaptation"`, `"level_constraint_check"`).

Other keys in `task_details` depend on the `task_type_for_prompt` and must provide the necessary variables for formatting the selected prompt template (see Prompt Strategies section). For variables that are lists or dictionaries, they should be provided in a string representation (e.g., using `json.dumps` or `str()`) as the prompt templates expect string substitution.

The `process_task` method returns a dictionary with the following structure:

```python
{
    "status": "success" | "failure",
    "message": "A descriptive message about the outcome.",
    "output": {
        # Resulting level data structure or error details
    }
}
```
If the status is `"failure"`, the `"message"` key will contain an error description, and `"output"` will be `None`.

## Prompt Strategies

The `LevelArchitectAgent` utilizes predefined prompt templates for different level design tasks. These templates are stored internally in the `prompt_templates` dictionary and selected based on the `"task_type_for_prompt"` provided in the `task_details`. The agent also maintains a `prompt_template_required_vars` dictionary to validate that necessary variables are present in `task_details` before attempting to format the prompt.

Core Prompt Templates defined as constants in [`src/agents/level_architect_agent.py`](src/agents/level_architect_agent.py:10):

*   **`LEVEL_GENERATION_INITIAL_TEMPLATE`**: Used for generating an initial level structure from scratch.
    *   System Role: Virtual environment architect specializing in residential spaces, focused on accuracy, coherence, and UV mapping.
    *   Expected Variables in `task_details`: `level_type`, `genre`, `theme`, `features_list`, `difficulty`.
*   **`LEVEL_STYLE_ADAPTATION_TEMPLATE`**: Used for adapting an existing level structure to a new visual style.
    *   System Role: Virtual environment architect focused on style adaptation.
    *   Expected Variables in `task_details`: `level_data_json` (string representation of level data), `new_style`, `style_elements`.
*   **`LEVEL_CONSTRAINT_CHECK_TEMPLATE`**: Used for checking an existing level structure against a set of constraints.
    *   System Role: Virtual environment architect focused on constraint review.
    *   Expected Variables in `task_details`: `level_data_json` (string representation of level data), `constraints_list`.

The `_resolve_prompt_and_simulate_llm` method handles the selection and formatting of these templates using the provided `task_details`. It also includes a placeholder for simulating the LLM's response based on the `task_type`.

## Integration with MCP Server

The `LevelArchitectAgent` integrates with the MCP (Master Control Program) Server for task orchestration and communication, leveraging the capabilities provided by the `BaseAgent` class:

1.  **Registration:** Upon calling the asynchronous `start_and_register()` method, the agent registers itself with the MCP server via the `/register_agent` endpoint (as implemented in `BaseAgent`). This informs the MCP of the agent's presence and its capabilities (`level_design`, `procedural_generation_guidance`).
2.  **Task Processing:** The agent's `process_task` method is invoked by the MCP when a task is assigned to it. The `task_details` are passed as input.
3.  **Event Reporting:** Throughout the `process_task` execution, the agent sends events back to the MCP server using the `post_event_to_mcp` method (inherited from `BaseAgent`, which calls the `/post_event` endpoint). These events allow the MCP to track the task's progress and status.
    *   Common event types used by `LevelArchitectAgent` include:
        *   `level_design_progress`: Sent during various stages of processing (e.g., "started", "resolving\_prompt", "generating\_structure", "applying\_theme\_constraints", "style\_adapted", "constraints\_checked", "external\_tool\_interaction").
        *   `level_design_complete`: Sent upon successful completion of the task, including the final `level_data` in the event data.
        *   `level_design_error`: Sent if an error occurs during processing, including error details in the event data.

This integration enables the MCP to effectively manage and monitor level design tasks performed by the agent.

:start_line:114
-------
## Direct Unity Interaction

The `LevelArchitectAgent` now directly interacts with the Unity Editor through the `UnityToolchainBridge`. After generating or adapting a level structure, the agent calls its `_create_unity_scene` method. This method translates the abstract level design into concrete Unity Editor commands, such as:

*   Creating basic scene geometry (e.g., planes, cubes).
*   Placing objects (e.g., rooms, props) at specified positions, rotations, and scales.
*   Executing C# scripts within the Unity Editor for game logic or custom behaviors.

This direct interaction ensures that the agent's designs are immediately reflected and testable within the game development environment. The `_interact_with_external_tool` method is now largely superseded by this direct Unity integration.

## Error Handling

The `LevelArchitectAgent` implements error handling within its `process_task` method and the `_resolve_prompt_and_simulate_llm` method. If errors occur during prompt resolution, formatting, or the simulated processing steps, the agent:

*   Logs the error using the standard Python `logging` module.
*   Posts a `level_design_error` event to the MCP Server with details about the failure, including the task ID and an error message.
*   Returns a dictionary from `process_task` with `"status": "failure"`, an informative error message, and `None` for the `"output"`.

Specific error handling is included for missing required prompt variables and `KeyError` during prompt formatting.

## Code Example

The following snippet demonstrates how to instantiate the `LevelArchitectAgent` and trigger its `process_task` method with mock data. This is similar to the logic found in the test script [`scripts/run_level_architect_scenario.py`](scripts/run_level_architect_scenario.py:0), but focuses on direct agent interaction rather than a full scenario run.

```python
import asyncio
import logging
from src.agents.level_architect_agent import LevelArchitectAgent

# Configure basic logging for visibility
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def run_mock_task():
    # Replace with actual MCP server URL if running with a server
    # For this example, the agent will attempt to post events, which will fail
    # unless an MCP server is running at this URL.
    mcp_url = "http://localhost:8000"
    agent_id = "mock_level_architect_001"

    logger.info(f"Instantiating LevelArchitectAgent with ID: {agent_id}")
    # Instantiate the agent
    agent = LevelArchitectAgent(agent_id=agent_id, mcp_server_url=mcp_url)

    # Example task details for initial level generation
    mock_task_details_generate = {
        "task_id": "mock_task_generate_123",
        "task_type_for_prompt": "level_generation_initial",
        "level_type": "dungeon",
        "genre": "fantasy",
        "theme": "dark and damp",
        "features_list": ["traps", "secret room", "treasure chamber"],
        "difficulty": "hard",
        "constraints": ["no_dead_ends"] # Example of an optional parameter
    }

    logger.info(f"Attempting to process mock generation task: {mock_task_details_generate['task_id']}")

    # Process the task (simulated workflow)
    result_generate = await agent.process_task(mock_task_details_generate)

    logger.info(f"Mock generation task processing result: {result_generate}")

    # Example task details for style adaptation
    mock_task_details_style = {
        "task_id": "mock_task_style_456",
        "task_type_for_prompt": "level_style_adaptation",
        "level_data_json": '{"rooms": [{"id": "room1", "type": "start"}], "connections": []}', # Simplified mock data (stringified JSON)
        "new_style": "cyberpunk",
        "style_elements": ["neon lights", "grimy textures"]
    }

    logger.info(f"\nAttempting to process mock style adaptation task: {mock_task_details_style['task_id']}")
    result_style = await agent.process_task(mock_task_details_style)
    logger.info(f"Mock style adaptation result: {result_style}")

    # Example task details for constraint check
    mock_task_details_check = {
        "task_id": "mock_task_check_789",
        "task_type_for_prompt": "level_constraint_check",
        "level_data_json": '{"rooms": [{"id": "room1", "type": "start"}, {"id": "room2", "type": "end"}], "connections": [["room1", "room2"]]}', # Simplified mock data (stringified JSON)
        "constraints_list": ["single_entry_point", "single_exit_point"]
    }

    logger.info(f"\nAttempting to process mock constraint check task: {mock_task_details_check['task_id']}")
    result_check = await agent.process_task(mock_task_details_check)
    logger.info(f"Mock constraint check result: {result_check}")


if __name__ == "__main__":
    # Note: This example does NOT run the agent's start_and_register or connect to a real MCP.
    # It only demonstrates calling the process_task method directly for mock tasks.
    # For full agent operation, run the agent script and ensure MCP server is running.
    asyncio.run(run_mock_task())