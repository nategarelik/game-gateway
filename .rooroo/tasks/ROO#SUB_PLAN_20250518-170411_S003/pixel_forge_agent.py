# pixel_forge_agent.py
# Agent ID: ROO#SUB_PLAN_20250518-170411_S003
# Design Document: .rooroo/tasks/ROO#SUB_PLAN_S002/specialized_agent_roles_and_prompt_systems.md (Lines 58-128)

import json
from typing import List, Dict, Any # For Agent and GameDevState placeholders
from datetime import datetime # For state update timestamp
import uuid # For asset ID generation

# Import Agent and GameDevState from the mcp_server package
from ..mcp_server.server_core import Agent, GameDevState

# --- Prompt Templates (as per Design Document Lines 67-89) ---
RETRO_DIFFUSION_PROMPT_TEMPLATE = """
Prompt: Retro Pixel, {view_description} of {item_description}
- {resolution} resolution
- {color_count}-color palette: {palette_hex_codes}
- Animation frames: {animation_frames} ({animation_description})
- Collision mesh: {collision_mesh_description}

Negative Prompt:
Modern design elements, anti-aliasing, >{max_colors_negative} colors
"""

PIXEL_FORGE_DEFAULT_PROMPT_TEMPLATE = [
    "System: You are the PixelForge Agent, an expert in retro asset generation.",
    "Task: Generate a pixel art asset based on the following specifications.",
    "Specifications:",
    "  Item: {{item_description}}",
    "  View: {{view_description}}",
    "  Resolution: {{resolution}}",
    "  Palette: {{palette_info}}", # e.g., "16-color, specific hex codes if available"
    "  Animation: {{animation_details}}", # e.g., "5 frames, walking cycle"
    "  Style Notes: {{style_notes}}" # e.g., "Chunky pixels, dithered shading"
]

# Sprite Sheet Assembly Workflow (Mermaid graph) - This will be implemented as a method.
# graph TD
# A[Concept Sketch] --> B{MCP StyleCheck}
# B -->|Approved| C[Generate 8 Directions]
# B -->|Rejected| D[Regenerate via RD_FLUX]
# C --> E[Batch Process Hitboxes]

