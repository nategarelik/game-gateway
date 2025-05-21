# Sub-Task: Develop Basic Tests for MCP Server

**Parent Task ID:** ROO#NAV_PROJECT_SETUP_PLAN_20250519-182251
**Sub-Task ID:** ROO#SUB_182251_S017
**Depends On:** ROO#SUB_182251_S002 (ensures MCP server files are at [`src/mcp_server/`](src/mcp_server/))

**Goal:**
Develop basic test scripts (e.g., using `pytest` and `httpx`) or outline manual test procedures for the MCP server's API endpoints. The primary focus should be on testing the `/execute_agent` endpoint. Test scripts can be placed in a new file like [`tests/test_mcp_server.py`](tests/test_mcp_server.py).

**Key Files to Test (Indirectly via API):**
*   Server Core: [`src/mcp_server/server_core.py`](src/mcp_server/server_core.py)

**Target Test File (Example):**
*   [`tests/test_mcp_server.py`](tests/test_mcp_server.py) (Developer to create)

**Instructions:**
1.  **Setup Test Environment:**
    *   Ensure `pytest` and `httpx` (for asynchronous HTTP requests to FastAPI) are added to `requirements.txt` if not already present.
2.  **Test `/execute_agent` Endpoint:**
    *   Write test cases that send requests to the `/execute_agent` endpoint.
    *   **Mocking Agents:** Since full agent implementations might still be in progress or complex, the tests should ideally mock the agent's `handle_direct_request` method or the response from the agent call within the MCP server if that's easier. The goal is to test the MCP's routing and request/response handling for this endpoint.
    *   Test with valid and invalid agent IDs.
    *   Test with example `request_data` payloads.
    *   Verify response status codes and basic response structure.
3.  **Other Endpoints (Optional):**
    *   If there are simple status or health check endpoints, add basic tests for them.
4.  **Manual Test Procedures (Alternative/Complementary):**
    *   If full automated tests are too complex initially, outline manual test steps using a tool like `curl` or Postman:
        *   How to start the MCP server.
        *   Example `curl` commands to hit `/execute_agent` with different payloads.
        *   Expected responses.
5.  **Documentation:**
    *   Briefly document how to run the tests in the main project `README.md` (or this task can note that ROO#SUB_182251_S010 should be updated later).

**Reference Parent Context:**
For MCP server design, see [`.rooroo/tasks/ROO#NAV_PROJECT_SETUP_PLAN_20250519-182251/context.md`](.rooroo/tasks/ROO#NAV_PROJECT_SETUP_PLAN_20250519-182251/context.md).