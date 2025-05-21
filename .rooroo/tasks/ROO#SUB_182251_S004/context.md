# Sub-Task: Relocate Toolchain Bridge Files and Update Imports

**Parent Task ID:** ROO#NAV_PROJECT_SETUP_PLAN_20250519-182251
**Sub-Task ID:** ROO#SUB_182251_S004
**Depends On:** ROO#SUB_182251_S001

**Goal:**
Relocate the existing toolchain bridge Python files to the `src/toolchains/` directory. Update their internal import statements and any imports from other project components. Optionally, create a `base_toolchain_bridge.py`.

**Files to Move:**
1.  **Muse Toolchain Bridge:**
    *   **Original Path:** [`.rooroo/tasks/ROO#SUB_PLAN_20250518-170411_S005/muse_integration.py`](.rooroo/tasks/ROO#SUB_PLAN_20250518-170411_S005/muse_integration.py)
    *   **New Path:** [`src/toolchains/muse_bridge.py`](src/toolchains/muse_bridge.py)
2.  **Retro Diffusion Toolchain Bridge:**
    *   **Original Path:** [`.rooroo/tasks/ROO#SUB_PLAN_20250518-170411_S005/retro_diffusion_integration.py`](.rooroo/tasks/ROO#SUB_PLAN_20250518-170411_S005/retro_diffusion_integration.py)
    *   **New Path:** [`src/toolchains/retro_diffusion_bridge.py`](src/toolchains/retro_diffusion_bridge.py)

**Instructions:**
1.  Ensure the target directory [`src/toolchains/`](src/toolchains/) exists (created in ROO#SUB_182251_S001).
2.  Move the specified toolchain bridge files to their new locations (consider renaming for clarity, e.g., `muse_bridge.py`).
3.  Review and update import statements within each bridge file:
    *   For imports of other bridges (if any): `from . import another_bridge`
    *   For imports from agents or MCP (if needed, though less likely for bridges): `from ..agents import some_agent`
4.  Consider if a `src/toolchains/base_toolchain_bridge.py` would be beneficial for shared bridge logic. If so, create it and refactor common elements.

**Reference Parent Context:**
For overall project goals and existing file locations, see [`.rooroo/tasks/ROO#NAV_PROJECT_SETUP_PLAN_20250519-182251/context.md`](.rooroo/tasks/ROO#NAV_PROJECT_SETUP_PLAN_20250519-182251/context.md).