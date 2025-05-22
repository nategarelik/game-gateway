# src/agents/pixel_forge_agent.py
import asyncio
import logging
from typing import Dict, Any
from .base_agent import BaseAgent

logger = logging.getLogger(__name__)

class PixelForgeAgent(BaseAgent):
    """
    PixelForgeAgent is responsible for generating game assets like images,
    textures, and simple 3D model placeholders based on prompts or tasks
    received from the MCP server. Its role is now shifted to placing existing
    assets/placeholders in the Unity Editor.
    """
    def __init__(self, agent_id: str, mcp_server_url: str, unity_bridge=None, capabilities: list = None):
        super().__init__(agent_id, mcp_server_url, capabilities or ["asset_generation_2d", "asset_generation_3d_placeholder", "asset_placement"])
        self.unity_bridge = unity_bridge
        # Potentially initialize connections to Retro Diffusion, Muse, etc. here
        # For now, we'll use placeholder logic.
        logger.info(f"PixelForgeAgent ({self.agent_id}) initialized with capabilities: {self.capabilities}")

    async def process_task(self, task_details: dict) -> dict:
        """
        Process an asset generation or placement task.
        """
        logger.info(f"PixelForgeAgent ({self.agent_id}) received task: {task_details}")
        task_id = task_details.get("task_id")
        task_type = task_details.get("task_type") # Use task_type for LLM simulation

        await self.post_event_to_mcp(
            event_type="pixel_forge_progress",
            event_data={"task_id": task_id, "status": "started", "task_type": task_type}
        )

        try:
            await self.post_event_to_mcp(
                event_type="pixel_forge_progress",
                event_data={"task_id": task_id, "status": "simulating_llm", "message": "Simulating LLM response."}
            )
            llm_response = await self._resolve_prompt_and_simulate_llm(task_type, task_details)

            if llm_response.get("error"):
                logger.error(f"Task {task_id}: LLM simulation failed. Error: {llm_response.get('error')}")
                return {"status": "failure", "message": llm_response.get('error'), "output": None}

            action = llm_response.get("action")
            parameters = llm_response.get("parameters", {})
            
            tool_execution_result = None

            if action == "generate_image":
                prompt = parameters.get("description")
                style_guidelines = parameters.get("image_style") # Re-using for style
                if not prompt:
                    error_msg = "Missing 'description' from LLM response for image generation."
                    logger.error(f"Task {task_id}: {error_msg}")
                    tool_execution_result = {"status": "error", "message": error_msg}
                else:
                    await self.post_event_to_mcp(
                        event_type="pixel_forge_progress",
                        event_data={"task_id": task_id, "status": "generating_image", "message": "Calling generate_image."}
                    )
                    tool_execution_result = await self.generate_image(prompt, {"style": style_guidelines})
            elif action == "manipulate_scene": # For placing assets
                asset_name = parameters.get("target_object")
                position = parameters.get("position")
                rotation = parameters.get("rotation", {"x": 0, "y": 0, "z": 0})
                scale = parameters.get("scale", {"x": 1, "y": 1, "z": 1})

                if not all([asset_name, position]):
                    error_msg = "Missing 'target_object' or 'position' from LLM response for asset placement."
                    logger.error(f"Task {task_id}: {error_msg}")
                    tool_execution_result = {"status": "error", "message": error_msg}
                else:
                    await self.post_event_to_mcp(
                        event_type="pixel_forge_progress",
                        event_data={"task_id": task_id, "status": "placing_asset", "message": "Calling place_asset_in_unity."}
                    )
                    tool_execution_result = await self.place_asset_in_unity(asset_name, position, rotation, scale)
            elif action == "log_task": # Default mock action
                logger.info(f"Task {task_id}: LLM suggested logging task: {parameters.get('message')}")
                tool_execution_result = {"status": "success", "message": "Task logged."}
            else:
                logger.warning(f"Task {task_id}: Unhandled LLM action: {action}. Parameters: {parameters}")
                tool_execution_result = {"status": "unhandled_action", "message": f"LLM suggested unhandled action: {action}"}

            final_status = "completed_successfully" if tool_execution_result and tool_execution_result.get("status") == "success" else "failed"
            final_message = tool_execution_result.get("message", "No specific message from tool execution.") if tool_execution_result else "No tool execution performed."

            await self.post_event_to_mcp(
                event_type="pixel_forge_complete",
                event_data={"task_id": task_id, "status": final_status, "output": tool_execution_result}
            )
            return {"status": final_status, "message": final_message, "output": tool_execution_result}

        except Exception as e:
            logger.error(f"Error processing task {task_id} in PixelForgeAgent: {e}", exc_info=True)
            await self.post_event_to_mcp(
                event_type="pixel_forge_error",
                event_data={"task_id": task_id, "status": "failed", "error": str(e)}
            )
            return {"status": "failure", "message": f"Error processing task: {str(e)}", "output": None}

    async def place_asset_in_unity(self, asset_name: str, position: dict, rotation: dict, scale: dict) -> dict:
        """
        Places an existing asset or placeholder in the Unity Editor via the UnityToolchainBridge.
        """
        if not self.unity_bridge:
            return {"status": "error", "message": "UnityToolchainBridge not available. Cannot place asset."}

        logger.info(f"Placing asset '{asset_name}' at position {position} in Unity.")
        try:
            response = await self.unity_bridge.manipulate_scene(
                operation="create_object", # Assuming 'create_object' can also place existing assets by name
                target_object=asset_name,
                parameters={"position": position, "rotation": rotation, "scale": scale}
            )
            logger.info(f"Asset '{asset_name}' placed in Unity: {response}")
            return {"status": "success", "message": f"Asset '{asset_name}' placed.", "unity_response": response}
        except Exception as e:
            logger.error(f"Failed to place asset '{asset_name}' in Unity: {e}")
            return {"status": "error", "message": f"Failed to place asset '{asset_name}': {e}"}

    async def generate_image(self, prompt: str, style_guidelines: dict = None) -> dict:
        """Placeholder for direct image generation call, perhaps using Retro Diffusion."""
        logger.info(f"PixelForgeAgent ({self.agent_id}): Simulating direct image generation for '{prompt}'...")
        # Actual implementation would call Retro Diffusion bridge
        await asyncio.sleep(1)
        return {"path": f"generated_assets/{self.agent_id}/direct_image_{hash(prompt)}.png", "status": "simulated_success"}

    async def generate_texture(self, prompt: str, style_guidelines: dict = None) -> dict:
        """Placeholder for direct texture generation call."""
        logger.info(f"PixelForgeAgent ({self.agent_id}): Simulating direct texture generation for '{prompt}'...")
        await asyncio.sleep(1)
        return {"path": f"generated_assets/{self.agent_id}/direct_texture_{hash(prompt)}.png", "status": "simulated_success"}

    async def generate_model_placeholder(self, prompt: str, style_guidelines: dict = None) -> dict:
        """Placeholder for direct 3D model placeholder generation, perhaps using Muse concepts."""
        logger.info(f"PixelForgeAgent ({self.agent_id}): Simulating 3D model placeholder for '{prompt}'...")
        # Actual implementation might involve conceptual generation via Muse bridge
        await asyncio.sleep(1)
        return {"path": f"generated_assets/{self.agent_id}/direct_model_{hash(prompt)}.obj", "status": "simulated_success"}

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

