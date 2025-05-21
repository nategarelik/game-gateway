# Task: Implement Unit Tests for LevelArchitectAgent

**Task ID:** ROO#SUB_20250520-024601_S005
**Parent Plan Task ID:** ROO#PLAN_LEVEL_ARCHITECT_20250520-024601
**Depends on:**
*   ROO#SUB_20250520-024601_S001 (LevelArchitectAgent Class Structure)
*   ROO#SUB_20250520-024601_S002 (LevelArchitectAgent Core Logic)
*   ROO#SUB_20250520-024601_S003 (LevelArchitectAgent MCP Integration)
*   ROO#SUB_20250520-024601_S004 (LevelArchitectAgent Prompts & Behavior)
**Overall Project Plan:** `.rooroo/plans/ROO#20250517-041757-PLAN_final_summary.md`
**Agent File:** [`src/agents/level_architect_agent.py`](src/agents/level_architect_agent.py:0)
**Base Agent File:** [`src/agents/base_agent.py`](src/agents/base_agent.py:0)
**Test Directory:** `tests/agents/`

**Goal for rooroo-developer:**
Implement comprehensive unit tests for the `LevelArchitectAgent`. These tests should cover its core logic, prompt handling, and interaction points with a mocked MCP server.

**Key Implementation Steps:**
1.  **Create Test File:**
    *   Create the directory `tests/agents/` if it doesn't exist.
    *   Create the test file [`tests/agents/test_level_architect_agent.py`](tests/agents/test_level_architect_agent.py:0).
    *   Add necessary imports, including `pytest`, `unittest.mock` (for `AsyncMock`, `MagicMock`, `patch`), and the `LevelArchitectAgent` and `BaseAgent` classes.
2.  **Set up Test Fixtures (using `pytest.fixture`):**
    *   **`mock_mcp_server_url`**: A fixture that returns a dummy URL string (e.g., "http://mock-mcp-server:8000").
    *   **`level_architect_agent_instance`**: A fixture that creates an instance of `LevelArchitectAgent`, using the `mock_mcp_server_url`.
        ```python
        import pytest
        from unittest.mock import AsyncMock, MagicMock, patch
        from src.agents.level_architect_agent import LevelArchitectAgent
        from src.agents.base_agent import BaseAgent # If BaseAgent methods are directly tested or need mocking structure

        @pytest.fixture
        def mock_mcp_server_url():
            return "http://mock-mcp-server:8000"

        @pytest.fixture
        def level_architect_agent_instance(mock_mcp_server_url):
            agent = LevelArchitectAgent(agent_id="test_level_architect_01", mcp_server_url=mock_mcp_server_url)
            # Mock the HTTP client within the agent to prevent real network calls
            agent.http_client = AsyncMock(spec=httpx.AsyncClient) 
            # Configure common mock return values for http_client methods if needed globally for tests
            # Example: agent.http_client.post.return_value = AsyncMock(status_code=200, json=lambda: {"status": "ok"})
            return agent
        ```
3.  **Test `__init__`:**
    *   Verify that the agent is initialized with correct default capabilities and any passed configurations.
4.  **Test `process_task` Method:**
    *   Test with various `task_details` inputs.
    *   Mock helper methods like `_interpret_design_prompt`, `_generate_initial_level_structure` to control their outputs and focus testing on `process_task`'s orchestration.
    *   Verify that `post_event_to_mcp` is called with expected event types and data at different stages. Use `agent.http_client.post.assert_any_call(...)` or similar, ensuring the mock `http_client` is properly set up on the agent instance.
    *   Verify the structure and content of the returned dictionary from `process_task`.
    *   Test error handling within `process_task` (e.g., if a helper method raises an exception).
5.  **Test Helper Methods (e.g., `_interpret_design_prompt`, `_generate_initial_level_structure`):**
    *   Test these methods in isolation.
    *   Provide various inputs and assert their outputs.
    *   Since these currently have placeholder logic, tests will be simple but should establish the testing structure.
6.  **Test Prompt Handling Logic (from S004):**
    *   Verify correct prompt template selection based on (mocked) task type.
    *   Test successful formatting of prompts.
    *   Test error handling for missing variables.
    *   Verify that the (mocked) output of prompt processing is used correctly.
7.  **Test `register_with_mcp` and `post_event_to_mcp` (from `BaseAgent`, as used by `LevelArchitectAgent`):**
    *   For `register_with_mcp`:
        *   Ensure `agent.http_client.post` is called with the correct URL and payload.
        *   Test successful registration (mock `agent.http_client.post` to return a successful response).
        *   Test HTTP error during registration (mock `agent.http_client.post` to raise `httpx.HTTPStatusError`).
        *   Test request error (mock `agent.http_client.post` to raise `httpx.RequestError`).
    *   For `post_event_to_mcp`:
        *   Ensure `agent.http_client.post` is called with the correct URL and payload for various events.
        *   Test successful event posting.
        *   Test HTTP and request errors during event posting.
8.  **Ensure Asynchronous Tests are Handled Correctly:**
    *   Use `pytest.mark.asyncio` for all async test functions.
    *   Use `await` when calling async methods of the agent.
    *   Ensure `pytest-asyncio` is installed (should be from MCP server setup).

**Key Considerations:**
*   **Mocking:** Extensively use `unittest.mock.AsyncMock` for asynchronous methods and `unittest.mock.MagicMock` or `unittest.mock.patch` for synchronous parts and external dependencies (like `httpx.AsyncClient`).
*   **Isolation:** Test methods in isolation as much as possible.
*   **Coverage:** Aim for good coverage of the agent's logic, especially decision points and interactions.
*   The MCP server itself is mocked; these are unit tests for the agent.

**Output Artifacts:**
*   New [`tests/agents/test_level_architect_agent.py`](tests/agents/test_level_architect_agent.py:0) file with comprehensive unit tests.
*   A brief report in `.rooroo/tasks/ROO#SUB_20250520-024601_S005/artifacts/level_architect_tests_report.md`.