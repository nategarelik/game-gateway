# Task: Define LevelArchitectAgent Class Structure

**Task ID:** ROO#SUB_20250520-024601_S001
**Parent Plan Task ID:** ROO#PLAN_LEVEL_ARCHITECT_20250520-024601
**Overall Project Plan:** `.rooroo/plans/ROO#20250517-041757-PLAN_final_summary.md`
**Relevant Design Document:** `docs/agents/level_architect.md` (if it exists, otherwise refer to overall plan and specialized agent roles document: `.rooroo/tasks/ROO#SUB_PLAN_S002/specialized_agent_roles_and_prompt_systems.md`)
**Base Agent Path:** `src/agents/base_agent.py`

**Goal for rooroo-developer:**
Define the Python class structure for the `LevelArchitectAgent`.
1.  Create the directory `src/agents/` if it doesn't exist.
2.  Create the file [`src/agents/base_agent.py`](src/agents/base_agent.py:0) if it doesn't exist. It should contain a basic `BaseAgent` class:
    ```python
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
    ```
3.  Create the file [`src/agents/level_architect_agent.py`](src/agents/level_architect_agent.py:0) if it doesn't exist.
4.  In [`src/agents/level_architect_agent.py`](src/agents/level_architect_agent.py:0), define the `LevelArchitectAgent` class, ensuring it inherits from `BaseAgent` (from `src.agents.base_agent`).
5.  Implement the `__init__` method for `LevelArchitectAgent`. It should call `super().__init__` and can accept additional specific configurations.
    ```python
    # src/agents/level_architect_agent.py
    from .base_agent import BaseAgent

    class LevelArchitectAgent(BaseAgent):
        def __init__(self, agent_id: str, mcp_server_url: str, level_design_tool_config: dict = None):
            super().__init__(agent_id, mcp_server_url, capabilities=["level_design", "procedural_generation_guidance"])
            self.level_design_tool_config = level_design_tool_config if level_design_tool_config is not None else {}
            # Initialize specific tools or settings for level architecture

        async def process_task(self, task_details: dict) -> dict:
            print(f"LevelArchitectAgent ({self.agent_id}) processing task: {task_details}")
            # TODO: Implement level design logic based on task_details
            # Example: interpret prompt, generate layout, refine design
            # For now, return a placeholder success
            await self.post_event_to_mcp("level_design_progress", {"task_id": task_details.get("task_id"), "status": "started"})
            
            # Simulate work
            level_data = {"layout": "complex_dungeon_layout_v1", "theme": task_details.get("theme", "generic_fantasy")}
            
            await self.post_event_to_mcp("level_design_complete", {"task_id": task_details.get("task_id"), "status": "completed", "level_data": level_data})
            return {"status": "success", "message": "Level design task processed.", "output": level_data}

        # Placeholder methods specific to Level Architect
        async def generate_level_layout(self, requirements: dict) -> dict:
            print(f"Generating level layout with requirements: {requirements}")
            # Placeholder
            return {"layout_id": "layout_123", "status": "generated"}

        async def refine_level_design(self, layout_id: str, feedback: dict) -> dict:
            print(f"Refining level design for {layout_id} with feedback: {feedback}")
            # Placeholder
            return {"layout_id": layout_id, "status": "refined"}
    ```
6.  Create `src/agents/__init__.py` if it doesn't exist, and ensure it makes `BaseAgent` and `LevelArchitectAgent` importable:
    ```python
    # src/agents/__init__.py
    from .base_agent import BaseAgent
    from .level_architect_agent import LevelArchitectAgent

    __all__ = [
        "BaseAgent",
        "LevelArchitectAgent",
    ]
    ```
**Key Considerations:**
*   Refer to [`docs/agents/level_architect.md`](docs/agents/level_architect.md:0) (if available) and the "Specialized Agent Roles & Prompt Systems" section of the main project plan ([`.rooroo/plans/ROO#20250517-041757-PLAN_final_summary.md`](.rooroo/plans/ROO#20250517-041757-PLAN_final_summary.md:0)) for design specifications.
*   The focus is on establishing the foundational class structure and configuration.

**Output Artifacts:**
*   New/modified [`src/agents/base_agent.py`](src/agents/base_agent.py:0).
*   New/modified [`src/agents/level_architect_agent.py`](src/agents/level_architect_agent.py:0).
*   New/modified [`src/agents/__init__.py`](src/agents/__init__.py:0).
*   A brief report in `.rooroo/tasks/ROO#SUB_20250520-024601_S001/artifacts/level_architect_structure_report.md`.