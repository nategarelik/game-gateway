# Code Review Planning Request

**User Request:** "Please review all code we have. Make sure it's up to date, efficient, not redundant, and properly commented and ready for full deployment. Use context7, and tools from the github mcp if needed."

**Current Project Files (from last `list_files`):**
*   Autonomous_AI_Agent_Ecosystem_Documentation.md
*   PROMPT.md
*   README.md
*   requirements.txt
*   docs/
    *   docs/mcp_server.md
    *   docs/agents/documentation_sentinel.md
    *   docs/agents/level_architect.md
    *   docs/agents/pixel_forge.md
    *   docs/toolchains/muse.md
    *   docs/toolchains/retro_diffusion.md
*   src/
    *   src/agents/base_agent.py
    *   src/agents/documentation_sentinel.py
    *   src/agents/level_architect_agent.py
    *   src/agents/pixel_forge_agent.py
    *   src/mcp_server/client.py
    *   src/mcp_server/server_core.py
    *   src/toolchains/__init__.py
    *   src/toolchains/base_toolchain_bridge.py
    *   src/toolchains/muse_bridge.py
    *   src/toolchains/retro_diffusion_bridge.py
*   tests/
    *   tests/test_mcp_server.py
    *   tests/agents/test_documentation_sentinel.py

**Objective for Planner:**
Create a detailed plan to review the entire Python codebase (`src/` and `tests/`). The plan should consist of sub-tasks, likely one per Python file. Each sub-task should be delegated to `rooroo-developer` with clear instructions to:
1.  Read the specified file.
2.  Review it for:
    *   Up-to-dateness (e.g., Python 3 features, modern practices, library versions if applicable).
    *   Efficiency (algorithmic, resource usage if inferable).
    *   Redundancy (within the file and potentially across the project if obvious).
    *   Proper commenting (docstrings for all public modules, classes, functions/methods; inline comments for complex logic).
    *   Readiness for deployment (robust error handling, comprehensive logging, clear configuration points, overall clarity and maintainability).
3.  The `rooroo-developer` should identify areas for improvement and can suggest changes or apply them if they are straightforward and low-risk. Complex changes should be noted for a separate implementation task.
4.  If external libraries are used within a file, `rooroo-developer` should list them. The planner can then decide if a separate task using `context7` (via `rooroo-developer` or `rooroo-navigator`) is needed to check for updates or best practices for those libraries.
5.  If specific code patterns, algorithms, or complex logic sections could benefit from comparison with established best practices or examples, `rooroo-developer` should note this. The planner can then decide if a task using the GitHub MCP (via `rooroo-developer` or `rooroo-navigator`) is warranted.

The final output from the planner should be a JSON array of task objects suitable for being added to the Navigator's `.rooroo/queue.jsonl` file.