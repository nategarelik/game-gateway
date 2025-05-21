import pytest
from typing import List, Dict, Any, Optional

# Adjust the import path based on your project structure
# This assumes tests/ is at the same level as src/ or that PYTHONPATH is set up
try:
    from src.mcp_server.core.prompt_registry import PromptRegistry
except ImportError:
    # Fallback for different project structures, e.g. when tests are inside src
    from mcp_server.core.prompt_registry import PromptRegistry


class TestPromptRegistry:

    @pytest.fixture
    def registry(self) -> PromptRegistry:
        """Provides a fresh PromptRegistry instance for each test."""
        return PromptRegistry()

    def test_register_prompt_success(self, registry: PromptRegistry):
        """Test successfully registering a new prompt."""
        registry.register_prompt(
            prompt_name="test_prompt",
            template="This is a {variable}.",
            required_variables=["variable"],
            agent_type="test_agent"
        )
        assert "test_prompt" in registry.prompts
        assert registry.prompts["test_prompt"]["template"] == "This is a {variable}."
        assert registry.prompts["test_prompt"]["required_variables"] == ["variable"]
        assert registry.prompts["test_prompt"]["agent_type"] == "test_agent"

    def test_register_prompt_duplicate_name(self, registry: PromptRegistry):
        """Test that registering a prompt with a duplicate name raises ValueError."""
        registry.register_prompt(
            prompt_name="test_prompt",
            template="First template.",
            required_variables=[],
        )
        with pytest.raises(ValueError) as excinfo:
            registry.register_prompt(
                prompt_name="test_prompt", # Duplicate name
                template="Second template.",
                required_variables=[],
            )
        assert "Prompt with name 'test_prompt' already registered." in str(excinfo.value)

    def test_get_prompt_template_success(self, registry: PromptRegistry):
        """Test retrieving an existing prompt template."""
        template_content = "Template for {name}."
        registry.register_prompt(
            prompt_name="get_test",
            template=template_content,
            required_variables=["name"]
        )
        retrieved_template = registry.get_prompt_template("get_test")
        assert retrieved_template == template_content

    def test_get_prompt_template_not_found(self, registry: PromptRegistry):
        """Test retrieving a non-existent prompt template returns None."""
        retrieved_template = registry.get_prompt_template("non_existent_prompt")
        assert retrieved_template is None

    def test_resolve_prompt_success(self, registry: PromptRegistry):
        """Test successfully resolving a prompt with correct variables."""
        registry.register_prompt(
            prompt_name="resolve_test",
            template="Hello, {user}! Your ID is {id}.",
            required_variables=["user", "id"]
        )
        resolved_prompt = registry.resolve_prompt(
            "resolve_test",
            {"user": "Alice", "id": 123}
        )
        assert resolved_prompt == "Hello, Alice! Your ID is 123."

    def test_resolve_prompt_missing_required_variable(self, registry: PromptRegistry):
        """Test resolving a prompt with a missing required variable raises ValueError."""
        registry.register_prompt(
            prompt_name="resolve_fail_test",
            template="Data: {data_point}, Time: {timestamp}",
            required_variables=["data_point", "timestamp"]
        )
        with pytest.raises(ValueError) as excinfo:
            registry.resolve_prompt(
                "resolve_fail_test",
                {"data_point": "ValueX"} # 'timestamp' is missing
            )
        assert "Missing required variables for prompt 'resolve_fail_test': timestamp" in str(excinfo.value)

    def test_resolve_prompt_non_existent_prompt(self, registry: PromptRegistry):
        """Test resolving a non-existent prompt raises ValueError."""
        with pytest.raises(ValueError) as excinfo:
            registry.resolve_prompt("unknown_prompt", {"var": "value"})
        assert "Prompt with name 'unknown_prompt' not found." in str(excinfo.value)
        
    def test_resolve_prompt_extra_variables_provided(self, registry: PromptRegistry):
        """Test resolving a prompt when extra variables are provided (should still work)."""
        registry.register_prompt(
            prompt_name="resolve_extra_vars",
            template="Name: {name}",
            required_variables=["name"]
        )
        resolved_prompt = registry.resolve_prompt(
            "resolve_extra_vars",
            {"name": "Bob", "age": 30} # 'age' is extra but okay
        )
        assert resolved_prompt == "Name: Bob"

    def test_resolve_prompt_template_key_error(self, registry: PromptRegistry):
        """Test resolving a prompt where template has a key not in required_vars or provided vars."""
        registry.register_prompt(
            prompt_name="resolve_key_error",
            template="Value: {value}, Detail: {detail_not_in_vars}", # {detail_not_in_vars} is problematic
            required_variables=["value"]
        )
        with pytest.raises(ValueError) as excinfo:
            registry.resolve_prompt(
                "resolve_key_error",
                {"value": "TestValue"} # 'detail_not_in_vars' is not provided
            )
        # The error message from str.format() might be "KeyError: 'detail_not_in_vars'"
        # Our wrapper changes it to a ValueError.
        assert "Error resolving prompt 'resolve_key_error'. Variable 'detail_not_in_vars' not found" in str(excinfo.value)


    def test_list_prompts_all(self, registry: PromptRegistry):
        """Test listing all prompts."""
        registry.register_prompt("prompt1", "Template 1", [], "typeA")
        registry.register_prompt("prompt2", "Template 2", [], "typeB")
        registry.register_prompt("prompt3", "Template 3", [], "typeA")
        
        prompts = registry.list_prompts()
        assert len(prompts) == 3
        assert "prompt1" in prompts
        assert "prompt2" in prompts
        assert "prompt3" in prompts

    def test_list_prompts_by_agent_type(self, registry: PromptRegistry):
        """Test listing prompts filtered by agent type."""
        registry.register_prompt("p_a1", "T_A1", [], "typeA")
        registry.register_prompt("p_b1", "T_B1", [], "typeB")
        registry.register_prompt("p_a2", "T_A2", [], "typeA")
        registry.register_prompt("p_c1", "T_C1", [], "typeC")

        prompts_type_a = registry.list_prompts(agent_type="typeA")
        assert len(prompts_type_a) == 2
        assert "p_a1" in prompts_type_a
        assert "p_a2" in prompts_type_a

        prompts_type_b = registry.list_prompts(agent_type="typeB")
        assert len(prompts_type_b) == 1
        assert "p_b1" in prompts_type_b
        
        prompts_type_c = registry.list_prompts(agent_type="typeC")
        assert len(prompts_type_c) == 1
        assert "p_c1" in prompts_type_c

        prompts_type_d_empty = registry.list_prompts(agent_type="typeD") # Non-existent type
        assert len(prompts_type_d_empty) == 0

    def test_list_prompts_empty_registry(self, registry: PromptRegistry):
        """Test listing prompts when the registry is empty."""
        assert registry.list_prompts() == []
        assert registry.list_prompts(agent_type="any_type") == []