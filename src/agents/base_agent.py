# src/agents/base_agent.py
import httpx
import os # Import os to access environment variables
import json # Import json for parsing LLM responses
from typing import Dict, Any, Optional # Import Dict, Any, and Optional for type hinting
from src.mcp_server.models.api_models import PromptResolutionRequest, PromptResolutionResponse
from langchain_openai import ChatOpenAI # Import ChatOpenAI for OpenAI LLM interaction
from langchain_core.messages import HumanMessage, SystemMessage # Import for ChatOpenAI/ChatOpenRouter
from langchain_core.utils.utils import secret_from_env
from pydantic import Field, SecretStr

# Custom ChatOpenRouter class
class ChatOpenRouter(ChatOpenAI):
    openai_api_key: Optional[SecretStr] = Field(
        alias="api_key",
        default_factory=secret_from_env("OPENROUTER_API_KEY", default=None),
    )
    @property
    def lc_secrets(self) -> dict[str, str]:
        return {"openai_api_key": "OPENROUTER_API_KEY"}

    def __init__(self,
                 openai_api_key: Optional[str] = None,
                 **kwargs):
        openai_api_key = (
            openai_api_key or os.environ.get("OPENROUTER_API_KEY")
        )
        super().__init__(
            base_url="https://openrouter.ai/api/v1",
            openai_api_key=openai_api_key,
            **kwargs
        )

class BaseAgent:
    def __init__(self, agent_id: str, mcp_server_url: str, capabilities: list = None):
        self.agent_id = agent_id
        self.mcp_server_url = mcp_server_url
        self.capabilities = capabilities if capabilities is not None else []
        self.http_client = httpx.AsyncClient() # For MCP communication
        # Initialize OpenRouter LLM
        self.llm = ChatOpenRouter(
            model="google/gemini-2.5-flash-preview-05-20",
            temperature=0
        )

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
            "endpoint": f"http://localhost:8000/agents/{self.agent_id}" # Provide a valid placeholder endpoint
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

    async def post_event_to_mcp(self, event_type: str, event_data: dict, task_id: Optional[str] = None):
        """
        Post an event to the MCP server.
        """
        event_url = f"{self.mcp_server_url}/api/v1/post_event"
        payload = {"event_type": event_type, "event_data": event_data, "source_agent_id": self.agent_id}
        if task_id:
            payload["task_id"] = task_id
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

    async def _resolve_prompt_and_invoke_llm(self, prompt_name: str, variables: Dict[str, Any]) -> Dict[str, Any]:
        """
        Resolves a prompt template using the MCP's PromptRegistry and invokes the LLM.
        The LLM is expected to return a JSON string with 'action' and 'parameters'.
        """
        prompt_resolution_url = f"{self.mcp_server_url}/api/v1/resolve_prompt"
        
        try:
            # Request prompt resolution from MCP
            prompt_request = PromptResolutionRequest(
                prompt_key=prompt_name,
                variables=variables
            )
            response = await self.http_client.post(prompt_resolution_url, json=prompt_request.model_dump())
            response.raise_for_status()
            resolved_prompt_response = PromptResolutionResponse(**response.json())
            
            full_prompt = resolved_prompt_response.resolved_prompt
            print(f"Agent {self.agent_id}: Resolved prompt for {prompt_name}: {full_prompt}")
            
            # Invoke the real LLM
            messages = [
                SystemMessage(content="You are a helpful AI assistant. Respond with a JSON object containing 'action' and 'parameters' keys."),
                HumanMessage(content=full_prompt),
            ]
            llm_response_content = self.llm.invoke(messages).content
            print(f"Agent {self.agent_id}: LLM raw response: {llm_response_content}")

            # Strip markdown code block if present
            if llm_response_content.startswith("```json") and llm_response_content.endswith("```"):
                llm_response_content = llm_response_content[7:-3].strip()
                print(f"Agent {self.agent_id}: LLM stripped response: {llm_response_content}")

            # Attempt to parse the LLM's response as JSON
            try:
                llm_output = json.loads(llm_response_content)
                if "action" not in llm_output or "parameters" not in llm_output:
                    raise ValueError("LLM response missing 'action' or 'parameters' keys.")
                llm_output["resolved_prompt"] = full_prompt # Add resolved prompt to output
                return llm_output
            except json.JSONDecodeError:
                print(f"Agent {self.agent_id}: LLM response is not valid JSON. Raw: {llm_response_content}")
                return {"error": "LLM response is not valid JSON.", "raw_response": llm_response_content, "resolved_prompt": full_prompt}
            except ValueError as ve:
                print(f"Agent {self.agent_id}: LLM response JSON is malformed: {ve}. Raw: {llm_response_content}")
                return {"error": f"LLM response JSON is malformed: {ve}", "raw_response": llm_response_content, "resolved_prompt": full_prompt}

        except httpx.HTTPStatusError as e:
            print(f"Error resolving prompt from MCP for {prompt_name}: {e.response.status_code} - {e.response.text}")
            return {"error": f"Failed to resolve prompt: {e.response.text}"}
        except httpx.RequestError as e:
            print(f"Request error while resolving prompt from MCP for {prompt_name}: {e}")
            return {"error": f"Request error: {e}"}
        except Exception as e:
            print(f"Unexpected error in _resolve_prompt_and_invoke_llm: {e}")
            return {"error": f"Unexpected error: {e}"}

    async def send_request_to_mcp(self, endpoint: str, request_payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sends a generic request to a specified MCP endpoint.
        """
        full_url = f"{self.mcp_server_url}/{endpoint.lstrip('/')}"
        try:
            response = await self.http_client.post(full_url, json=request_payload)
            response.raise_for_status()
            print(f"Agent {self.agent_id}: Successfully sent request to {endpoint}.")
            return response.json()
        except httpx.HTTPStatusError as e:
            print(f"Error sending request to MCP endpoint {endpoint}: {e.response.status_code} - {e.response.text}")
            return {"error": f"Failed to send request: {e.response.text}"}
        except httpx.RequestError as e:
            print(f"Request error while sending request to MCP endpoint {endpoint}: {e}")
            return {"error": f"Request error: {e}"}
        except Exception as e:
            print(f"Unexpected error in send_request_to_mcp to {endpoint}: {e}")
            return {"error": f"Unexpected error: {e}"}
