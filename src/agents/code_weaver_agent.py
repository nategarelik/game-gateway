import logging
from typing import Dict, Any

from .base_agent import BaseAgent

logger = logging.getLogger(__name__)

class CodeWeaverAgent(BaseAgent):
    def __init__(self, agent_id: str, mcp_server_url: str, unity_bridge=None):
        super().__init__(agent_id, mcp_server_url, capabilities=["script_generation", "game_logic_implementation", "ui_scripting"])
        self.unity_bridge = unity_bridge
        logger.info(f"CodeWeaverAgent ({self.agent_id}) initialized with capabilities: {self.capabilities}")

    async def generate_and_implement_script(self, script_name: str, script_content: str, script_path: str = None) -> Dict[str, Any]:
        """
        Generates a C# script and implements it in Unity via the UnityToolchainBridge.

        Args:
            script_name (str): The name of the script (e.g., "PlayerController").
            script_content (str): The actual C# code content for the script.
            script_path (str, optional): The full path where the script should be created/updated in Unity.
                                         If None, a default path like "Assets/Scripts/{script_name}.cs" will be used.

        Returns:
            Dict[str, Any]: The result of the script implementation from Unity.
        """
        if not self.unity_bridge:
            logger.error("UnityToolchainBridge not available. Cannot implement script.")
            return {"status": "error", "message": "UnityToolchainBridge not available."}

        if not script_path:
            script_path = f"Assets/Scripts/{script_name}.cs"

        logger.info(f"CodeWeaverAgent: Implementing script '{script_name}' at '{script_path}' in Unity.")
        try:
            response = await self.unity_bridge.execute_script(script_content, script_path)
            logger.info(f"Script '{script_name}' implemented in Unity: {response}")
            return {"status": "success", "message": f"Script '{script_name}' implemented successfully.", "unity_response": response}
        except Exception as e:
            logger.error(f"Failed to implement script '{script_name}' in Unity: {e}")
            return {"status": "error", "message": f"Failed to implement script '{script_name}': {e}"}

    async def process_task(self, task_details: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processes a task related to script generation and implementation.

        Expected task_details:
        {
            "task_id": "unique_task_id",
            "task_type": "generate_script" or "modify_script",
            "script_name": "NameOfScript",
            "script_content": "string_containing_csharp_code",
            "script_path": "Optional/Path/To/Script.cs"
        }
        """
        task_id = task_details.get("task_id", "unknown_task")
        task_type = task_details.get("task_type")
        script_name = task_details.get("script_name")
        script_content = task_details.get("script_content")
        script_path = task_details.get("script_path")

        logger.info(f"CodeWeaverAgent ({self.agent_id}) processing task ID: {task_id}, Type: {task_type}")
        await self.post_event_to_mcp(
            event_type="code_weaver_progress",
            event_data={"task_id": task_id, "status": "started", "message": f"Processing task type: {task_type}"}
        )

        if task_type == "generate_script" or task_type == "modify_script":
            if not script_name or not script_content:
                error_msg = "Missing 'script_name' or 'script_content' for script generation/modification task."
                logger.error(error_msg)
                await self.post_event_to_mcp(
                    event_type="code_weaver_error",
                    event_data={"task_id": task_id, "status": "failed", "error": error_msg}
                )
                return {"status": "failure", "message": error_msg}
            
            result = await self.generate_and_implement_script(script_name, script_content, script_path)
            if result.get("status") == "success":
                await self.post_event_to_mcp(
                    event_type="code_weaver_complete",
                    event_data={"task_id": task_id, "status": "completed_successfully", "result": result}
                )
                return {"status": "success", "message": f"Script '{script_name}' processed successfully.", "output": result}
            else:
                await self.post_event_to_mcp(
                    event_type="code_weaver_error",
                    event_data={"task_id": task_id, "status": "failed", "error": result.get("message")}
                )
                return {"status": "failure", "message": result.get("message")}
        else:
            error_msg = f"Unsupported task type: {task_type}"
            logger.error(error_msg)
            await self.post_event_to_mcp(
                event_type="code_weaver_error",
                event_data={"task_id": task_id, "status": "failed", "error": error_msg}
            )
            return {"status": "failure", "message": error_msg}

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