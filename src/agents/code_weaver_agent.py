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
        """
        task_id = task_details.get("task_id", "unknown_task")
        task_type = task_details.get("task_type") # This is the task_type for the LLM simulation

        if not task_type:
            error_msg = f"'task_type' missing in task_details for task {task_id}."
            logger.error(error_msg)
            await self.post_event_to_mcp(
                event_type="code_weaver_error",
                event_data={"task_id": task_id, "status": "failed", "error": error_msg}
            )
            return {"status": "failure", "message": error_msg, "output": None}

        logger.info(f"CodeWeaverAgent ({self.agent_id}) processing task ID: {task_id}, Type: {task_type}")
        await self.post_event_to_mcp(
            event_type="code_weaver_progress",
            event_data={"task_id": task_id, "status": "started", "message": f"Processing task type: {task_type}"}
        )

        try:
            await self.post_event_to_mcp(
                event_type="code_weaver_progress",
                event_data={"task_id": task_id, "status": "simulating_llm", "message": "Simulating LLM response."}
            )
            llm_response = await self._resolve_prompt_and_simulate_llm(task_type, task_details)

            if llm_response.get("error"):
                logger.error(f"Task {task_id}: LLM simulation failed. Error: {llm_response.get('error')}")
                return {"status": "failure", "message": llm_response.get('error'), "output": None}

            action = llm_response.get("action")
            parameters = llm_response.get("parameters", {})
            
            tool_execution_result = None

            if action == "generate_script":
                script_name = parameters.get("script_name")
                script_content = parameters.get("script_content")
                script_path = parameters.get("script_path") # Optional
                
                if not script_name or not script_content:
                    error_msg = "Missing 'script_name' or 'script_content' from LLM response for script generation."
                    logger.error(f"Task {task_id}: {error_msg}")
                    tool_execution_result = {"status": "error", "message": error_msg}
                else:
                    await self.post_event_to_mcp(
                        event_type="code_weaver_progress",
                        event_data={"task_id": task_id, "status": "implementing_script", "message": "Calling Unity Bridge to implement script."}
                    )
                    tool_execution_result = await self.generate_and_implement_script(script_name, script_content, script_path)
            elif action == "log_task": # Default mock action
                logger.info(f"Task {task_id}: LLM suggested logging task: {parameters.get('message')}")
                tool_execution_result = {"status": "success", "message": "Task logged."}
            else:
                logger.warning(f"Task {task_id}: Unhandled LLM action: {action}. Parameters: {parameters}")
                tool_execution_result = {"status": "unhandled_action", "message": f"LLM suggested unhandled action: {action}"}

            final_status = "completed_successfully" if tool_execution_result and tool_execution_result.get("status") == "success" else "failed"
            final_message = tool_execution_result.get("message", "No specific message from tool execution.") if tool_execution_result else "No tool execution performed."

            await self.post_event_to_mcp(
                event_type="code_weaver_complete",
                event_data={"task_id": task_id, "status": final_status, "output": tool_execution_result}
            )
            return {"status": final_status, "message": final_message, "output": tool_execution_result}

        except Exception as e:
            logger.error(f"Error processing task {task_id} in CodeWeaverAgent: {e}", exc_info=True)
            await self.post_event_to_mcp(
                event_type="code_weaver_error",
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