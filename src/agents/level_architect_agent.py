# src/agents/level_architect_agent.py
import logging
import json # For potential future use with prompt formatting, and for current mock outputs
# import re # Not strictly needed for current implementation but good for future regex-based var extraction

from .base_agent import BaseAgent

logger = logging.getLogger(__name__)

# Define prompt templates as constants
LEVEL_GENERATION_INITIAL_TEMPLATE = """System: You are a virtual environment architect specializing in residential spaces.
- Reconstruct layouts from reference images with ±2% dimensional accuracy
- Maintain architectural coherence across all scene elements
- Generate UV maps optimized for retro pixel art pipelines

User Input:
{{
  "task_type": "level_generation_initial",
  "level_type": "{level_type}",
  "genre": "{genre}",
  "theme": "{theme}",
  "features_list": "{features_list}",
  "difficulty": "{difficulty}"
}}"""

LEVEL_STYLE_ADAPTATION_TEMPLATE = """System: You are a virtual environment architect.
Adapt the following level data to a new style.

User Input:
{{
  "task_type": "level_style_adaptation",
  "level_data_json": "{level_data_json}",
  "new_style": "{new_style}",
  "style_elements": "{style_elements}"
}}"""

LEVEL_CONSTRAINT_CHECK_TEMPLATE = """System: You are a virtual environment architect.
Review the following level design and ensure it meets the specified constraints.

User Input:
{{
  "task_type": "level_constraint_check",
  "level_data_json": "{level_data_json}",
  "constraints_list": "{constraints_list}"
}}"""


