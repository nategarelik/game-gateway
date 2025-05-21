from typing import List, Dict, Any
import json
from datetime import datetime # Added for state update timestamp

# Import Agent and GameDevState from the mcp_server package
from ..mcp_server.server_core import Agent, GameDevState

class LevelArchitectAgent(Agent):
    """
    The Level Architect agent reconstructs virtual environments from reference images,
    maintains architectural coherence, generates UV maps, and assembles scenes using Unity Muse.
    """

    DEFAULT_PROMPT_TEMPLATE = [
        "System: You are a virtual environment architect specializing in residential spaces.",
        "- Reconstruct layouts from reference images with ±2% dimensional accuracy",
        "- Maintain architectural coherence across all scene elements",
        "- Generate UV maps optimized for retro pixel art pipelines",
        "",
        "User Input:",
        "{",
        "  \"reference_image\": \"{{reference_image}}\",",
        "  \"style_constraints\": \"{{style_constraints}}\",",
        "  \"interactive_elements\": {{interactive_elements}}",
        "}"
    ]

    def __init__(self, role=None, prompt_template: List[str] = None, mcp_server=None, **kwargs): # Added role, mcp_server (as optional), **kwargs
        # role and prompt_template are passed by mcp_server_core during generic instantiation.
        # This agent uses its class-defined DEFAULT_PROMPT_TEMPLATE if one isn't passed.
        # The 'role' argument from the server is accepted but this agent uses "LevelArchitect" internally.
        super().__init__(
            role=role if role else "LevelArchitect", # Use passed role or default
            prompt_template=prompt_template if prompt_template is not None else self.DEFAULT_PROMPT_TEMPLATE
        )
        self.mcp_server = mcp_server # Store mcp_server instance
        # Initialize any specific tools or clients the agent might need
        # e.g., self.unity_muse_client = UnityMuseClient()

    def _parse_and_validate_input(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parses and validates the input data against expected schema.
        Expected input fields: "reference_image", "style_constraints", "interactive_elements".
        """
        print(f"Level Architect: Parsing and validating input: {input_data}")
        required_fields = ["reference_image", "style_constraints", "interactive_elements"]
        for field in required_fields:
            if field not in input_data:
                raise ValueError(f"Missing required input field: {field}")

        # Further validation can be added here (e.g., type checking, format checking)
        # For example, interactive_elements should be a list.
        if not isinstance(input_data.get("interactive_elements"), list):
            raise ValueError("\"interactive_elements\" must be a list.")

        print("Level Architect: Input validated successfully.")
        return input_data

    def _process_reference_image(self, image_path: str) -> Dict[str, Any]:
        """
        Analyzes the reference image to extract dimensional data and spatial relationships.
        Placeholder implementation.
        """
        print(f"Level Architect: Processing reference image: {image_path}")
        # In a real implementation, this would involve image processing libraries
        # and algorithms to extract features, dimensions, etc.
        dimensional_data = {"width": "10m", "height": "3m", "depth": "8m"} # Example
        spatial_relationships = {"door_to_wall_distance": "1m"} # Example
        print(f"Level Architect: Extracted dimensional data: {dimensional_data}")
        return {"dimensional_data": dimensional_data, "spatial_relationships": spatial_relationships}

    def _ensure_architectural_coherence(self, scene_elements: Dict[str, Any], style_constraints: str) -> bool:
        """
        Validates style consistency and element relationships.
        Placeholder implementation.
        """
        print(f"Level Architect: Ensuring architectural coherence for elements with style: {style_constraints}")
        # Real implementation would check against architectural rules and style guides.
        print("Level Architect: Architectural coherence validated.")
        return True

    def _generate_uv_maps(self, scene_elements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generates UV maps optimized for retro pixel art pipelines.
        Placeholder implementation.
        """
        print("Level Architect: Generating UV maps.")
        uv_maps = {element: f"/path/to/{element}_uv.map" for element in scene_elements.get("elements", [])} # Example
        # Real implementation would use UV generation algorithms.
        print(f"Level Architect: UV maps generated: {uv_maps}")
        return uv_maps

    def _assemble_scene_in_unity_muse(self, processed_data: Dict[str, Any]) -> str:
        """
        Uses Unity Muse to assemble the real-time scene.
        Placeholder implementation.
        """
        print("Level Architect: Assembling scene in Unity Muse.")
        # Real implementation would interact with Unity Muse API or tools.
        scene_file_path = "/path/to/generated_scene.unity" # Example
        print(f"Level Architect: Scene assembled at {scene_file_path}")
        return scene_file_path

    def execute(self, state: GameDevState) -> GameDevState: # Signature changed
        """
        Executes the Level Architect's tasks based on the current state.
        It will use the mcp_server to resolve prompts and send commands to Unity Muse.
        """
        print(f"Level Architect ({self.role}): Executing task with current state.")
        
        try:
            # 1. Get the prompt from the prompt engine via mcp_server
            # Assumes mcp_server and its prompt_engine are available and initialized.
            prompt_variables = self._extract_variables_from_state(state)
            
            # Check if mcp_server and prompt_engine are available
            if not self.mcp_server or not hasattr(self.mcp_server, 'prompt_engine'):
                print("Error: MCPServer or PromptEngine not available to LevelArchitectAgent.")
                # Handle error appropriately, e.g., by setting an error state or raising
                state.agent_states[self.role] = {"error": "MCPServer or PromptEngine not configured", "status": "failed_config"}
                return state

            # The design doc uses self.mcp_server.prompt_engine.resolve_prompt("LevelArchitect", ...)
            # However, the MCPServer class in S001 has get_resolved_prompt_for_agent(role, variables)
            # Using the method available on MCPServer:
            prompt_text = self.mcp_server.get_resolved_prompt_for_agent(self.role, prompt_variables)
            if prompt_text is None:
                print(f"Error: Could not resolve prompt for {self.role}.")
                state.agent_states[self.role] = {"error": "Prompt resolution failed", "status": "failed_prompt"}
                return state
            
            print(f"Level Architect: Resolved prompt: {prompt_text}")

            # 2. Process the prompt to extract scene generation parameters
            scene_params = self._extract_scene_params(prompt_text) # E.g. description, style, collision_type, name
            print(f"Level Architect: Extracted scene parameters: {scene_params}")

            # 3. Format the command text for Unity Muse
            # The design doc shows: f"{scene_params['description']} -Style:{scene_params['style']} -CollisionType:{scene_params['collision_type']}"
            # This can be achieved using the format_muse_command utility if it's made available/imported,
            # or constructed directly here. For now, direct construction.
            muse_command_text = f"{scene_params.get('description','default scene')} -Style:{scene_params.get('style','RetroPixel')} -CollisionType:{scene_params.get('collision_type','Grid2D')}"

            # 4. Generate the level section using Unity Muse via mcp_server
            print(f"Level Architect: Sending ASSEMBLE_SCENE command to Unity Muse: '{muse_command_text}'")
            future = self.mcp_server.send_muse_command(
                command_type="ASSEMBLE_SCENE",
                command_text=muse_command_text,
                agent_id=self.role
            )
            
            # 5. Wait for the response (blocking call for this example)
            # In a more complex system, this might be handled asynchronously.
            print("Level Architect: Waiting for Unity Muse response...")
            response = future.result(timeout=30) # Add a timeout
            print(f"Level Architect: Received response from Unity Muse: {response}")
            
            # 6. Update the state with the generated scene information
            # Ensure 'assets' and 'scenes' keys exist
            if "assets" not in state: state.assets = {}
            state.assets["scenes"] = state.assets.get("scenes", {})
            
            scene_name = scene_params.get("name", f"scene_{response.get('scene_id', 'unknown')}")
            state.assets["scenes"][scene_name] = {
                "id": response.get("scene_id"), # Assuming response contains 'scene_id'
                "description": scene_params.get("description"),
                "style": scene_params.get("style"),
                "collision_type": scene_params.get("collision_type"),
                "status": response.get("status", "unknown"),
                "muse_response": response, # Store full response for audit/debug
                "created_at": datetime.now().isoformat()
            }
            
            state.agent_states[self.role] = {
                "last_action": "ASSEMBLE_SCENE",
                "last_scene_id": response.get("scene_id"),
                "status": "success"
            }
            print(f"Level Architect: Execution completed. Scene '{scene_name}' info added to state.")

        except Exception as e:
            print(f"Level Architect: Error during execution: {e}")
            import traceback
            traceback.print_exc()
            state.agent_states[self.role] = {"error": str(e), "status": "failed_execution"}
            # Optionally re-raise or handle as per error strategy
            # For now, we return the state with error info.

        return state

    def _extract_scene_params(self, prompt_text: str) -> Dict[str, Any]:
        """
        Placeholder: Extract scene generation parameters from the prompt text.
        This would use NLP or pattern matching.
        """
        print(f"Level Architect: Extracting scene params from prompt (placeholder): '{prompt_text[:100]}...'")
        # Example: "Create a vibrant forest scene named 'ForestGlade' with style 'Cartoon' and collision 'Mesh'."
        # This is a simplified extraction. Real NLP would be more robust.
        params = {
            "name": "GeneratedScene1",
            "description": "A default scene based on prompt.",
            "style": "RetroPixel", # Default if not found
            "collision_type": "Grid2D" # Default if not found
        }
        if "named" in prompt_text:
            try:
                # Very naive extraction
                name_match = prompt_text.split("named '")[1].split("'")[0]
                if name_match: params["name"] = name_match
            except IndexError: pass # Ignore if parsing fails

        # For description, we might take a large part of the prompt or a summary
        params["description"] = prompt_text # Or a more sophisticated extraction
        
        # Extract style (example)
        if "-Style:" in prompt_text: # Assuming format from Muse command template
            try:
               style_match = prompt_text.split("-Style:")[1].split(" ")[0]
               if style_match: params["style"] = style_match
            except IndexError: pass

        # Extract collision_type (example)
        if "-CollisionType:" in prompt_text:
            try:
                collision_match = prompt_text.split("-CollisionType:")[1].split(" ")[0]
                if collision_match: params["collision_type"] = collision_match
            except IndexError: pass

        return params

    def _extract_variables_from_state(self, state: GameDevState) -> Dict[str, Any]:
        """
        Placeholder: Extract variables from the GameDevState for prompt resolution.
        """
        print("Level Architect: Extracting variables from state (placeholder).")
        variables = {
            # Example: these could come from state.project_metadata, state.current_tasks, etc.
            "reference_image": state.agent_states.get(self.role, {}).get("target_image", "default_ref.png"),
            "style_constraints": state.project_metadata.get("global_style", "PixelArt"),
            "interactive_elements": ["doors", "chests"] # Default or from state
        }
        # Add more complex extraction logic as needed based on actual state structure
        return variables

    def handle_direct_request(self, parameters: dict) -> dict:
        """
        Handles a direct API request to the Level Architect agent.
        Expected parameters: "reference_image" (str), "style_constraints" (str),
                             "interactive_elements" (list).
        """
        print(f"Level Architect ({self.role}): Handling direct request with parameters: {parameters}")
        try:
            validated_params = self._parse_and_validate_input(parameters)
            
            # Simulate core logic based on parameters
            image_analysis = self._process_reference_image(validated_params["reference_image"])
            # For a direct request, we might not have a full scene to check for coherence yet,
            # or we might apply style constraints to the initial analysis.
            # self._ensure_architectural_coherence(image_analysis, validated_params["style_constraints"])
            
            # This agent's primary output via direct request might be the initial analysis
            # or a plan, rather than a fully assembled scene which might be too complex.
            # For now, return the analysis.
            
            result_data = {
                "status": "success",
                "message": "Reference image processed and initial analysis complete.",
                "image_analysis": image_analysis,
                "requested_style": validated_params["style_constraints"],
                "interactive_elements_plan": validated_params["interactive_elements"]
            }
            print(f"Level Architect: Direct request processed successfully.")
            return result_data

        except ValueError as ve:
            print(f"Level Architect: Validation error in direct request: {ve}")
            return {"status": "error", "message": f"Invalid parameters: {ve}"}
        except Exception as e:
            print(f"Level Architect: Error processing direct request: {e}")
            import traceback
            traceback.print_exc()
            return {"status": "error", "message": f"Internal server error: {e}"}

# Example Usage needs to be updated to reflect new __init__ and execute signatures
if __name__ == '__main__':
    # Example Usage (for testing the agent directly)
    print("--- Testing LevelArchitectAgent ---")
    
    # Create a dummy GameDevState
    initial_state = GameDevState(
        project_metadata={"project_name": "Retro Residential Remake"},
        agent_states={}
    )
    
    # Mock MCPServer for testing
    class MockMCPServer:
        def __init__(self):
            self.prompt_engine = self # Mocking prompt engine on mcp_server itself
            self.muse_bridge = self # Mocking muse_bridge for send_muse_command
            self.templates = {}

        def add_template(self, role, template_lines):
            self.templates[role] = template_lines

        def get_resolved_prompt_for_agent(self, role, variables):
            template = self.templates.get(role, ["Default prompt for {{reference_image}}"])
            # Simplified resolution for mock
            resolved_lines = []
            for line in template:
                for var_name, value in variables.items():
                    line = line.replace(f'{{{{{var_name}}}}}', str(value))
                resolved_lines.append(line)
            return "\n".join(resolved_lines)

        def send_muse_command(self, command_type, command_text, agent_id=None):
            print(f"MockMCPServer: send_muse_command received: type={command_type}, text='{command_text}', agent_id={agent_id}")
            from concurrent.futures import Future
            future = Future()
            # Simulate a successful response from Muse
            mock_response = {
                "type": command_type,
                "status": "success_mock",
                "message": "Command processed by Mock Unity Muse",
                "scene_id": "mock_scene_12345" if command_type == "ASSEMBLE_SCENE" else None,
                "original_command_id": "mock_cmd_id"
            }
            future.set_result(mock_response)
            return future

    mock_mcp_server = MockMCPServer()
    
    # Instantiate the agent with the mock server
    level_architect = LevelArchitectAgent(mcp_server=mock_mcp_server)
    
    # Add a template for the agent to the mock server's prompt engine
    mock_mcp_server.add_template(level_architect.role, LevelArchitectAgent.DEFAULT_PROMPT_TEMPLATE)

    # Initial state might contain info that _extract_variables_from_state uses
    initial_state.project_metadata["global_style"] = "DetailedFantasy"
    initial_state.agent_states[level_architect.role] = {"target_image": "concept_art_castle.png"}

    print(f"Initial GameDevState (for agent execution): {initial_state.__dict__}")
    print(f"Agent Role: {level_architect.role}")

    try:
        # Execute the agent's task. No separate input_data needed if logic is in _extract_variables_from_state
        updated_state = level_architect.execute(initial_state)
        print(f"Updated GameDevState after LevelArchitect execution: {json.dumps(updated_state.__dict__, indent=2)}")
        
        # Verify outputs (example checks)
        assert "scenes" in updated_state.assets
        # The scene name is now dynamic, check if any scene was added
        assert len(updated_state.assets['scenes']) > 0
        first_scene_name = list(updated_state.assets['scenes'].keys())[0]
        assert "mock_scene_12345" == updated_state.assets['scenes'][first_scene_name].get("id")
        assert "success" == updated_state.agent_states[level_architect.role].get("status")
        print("--- LevelArchitectAgent Test with Mock MCPServer Successful ---")

    except Exception as e:
        print(f"--- LevelArchitectAgent Test with Mock MCPServer Failed: {e} ---")
        import traceback
        traceback.print_exc()

    # Note: The input validation failure test would need to be adapted
    # as input is now primarily derived from state within the execute method.
    # Testing _parse_and_validate_input directly might be more appropriate for that.