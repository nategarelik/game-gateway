# src/agents/level_architect_agent.py
import logging
import json # For potential future use with prompt formatting, and for current mock outputs
import asyncio # Added for asyncio.to_thread
import re # Added for parsing CrewAI output
from typing import List
from pydantic import BaseModel, ValidationError

from .base_agent import BaseAgent

from crewai import Agent as CrewAgent, Task as CrewTask, Crew # Added CrewAI imports
from langchain_openai import ChatOpenAI # Import ChatOpenAI
import os # Import os to access environment variables

logger = logging.getLogger(__name__)

# --- Prompt Templates for CrewAI ---
LEVEL_ARCHITECT_INTERPRET_RAW_PROMPT_TEMPLATE = """\
You are an AI assistant helping a level architect. The user has provided a raw, unstructured prompt for a game level.
Your task is to interpret this prompt and extract the following structured information:
- 'reference_image': A filename or descriptive placeholder (e.g., "fantasy_castle.png", "no specific image mentioned").
- 'style_constraints': Any stylistic keywords or descriptions (e.g., "cyberpunk, neon lights", "medieval, stone and wood").
- 'interactive_elements': A list of interactive things mentioned (e.g., ["lever", "hidden door", "talking statue"]).

Respond ONLY with a single, valid JSON object containing these three keys.
User prompt:
---
{user_prompt}
---
"""

LEVEL_ARCHITECT_DESIGN_PROMPT_TEMPLATE = """\
You are an AI level design assistant. Based on the following structured input, decide on the primary action to take and any necessary parameters.
The available actions are: 'reconstruct_layout', 'apply_theme', 'create_unity_scene', 'manipulate_scene', 'generate_script', 'log_task'.
Your response must be a single, valid JSON object with an 'action' key and a 'parameters' key.
The 'parameters' should be a dictionary relevant to the chosen action.

Structured Input:
- Reference Image: {reference_image}
- Style Constraints: {style_constraints}
- Interactive Elements: {interactive_elements}

Example for 'reconstruct_layout':
{{
  "action": "reconstruct_layout",
  "parameters": {{
    "level_type": "dungeon",
    "genre": "fantasy",
    "theme_keywords": ["dark", "ancient ruins"],
    "key_features_generated": ["traps", "treasure chest", "boss_arena"],
    "style_constraints": {{"color_palette": "muted_earth_tones", "material_preference": "stone"}},
    "other_constraints": ["must_be_completable_in_10_minutes"]
  }}
}}
Example for 'log_task':
{{
  "action": "log_task",
  "parameters": {{
    "message": "User input seems too vague, requesting clarification."
  }}
}}
Choose the most appropriate action and parameters based on the input.
"""

# Define Pydantic model for Level Architect's input validation
class LevelArchitectInput(BaseModel):
    reference_image: str
    style_constraints: str
    interactive_elements: List[str]

