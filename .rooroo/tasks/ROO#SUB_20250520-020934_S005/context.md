# Task: MCP Server Initial Integration Testing & Documentation Update

**Task ID:** ROO#SUB_20250520-020934_S005
**Parent Plan Task ID:** ROO#PLAN_MCP_SETUP_20250520-020934
**Depends on:** ROO#SUB_20250520-020934_S001, ROO#SUB_20250520-020934_S002, ROO#SUB_20250520-020934_S003, ROO#SUB_20250520-020934_S004
**Overall Project Plan:** `../../plans/ROO#20250517-041757-PLAN_final_summary.md`
**MCP Server Core Structure Document:** `../../ROO#SUB_PLAN_S001/mcp_server_core_structure.md` (relative path, actual: `.rooroo/tasks/ROO#SUB_PLAN_S001/mcp_server_core_structure.md`)

**Goal for rooroo-developer:**
Perform initial integration testing of the MCP server's core components (API endpoints, StateManager, PromptRegistry) and update/create basic documentation for these components.

**Key Implementation Steps:**
1.  **Integrate Core Components:**
    *   In `src/mcp_server/main.py` (or `src/mcp_server/core/server.py` if a dedicated server class exists):
        *   Ensure instances of `StateManager` and `PromptRegistry` are created and made available to the API route handlers. This might involve passing them as dependencies or making them accessible via the FastAPI app state.
        *   Update the placeholder API endpoint implementations from ROO#SUB_20250520-020934_S002 to make actual calls to the `StateManager` and `PromptRegistry` where appropriate. For example:
            *   `/register_agent`: Store agent details (can be in-memory in the server instance for now).
            *   `/discover_agents`: Retrieve from the in-memory store.
            *   `/request_action`: Trigger the `StateManager` to start a new LangGraph workflow.
            *   (Potentially add a new endpoint to register prompts in the `PromptRegistry` via API, or pre-populate some test prompts).
2.  **Write Basic Integration Tests:**
    *   In `tests/mcp_server/`, create or expand `test_integration_mcp_server.py`.
    *   These tests should verify basic end-to-end flows:
        *   Test registering an agent and then discovering it.
        *   Test posting a `/request_action` and verifying (e.g., by checking logs or a conceptual task status endpoint if simple enough to add) that the `StateManager` was invoked.
        *   Test registering a prompt and then resolving it successfully using variables provided via an API call (if a prompt registration endpoint was added).
    *   Use `httpx.AsyncClient` for testing the FastAPI application.
3.  **Run All MCP Server Tests:**
    *   Execute `python -m pytest tests/mcp_server/` to ensure all unit and integration tests for the MCP server pass.
4.  **Update/Create Basic Documentation:**
    *   For each core component (`StateManager`, `PromptRegistry`, main API routes):
        *   Ensure class and public method docstrings are present and informative in the source code.
        *   Create or update simple Markdown files in a new `docs/mcp_server/` directory (e.g., `docs/mcp_server/api.md`, `docs/mcp_server/state_management.md`, `docs/mcp_server/prompt_registry.md`).
        *   These documents should briefly describe the purpose, key functionalities, and basic usage of each component/API.
        *   This is initial documentation; more comprehensive docs will be developed later.

**Key Considerations:**
*   The goal is to ensure the core pieces can "talk" to each other, not to implement full business logic.
*   Keep tests focused on basic successful interactions.
*   Documentation should be clear and provide a starting point for understanding the server's core.

**Output Artifacts:**
*   Modified `src/mcp_server/main.py`, `src/mcp_server/api/routes.py`, `src/mcp_server/core/server.py` (as applicable).
*   New/modified `tests/mcp_server/test_integration_mcp_server.py`.
*   New Markdown documentation files in `docs/mcp_server/`.
*   Updated docstrings in relevant source files.
*   A brief report in `.rooroo/tasks/ROO#SUB_20250520-020934_S005/artifacts/integration_testing_and_docs_report.md`.