# Contributing to Unity Agent MCP

Thank you for considering contributing to Unity Agent MCP! This document provides guidelines and instructions for contributing to the project.

## Code of Conduct

Please be respectful and considerate of others when contributing to this project. We aim to foster an inclusive and welcoming community.

## How to Contribute

There are many ways to contribute to the Unity Agent MCP project:

- Reporting bugs
- Suggesting enhancements
- Writing documentation
- Improving code
- Creating new features
- Reviewing pull requests

### Reporting Bugs

If you find a bug, please create an issue on GitHub with the following information:

- A clear, descriptive title
- A detailed description of the bug
- Steps to reproduce the bug
- Expected behavior
- Actual behavior
- Screenshots or logs (if applicable)
- Environment information (Unity version, OS, etc.)

### Suggesting Enhancements

If you have an idea for an enhancement, please create an issue on GitHub with the following information:

- A clear, descriptive title
- A detailed description of the enhancement
- Why the enhancement would be useful
- Any potential implementation details
- Any relevant examples or references

### Pull Requests

If you want to contribute code or documentation, please follow these steps:

1. Fork the repository
2. Create a new branch for your feature or bugfix
3. Make your changes
4. Run tests to ensure your changes don't break existing functionality
5. Submit a pull request

## Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/YOUR_USERNAME/unity-agent-mcp.git
   cd unity-agent-mcp
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run tests:
   ```bash
   python -m pytest tests/
   ```

## Project Structure

- `src/`: Core source code
  - `agents/`: Agent implementations
  - `mcp_server/`: MCP server implementation
  - `protocols/`: Communication protocols
  - `systems/`: System components
  - `toolchains/`: Toolchain integrations
  - `workflows/`: Workflow definitions
- `docs/`: Documentation
- `tests/`: Test files
- `unity-package/`: Unity integration package
- `scripts/`: Utility scripts

## Coding Standards

### Python

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide
- Use type hints where appropriate
- Write docstrings for all functions, classes, and modules
- Keep functions and methods focused on a single responsibility
- Use meaningful variable and function names

### C# (Unity)

- Follow [Microsoft's C# Coding Conventions](https://docs.microsoft.com/en-us/dotnet/csharp/fundamentals/coding-style/coding-conventions)
- Use PascalCase for class names, public methods, and properties
- Use camelCase for private fields and local variables
- Write XML documentation comments for all public members
- Keep classes focused on a single responsibility
- Use meaningful variable and function names

## Testing

All new features should include tests. Run the test suite with:

```bash
python -m pytest tests/
```

For Unity code, write Editor tests using Unity's Test Framework.

## Documentation

Please update documentation when adding or modifying features. Documentation is in Markdown format in the `docs/` directory.

Follow these guidelines for documentation:

- Use clear, concise language
- Include examples where appropriate
- Keep documentation up to date with code changes
- Use proper Markdown formatting

## Commit Messages

Write clear, descriptive commit messages:

- Use the present tense ("Add feature" not "Added feature")
- Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit the first line to 72 characters or less
- Reference issues and pull requests after the first line

Example:
```
Add Level Architect scene validation

- Add validation for scene constraints
- Ensure all objects have proper colliders
- Fix issue with object placement

Fixes #123
```

## Pull Request Process

1. Ensure your code passes all tests
2. Update documentation if necessary
3. Update the README.md if necessary
4. Submit your pull request with a clear description of the changes
5. Wait for review and address any feedback

## Versioning

We use [Semantic Versioning](https://semver.org/) for versioning. For the versions available, see the tags on this repository.

## License

By contributing to this project, you agree that your contributions will be licensed under the project's MIT License.

## Questions?

If you have any questions about contributing, please create an issue on GitHub or reach out to the project maintainers.

Thank you for contributing to Unity Agent MCP!