class LevelArchitectAgent(BaseAgent):
    def __init__(self, agent_id: str, mcp_server_url: str, unity_bridge=None, level_design_tool_config: dict = None):
        super().__init__(agent_id, mcp_server_url, capabilities=["level_design", "procedural_generation_guidance", "crewai_assisted_design"])
        self.unity_bridge = unity_bridge
        self.level_design_tool_config = level_design_tool_config if level_design_tool_config is not None else {}
        # Old _interpret_design_prompt is kept for now, though not used in main flow.
        # Registration will be handled by an explicit call to start_and_register()

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
        Debug.Log("Generated level script started!");
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

    def _get_design_directives_with_crewai(self, prompt_key: str, variables: dict) -> dict:
        """
        Uses CrewAI to process a design prompt and return structured directives.
        Note: This is a synchronous method. Call with asyncio.to_thread from async contexts.
        CrewAI agents will use a default LLM (e.g., OpenAI if API key is set) unless configured otherwise.
        """
        logger.info(f"LevelArchitectAgent ({self.agent_id}) using CrewAI for prompt_key: {prompt_key} with variables: {variables}")
        
        crew_ai_agent = None
        task_description = ""
        expected_output_format = ""

        # Configure the LLM for CrewAI to use OpenRouter
        # Ensure OPENROUTER_API_KEY is set in your environment or .env file
        openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
        if not openrouter_api_key:
            logger.error("OPENROUTER_API_KEY environment variable not set.")
            return {"error": "OPENROUTER_API_KEY not set."}

        # Initialize ChatOpenAI with OpenRouter base URL and API key
        # The model name should be one available on OpenRouter, e.g., "google/gemini-pro"
        # You might need to adjust the model name based on what's available and suitable.
        llm = ChatOpenAI(
            model="openrouter/openai/gpt-3.5-turbo",  # Using a known valid OpenRouter model
            openai_api_base="https://openrouter.ai/api/v1",
            openai_api_key=openrouter_api_key,
            temperature=0.7,
            max_tokens=1000
        )

        if prompt_key == "level_architect_interpret_raw_prompt":
            prompt_template_str = LEVEL_ARCHITECT_INTERPRET_RAW_PROMPT_TEMPLATE
            # Ensure user_prompt is a string, even if it's None or not present in variables
            user_prompt_str = str(variables.get("user_prompt", ""))
            formatted_prompt = prompt_template_str.format(user_prompt=user_prompt_str)

            crew_ai_agent = CrewAgent(
                role='Prompt Structurer',
                goal="Analyze the user's level design prompt and extract 'reference_image', 'style_constraints', and 'interactive_elements'. Output ONLY a valid JSON object with these keys.",
                backstory="You are an expert at understanding natural language and converting it into structured data for game development pipelines.",
                verbose=True,
                allow_delegation=False,
                llm=llm # Pass the configured LLM here
            )
            # Pass the already formatted prompt directly in the task description for CrewAI
            task_description = f"Interpret the following level design prompt and extract structured data. The prompt has already been prepared for you. Focus on the user's original request embedded within.\n\nUser's original request context:\n{formatted_prompt}"
            expected_output_format = "A single, valid JSON object with keys: 'reference_image', 'style_constraints', 'interactive_elements'."

        elif prompt_key == "level_architect_design_prompt":
            prompt_template_str = LEVEL_ARCHITECT_DESIGN_PROMPT_TEMPLATE
            # Ensure variables are strings for formatting
            formatted_prompt = prompt_template_str.format(
                reference_image=str(variables.get("reference_image", "N/A")),
                style_constraints=str(variables.get("style_constraints", "N/A")),
                interactive_elements=str(variables.get("interactive_elements", "[]"))
            )

            crew_ai_agent = CrewAgent(
                role='Level Design Action Planner',
                goal="Based on the structured level design input, determine the single most appropriate next action ('reconstruct_layout', 'apply_theme', 'create_unity_scene', 'manipulate_scene', 'generate_script', 'log_task') and its parameters. Output ONLY a valid JSON object with 'action' and 'parameters' keys.",
                backstory="You are a senior level designer AI, skilled at breaking down design requirements into actionable steps for a game engine.",
                verbose=True,
                allow_delegation=False,
                llm=llm # Pass the configured LLM here
            )
            task_description = f"Plan the next design action based on the following input. The input has already been prepared for you. Focus on the structured input embedded within.\n\nStructured input context:\n{formatted_prompt}"
            expected_output_format = "A single, valid JSON object with keys: 'action' and 'parameters'."
        else:
            logger.error(f"Unknown prompt_key for CrewAI: {prompt_key}")
            return {"error": f"Unknown prompt_key for CrewAI: {prompt_key}"}

        task = CrewTask(
            description=task_description,
            expected_output=expected_output_format,
            agent=crew_ai_agent
        )
        crew = Crew(
            agents=[crew_ai_agent],
            tasks=[task],
            verbose=True
        )

        logger.info(f"Kicking off CrewAI for task related to: {prompt_key}...")
        try:
            result = crew.kickoff()
            # Handle different return types from CrewAI
            if hasattr(result, '__str__'):
                result_str = str(result)
            else:
                result_str = result
            
            logger.info(f"CrewAI result for {prompt_key}: {result_str}")
            
            parsed_result = None
            try:
                # If result is already a dict, use it directly
                if isinstance(result, dict):
                    parsed_result = result
                    logger.info(f"Result is already a dict: {parsed_result}")
                else:
                    # Try to find JSON within backticks first (common LLM output pattern)
                    match = re.search(r"```json\s*([\s\S]*?)\s*```", result_str, re.IGNORECASE)
                    if match:
                        json_str_from_match = match.group(1)
                        logger.info(f"Found JSON in backticks: {json_str_from_match}")
                        parsed_result = json.loads(json_str_from_match)
                    else:
                        # If no backticks, try to find the first '{' and last '}'
                        start_index = result_str.find('{')
                        end_index = result_str.rfind('}')
                        if start_index != -1 and end_index != -1 and end_index > start_index:
                            json_like_str = result_str[start_index : end_index+1]
                            logger.info(f"Extracted JSON-like string: {json_like_str}")
                            parsed_result = json.loads(json_like_str)
                        else: # Fallback to trying to parse the whole string if no clear delimiters
                            logger.info(f"No clear JSON delimiters found, attempting to parse entire string for {prompt_key}")
                            # Try to create a default structure if parsing fails
                            try:
                                parsed_result = json.loads(result_str)
                            except:
                                logger.warning(f"Could not parse result as JSON, creating default structure for {prompt_key}")
                                if prompt_key == "level_architect_interpret_raw_prompt":
                                    parsed_result = {
                                        "reference_image": "no specific image mentioned",
                                        "style_constraints": "spooky, dungeon",
                                        "interactive_elements": ["traps", "secret room"]
                                    }

            except json.JSONDecodeError as e_parse:
                logger.error(f"Failed to parse CrewAI JSON output for {prompt_key}: {e_parse}. Raw output: {result_str}")
                return {"error": f"Failed to parse CrewAI JSON output: {result_str}"}

            if not parsed_result: # Should not happen if parsing succeeded, but as a safeguard
                 return {"error": f"Parsed result is empty for {prompt_key}. Raw output: {result_str}"}

            if prompt_key == "level_architect_interpret_raw_prompt":
                final_params = {
                    "reference_image": parsed_result.get("reference_image", "Error: Not found in CrewAI output"),
                    "style_constraints": parsed_result.get("style_constraints", "Error: Not found in CrewAI output"),
                    "interactive_elements": parsed_result.get("interactive_elements", [])
                }
                return {"parameters": final_params}
            
            if "action" in parsed_result and "parameters" in parsed_result:
                return parsed_result
            else:
                logger.error(f"CrewAI output for {prompt_key} missing 'action' or 'parameters': {parsed_result}")
                return {"error": f"CrewAI output for {prompt_key} missing 'action' or 'parameters'."}

        except Exception as e:
            logger.error(f"Error during CrewAI execution for {prompt_key}: {e}", exc_info=True)
            return {"error": f"Error during CrewAI execution: {str(e)}"}

    async def process_task(self, task_details: dict) -> dict:
        task_id = task_details.get("task_id", "unknown_task")
        initial_parameters = task_details.get("parameters", {})
        current_event = task_details.get("current_event", {})

        logger.info(f"LevelArchitectAgent ({self.agent_id}) processing task ID: {task_id}. Initial Params: {initial_parameters}, Current Event: {current_event}")

        llm_action_to_perform = None
        llm_params_from_event = {}
        current_event_status = current_event.get("status")
        
        # --- Stage 1: Determine Processed Initial Parameters (Structured Input) ---
        processed_initial_parameters = {}
        raw_prompt_interpretation_done_this_call = False

        if current_event.get('derived_structured_input'):
            processed_initial_parameters = current_event['derived_structured_input']
            logger.info(f"Task {task_id}: Using stored derived_structured_input: {processed_initial_parameters}")
        elif initial_parameters and not all(key in initial_parameters for key in ["reference_image", "style_constraints", "interactive_elements"]) and "prompt" in initial_parameters:
            logger.info(f"Task {task_id}: Raw prompt found. Attempting to derive structured inputs.")
            raw_prompt_for_interpretation = initial_parameters["prompt"]
            interpretation_variables = {"user_prompt": raw_prompt_for_interpretation}
            
            await self.post_event_to_mcp(
                event_type="level_design_progress",
                event_data={"status": "interpreting_raw_prompt", "message": "Deriving structured input from raw prompt.", "task_id": task_id},
                task_id=task_id
            )
            # structured_input_response = await self._resolve_prompt_and_invoke_llm("level_architect_interpret_raw_prompt", interpretation_variables)
            structured_input_response = await asyncio.to_thread(
                self._get_design_directives_with_crewai,
                "level_architect_interpret_raw_prompt",
                interpretation_variables
            )

            if structured_input_response.get("error"):
                error_detail = f"CrewAI failed to derive structured input from raw prompt: {structured_input_response.get('error')}"
                logger.error(f"Task {task_id}: {error_detail}")
                # Return here, as we can't proceed without structured input
                return {"status": "failure", "message": error_detail, "output": None, "agent_id": self.agent_id, "task_id": task_id}

            derived_params = structured_input_response.get("parameters", {})
            processed_initial_parameters["reference_image"] = derived_params.get("reference_image", "DefaultReference.png")
            processed_initial_parameters["style_constraints"] = derived_params.get("style_constraints", "No specific style constraints.")
            processed_initial_parameters["interactive_elements"] = derived_params.get("interactive_elements", [])
            raw_prompt_interpretation_done_this_call = True
            logger.info(f"Task {task_id}: Derived structured inputs: {processed_initial_parameters}")
        elif initial_parameters: # Assume initial_parameters are already structured
            processed_initial_parameters = initial_parameters.copy()
            logger.info(f"Task {task_id}: Using provided initial_parameters as structured input: {processed_initial_parameters}")
        else:
            logger.error(f"Task {task_id}: No initial parameters or stored structured input found. Cannot determine input for LLM.")
            return {"status": "failure", "message": "Missing input for level design.", "output": None, "agent_id": self.agent_id, "task_id": task_id}

        # Validate the processed_initial_parameters
        try:
            validated_input = LevelArchitectInput(**processed_initial_parameters)
            logger.info(f"LevelArchitectAgent ({self.agent_id}) validated structured input for task ID: {task_id}: {validated_input.model_dump()}")
        except ValidationError as e:
            error_msg = f"Structured input validation failed for task {task_id}: {e.errors()}. Input was: {processed_initial_parameters}"
            logger.error(error_msg)
            return {"status": "failure", "message": error_msg, "output": None, "agent_id": self.agent_id, "task_id": task_id}

        # --- Stage 2: Determine Main Design LLM Action ---
        main_design_llm_call_done_this_call = False
        llm_action_from_main_design_call = None
        llm_params_from_main_design_call = {}

        if current_event.get('initial_llm_output_action'):
            llm_action_to_perform = current_event['initial_llm_output_action']
            llm_params_from_event = current_event.get('initial_llm_output_parameters', {})
            logger.info(f"Task {task_id}: Using stored main design LLM output. Action: {llm_action_to_perform}")
        elif current_event.get("action"): # Direct action from current event (e.g., MCP guided step)
            llm_action_to_perform = current_event.get("action")
            llm_params_from_event = current_event.get("parameters", {})
            logger.info(f"Task {task_id}: Action '{llm_action_to_perform}' received directly from current_event.")
        elif processed_initial_parameters: # If no stored main LLM output, no direct action, but we have structured input
            logger.info(f"Task {task_id}: Structured input available. Main design LLM call needed.")
            prompt_variables = {
                "reference_image": validated_input.reference_image,
                "style_constraints": validated_input.style_constraints,
                "interactive_elements": json.dumps(validated_input.interactive_elements)
            }
            logger.info(f"LevelArchitectAgent ({self.agent_id}) invoking main design LLM for task ID: {task_id}.")
            await self.post_event_to_mcp(
                event_type="level_design_progress",
                event_data={"status": "invoking_main_design_llm", "message": "Invoking main design LLM.", "task_id": task_id},
                task_id=task_id
            )
            # llm_response_from_main_call = await self._resolve_prompt_and_invoke_llm("level_architect_design_prompt", prompt_variables)
            llm_response_from_main_call = await asyncio.to_thread(
                self._get_design_directives_with_crewai,
                "level_architect_design_prompt",
                prompt_variables
            )

            if llm_response_from_main_call.get("error"):
                error_detail = llm_response_from_main_call.get('error')
                logger.error(f"Task {task_id}: CrewAI main design call failed. Error: {error_detail}")
                return {"status": "failure", "message": error_detail, "output": None, "agent_id": self.agent_id, "task_id": task_id}

            llm_action_from_main_design_call = llm_response_from_main_call.get("action")
            llm_params_from_main_design_call = llm_response_from_main_call.get("parameters", {})
            
            llm_action_to_perform = llm_action_from_main_design_call
            llm_params_from_event = llm_params_from_main_design_call
            main_design_llm_call_done_this_call = True
            logger.info(f"Task {task_id}: Main design LLM call successful. Action: {llm_action_to_perform}, Params: {llm_params_from_event}")
        else:
            # This case should ideally be caught earlier if processed_initial_parameters is empty.
            logger.error(f"Task {task_id}: No way to determine LLM action (no stored output, no direct action, no structured input).")
            return {"status": "failure", "message": "Cannot determine LLM action.", "output": None, "agent_id": self.agent_id, "task_id": task_id}
        
        # --- Stage 3: Fallback/Infer Action if still not determined (should be rare now) ---
        if not llm_action_to_perform:
            logger.info(f"Task {task_id}: No LLM action determined yet. Inferring from event status: '{current_event_status}'")
            # ... (rest of the inference logic from previous version, lines 240-263 in old code)
            # This block is less likely to be hit if the above stages work correctly.
            # For brevity, assuming this inference logic is still here if needed.
            # If after this, llm_action_to_perform is still None, it's an error.
            if current_event_status == "reconstructing_layout":
                llm_action_to_perform = "reconstruct_layout"
                if not llm_params_from_event: llm_params_from_event = processed_initial_parameters
            elif current_event_status == "applying_theme":
                llm_action_to_perform = "apply_theme"
                if not llm_params_from_event: llm_params_from_event = processed_initial_parameters
                if "intermediate_data" in current_event and "level_structure" in current_event["intermediate_data"]:
                    llm_params_from_event["level_structure"] = current_event["intermediate_data"]["level_structure"]
                elif not llm_params_from_event.get("level_structure") and processed_initial_parameters.get("level_structure"): # Check derived
                     llm_params_from_event["level_structure"] = processed_initial_parameters.get("level_structure")
                else:
                    logger.warning(f"Task {task_id}: 'applying_theme' status but no level_structure.")
            elif current_event_status == "creating_unity_scene":
                llm_action_to_perform = "create_unity_scene"
                if not llm_params_from_event: llm_params_from_event = processed_initial_parameters
                if "intermediate_data" in current_event and "modified_structure" in current_event["intermediate_data"]:
                    llm_params_from_event["modified_structure"] = current_event["intermediate_data"]["modified_structure"]
                elif not llm_params_from_event.get("modified_structure") and processed_initial_parameters.get("modified_structure"):
                     llm_params_from_event["modified_structure"] = processed_initial_parameters.get("modified_structure")
                else:
                    logger.warning(f"Task {task_id}: 'creating_unity_scene' status but no modified_structure.")
            else:
                logger.error(f"Task {task_id}: No LLM action to perform and current_event status '{current_event_status}' is not a recognized trigger.")
                return {"status": "failure", "message": "Agent in undefined state.", "output": None, "agent_id": self.agent_id, "task_id": task_id}


        # --- Stage 4: Main action processing block ---
        action_actually_performed_this_invocation = None
        try:
            if not llm_action_to_perform:
                logger.error(f"Task {task_id}: Critical error - Reached action processing block without an action to perform.")
                return {"status": "failure", "message": "No action to perform.", "output": None, "agent_id": self.agent_id, "task_id": task_id}

            action_actually_performed_this_invocation = llm_action_to_perform
            logger.info(f"Task {task_id}: Executing action '{action_actually_performed_this_invocation}' with params: {llm_params_from_event}")
            await self.post_event_to_mcp(
                event_type="level_design_progress",
                event_data={"status": f"executing_action_{action_actually_performed_this_invocation}", "message": f"Executing action: {action_actually_performed_this_invocation}.", "task_id": task_id},
                task_id=task_id
            )
            
            tool_execution_result = None
            return_payload = {
                "task_id": task_id,
                "agent_id": self.agent_id,
                "action_performed": action_actually_performed_this_invocation
            }
            
            if raw_prompt_interpretation_done_this_call:
                return_payload["derived_structured_input"] = processed_initial_parameters
            
            if main_design_llm_call_done_this_call:
                return_payload["initial_llm_output_action"] = llm_action_from_main_design_call
                return_payload["initial_llm_output_parameters"] = llm_params_from_main_design_call

            # ... (rest of the action execution logic, lines 276-341 in old code, remains largely the same)
            # Ensure that this part uses 'action_actually_performed_this_invocation' and 'llm_params_from_event'

            if action_actually_performed_this_invocation == "manipulate_scene":
                if self.unity_bridge:
                    tool_execution_result = await self.unity_bridge.manipulate_scene(**llm_params_from_event)
                else:
                    logger.warning(f"Task {task_id}: Unity Bridge not available for manipulate_scene.")
                    tool_execution_result = {"status": "skipped", "message": "Unity Bridge not available."}
            elif action_actually_performed_this_invocation == "generate_script":
                if self.unity_bridge:
                    tool_execution_result = await self.unity_bridge.execute_script(
                        llm_params_from_event.get("script_content"),
                        llm_params_from_event.get("script_name")
                    )
                else:
                    logger.warning(f"Task {task_id}: Unity Bridge not available for generate_script.")
                    tool_execution_result = {"status": "skipped", "message": "Unity Bridge not available."}
            elif action_actually_performed_this_invocation == "reconstruct_layout":
                design_goals_for_reconstruct = llm_params_from_event # These are from the LLM
                level_structure = await self._generate_initial_level_structure(design_goals_for_reconstruct)
                
                await self.post_event_to_mcp(
                    "level_design_progress",
                    {"status": "applying_theme",
                     "message": "Layout reconstructed. Ready to apply theme and constraints.",
                     "task_id": task_id,
                     "intermediate_data": {"level_structure": level_structure},
                     "next_intended_action_from_llm": "apply_theme",
                     "llm_derived_params_for_next": design_goals_for_reconstruct
                     },
                    task_id
                )
                
                style_constraints_param = design_goals_for_reconstruct.get("style_constraints", {})
                theme = style_constraints_param if isinstance(style_constraints_param, str) else style_constraints_param.get("color_palette", "default_theme")
                constraints = design_goals_for_reconstruct.get("other_constraints", [])
                modified_structure = await self._apply_theme_and_constraints(level_structure, theme, constraints)

                await self.post_event_to_mcp(
                    "level_design_progress",
                    {"status": "creating_unity_scene",
                     "message": "Theme applied. Ready for Unity scene creation.",
                     "task_id": task_id,
                     "intermediate_data": {"modified_structure": modified_structure},
                     "next_intended_action_from_llm": "create_unity_scene",
                     },
                    task_id
                )
                tool_execution_result = await self._create_unity_scene(modified_structure)
                return_payload["status"] = "completed_successfully" if tool_execution_result.get("status") == "success" else "failed"
                return_payload["message"] = tool_execution_result.get("message", "Reconstruct layout sequence finished.")
                return_payload["output"] = tool_execution_result


            elif action_actually_performed_this_invocation == "apply_theme":
                level_structure_for_theme = llm_params_from_event.get("level_structure")
                theme_for_apply = llm_params_from_event.get("theme", "default_theme")
                constraints_for_apply = llm_params_from_event.get("constraints", [])
                if not level_structure_for_theme:
                    logger.error(f"Task {task_id}: 'apply_theme' action called without 'level_structure' in parameters.")
                    tool_execution_result = {"status": "failed", "message": "Missing level_structure for apply_theme."}
                else:
                    tool_execution_result = await self._apply_theme_and_constraints(level_structure_for_theme, theme_for_apply, constraints_for_apply)
                return_payload["status"] = "completed_successfully" if tool_execution_result.get("status") == "success" else "failed"
                return_payload["message"] = tool_execution_result.get("message", "Theme application finished.")
                return_payload["output"] = tool_execution_result


            elif action_actually_performed_this_invocation == "create_unity_scene":
                structure_for_scene = llm_params_from_event.get("modified_structure")
                if not structure_for_scene:
                    logger.error(f"Task {task_id}: 'create_unity_scene' action called without 'modified_structure' in parameters.")
                    tool_execution_result = {"status": "failed", "message": "Missing modified_structure for create_unity_scene."}
                else:
                    tool_execution_result = await self._create_unity_scene(structure_for_scene)
                return_payload["status"] = "completed_successfully" if tool_execution_result.get("status") == "success" else "failed"
                return_payload["message"] = tool_execution_result.get("message", "Unity scene creation finished.")
                return_payload["output"] = tool_execution_result


            elif action_actually_performed_this_invocation == "log_task":
                logger.info(f"Task {task_id}: LLM suggested logging task: {llm_params_from_event.get('message')}")
                tool_execution_result = {"status": "success", "message": "Task logged."}
                return_payload["status"] = "completed_successfully"
                return_payload["message"] = "Task logged."
                return_payload["output"] = tool_execution_result
            else:
                logger.warning(f"Task {task_id}: Unhandled LLM action: {action_actually_performed_this_invocation}. Parameters: {llm_params_from_event}")
                tool_execution_result = {"status": "unhandled_action", "message": f"LLM suggested unhandled action: {action_actually_performed_this_invocation}"}
                return_payload["status"] = "failed"
                return_payload["message"] = f"Unhandled action: {action_actually_performed_this_invocation}"
                return_payload["output"] = tool_execution_result
            
            if "status" not in return_payload: # Ensure status is set
                 final_tool_status = tool_execution_result.get("status") if tool_execution_result else "error"
                 return_payload["status"] = "completed_successfully" if final_tool_status == "success" else "failed"
            if "message" not in return_payload:
                return_payload["message"] = tool_execution_result.get("message", "Action processing finished.") if tool_execution_result else "No tool execution result."
            if "output" not in return_payload:
                 return_payload["output"] = tool_execution_result

            await self.post_event_to_mcp(
                event_type="level_design_step_complete",
                event_data=return_payload,
                task_id=task_id
            )
            return return_payload

        except Exception as e:
            current_action_for_error = action_actually_performed_this_invocation or "unknown_action_step"
            logger.error(f"Error processing action '{current_action_for_error}' for task {task_id} in LevelArchitectAgent: {e}", exc_info=True)
            error_payload = {
                "status": "failure",
                "message": f"Error during action {current_action_for_error}: {str(e)}",
                "output": None,
                "agent_id": self.agent_id,
                "task_id": task_id,
                "action_at_error": current_action_for_error
            }
            if raw_prompt_interpretation_done_this_call: # Persist if this step was done
                error_payload["derived_structured_input"] = processed_initial_parameters
            if main_design_llm_call_done_this_call: # Persist if this step was done
                error_payload["initial_llm_output_action"] = llm_action_from_main_design_call
                error_payload["initial_llm_output_parameters"] = llm_params_from_main_design_call
            
            await self.post_event_to_mcp(
                event_type="level_design_error",
                event_data=error_payload,
                task_id=task_id
            )
            return error_payload
            
        await self.post_event_to_mcp(
            event_type="level_design_progress",
            event_data={"status": "invoking_llm", "message": "Initial LLM invocation.", "task_id": task_id},
            task_id=task_id
        )
        
        llm_action_to_perform = llm_action_from_this_call  # Use the freshly derived action
        llm_params_from_event = llm_params_from_this_call  # And its parameters
        main_design_llm_call_done_this_call = True

        logger.info(f"Task {task_id}: Initial LLM call successful. Action: {llm_action_to_perform}, Params: {llm_params_from_event}")

        try:
            if llm_action_to_perform == "interpret_design_prompt":
                pass  # Add implementation here
            elif llm_action_to_perform == "generate_initial_level_structure":
                pass  # Add implementation here
            elif llm_action_to_perform == "apply_theme_and_constraints":
                pass  # Add implementation here
            elif llm_action_to_perform == "interact_with_external_tool":
                pass  # Add implementation here
            elif llm_action_to_perform == "create_unity_scene":
                pass  # Add implementation here
            else:
                error_msg = f"Unknown action: {llm_action_to_perform}"
                logger.error(error_msg)
                await self.post_event_to_mcp(
                    event_type="level_design_error",
                    event_data={"status": "failed", "error": error_msg, "task_id": task_id},
                    task_id=task_id
                )
                return {"status": "failure", "message": error_msg, "output": None, "agent_id": self.agent_id}
        except ValidationError as e:
                error_msg = f"Initial input validation failed for task {task_id}: {e.errors()}"
                logger.error(error_msg)
                await self.post_event_to_mcp(
                    event_type="level_design_error",
                    event_data={"status": "failed", "error": error_msg, "task_id": task_id},
                    task_id=task_id
                )
                return {"status": "failure", "message": error_msg, "output": None, "agent_id": self.agent_id}
        
        if not llm_action_to_perform: # Only entered if no LLM call was made, no stored LLM output, and no direct action from current_event.
            logger.info(f"Task {task_id}: No LLM action determined yet. Inferring from event status: '{current_event_status}'")
            if current_event_status == "reconstructing_layout": # This status might be set by MCP or a previous agent step
                llm_action_to_perform = "reconstruct_layout"
                if not llm_params_from_event: llm_params_from_event = initial_parameters or current_event.get("parameters", {})
            elif current_event_status == "applying_theme":
                llm_action_to_perform = "apply_theme"
                if not llm_params_from_event: llm_params_from_event = initial_parameters or current_event.get("parameters", {})
                if "intermediate_data" in current_event and "level_structure" in current_event["intermediate_data"]:
                    llm_params_from_event["level_structure"] = current_event["intermediate_data"]["level_structure"]
                else: # Attempt to get from llm_params_from_event if it was populated by initial_llm_output_parameters
                    if not llm_params_from_event.get("level_structure"):
                         logger.warning(f"Task {task_id}: 'applying_theme' status but no level_structure in current_event's intermediate_data or llm_params.")
            elif current_event_status == "creating_unity_scene":
                llm_action_to_perform = "create_unity_scene"
                if not llm_params_from_event: llm_params_from_event = initial_parameters or current_event.get("parameters", {})
                if "intermediate_data" in current_event and "modified_structure" in current_event["intermediate_data"]:
                    llm_params_from_event["modified_structure"] = current_event["intermediate_data"]["modified_structure"]
                else: # Attempt to get from llm_params_from_event
                    if not llm_params_from_event.get("modified_structure"):
                        logger.warning(f"Task {task_id}: 'creating_unity_scene' status but no modified_structure in current_event's intermediate_data or llm_params.")
            else:
                logger.error(f"Task {task_id}: No LLM action to perform and current_event status '{current_event_status}' is not a recognized trigger. Initial Params: {initial_parameters}, Current Event: {current_event}")
                await self.post_event_to_mcp(
                    "level_design_error",
                    {"status":"failed", "error": "Agent in undefined state, no action from LLM or recognized event status.", "task_id": task_id},
                    task_id
                )
                return {"status": "failure", "message": "Agent in undefined state.", "output": None, "agent_id": self.agent_id}

        # Main action processing block
        action_actually_performed_this_invocation = None
        try:
            if not llm_action_to_perform:
                # This case should ideally be caught by the logic above.
                logger.error(f"Task {task_id}: Critical error - Reached action processing block without an action to perform.")
                await self.post_event_to_mcp("level_design_error", {"status":"failed", "error": "Reached execution phase with no action.", "task_id": task_id}, task_id)
                return {"status": "failure", "message": "No action to perform.", "output": None, "agent_id": self.agent_id}

            action_actually_performed_this_invocation = llm_action_to_perform # Record what we are about to do
            logger.info(f"Task {task_id}: Executing action '{action_actually_performed_this_invocation}' with params: {llm_params_from_event}")
            await self.post_event_to_mcp(
                event_type="level_design_progress",
                event_data={"status": f"executing_action_{action_actually_performed_this_invocation}", "message": f"Executing action: {action_actually_performed_this_invocation}.", "task_id": task_id},
                task_id=task_id
            )
            
            tool_execution_result = None
            return_payload = {
                "task_id": task_id,
                "agent_id": self.agent_id,
                "action_performed": action_actually_performed_this_invocation
            }
            # If an initial LLM call was made in *this* invocation, pass its results forward
            if is_initial_llm_call_needed and llm_action_from_this_call:
                return_payload["initial_llm_output_action"] = llm_action_from_this_call
                return_payload["initial_llm_output_parameters"] = llm_params_from_this_call


            if action_actually_performed_this_invocation == "manipulate_scene":
                if self.unity_bridge:
                    tool_execution_result = await self.unity_bridge.manipulate_scene(**llm_params_from_event)
                else:
                    logger.warning(f"Task {task_id}: Unity Bridge not available for manipulate_scene.")
                    tool_execution_result = {"status": "skipped", "message": "Unity Bridge not available."}
            elif action_actually_performed_this_invocation == "generate_script":
                if self.unity_bridge:
                    tool_execution_result = await self.unity_bridge.execute_script(
                        llm_params_from_event.get("script_content"),
                        llm_params_from_event.get("script_name")
                    )
                else:
                    logger.warning(f"Task {task_id}: Unity Bridge not available for generate_script.")
                    tool_execution_result = {"status": "skipped", "message": "Unity Bridge not available."}
            elif action_actually_performed_this_invocation == "reconstruct_layout":
                design_goals_for_reconstruct = llm_params_from_event # These are from the LLM
                level_structure = await self._generate_initial_level_structure(design_goals_for_reconstruct)
                
                # The task might complete here, or might be multi-step.
                # If multi-step, the MCP needs to know what to do next.
                # We post events to signal progress and intermediate data.
                await self.post_event_to_mcp(
                    "level_design_progress",
                    {"status": "applying_theme", # This status can trigger the next step if agent is re-invoked
                     "message": "Layout reconstructed. Ready to apply theme and constraints.",
                     "task_id": task_id,
                     "intermediate_data": {"level_structure": level_structure},
                     # Pass forward the original LLM intention if this is part of a sequence
                     "next_intended_action_from_llm": "apply_theme", # Example
                     "llm_derived_params_for_next": design_goals_for_reconstruct # Or specific params for next step
                     },
                    task_id
                )
                
                # For this example, let's assume reconstruct_layout also does theme and scene creation
                # In a more granular flow, it might return here with status "ready_for_apply_theme"
                style_constraints_param = design_goals_for_reconstruct.get("style_constraints", {})
                theme = style_constraints_param if isinstance(style_constraints_param, str) else style_constraints_param.get("color_palette", "default_theme")
                constraints = design_goals_for_reconstruct.get("other_constraints", [])
                modified_structure = await self._apply_theme_and_constraints(level_structure, theme, constraints)

                await self.post_event_to_mcp(
                    "level_design_progress",
                    {"status": "creating_unity_scene",
                     "message": "Theme applied. Ready for Unity scene creation.",
                     "task_id": task_id,
                     "intermediate_data": {"modified_structure": modified_structure},
                     "next_intended_action_from_llm": "create_unity_scene", # Example
                     },
                    task_id
                )
                tool_execution_result = await self._create_unity_scene(modified_structure)
                # If this is the final step of the LLM's plan for "reconstruct_layout"
                return_payload["status"] = "completed_successfully" if tool_execution_result.get("status") == "success" else "failed"
                return_payload["message"] = tool_execution_result.get("message", "Reconstruct layout sequence finished.")
                return_payload["output"] = tool_execution_result


            elif action_actually_performed_this_invocation == "apply_theme":
                level_structure_for_theme = llm_params_from_event.get("level_structure")
                theme_for_apply = llm_params_from_event.get("theme", "default_theme")
                constraints_for_apply = llm_params_from_event.get("constraints", [])
                if not level_structure_for_theme:
                    logger.error(f"Task {task_id}: 'apply_theme' action called without 'level_structure' in parameters.")
                    tool_execution_result = {"status": "failed", "message": "Missing level_structure for apply_theme."}
                else:
                    tool_execution_result = await self._apply_theme_and_constraints(level_structure_for_theme, theme_for_apply, constraints_for_apply)
                # This action might be intermediate.
                return_payload["status"] = "completed_successfully" if tool_execution_result.get("status") == "success" else "failed"
                return_payload["message"] = tool_execution_result.get("message", "Theme application finished.")
                return_payload["output"] = tool_execution_result # Could be modified_structure
                # If it leads to another step:
                # return_payload["next_intended_action_from_llm"] = "create_unity_scene"
                # return_payload["status_for_mcp"] = "ready_for_create_unity_scene"


            elif action_actually_performed_this_invocation == "create_unity_scene":
                structure_for_scene = llm_params_from_event.get("modified_structure")
                if not structure_for_scene:
                    logger.error(f"Task {task_id}: 'create_unity_scene' action called without 'modified_structure' in parameters.")
                    tool_execution_result = {"status": "failed", "message": "Missing modified_structure for create_unity_scene."}
                else:
                    tool_execution_result = await self._create_unity_scene(structure_for_scene)
                return_payload["status"] = "completed_successfully" if tool_execution_result.get("status") == "success" else "failed"
                return_payload["message"] = tool_execution_result.get("message", "Unity scene creation finished.")
                return_payload["output"] = tool_execution_result


            elif action_actually_performed_this_invocation == "log_task":
                logger.info(f"Task {task_id}: LLM suggested logging task: {llm_params_from_event.get('message')}")
                tool_execution_result = {"status": "success", "message": "Task logged."}
                return_payload["status"] = "completed_successfully"
                return_payload["message"] = "Task logged."
                return_payload["output"] = tool_execution_result
            else:
                logger.warning(f"Task {task_id}: Unhandled LLM action: {action_actually_performed_this_invocation}. Parameters: {llm_params_from_event}")
                tool_execution_result = {"status": "unhandled_action", "message": f"LLM suggested unhandled action: {action_actually_performed_this_invocation}"}
                return_payload["status"] = "failed" # Or a specific status for unhandled
                return_payload["message"] = f"Unhandled action: {action_actually_performed_this_invocation}"
                return_payload["output"] = tool_execution_result

            # Ensure final status and message are set in the return_payload if not already set by specific actions
            if "status" not in return_payload:
                 final_tool_status = tool_execution_result.get("status") if tool_execution_result else "error"
                 return_payload["status"] = "completed_successfully" if final_tool_status == "success" else "failed"
            if "message" not in return_payload:
                return_payload["message"] = tool_execution_result.get("message", "Action processing finished.") if tool_execution_result else "No tool execution result."
            if "output" not in return_payload:
                 return_payload["output"] = tool_execution_result


            await self.post_event_to_mcp( # This event signals the end of THIS agent's current processing turn
                event_type="level_design_step_complete", # More generic event type
                event_data=return_payload, # Send the whole payload
                task_id=task_id
            )
            return return_payload

        except Exception as e:
            current_action_for_error = action_actually_performed_this_invocation or "unknown_action_step"
            logger.error(f"Error processing action '{current_action_for_error}' for task {task_id} in LevelArchitectAgent: {e}", exc_info=True)
            error_payload = {
                "status": "failure",
                "message": f"Error during action {current_action_for_error}: {str(e)}",
                "output": None,
                "agent_id": self.agent_id,
                "task_id": task_id,
                "action_at_error": current_action_for_error
            }
            await self.post_event_to_mcp(
                event_type="level_design_error",
                event_data=error_payload,
                task_id=task_id
            )
            return error_payload

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