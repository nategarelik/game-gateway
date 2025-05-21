# Task: Implement MCP PromptRegistry

**Task ID:** ROO#SUB_20250520-020934_S004
**Parent Plan Task ID:** ROO#PLAN_MCP_SETUP_20250520-020934
**Depends on:** ROO#SUB_20250520-020934_S001 (Initialize MCP Server Project Structure & Dependencies)
**Overall Project Plan:** `../../plans/ROO#20250517-041757-PLAN_final_summary.md`
**MCP Server Core Structure Document:** `../../ROO#SUB_PLAN_S001/mcp_server_core_structure.md` (relative path, actual: `.rooroo/tasks/ROO#SUB_PLAN_S001/mcp_server_core_structure.md`)
**MCP Prompt Orchestration System Document:** `../../ROO#SUB_PLAN_S003/mcp_prompt_orchestration_system.md` (relative path, actual: `.rooroo/tasks/ROO#SUB_PLAN_S003/mcp_prompt_orchestration_system.md`)

**Goal for rooroo-developer:**
Implement the `PromptRegistry` class within the MCP server's core components. This registry will be responsible for storing, managing, and resolving prompts used by various agents.

**Key Implementation Steps:**
1.  **Define `PromptRegistry` Class:**
    *   Create the `PromptRegistry` class in `src/mcp_server/core/prompt_registry.py`.
    *   It should have methods for:
        *   `register_prompt(prompt_name: str, template: str, required_variables: List[str], agent_type: Optional[str] = None)`: Stores a prompt template and its metadata.
        *   `get_prompt_template(prompt_name: str) -> Optional[str]`: Retrieves a raw prompt template.
        *   `resolve_prompt(prompt_name: str, variables: Dict[str, Any]) -> Optional[str]`: Takes a prompt name and a dictionary of variables, then formats the prompt template with these variables. It should validate that all required variables are provided.
        *   `list_prompts(agent_type: Optional[str] = None) -> List[str]`: Lists available prompt names, optionally filtered by agent type.
2.  **Prompt Storage:**
    *   For this initial implementation, prompts can be stored in an in-memory dictionary within the `PromptRegistry` instance (e.g., `self.prompts = {}`).
    *   Each entry could store the template, required variables, and agent type.
3.  **Variable Substitution:**
    *   Implement a basic variable substitution mechanism in `resolve_prompt`. Python's `str.format()` or f-strings can be used if templates are designed accordingly. Consider more robust templating engines (like Jinja2) for future enhancements if complex logic is needed, but start simple.
4.  **Error Handling:**
    *   `resolve_prompt` should raise an error (e.g., `ValueError` or a custom exception) if a required variable is missing or if the prompt name is not found.
    *   `get_prompt_template` should return `None` or raise an error if the prompt is not found.
5.  **Integration with Server Core (Conceptual):**
    *   The `PromptRegistry` will eventually be instantiated and used by the main `MCPServer` instance in `src/mcp_server/core/server.py`. For this task, ensure the class is defined correctly. Actual instantiation and usage by the server can be a light touch or placeholder.
6.  **Unit Tests:**
    *   Create `tests/mcp_server/test_prompt_registry.py`.
    *   Add tests for:
        *   Registering a new prompt.
        *   Retrieving a prompt template.
        *   Successfully resolving a prompt with correct variables.
        *   Failing to resolve a prompt due to missing variables.
        *   Failing to resolve a non-existent prompt.
        *   Listing prompts.

**Key Considerations:**
*   Refer to the "PromptRegistry for dynamic prompt handling" section in `mcp_server_core_structure.md` and the more detailed "MCP Prompt Orchestration System" document.
*   The focus is on the core mechanics of storing, retrieving, and resolving prompts. Advanced features like versioning or loading from external files are for later.

**Output Artifacts:**
*   New/modified `src/mcp_server/core/prompt_registry.py`.
*   New `tests/mcp_server/test_prompt_registry.py`.
*   A brief report in `.rooroo/tasks/ROO#SUB_20250520-020934_S004/artifacts/prompt_registry_implementation_report.md`.