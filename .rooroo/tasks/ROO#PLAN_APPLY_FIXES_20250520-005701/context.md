# Plan Request: Apply Straightforward Code Review Fixes

**Task ID:** ROO#PLAN_APPLY_FIXES_20250520-005701
**Parent Task ID (Summarization):** ROO#SUMMARIZE_REVIEWS_20250520-002939

**Goal for rooroo-planner:**
Based on the consolidated code review summary report located at `.rooroo/tasks/ROO#SUMMARIZE_REVIEWS_20250520-002939/artifacts/code_review_summary_report.md`, create a plan to apply only the straightforward, low-risk changes suggested.

1.  **Read the Summary Report:** The planner needs to parse the summary report to identify actionable, low-risk suggestions. These typically include:
    *   Adding missing docstrings or comments.
    *   Minor refactoring for clarity or efficiency that doesn't alter core logic significantly.
    *   Fixing typos.
    *   Addressing minor linting issues or style inconsistencies.
    *   Removing unused imports or variables.

2.  **Filter for Low-Risk Changes:** Exclude suggestions that involve:
    *   Significant refactoring of core logic.
    *   Changes to public APIs.
    *   Updates to external library versions (unless explicitly stated as trivial and safe).
    *   Complex algorithmic changes.
    *   Anything marked as requiring "deeper research" or "further discussion" in the reports.

3.  **Create Sub-Tasks for `rooroo-developer`:** For each file or group of related low-risk changes, create a sub-task for `rooroo-developer`. Each sub-task should:
    *   Clearly state the file(s) to be modified.
    *   List the specific low-risk changes to be applied, referencing the summary report or original sub-task reports if necessary for detail.
    *   Instruct the developer to apply the changes using appropriate tools (`apply_diff`, `insert_content`, etc.).
    *   Emphasize caution and to only apply the specified low-risk changes.

**Input Artifact:**
*   Consolidated Code Review Summary Report: `.rooroo/tasks/ROO#SUMMARIZE_REVIEWS_20250520-002939/artifacts/code_review_summary_report.md`

**Output from Planner:**
*   A JSON array of task objects suitable for being added to the Navigator's `.rooroo/queue.jsonl` file.
*   An overview plan document saved to `.rooroo/plans/ROO#PLAN_APPLY_FIXES_20250520-005701_plan_overview.md`.

**Guidance:**
*   The planner should be conservative in what it deems "low-risk." If there's doubt, the change should be deferred for manual review or a more detailed implementation task.
*   The goal is to quickly improve code quality with minimal risk.