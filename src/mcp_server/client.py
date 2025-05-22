import json
import httpx # Using httpx for async requests
from typing import Dict, Any

class MCPClient:
    """
    A client for interacting with the MCP Server.
    This is a basic implementation. Agents will use this to communicate.
    """
    def __init__(self, server_url: str, agent_id: str):
        self.server_url = server_url
        self.agent_id = agent_id
        self.connected = False # This will be set by connect method
        self.client = httpx.AsyncClient() # Initialize httpx client
        print(f"[MCPClient INFO] Instance created for agent '{self.agent_id}' targeting server '{self.server_url}'.")

    async def connect(self) -> bool:
        """Simulates connecting to the MCP server. In a real scenario, this might involve a handshake."""
        print(f"[MCPClient INFO] Agent '{self.agent_id}' attempting to connect to {self.server_url}...")
        # For now, simply mark as connected. A real connect might ping an endpoint.
        try:
            # Example: Ping a status endpoint if available, or just assume connection for now
            # response = await self.client.get(f"{self.server_url}/status") # Assuming a status endpoint
            # response.raise_for_status()
            self.connected = True
            print(f"[MCPClient INFO] Agent '{self.agent_id}' connected successfully (simulated).")
            return True
        except httpx.RequestError as e:
            print(f"[MCPClient ERROR] Agent '{self.agent_id}' failed to connect: {e}")
            self.connected = False
            return False

    async def disconnect(self):
        """Closes the httpx client session."""
        if self.connected:
            print(f"[MCPClient INFO] Agent '{self.agent_id}' disconnecting from {self.server_url}.")
            await self.client.aclose()
            self.connected = False
        else:
            print(f"[MCPClient INFO] Agent '{self.agent_id}' was not connected.")

    async def post_event(self, event_type: str, payload: Dict[str, Any]) -> bool:
        """
        Posts an event to the MCP server asynchronously.
        """
        if not self.connected:
            print(f"[MCPClient ERROR] Agent '{self.agent_id}' cannot post event: Not connected. Attempting to connect...")
            await self.connect()
            if not self.connected:
                print(f"[MCPClient ERROR] Agent '{self.agent_id}' failed to connect. Event not posted.")
                return False
        
        event_endpoint = f"{self.server_url}/api/v1/post_event" # Assuming this is the correct endpoint
        event_payload = {
            "event_type": event_type,
            "event_data": payload, # The API expects event_data to contain the task_id and other details
            "agent_id": self.agent_id # Though API might not use this directly if task_id is primary
        }
        print(f"[MCPClient INFO] Agent '{self.agent_id}' posting event '{event_type}' to {event_endpoint} with payload: {json.dumps(event_payload, indent=1)}")
        
        try:
            response = await self.client.post(event_endpoint, json=event_payload)
            response.raise_for_status()
            print(f"[MCPClient INFO] Event '{event_type}' posted successfully. Server response: {response.json()}")
            return True
        except httpx.HTTPStatusError as http_err:
            print(f"[MCPClient ERROR] HTTP error occurred while posting event '{event_type}': {http_err} - {http_err.response.text}")
            return False
        except httpx.RequestError as req_err:
            print(f"[MCPClient ERROR] An unexpected error occurred while posting event '{event_type}': {req_err}")
            return False

    async def use_mcp_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
            """
            Calls a tool on the target MCP server asynchronously.
            """
            if not self.connected:
                print(f"[MCPClient ERROR] Agent '{self.agent_id}' cannot use tool: Not connected. Attempting to connect...")
                await self.connect() # Attempt to connect before using a tool
                if not self.connected:
                    print(f"[MCPClient ERROR] Agent '{self.agent_id}' failed to connect. Tool not used.")
                    return {"error": "Failed to connect to MCP server before using tool."}

            endpoint = f"{self.server_url}/api/v1/tools/{tool_name}/use"
            payload = {
                "agent_id": self.agent_id,
                "arguments": arguments
            }
            print(f"[MCPClient INFO] Agent '{self.agent_id}' using tool '{tool_name}' on {self.server_url} with arguments: {arguments}")
            
            try:
                response = await self.client.post(endpoint, json=payload)
                response.raise_for_status()
                response_data = response.json()
                print(f"[MCPClient INFO] Tool '{tool_name}' executed successfully. Response: {response_data}")
                return response_data
            except httpx.HTTPStatusError as http_err:
                print(f"[MCPClient ERROR] HTTP error occurred while using tool '{tool_name}': {http_err} - {http_err.response.text}")
                return {"error": f"HTTP error: {http_err}", "status_code": http_err.response.status_code, "details": http_err.response.text}
            except httpx.RequestError as req_err: # Catches ConnectionError, Timeout, etc.
                print(f"[MCPClient ERROR] Request error occurred while using tool '{tool_name}': {req_err}")
                return {"error": f"Request error: {req_err}"}
            except json.JSONDecodeError as json_err: # If response is not valid JSON
                print(f"[MCPClient ERROR] Failed to decode JSON response from tool '{tool_name}'. Response text: {response.text if 'response' in locals() else 'N/A'}. Error: {json_err}")
                return {"error": "Failed to decode JSON response", "response_text": response.text if 'response' in locals() else None}