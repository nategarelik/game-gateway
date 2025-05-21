from typing import List, Dict, Any, Optional

class PromptRegistry:
    """
    Manages storing, retrieving, and resolving prompt templates.
    """
    def __init__(self):
        """
        Initializes the PromptRegistry with an empty prompt store.
        """
        self.prompts: Dict[str, Dict[str, Any]] = {}

    def register_prompt(
        self,
        prompt_name: str,
        template: str,
        required_variables: List[str],
        agent_type: Optional[str] = None
    ):
        """
        Registers a new prompt template and its metadata.

        Args:
            prompt_name: The unique name for the prompt.
            template: The prompt template string (e.g., "Hello, {name}!").
            required_variables: A list of variable names that must be provided
                                when resolving this prompt.
            agent_type: Optional category for the prompt, e.g., 'text_generation'.
        
        Raises:
            ValueError: If the prompt_name already exists.
        """
        if prompt_name in self.prompts:
            raise ValueError(f"Prompt with name '{prompt_name}' already registered.")
        
        self.prompts[prompt_name] = {
            "template": template,
            "required_variables": required_variables,
            "agent_type": agent_type
        }

    def get_prompt_template(self, prompt_name: str) -> Optional[str]:
        """
        Retrieves the raw prompt template string.

        Args:
            prompt_name: The name of the prompt to retrieve.

        Returns:
            The prompt template string if found, otherwise None.
        """
        prompt_data = self.prompts.get(prompt_name)
        return prompt_data["template"] if prompt_data else None

    def resolve_prompt(self, prompt_name: str, variables: Dict[str, Any]) -> Optional[str]:
        """
        Resolves a prompt template with the given variables.

        Args:
            prompt_name: The name of the prompt to resolve.
            variables: A dictionary of variables to substitute into the template.

        Returns:
            The resolved prompt string if successful.

        Raises:
            ValueError: If the prompt_name is not found.
            ValueError: If any required variables are missing from the 'variables' dict.
        """
        prompt_data = self.prompts.get(prompt_name)
        if not prompt_data:
            raise ValueError(f"Prompt with name '{prompt_name}' not found.")

        template = prompt_data["template"]
        required_vars = prompt_data["required_variables"]

        missing_vars = [var for var in required_vars if var not in variables]
        if missing_vars:
            raise ValueError(f"Missing required variables for prompt '{prompt_name}': {', '.join(missing_vars)}")

        try:
            # Using str.format for substitution.
            # Ensure template uses {variable_name} syntax.
            return template.format(**variables)
        except KeyError as e:
            # This might happen if the template contains a placeholder not in required_vars
            # and also not provided in variables.
            raise ValueError(f"Error resolving prompt '{prompt_name}'. Variable {e} not found in provided variables, though not listed as required.")


    def list_prompts(self, agent_type: Optional[str] = None) -> List[str]:
        """
        Lists available prompt names, optionally filtered by agent type.

        Args:
            agent_type: If provided, only prompts matching this agent type are returned.

        Returns:
            A list of prompt names.
        """
        if agent_type:
            return [
                name for name, data in self.prompts.items()
                if data["agent_type"] == agent_type
            ]
        return list(self.prompts.keys())

# Example Usage (can be removed or kept for quick testing)
if __name__ == '__main__':
    registry = PromptRegistry()

    # Registering prompts
    try:
        registry.register_prompt(
            prompt_name="greet_user",
            template="Hello, {name}! Welcome to {system}.",
            required_variables=["name", "system"],
            agent_type="greeting"
        )
        registry.register_prompt(
            prompt_name="task_summary",
            template="Task: {task_description}\nPriority: {priority}",
            required_variables=["task_description", "priority"],
            agent_type="task_management"
        )
        registry.register_prompt(
            prompt_name="simple_greet",
            template="Hi there, {user_name}!",
            required_variables=["user_name"]
        )
    except ValueError as e:
        print(f"Error during registration: {e}")

    # Getting a template
    template = registry.get_prompt_template("greet_user")
    print(f"Template for 'greet_user': {template}\n")

    # Resolving prompts
    try:
        resolved_greeting = registry.resolve_prompt(
            "greet_user",
            {"name": "Alice", "system": "MCP"}
        )
        print(f"Resolved 'greet_user': {resolved_greeting}\n")

        resolved_task = registry.resolve_prompt(
            "task_summary",
            {"task_description": "Implement feature X", "priority": "High"}
        )
        print(f"Resolved 'task_summary': {resolved_task}\n")

        # Test missing variable
        print("Attempting to resolve 'greet_user' with missing 'system' variable:")
        registry.resolve_prompt("greet_user", {"name": "Bob"})
    except ValueError as e:
        print(f"Error resolving prompt: {e}\n")

    # Test non-existent prompt
    try:
        print("Attempting to resolve non-existent prompt 'unknown_prompt':")
        registry.resolve_prompt("unknown_prompt", {})
    except ValueError as e:
        print(f"Error resolving prompt: {e}\n")
    
    # Listing prompts
    all_prompts = registry.list_prompts()
    print(f"All prompts: {all_prompts}")

    greeting_prompts = registry.list_prompts(agent_type="greeting")
    print(f"Greeting prompts: {greeting_prompts}")

    task_prompts = registry.list_prompts(agent_type="task_management")
    print(f"Task management prompts: {task_prompts}")

    unknown_type_prompts = registry.list_prompts(agent_type="unknown")
    print(f"Unknown type prompts: {unknown_type_prompts}")