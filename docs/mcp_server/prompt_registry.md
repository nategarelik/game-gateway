# MCP Server Prompt Registry

The MCP Server includes a `PromptRegistry` to manage and resolve prompt templates, facilitating consistent and reusable prompts across different agents and tasks.

## Core Component: `PromptRegistry`

-   **Location:** `src.mcp_server.core.prompt_registry.PromptRegistry`
-   **Purpose:**
    -   To store named prompt templates along with their metadata (e.g., required variables, description).
    -   To provide a mechanism for resolving these templates by substituting variables at runtime.
    -   To allow listing of available prompts, potentially filtered by criteria like agent type.

## Key Functionalities

1.  **Prompt Registration (`register_prompt_template` or `register_prompt`):**
    -   Allows new prompt templates to be added to the registry.
    -   Each prompt is stored with:
        -   A unique key or name (e.g., `greet_user`, `summarize_text`).
        -   The template string itself (e.g., "Hello, {name}! Your task is {task_details}.").
        -   A list of required variable names that must be supplied when resolving the prompt.
        -   An optional description or agent type for categorization.
    -   The API endpoint `/register_prompt` uses fields like `prompt_key`, `template_string`, `required_vars`, and `description`. The internal `PromptRegistry` class might use slightly different parameter names (e.g. `prompt_name`, `template`) but serves the same function.

2.  **Prompt Retrieval (`get_prompt_template`):**
    -   Allows fetching the raw template string for a given prompt name.
    -   Useful for inspection or if an agent wants to handle substitution logic differently.

3.  **Prompt Resolution (`resolve_prompt`):**
    -   The primary method for using a registered prompt.
    -   Takes the prompt name/key and a dictionary of variables.
    -   Validates that all required variables for the prompt are present in the provided dictionary.
    -   Substitutes the variables into the template string (typically using Python's `str.format()` method).
    -   Returns the fully resolved prompt string.
    -   Raises errors if the prompt is not found or if required variables are missing.
    -   The API endpoint `/resolve_prompt` facilitates this.

4.  **Listing Prompts (`list_prompts`):**
    -   Provides a way to discover available prompts in the registry.
    -   Can optionally filter prompts by `agent_type` or other metadata if implemented.

## Usage Example (Conceptual)

1.  **Registration (e.g., at server startup or via API):**
    ```python
    # Via API POST /register_prompt
    # {
    #     "prompt_key": "generate_character_bio",
    #     "template_string": "Create a biography for a character named {character_name} who is a {character_role} in a {setting_type} world.",
    #     "required_vars": ["character_name", "character_role", "setting_type"],
    #     "description": "Generates a character biography."
    # }
    ```

2.  **Resolution (e.g., by an agent preparing to call an LLM):**
    ```python
    # Via API POST /resolve_prompt
    # {
    #     "prompt_key": "generate_character_bio",
    #     "variables": {
    #         "character_name": "Elara",
    #         "character_role": "mage",
    #         "setting_type": "fantasy"
    #     }
    # }
    # Expected Response:
    # {
    #     "prompt_key": "generate_character_bio",
    #     "resolved_prompt": "Create a biography for a character named Elara who is a mage in a fantasy world."
    # }
    ```

## Benefits

-   **Consistency:** Ensures prompts are phrased uniformly.
-   **Reusability:** Avoids duplicating prompt text across the system.
-   **Maintainability:** Prompts can be updated in one central place.
-   **Clarity:** Explicitly defines required inputs for each prompt.

This component is crucial for standardizing interactions with language models within the MCP ecosystem.