# Example Usage (requires a running MCP server or mock)
if __name__ == '__main__':
    async def main():
        mcp_url = "http://localhost:8000/mcp" # Example MCP URL
        agent = PixelForgeAgent(agent_id="pixel_forge_001", mcp_server_url=mcp_url)
        
        # Simulate registration (in a real scenario, MCP would confirm)
        # await agent.register_with_mcp()

        # Example task: Place an asset
        example_place_task = {
            "task_id": "pf_place_task_123",
            "task_type": "manipulate_scene", # Changed to match LLM output action
            "target_object": "Prefab_Tree_01", # Changed to match LLM output parameter
            "position": {"x": 10, "y": 0, "z": 5},
            "rotation": {"x": 0, "y": 45, "z": 0},
            "scale": {"x": 2, "y": 2, "z": 2}
        }
        result_place = await agent.process_task(example_place_task)
        logger.info(f"Asset placement task result: {result_place}")

        # Example task: Generate an asset (de-prioritized but still functional)
        example_generate_task = {
            "task_id": "pf_generate_task_456",
            "task_type": "image_generation", # Changed to match LLM output action
            "description": "A stylized rock texture", # Changed to match LLM output parameter
            "image_style": "512x512", # Changed to match LLM output parameter
            "output_path_suggestion": "project_x/assets/textures/"
        }
        result_generate = await agent.process_task(example_generate_task)
        logger.info(f"Asset generation task result: {result_generate}")
        
        await agent.shutdown()

    asyncio.run(main())