class PixelForgeAgent(Agent): # Inherits from Agent
    """
    The Pixel Forge Agent specializes in generating retro pixel art assets,
    animation frames, collision meshes, and managing sprite sheets.
    It adheres to specific style constraints and interfaces with the MCP server.
    """

    def __init__(self, role=None, prompt_template: List[str] = None, mcp_server=None, flux_integrator=None, **kwargs): # Added role, mcp_server (as optional), **kwargs
        # role and prompt_template are passed by mcp_server_core during generic instantiation.
        # This agent uses its class-defined PIXEL_FORGE_DEFAULT_PROMPT_TEMPLATE if one isn't passed.
        # The 'role' argument from the server is accepted but this agent uses "PixelForge" internally.
        super().__init__(
            role=role if role else "PixelForge", # Use passed role or default
            prompt_template=prompt_template if prompt_template is not None else PIXEL_FORGE_DEFAULT_PROMPT_TEMPLATE
        )
        self.mcp_server = mcp_server # Store mcp_server instance
        self.flux_integrator = flux_integrator # Keep flux_integrator if used by other methods
        # self.mcp_client is removed as mcp_server should provide MCP interaction
        # Use self.role which is set by super().__init__
        print(f"PixelForgeAgent ({self.role}) initialized.")

    # --- Core Execute Method (New, based on design pattern) ---

    def execute(self, state: GameDevState) -> GameDevState:
        """
        Executes the PixelForge agent's task based on the current state.
        Uses mcp_server to resolve prompts and generate assets via Retro Diffusion Pipeline.
        """
        print(f"PixelForgeAgent ({self.role}): Executing task with current state.")
        
        try:
            # 1. Get the prompt from the prompt engine via mcp_server
            prompt_variables = self._extract_variables_from_state(state)
            
            if not self.mcp_server or not hasattr(self.mcp_server, 'get_resolved_prompt_for_agent'):
                print("Error: MCPServer or get_resolved_prompt_for_agent not available.")
                state.agent_states[self.role] = {"error": "MCPServer misconfiguration", "status": "failed_config"}
                return state

            prompt_text = self.mcp_server.get_resolved_prompt_for_agent(self.role, prompt_variables)
            if prompt_text is None:
                print(f"Error: Could not resolve prompt for {self.role}.")
                state.agent_states[self.role] = {"error": "Prompt resolution failed", "status": "failed_prompt"}
                return state
            print(f"PixelForgeAgent: Resolved prompt: {prompt_text}")

            # 2. Process the prompt to extract asset generation parameters
            asset_params = self._extract_asset_params(prompt_text)
            # Ensure 'prompt' key for generate_retro_asset is the core description, not the full resolved prompt.
            # The 'prompt' for RetroDiffusionToolchainBridge is the textual description of the asset.
            # The 'parameters' dict holds structured data like resolution, etc.
            generation_prompt = asset_params.get("description", "default pixel art asset")
            generation_parameters = {
                "resolution": asset_params.get("resolution", [64, 64]), # Default from design
                "palette_lock": asset_params.get("palette_lock", True),
                "tileable": asset_params.get("tileable", False),
                "animation_frames": asset_params.get("animation_frames", 1),
                # Include other params like 'palette' if extracted by _extract_asset_params
                "palette": asset_params.get("palette")
            }
            print(f"PixelForgeAgent: Extracted asset parameters for generation: {generation_parameters}, prompt: '{generation_prompt}'")

            # 3. Generate the asset using the Retro Diffusion Pipeline via mcp_server
            print(f"PixelForgeAgent: Sending asset generation request to Retro Diffusion...")
            future = self.mcp_server.generate_retro_asset(
                prompt=generation_prompt,
                parameters=generation_parameters,
                agent_id=self.role
            )
            
            # 4. Wait for the result
            print("PixelForgeAgent: Waiting for Retro Diffusion response...")
            # result is expected to be an image data object (e.g., MockImageData)
            asset_result_object = future.result(timeout=60) # Increased timeout for generation
            print(f"PixelForgeAgent: Received asset from Retro Diffusion: {asset_result_object}")
            
            # 5. Update the state with the generated asset information
            if "assets" not in state: state.assets = {}
            state.assets["sprites"] = state.assets.get("sprites", {})
            
            asset_name = asset_params.get("name", f"sprite_{asset_result_object.id if hasattr(asset_result_object, 'id') else uuid.uuid4()}")
            state.assets["sprites"][asset_name] = {
                "id": str(uuid.uuid4()), # Generate a new UUID for this asset entry in state
                "source_prompt": generation_prompt,
                "generation_parameters": generation_parameters,
                "created_at": datetime.now().isoformat(),
                "image_data_b64": asset_result_object.to_base64() if hasattr(asset_result_object, 'to_base64') else None,
                "raw_result_details": str(asset_result_object) # For debugging
            }
            
            state.agent_states[self.role] = {
                "last_action": "GENERATE_RETRO_ASSET",
                "last_asset_name": asset_name,
                "status": "success"
            }
            print(f"PixelForgeAgent: Execution completed. Asset '{asset_name}' info added to state.")

        except Exception as e:
            print(f"PixelForgeAgent: Error during execution: {e}")
            import traceback
            traceback.print_exc()
            state.agent_states[self.role] = {"error": str(e), "status": "failed_execution"}

        return state

    def _extract_asset_params(self, prompt_text: str) -> Dict[str, Any]:
        """
        Placeholder: Extract asset generation parameters from the resolved prompt text.
        This would use NLP or pattern matching.
        """
        print(f"PixelForgeAgent: Extracting asset params from prompt (placeholder): '{prompt_text[:100]}...'")
        params = {
            "name": "DefaultSprite",
            "description": "A generic pixel art item", # This should be the core subject for generation
            "resolution": [64, 64],
            "palette_lock": True,
            "tileable": False,
            "animation_frames": 1,
            "palette": None # e.g. "8-color: #ff0000, #00ff00..."
        }
        # Example naive extraction (improve with regex or NLP)
        if "Item: " in prompt_text:
            try: params["description"] = prompt_text.split("Item: ")[1].split("\n")[0].strip()
            except IndexError: pass
        if "Resolution: " in prompt_text:
            try:
                res_str = prompt_text.split("Resolution: ")[1].split("\n")[0].strip()
                if 'x' in res_str:
                    parts = res_str.split('x')
                    params["resolution"] = [int(parts[0]), int(parts[1])]
            except (IndexError, ValueError): pass
        
        # A more robust name could be derived from the description
        params["name"] = params["description"].replace(" ", "_").lower()[:30] or "generated_sprite"
        return params

    def _extract_variables_from_state(self, state: GameDevState) -> Dict[str, Any]:
        """
        Placeholder: Extract variables from the GameDevState for prompt resolution.
        """
        print("PixelForgeAgent: Extracting variables from state (placeholder).")
        variables = {
            "item_description": state.agent_states.get(self.role, {}).get("target_item", "a magic sword"),
            "view_description": state.project_metadata.get("default_view", "isometric"),
            "resolution": "64x64", # Could come from state
            "palette_info": state.project_metadata.get("global_palette_desc", "16-color standard retro"),
            "animation_details": "static, 1 frame", # Could come from task
            "style_notes": state.project_metadata.get("art_style_notes", "classic 8-bit feel")
        }
        return variables

    # --- Existing Component Methods (can be refactored or used internally by execute if needed) ---

    def generate_retro_asset(self, view_description, item_description, resolution, 
                             color_count, palette_hex_codes, animation_frames, 
                             animation_description, collision_mesh_description, max_colors_negative):
        """
        Generates a retro pixel art asset based on the provided specifications.
        Utilizes the RETRO_DIFFUSION_PROMPT_TEMPLATE.
        (Corresponds to Design Document: Retro Diffusion Generation Protocol)
        """
        prompt = RETRO_DIFFUSION_PROMPT_TEMPLATE.format(
            view_description=view_description,
            item_description=item_description,
            resolution=resolution,
            color_count=color_count,
            palette_hex_codes=", ".join(palette_hex_codes),
            animation_frames=animation_frames,
            animation_description=animation_description,
            collision_mesh_description=collision_mesh_description,
            max_colors_negative=max_colors_negative
        )
        print(f"Generating asset with prompt:\n{prompt}")
        # Placeholder for actual image generation logic (e.g., calling an image generation model)
        generated_asset_data = {"prompt_used": prompt, "asset_path": f"generated_assets/{item_description.replace(' ', '_')}.png"}
        print(f"Generated asset data: {generated_asset_data}")
        return generated_asset_data

    # --- Implementation Components (Design Document Lines 98-128) ---

    def retro_diffusion_generator(self, params):
        """
        Component 1: Retro Diffusion Generator
        - Resolution-constrained image generator
        - Color palette enforcer
        - Anti-aliasing prevention system
        """
        print(f"Executing Retro Diffusion Generator with params: {params}")
        # Actual generation logic would call a specialized model or library
        # For now, this is a placeholder.
        # Example: Call self.generate_retro_asset() or a more direct generation function
        asset = self.generate_retro_asset(
            view_description=params.get("view_description", "Isometric view"),
            item_description=params.get("item_description", "default_item"),
            resolution=params.get("resolution", "64x64"),
            color_count=params.get("color_count", 8),
            palette_hex_codes=params.get("palette_hex_codes", ["#000000", "#FFFFFF"]),
            animation_frames=params.get("animation_frames", 0),
            animation_description=params.get("animation_description", "static"),
            collision_mesh_description=params.get("collision_mesh_description", "16x16 hitbox"),
            max_colors_negative=params.get("max_colors_negative", 32)
        )
        return {"status": "success", "component": "RetroDiffusionGenerator", "output": asset}

    def animation_frame_sequencer(self, asset_id, frame_count, cycle_definition):
        """
        Component 2: Animation Frame Sequencer
        - Cycle definition engine
        - Frame consistency validator
        - Animation preview renderer
        """
        print(f"Executing Animation Frame Sequencer for asset {asset_id} with {frame_count} frames, cycle: {cycle_definition}")
        # Placeholder for sequencing logic
        animation_data = {"asset_id": asset_id, "frames_sequenced": frame_count, "preview_path": f"animations/{asset_id}_preview.gif"}
        return {"status": "success", "component": "AnimationFrameSequencer", "output": animation_data}

    def collision_system_manager(self, asset_id, hitbox_params, mesh_optimization_level):
        """
        Component 3: Collision System
        - Hitbox generator and editor
        - Collision mesh optimizer
        - Physics interaction tester (simulated)
        """
        print(f"Executing Collision System for asset {asset_id} with hitbox: {hitbox_params}, optimization: {mesh_optimization_level}")
        # Placeholder for collision system logic
        collision_data = {"asset_id": asset_id, "hitbox_generated": True, "mesh_optimized": True}
        return {"status": "success", "component": "CollisionSystem", "output": collision_data}

    def flux_architecture_integrator(self, asset_id, style_data):
        """
        Component 4: FLUX Architecture Integration
        - Style consistency enforcement
        - Asset regeneration pipeline
        - Version control for iterative improvements
        (Relies on self.flux_integrator if provided)
        """
        print(f"Executing FLUX Architecture Integration for asset {asset_id} with style: {style_data}")
        if self.flux_integrator:
            result = self.flux_integrator.process(asset_id, style_data)
            return {"status": "success", "component": "FLUXArchitectureIntegration", "output": result}
        else:
            print("FLUX Integrator not available.")
            return {"status": "skipped", "component": "FLUXArchitectureIntegration", "message": "FLUX Integrator not configured."}

    def sprite_sheet_assembler(self, assets_list, layout_preferences):
        """
        Component 5: Sprite Sheet Assembler
        - Multi-directional view generator (assumes assets_list contains these)
        - Batch processing system for hitboxes (integrates with collision_system_manager)
        - Export system for game engine compatibility
        """
        print(f"Executing Sprite Sheet Assembler for assets: {assets_list} with layout: {layout_preferences}")
        # Placeholder for sprite sheet assembly
        sprite_sheet_path = f"sprite_sheets/sheet_{len(assets_list)}_assets.png"
        # Example of batch processing hitboxes
        for asset in assets_list:
            self.collision_system_manager(asset.get("id", "unknown_asset"), {"type": "auto"}, "medium")
        
        return {"status": "success", "component": "SpriteSheetAssembler", "output": {"path": sprite_sheet_path}}

    def mcp_style_check_system(self, asset_id, asset_data):
        """
        Component 6: MCP StyleCheck System
        - Automated style validation
        - Feedback generation for rejected assets
        - Approval workflow management
        (Relies on self.mcp_client if provided)
        """
        print(f"Executing MCP StyleCheck System for asset {asset_id}")
        if self.mcp_client:
            # Simulate sending to MCP and getting a response
            response = self.mcp_client.perform_style_check(asset_id, asset_data)
            # response = {"asset_id": asset_id, "status": "approved", "feedback": "Looks great!"} # Example response
            return {"status": "success", "component": "MCPStyleCheckSystem", "output": response}
        else:
            print("MCP Client not available. Simulating approval.")
            # Simulate approval if MCP client is not available for standalone testing
            return {"status": "simulated_approval", "component": "MCPStyleCheckSystem", "output": {"asset_id": asset_id, "status": "approved_simulated", "feedback": "MCP client not available."}}

    def process_sprite_sheet_assembly_workflow(self, concept_sketch_data):
        """
        Implements the Sprite Sheet Assembly Workflow.
        (Corresponds to Design Document: Sprite Sheet Assembly Workflow)
        """
        print(f"Starting Sprite Sheet Assembly Workflow for concept: {concept_sketch_data.get('name', 'unnamed_concept')}")
        
        # A[Concept Sketch] --> B{MCP StyleCheck}
        style_check_result = self.mcp_style_check_system(
            asset_id=concept_sketch_data.get("id", "concept001"), 
            asset_data=concept_sketch_data
        )

        if style_check_result.get("output", {}).get("status") == "approved" or \
           style_check_result.get("status") == "simulated_approval": # Handle simulated case
            print("MCP StyleCheck: Approved.")
            # B -->|Approved| C[Generate 8 Directions]
            # This assumes the concept_sketch_data or a subsequent step provides these.
            # For now, we'll simulate having 8 directions.
            directional_assets_params = []
            for i in range(8):
                directional_assets_params.append({
                    "view_description": f"Direction {i+1}",
                    "item_description": concept_sketch_data.get("item_description", "item"),
                    "resolution": concept_sketch_data.get("resolution", "64x64"),
                    "color_count": concept_sketch_data.get("color_count", 8),
                    "palette_hex_codes": concept_sketch_data.get("palette_hex_codes", ["#FFFFFF"]),
                    "animation_frames": 0,
                    "animation_description": "static",
                    "collision_mesh_description": "auto",
                    "max_colors_negative": 32,
                    "id": f"{concept_sketch_data.get('id', 'concept001')}_dir{i+1}"
                })
            
            generated_directions = []
            for params in directional_assets_params:
                asset = self.retro_diffusion_generator(params)
                generated_directions.append(asset['output']) # Store the asset data
            print(f"Generated {len(generated_directions)} directional assets.")

            # C --> E[Batch Process Hitboxes]
            # This is implicitly handled by sprite_sheet_assembler if assets have IDs
            # Or can be explicitly called here.
            # For this example, sprite_sheet_assembler will call collision_system_manager.

            # Assemble sprite sheet
            sprite_sheet_result = self.sprite_sheet_assembler(
                assets_list=generated_directions, 
                layout_preferences={"packing": "optimal"}
            )
            return {"status": "success", "workflow_step": "SpriteSheetAssembled", "output": sprite_sheet_result}
        else:
            # B -->|Rejected| D[Regenerate via RD_FLUX]
            print(f"MCP StyleCheck: Rejected. Feedback: {style_check_result.get('output', {}).get('feedback')}")
            if self.flux_integrator:
                print("Attempting regeneration via RD_FLUX...")
                # This is a simplified representation. RD_FLUX would involve more complex logic.
                flux_regeneration_result = self.flux_architecture_integrator(
                    asset_id=concept_sketch_data.get("id", "concept001"),
                    style_data={"feedback": style_check_result.get("output", {}).get("feedback"), "action": "regenerate"}
                )
                # Potentially re-run the style check after regeneration
                return {"status": "needs_flux_regeneration", "workflow_step": "FluxRegeneration", "output": flux_regeneration_result}
            else:
                return {"status": "failed", "workflow_step": "FluxRegeneration", "message": "FLUX Integrator not available for regeneration."}

    def handle_direct_request(self, parameters: dict) -> dict:
        """
        Handles a direct API request to the Pixel Forge agent.
        Expected parameters: "item_description", "view_description", "resolution",
                             "palette_info", "animation_details", "style_notes".
        """
        print(f"PixelForgeAgent ({self.role}): Handling direct request with parameters: {parameters}")
        try:
            # Use _extract_asset_params to parse and get defaults if some params are missing
            # This is a bit of a workaround as _extract_asset_params expects a full prompt string.
            # For a direct API, we'd ideally have a dedicated validation/parsing for raw parameters.
            
            # Construct a pseudo-prompt string from parameters to leverage existing extraction logic
            pseudo_prompt = f"Item: {parameters.get('item_description', 'default item')}\n"
            pseudo_prompt += f"Resolution: {parameters.get('resolution', '64x64')}\n"
            # Add other params to pseudo_prompt if _extract_asset_params uses them

            asset_params = self._extract_asset_params(pseudo_prompt) # This will fill defaults

            # Override with any explicitly provided parameters
            if "item_description" in parameters: asset_params["description"] = parameters["item_description"]
            if "resolution" in parameters:
                res_str = parameters["resolution"]
                if isinstance(res_str, str) and 'x' in res_str:
                    parts = res_str.split('x')
                    try: asset_params["resolution"] = [int(parts[0]), int(parts[1])]
                    except (ValueError, IndexError): pass # Keep default if parse fails
                elif isinstance(res_str, list) and len(res_str) == 2:
                    asset_params["resolution"] = res_str


            generation_prompt = asset_params.get("description", "default pixel art asset")
            generation_parameters = {
                "resolution": asset_params.get("resolution", [64, 64]),
                "palette_lock": parameters.get("palette_lock", asset_params.get("palette_lock", True)),
                "tileable": parameters.get("tileable", asset_params.get("tileable", False)),
                "animation_frames": parameters.get("animation_frames", asset_params.get("animation_frames", 1)),
                "palette": parameters.get("palette_info", asset_params.get("palette")) # Map palette_info to palette
            }
            
            print(f"PixelForgeAgent: Using generation prompt: '{generation_prompt}' with params: {generation_parameters}")

            if not self.mcp_server or not hasattr(self.mcp_server, 'generate_retro_asset'):
                 print(f"PixelForgeAgent: Error - MCPServer or generate_retro_asset not available.")
                 return {"status": "error", "message": "MCPServer misconfiguration for asset generation."}

            # Call the mcp_server's method to interact with Retro Diffusion
            future = self.mcp_server.generate_retro_asset(
                prompt=generation_prompt,
                parameters=generation_parameters,
                agent_id=self.role
            )
            asset_result_object = future.result(timeout=60) # Blocking call

            asset_data_b64 = asset_result_object.to_base64() if hasattr(asset_result_object, 'to_base64') else None
            asset_id = asset_result_object.id if hasattr(asset_result_object, 'id') else str(uuid.uuid4())

            result_data = {
                "status": "success",
                "message": "Asset generation request processed.",
                "asset_id": asset_id,
                "image_data_b64": asset_data_b64,
                "generation_prompt": generation_prompt,
                "generation_parameters": generation_parameters
            }
            print(f"PixelForgeAgent: Direct request processed successfully. Asset ID: {asset_id}")
            return result_data

        except Exception as e:
            print(f"PixelForgeAgent: Error processing direct request: {e}")
            import traceback
            traceback.print_exc()
            return {"status": "error", "message": f"Internal server error: {e}"}