class LevelArchitectAgent(BaseAgent):
    def __init__(self, agent_id: str, mcp_server_url: str, unity_bridge=None, level_design_tool_config: dict = None):
        super().__init__(agent_id, mcp_server_url, capabilities=["level_design", "procedural_generation_guidance"])
        self.unity_bridge = unity_bridge
        self.level_design_tool_config = level_design_tool_config if level_design_tool_config is not None else {}
        self.prompt_templates = {
            "level_generation_initial": LEVEL_GENERATION_INITIAL_TEMPLATE,
            "level_style_adaptation": LEVEL_STYLE_ADAPTATION_TEMPLATE,
            "level_constraint_check": LEVEL_CONSTRAINT_CHECK_TEMPLATE,
        }
        # Store required variables for each template
        self.prompt_template_required_vars = {
            "level_generation_initial": ["level_type", "genre", "theme", "features_list", "difficulty"],
            "level_style_adaptation": ["level_data_json", "new_style", "style_elements"],
            "level_constraint_check": ["level_data_json", "constraints_list"],
        }
        # Old _interpret_design_prompt is kept for now, though not used in main flow.
        # Registration will be handled by an explicit call to start_and_register()

    def _get_prompt_template_for_task(self, task_type: str) -> str | None:
        """
        Retrieves a prompt template string based on the task type.
        Conceptually, this could later query the MCP PromptRegistry.
        """
        return self.prompt_templates.get(task_type)

    async def _resolve_prompt_and_simulate_llm(self, task_type: str, task_details: dict) -> dict:
        """
        Selects a prompt template, resolves it with task_details, logs it,
        and returns a mocked LLM output. Includes basic behavior enforcement.
        """
        logger.info(f"Resolving prompt for task_type: {task_type} with details: {task_details}")
        task_id = task_details.get("task_id", "unknown_prompt_task")

        template_string = self._get_prompt_template_for_task(task_type)
        if not template_string:
            error_msg = f"No prompt template found for task_type: {task_type}"
            logger.error(f"Task {task_id}: {error_msg}")
            await self.post_event_to_mcp(
                event_type="level_design_error",
                event_data={"task_id": task_id, "status": "prompt_error", "error": error_msg}
            )
            return {"status": "error", "error_message": error_msg, "mock_output": None}

        required_vars = self.prompt_template_required_vars.get(task_type, [])
        missing_vars = [var for var in required_vars if var not in task_details]

        if missing_vars:
            error_msg = f"Missing required variables for prompt {task_type}: {', '.join(missing_vars)}"
            logger.error(f"Task {task_id}: {error_msg}")
            await self.post_event_to_mcp(
                event_type="level_design_error",
                event_data={"task_id": task_id, "status": "prompt_error", "error": error_msg}
            )
            return {"status": "error", "error_message": error_msg, "mock_output": None}

        try:
            formatting_data = task_details.copy()
            for key, value in formatting_data.items():
                if key in required_vars and isinstance(value, (list, dict)):
                    # For lists/dicts that are part of the template, convert to string representation
                    # Using json.dumps for a more structured string representation if it's complex
                    # For simple lists of strings, str() might be fine e.g. "['item1', 'item2']"
                    # The templates expect simple string substitution for these.
                    formatting_data[key] = str(value)
            
            resolved_prompt = template_string.format(**formatting_data)
        except KeyError as e:
            error_msg = f"Error formatting prompt {task_type}: Missing key {e} in task_details for formatting."
            logger.error(f"Task {task_id}: {error_msg} (Available keys: {list(formatting_data.keys())})")
            await self.post_event_to_mcp(
                event_type="level_design_error",
                event_data={"task_id": task_id, "status": "prompt_error", "error": error_msg}
            )
            return {"status": "error", "error_message": error_msg, "mock_output": None}

        logger.info(f"Resolved prompt for task {task_id} ({task_type}):\n{resolved_prompt}")

        mock_output = {}
        if task_type == "level_generation_initial":
            mock_output = {
                "level_type": task_details.get("level_type", "unknown"),
                "size": "medium",  # Mocked, could be derived or part of task_details
                "theme": task_details.get("theme", "unknown"),
                "key_features_generated": task_details.get("features_list", []), # Use the input list directly
                "description": f"A generated {task_details.get('level_type','level')} with {task_details.get('theme','generic')} theme and difficulty {task_details.get('difficulty','medium')}."
            }
        elif task_type == "level_style_adaptation":
            mock_output = {
                "original_data_summary": f"Summary of data: {str(task_details.get('level_data_json', {}))[:100]}...", # Mocked
                "adapted_style": task_details.get("new_style", "unknown"),
                "style_elements_applied": task_details.get("style_elements", []),
                "changes_made": ["Color palette adjusted", "Texture details enhanced for new style"],  # Mocked
                "adapted_level_data": {"structure": "modified_for_style", "style": task_details.get("new_style"), "details": "mock adaptation details"}  # Mocked
            }
        elif task_type == "level_constraint_check":
            mock_output = {
                "constraints_checked": task_details.get("constraints_list", []),
                "violations_found": [],  # Mocked - assume compliant for now
                "report": "Level design meets all specified constraints based on mock check.",  # Mocked
                "checked_data_summary": f"Summary of data: {str(task_details.get('level_data_json', {}))[:100]}..."
            }
        else:
            mock_output = {"message": f"Mock output for unhandled task type: {task_type}."}
            
        logger.info(f"Simulated LLM output for task {task_id} ({task_type}): {mock_output}")
        return {"status": "success", "resolved_prompt": resolved_prompt, "mock_output": mock_output}

    async def _interpret_design_prompt(self, prompt: str, context: dict) -> dict:
        """
        (Legacy Placeholder) Interprets the design prompt.
        For now, performs simple keyword extraction.
        This method is not actively used in the new process_task flow.
        """
        logger.info(f"Legacy _interpret_design_prompt called with: {prompt} and context: {context}")
        design_goals = {"level_type": "unknown", "size": "medium", "key_features": []}
        if "dungeon" in prompt.lower():
            design_goals["level_type"] = "dungeon"
        if "small" in prompt.lower():
            design_goals["size"] = "small"
        elif "large" in prompt.lower():
            design_goals["size"] = "large"
        if "traps" in prompt.lower():
            design_goals["key_features"].append("traps")
        if "secret room" in prompt.lower():
            design_goals["key_features"].append("secret_room")
        return design_goals

    async def _generate_initial_level_structure(self, design_goals: dict) -> dict:
        """
        (Placeholder) Generates an initial level structure based on design goals
        (which now come from the simulated LLM output).
        """
        logger.info(f"Generating initial level structure for: {design_goals}")
        level_structure = {
            "rooms": [{"id": "room1", "type": "start", "description": "Starting room"},
                      {"id": "room2", "type": "corridor", "description": "A narrow passage"}],
            "connections": [("room1", "room2")],
            "details": design_goals # design_goals is the LLM output here
        }
        if design_goals.get("level_type") == "dungeon":
            level_structure["rooms"].append({"id": "room3", "type": "boss_chamber", "description": "The final challenge awaits"})
            level_structure["connections"].append(("room2", "room3"))
        
        # Incorporate key features from design_goals if present
        if "key_features_generated" in design_goals and isinstance(design_goals["key_features_generated"], list):
            level_structure["features_included"] = design_goals["key_features_generated"]
            # Example: add a special room if "secret_room" is a feature
            if "secret_room" in design_goals["key_features_generated"]:
                 level_structure["rooms"].append({"id": "secret_room_1", "type": "secret", "description": "A hidden secret room"})
                 # Assume it connects from room1 for simplicity
                 if any(r["id"] == "room1" for r in level_structure["rooms"]):
                    level_structure["connections"].append(("room1", "secret_room_1"))


        return level_structure

    async def _apply_theme_and_constraints(self, level_structure: dict, theme: str, constraints: list) -> dict:
        """
        (Placeholder) Modifies the level structure based on theme and constraints.
        """
        logger.info(f"Applying theme '{theme}' and constraints {constraints} to level structure.")
        modified_structure = level_structure.copy()
        modified_structure["theme_applied"] = theme
        modified_structure["constraints_considered"] = constraints
        if "no_dead_ends" in constraints and "connections" in modified_structure:
            logger.warning("Constraint 'no_dead_ends' noted, but not fully implemented in placeholder.")
        return modified_structure

    async def _interact_with_external_tool(self, tool_name: str, tool_input: dict) -> dict:
        """
        (Placeholder) Simulates interaction with an external level generation tool.
        This method will be replaced by direct Unity interactions.
        """
        logger.info(f"Simulating interaction with external tool: {tool_name} with input: {tool_input}")
        logger.info(f"Tool config available: {self.level_design_tool_config.get(tool_name)}")
        return {"tool_name": tool_name, "status": "success", "output": {"mock_data": "data_from_" + tool_name}}

    async def _create_unity_scene(self, level_structure: dict) -> dict:
        """
        Translates the generated level structure into Unity Editor commands
        using the UnityToolchainBridge.
        """
        if not self.unity_bridge:
            logger.error("UnityToolchainBridge not available. Cannot create Unity scene.")
            return {"status": "error", "message": "UnityToolchainBridge not available."}

        logger.info(f"Creating Unity scene from level structure: {level_structure}")
        
        # Example: Create a base plane or terrain
        try:
            response = await self.unity_bridge.manipulate_scene(
                operation="create_object",
                target_object="Plane", # Or "Terrain"
                parameters={"position": {"x": 0, "y": 0, "z": 0}, "scale": {"x": 10, "y": 1, "z": 10}}
            )
            logger.info(f"Created base plane in Unity: {response}")
        except Exception as e:
            logger.error(f"Failed to create base plane in Unity: {e}")
            return {"status": "error", "message": f"Failed to create base plane: {e}"}

        # Example: Place some mock objects based on level_structure
        # This is a simplified example; real implementation would parse level_structure
        # and create objects accordingly (e.g., rooms, walls, props).
        if "rooms" in level_structure:
            for i, room in enumerate(level_structure["rooms"]):
                obj_name = f"RoomObject_{room.get('id', i)}"
                position = {"x": i * 5, "y": 0.5, "z": 0} # Simple offset for demonstration
                try:
                    response = await self.unity_bridge.manipulate_scene(
                        operation="create_object",
                        target_object="Cube", # Placeholder for a room
                        parameters={"name": obj_name, "position": position, "scale": {"x": 4, "y": 2, "z": 4}}
                    )
                    logger.info(f"Created room object '{obj_name}' in Unity: {response}")
                except Exception as e:
                    logger.error(f"Failed to create room object '{obj_name}' in Unity: {e}")
                    # Continue to next object or return error based on desired robustness

        # Example: Create a simple C# script and execute it (e.g., for game logic)
        # This would be for more complex behaviors than simple object placement.
        script_content = """
using UnityEngine;

public class GeneratedLevelScript : MonoBehaviour
{
    void Start()
    {
        Debug.Log(\"Generated level script started!\");
    }
}
"""
        script_path = "Assets/Scripts/GeneratedLevelScript.cs"
        try:
            response = await self.unity_bridge.execute_script(script_content, script_path)
            logger.info(f"Executed generated script in Unity: {response}")
        except Exception as e:
            logger.error(f"Failed to execute generated script in Unity: {e}")

        return {"status": "success", "message": "Unity scene creation commands sent."}

    async def process_task(self, task_details: dict) -> dict:
        task_id = task_details.get("task_id", "unknown_task")
        task_type_for_prompt = task_details.get("task_type_for_prompt")

        if not task_type_for_prompt:
            error_msg = f"'task_type_for_prompt' missing in task_details for task {task_id}."
            logger.error(error_msg)
            await self.post_event_to_mcp(
                event_type="level_design_error",
                event_data={"task_id": task_id, "status": "failed", "error": error_msg}
            )
            return {"status": "failure", "message": error_msg, "output": None}

        logger.info(f"LevelArchitectAgent ({self.agent_id}) processing task ID: {task_id} of type: {task_type_for_prompt}")
        await self.post_event_to_mcp(
            event_type="level_design_progress",
            event_data={"task_id": task_id, "status": "started", "message": "Task processing started."}
        )

        try:
            await self.post_event_to_mcp(
                event_type="level_design_progress",
                event_data={"task_id": task_id, "status": "resolving_prompt", "message": "Resolving prompt and simulating LLM."}
            )
            prompt_resolution_result = await self._resolve_prompt_and_simulate_llm(task_type_for_prompt, task_details)

            if prompt_resolution_result.get("status") == "error":
                logger.error(f"Task {task_id}: Failed to resolve prompt or simulate LLM. Error: {prompt_resolution_result.get('error_message')}")
                return {"status": "failure", "message": prompt_resolution_result.get('error_message'), "output": None}

            simulated_llm_output = prompt_resolution_result.get("mock_output")
            logger.info(f"Task {task_id}: Simulated LLM output received: {simulated_llm_output}")

            current_level_structure = {}

            if task_type_for_prompt == "level_generation_initial":
                await self.post_event_to_mcp(
                    event_type="level_design_progress",
                    event_data={"task_id": task_id, "status": "generating_structure", "message": "Generating initial level structure based on prompt output."}
                )
                current_level_structure = await self._generate_initial_level_structure(simulated_llm_output)
                logger.info(f"Task {task_id}: Initial structure generated: {current_level_structure}")

                theme = task_details.get("theme", simulated_llm_output.get("theme", "generic"))
                constraints = task_details.get("constraints", [])
                if theme or constraints:
                    await self.post_event_to_mcp(
                        event_type="level_design_progress",
                        event_data={"task_id": task_id, "status": "applying_theme_constraints", "message": "Applying theme and constraints."}
                    )
                    current_level_structure = await self._apply_theme_and_constraints(current_level_structure, theme, constraints)
                    logger.info(f"Task {task_id}: Theme and constraints applied.")

            elif task_type_for_prompt == "level_constraint_check":
                level_data_checked = task_details.get("level_data_json", {})
                current_level_structure = {
                    "original_data": level_data_checked,
                    "constraint_check_report": simulated_llm_output
                }
                logger.info(f"Task {task_id}: Constraint check performed. Report: {simulated_llm_output}")
                await self.post_event_to_mcp(
                    event_type="level_design_progress",
                    event_data={"task_id": task_id, "status": "constraints_checked", "message": "Constraints checked based on prompt output."}
                )
            else:
                logger.warning(f"Task {task_id}: No specific processing logic for task_type_for_prompt '{task_type_for_prompt}' after LLM simulation.")
                current_level_structure = simulated_llm_output

            if simulated_llm_output.get("requires_external_tool"):
                await self.post_event_to_mcp(
                    event_type="level_design_progress",
                    event_data={"task_id": task_id, "status": "external_tool_interaction", "message": "Interacting with external tool."}
                )
                tool_output = await self._interact_with_external_tool("example_generator", {"input_data": current_level_structure})
                logger.info(f"Task {task_id}: External tool output: {tool_output}")
                if isinstance(current_level_structure, dict):
                    current_level_structure["external_tool_data"] = tool_output
                else: # If current_level_structure wasn't a dict (e.g. from an unhandled task type)
                    current_level_structure = {"main_data": current_level_structure, "external_tool_data": tool_output}


            # After generating or adapting the level structure, send commands to Unity
            await self.post_event_to_mcp(
                event_type="level_design_progress",
                event_data={"task_id": task_id, "status": "creating_unity_scene", "message": "Sending commands to Unity to create/update scene."}
            )
            unity_creation_result = await self._create_unity_scene(current_level_structure)
            if unity_creation_result.get("status") == "error":
                raise Exception(f"Unity scene creation failed: {unity_creation_result.get('message')}")

            # Add Unity creation result to the output
            if isinstance(current_level_structure, dict):
                current_level_structure["unity_creation_status"] = unity_creation_result
            else:
                current_level_structure = {"main_data": current_level_structure, "unity_creation_status": unity_creation_result}


            await self.post_event_to_mcp(
                event_type="level_design_complete",
                event_data={"task_id": task_id, "status": "completed_successfully", "level_data": current_level_structure}
            )
            return {"status": "success", "message": "Level design task processed successfully.", "output": current_level_structure}

        except Exception as e:
            logger.error(f"Error processing task {task_id} in LevelArchitectAgent: {e}", exc_info=True)
            await self.post_event_to_mcp(
                event_type="level_design_error",
                event_data={"task_id": task_id, "status": "failed", "error": str(e)}
            )
            return {"status": "failure", "message": f"Error processing task: {str(e)}", "output": None}

    async def start_and_register(self):
        """
        Performs any necessary startup and registers the agent with the MCP server.
        """
        logger.info(f"Agent {self.agent_id} starting and attempting registration...")
        registration_result = await self.register_with_mcp()
        if registration_result:
            logger.info(f"Agent {self.agent_id} registration successful.")
        else:
            logger.error(f"Agent {self.agent_id} registration failed. Check MCP server logs and agent logs.")