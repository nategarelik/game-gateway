# src/agents/base_agent.py
import httpx # Or any other HTTP client library you prefer

class BaseAgent:
    def __init__(self, agent_id: str, mcp_server_url: str, capabilities: list = None):
        self.agent_id = agent_id
        self.mcp_server_url = mcp_server_url
        self.capabilities = capabilities if capabilities is not None else []
        self.http_client = httpx.AsyncClient() # For MCP communication

    async def process_task(self, task_details: dict) -> dict:
        """
        Process a task assigned by the MCP server.
        This method should be overridden by specialized agents.
        """
        print(f"Agent {self.agent_id} received task: {task_details}")
        raise NotImplementedError("Subclasses must implement process_task")

    async def register_with_mcp(self):
        """
        Register this agent with the MCP server.
        """
        registration_url = f"{self.mcp_server_url}/register_agent"
        payload = {
            "agent_id": self.agent_id,
            "capabilities": self.capabilities,
            "endpoint": f"http://localhost:XXXX/{self.agent_id}" # Placeholder agent's own endpoint
        }
        try:
            response = await self.http_client.post(registration_url, json=payload)
            response.raise_for_status()
            print(f"Agent {self.agent_id} registered successfully with MCP.")
            return response.json()
        except httpx.HTTPStatusError as e:
            print(f"Error registering agent {self.agent_id} with MCP: {e.response.status_code} - {e.response.text}")
            return None
        except httpx.RequestError as e:
            print(f"Request error while registering agent {self.agent_id}: {e}")
            return None

    async def post_event_to_mcp(self, event_type: str, event_data: dict):
        """
        Post an event to the MCP server.
        """
        event_url = f"{self.mcp_server_url}/post_event"
        payload = {"event_type": event_type, "data": event_data, "source_agent_id": self.agent_id}
        try:
            response = await self.http_client.post(event_url, json=payload)
            response.raise_for_status()
            print(f"Agent {self.agent_id} posted event '{event_type}' successfully.")
            return response.json()
        except httpx.HTTPStatusError as e:
            print(f"Error posting event from agent {self.agent_id}: {e.response.status_code} - {e.response.text}")
            return None
        except httpx.RequestError as e:
            print(f"Request error while posting event from agent {self.agent_id}: {e}")
            return None

    async def shutdown(self):
        await self.http_client.aclose()