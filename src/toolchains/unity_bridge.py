import os
from typing import Dict, Any
from src.mcp_server.client import MCPClient # Corrected import path

class UnityToolchainBridge:
    def __init__(self, mcp_server_instance):
        self.mcp_server_instance = mcp_server_instance
        self.unity_mcp_client = MCPClient(
            server_url=os.environ.get("UNITY_MCP_URL", "http://localhost:8080"), # Default URL for Unity MCP
            agent_id="unity_toolchain_bridge_client" # Identifier for this client component
        )
        print("[INFO] UnityToolchainBridge initialized.")

    async def send_command(self, command_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sends a command to the external Unity MCP server asynchronously.

        Args:
            command_name (str): The name of the tool/command to execute on the Unity MCP.
            arguments (Dict[str, Any]): A dictionary of arguments for the command.

        Returns:
            Dict[str, Any]: The response from the Unity MCP server.
        """
        print(f"UnityToolchainBridge: Sending command '{command_name}' to Unity MCP with args: {arguments}")
        try:
            # Use the MCPClient to interact with the external Unity MCP server
            # Ensure the client is connected before making a call
            if not self.unity_mcp_client.connected:
                await self.unity_mcp_client.connect() # Attempt to connect if not already
            
            response = await self.unity_mcp_client.use_mcp_tool(
                tool_name=command_name,
                arguments=arguments
            )
            print(f"Unity MCP response: {response}")
            return response
        except Exception as e:
            print(f"[ERROR] Failed to send command to Unity MCP: {e}")
            # Consider how to handle this error. Raising ConnectionError might be too generic.
            # Returning an error dictionary might be more consistent with use_mcp_tool's error handling.
            return {"error": f"Failed to communicate with Unity MCP: {e}", "details": str(e)}

    async def execute_script(self, script_content: str, script_path: str = None) -> Dict[str, Any]:
        """
        Executes a C# script in the Unity Editor asynchronously.

        Args:
            script_content (str): The content of the C# script to execute.
            script_path (str, optional): The path where the script should be created/updated in Unity.
                                         If None, a temporary path might be used by the Unity MCP.

        Returns:
            Dict[str, Any]: The result of the script execution from Unity.
        """
        print(f"UnityToolchainBridge: Executing script in Unity. Path: {script_path}")
        return await self.send_command("execute_script", {"script_content": script_content, "script_path": script_path})

    async def manipulate_scene(self, operation: str, target_object: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sends a scene manipulation command to the Unity Editor asynchronously.

        Args:
            operation (str): The type of scene operation (e.g., "create_object", "move_object", "delete_object").
            target_object (str): The name or ID of the object to manipulate.
            parameters (Dict[str, Any]): Specific parameters for the operation (e.g., position, rotation, scale).

        Returns:
            Dict[str, Any]: The result of the scene manipulation from Unity.
        """
        print(f"UnityToolchainBridge: Manipulating scene in Unity. Operation: {operation}, Target: {target_object}")
        return await self.send_command("manipulate_scene", {"operation": operation, "target_object": target_object, "parameters": parameters})

    # Add more specific Unity interaction methods as needed