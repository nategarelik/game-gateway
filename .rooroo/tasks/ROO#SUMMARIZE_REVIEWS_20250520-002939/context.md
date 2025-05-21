# Code Review Summarization Request

**Task ID:** ROO#SUMMARIZE_REVIEWS_20250520-002939
**Parent Task ID (Code Review Plan):** ROO#PLAN_CODE_REVIEW_20250519-200706

**Goal for rooroo-documenter:**
Read all individual code review reports listed below and produce a single, consolidated summary report. The summary should highlight:
1.  Common themes or recurring issues found across multiple files.
2.  Key findings and critical suggestions for each reviewed file (briefly).
3.  A list of all external libraries identified across all reports.
4.  A list of all areas noted for deeper research across all reports.
5.  Overall assessment of code quality, readiness for deployment, and main areas needing attention.

**Input Report Files (12 total):**
*   `.rooroo/tasks/ROO#SUB_PLAN_CODE_REVIEW_S001/artifacts/ROO#SUB_PLAN_CODE_REVIEW_S001_report.md` (for `src/agents/base_agent.py`)
*   `.rooroo/tasks/ROO#SUB_PLAN_CODE_REVIEW_S002/artifacts/ROO#SUB_PLAN_CODE_REVIEW_S002_report.md` (for `src/agents/documentation_sentinel.py`)
*   `.rooroo/tasks/ROO#SUB_PLAN_CODE_REVIEW_S003/artifacts/ROO#SUB_PLAN_CODE_REVIEW_S003_report.md` (for `src/agents/level_architect_agent.py`)
*   `.rooroo/tasks/ROO#SUB_PLAN_CODE_REVIEW_S004/artifacts/ROO#SUB_PLAN_CODE_REVIEW_S004_report.md` (for `src/agents/pixel_forge_agent.py`)
*   `.rooroo/tasks/ROO#SUB_PLAN_CODE_REVIEW_S005/artifacts/ROO#SUB_PLAN_CODE_REVIEW_S005_report.md` (for `src/mcp_server/client.py`)
*   `.rooroo/tasks/ROO#SUB_PLAN_CODE_REVIEW_S006/artifacts/ROO#SUB_PLAN_CODE_REVIEW_S006_report.md` (for `src/mcp_server/server_core.py`)
*   `.rooroo/tasks/ROO#SUB_PLAN_CODE_REVIEW_S007/artifacts/ROO#SUB_PLAN_CODE_REVIEW_S007_report.md` (for `src/toolchains/__init__.py`)
*   `.rooroo/tasks/ROO#SUB_PLAN_CODE_REVIEW_S008/artifacts/ROO#SUB_PLAN_CODE_REVIEW_S008_report.md` (for `src/toolchains/base_toolchain_bridge.py`)
*   `.rooroo/tasks/ROO#SUB_PLAN_CODE_REVIEW_S009/artifacts/ROO#SUB_PLAN_CODE_REVIEW_S009_report.md` (for `src/toolchains/muse_bridge.py`)
*   `.rooroo/tasks/ROO#SUB_PLAN_CODE_REVIEW_S010/artifacts/ROO#SUB_PLAN_CODE_REVIEW_S010_report.md` (for `src/toolchains/retro_diffusion_bridge.py`)
*   `.rooroo/tasks/ROO#SUB_PLAN_CODE_REVIEW_S011/artifacts/ROO#SUB_PLAN_CODE_REVIEW_S011_report.md` (for `tests/test_mcp_server.py`)
*   `.rooroo/tasks/ROO#SUB_PLAN_CODE_REVIEW_S012/artifacts/ROO#SUB_PLAN_CODE_REVIEW_S012_report.md` (for `tests/agents/test_documentation_sentinel.py`)

**Output Artifact:**
*   The consolidated summary report should be saved to: `.rooroo/tasks/ROO#SUMMARIZE_REVIEWS_20250520-002939/artifacts/code_review_summary_report.md`

**Guidance:**
*   Ensure the summary is well-organized and easy to read.
*   Focus on actionable insights.