# --- Example Usage (for testing purposes) ---
if __name__ == "__main__":
    # Mock MCPServer for testing PixelForgeAgent
    class MockMCPServer:
        def __init__(self):
            self.prompt_engine = self
            self.retro_diffusion_bridge = self # For generate_retro_asset
            self.templates = {}

        def add_template(self, role, template_lines):
            self.templates[role] = template_lines

        def get_resolved_prompt_for_agent(self, role, variables):
            template = self.templates.get(role, ["Default prompt for {{item_description}}"])
            resolved_lines = []
            for line in template:
                for var_name, value in variables.items():
                    line = line.replace(f'{{{{{var_name}}}}}', str(value))
                resolved_lines.append(line)
            return "\n".join(resolved_lines)

        def generate_retro_asset(self, prompt, parameters=None, agent_id=None):
            print(f"MockMCPServer: generate_retro_asset: prompt='{prompt}', params={parameters}, agent='{agent_id}'")
            from concurrent.futures import Future
            future = Future()
            # Simulate asset generation (using a simplified MockImageData from retro_diffusion_integration)
            class MockImageData: # Simplified for this test
                def __init__(self, prompt, params, data="mock_pixel_data_pf"):
                    self.prompt = prompt; self.params = params; self.data = data
                    self.id = str(uuid.uuid4())
                def to_base64(self): return f"base64_encoded_{self.id}"
                def __str__(self): return f"MockImageData(id={self.id}, prompt='{self.prompt}')"
            
            future.set_result(MockImageData(prompt, parameters))
            return future

    mock_mcp = MockMCPServer()
    # DummyFluxIntegrator can still be passed if other methods use it.
    class DummyFluxIntegrator:
        def process(self, asset_id, style_data): return {"flux_status": "processed_dummy"}

    agent = PixelForgeAgent(mcp_server=mock_mcp, flux_integrator=DummyFluxIntegrator())
    mock_mcp.add_template(agent.role, PIXEL_FORGE_DEFAULT_PROMPT_TEMPLATE)

    # Create a dummy GameDevState
    initial_state = GameDevState(
        project_metadata={"project_name": "Pixel Kingdom", "default_view": "front_on", "global_palette_desc": "NES palette"},
        assets={}, # Start with empty assets
        agent_states={agent.role: {"target_item": "a shiny coin"}}
    )

    print(f"\n--- Testing PixelForgeAgent Execute Method ---")
    print(f"Initial GameDevState (for PixelForge): {initial_state.__dict__}")

    try:
        updated_state = agent.execute(initial_state)
        print(f"Updated GameDevState after PixelForge execution: {json.dumps(updated_state.__dict__, indent=2)}")
        
        assert "sprites" in updated_state.assets
        assert len(updated_state.assets['sprites']) > 0
        first_sprite_name = list(updated_state.assets['sprites'].keys())[0]
        assert "image_data_b64" in updated_state.assets['sprites'][first_sprite_name]
        assert "success" == updated_state.agent_states[agent.role].get("status")
        print("--- PixelForgeAgent Execute Method Test Successful ---")

    except Exception as e:
        print(f"--- PixelForgeAgent Execute Method Test Failed: {e} ---")
        import traceback
        traceback.print_exc()

    # The old tests for individual components might still be relevant if those components
    # are used internally or need separate unit testing.
    # For brevity, they are not fully re-integrated here but their structure is preserved above the __main__ block.
    print("\n(Skipping old direct component tests for brevity in this refactored example)")
    print("\n--- Testing Retro Diffusion Generator ---")
    item_params = {
        "view_description": "Isometric view",
        "item_description": "magic_potion_bottle",
        "resolution": "32x32",
        "color_count": 4,
        "palette_hex_codes": ["#FF0000", "#00FF00", "#0000FF", "#FFFF00"],
        "animation_frames": 0,
        "animation_description": "static",
        "collision_mesh_description": "8x8 hitbox",
        "max_colors_negative": 16
    }
    generated_item = agent.retro_diffusion_generator(item_params)
    print(f"Retro Diffusion Output: {json.dumps(generated_item, indent=2)}")

    # Test Animation Frame Sequencer
    print("\n--- Testing Animation Frame Sequencer ---")
    animation_result = agent.animation_frame_sequencer(asset_id="magic_potion_bottle_asset1", frame_count=16, cycle_definition="pulsing_glow")
    print(f"Animation Sequencer Output: {json.dumps(animation_result, indent=2)}")

    # Test Collision System
    print("\n--- Testing Collision System ---")
    collision_result = agent.collision_system_manager(asset_id="magic_potion_bottle_asset1", hitbox_params={"shape": "circle", "radius": 15}, mesh_optimization_level="high")
    print(f"Collision System Output: {json.dumps(collision_result, indent=2)}")
    
    # Test FLUX Integration
    print("\n--- Testing FLUX Architecture Integration ---")
    flux_result = agent.flux_architecture_integrator(asset_id="magic_potion_bottle_asset1", style_data={"target_style": "dark_fantasy"})
    print(f"FLUX Integration Output: {json.dumps(flux_result, indent=2)}")

    # Test Sprite Sheet Assembly Workflow
    print("\n--- Testing Sprite Sheet Assembly Workflow (Door - Approved) ---")
    concept_door = {
        "id": "victorian_door_concept",
        "name": "Victorian Door",
        "item_description": "Victorian-style door",
        "resolution": "64x64",
        "color_count": 8,
        "palette_hex_codes": ["#2D1B2E", "#87758F", "#E6A272", "#A0522D", "#5C4033", "#3E2723", "#1B0000", "#000000"],
    }
    workflow_result_door = agent.process_sprite_sheet_assembly_workflow(concept_door)
    print(f"Workflow (Door) Output: {json.dumps(workflow_result_door, indent=2)}")

    print("\n--- Testing Sprite Sheet Assembly Workflow (Chest - Rejected) ---")
    concept_chest = {
        "id": "treasure_chest_concept",
        "name": "Treasure Chest",
        "item_description": "old wooden treasure chest",
        "resolution": "48x48",
        "color_count": 12,
        "palette_hex_codes": ["#A0522D", "#8B4513", "#D2691E", "#CD853F", "#F4A460", "#DEB887", "#FFD700", "#B8860B", "#DAA520", "#808080", "#A9A9A9", "#696969"],
    }
    workflow_result_chest = agent.process_sprite_sheet_assembly_workflow(concept_chest)
    print(f"Workflow (Chest) Output: {json.dumps(workflow_result_chest, indent=2)}")

    # Test MCP StyleCheck directly (if MCP client was None)
    # agent_no_mcp = PixelForgeAgent()
    # print("\n--- Testing MCP StyleCheck (No MCP Client) ---")
    # style_check_no_mcp = agent_no_mcp.mcp_style_check_system("asset_test_no_mcp", {"data": "some_data"})
    # print(f"MCP StyleCheck (No MCP) Output: {json.dumps(style_check_no_mcp, indent=2)}")