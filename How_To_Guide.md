# Autonomous AI Agent Ecosystem for Unity Game Development: How-To Guide

This guide provides step-by-step instructions on how to set up and effectively use the Autonomous AI Agent Ecosystem within Unity for game development.

## 1. Initial Setup

### 1.1. MCP Server Setup

The Master Control Program (MCP) Server is the backbone of the ecosystem. It needs to be running for the Unity Editor to communicate with the AI agents.

1.  **Prerequisites:** Ensure you have Python (3.8+) and `pip` installed.
2.  **Clone the Repository:** If you haven't already, clone the project repository containing the MCP Server code.
    ```bash
    git clone [repository_url]
    cd [repository_name]
    ```
3.  **Install Dependencies:** Navigate to the `src/mcp_server` directory and install the required Python packages.
    ```bash
    cd src/mcp_server
    pip install -r requirements.txt
    ```
4.  **Run the MCP Server:** Start the FastAPI server. It will typically run on `http://127.0.0.1:8000`.
    ```bash
    uvicorn main:app --reload
    ```
    *   Keep this terminal window open as long as you are using the agents.

### 1.2. Unity Integration Setup

The Unity integration allows you to interact with the MCP Server directly from the Unity Editor.

1.  **Open Your Unity Project:** Launch Unity Hub and open the Unity project where you want to use the AI agents.
2.  **Import the Unity Package:**
    *   Locate the `unity-package` directory in the cloned repository.
    *   In Unity, go to `Window > Package Manager`.
    *   Click the `+` icon in the top-left corner and select `Add package from tarball...`.
    *   Navigate to the `unity-package` directory and select `com.unity-agent-mcp.tgz`.
    *   This will import the necessary Editor tools and runtime components.
3.  **Configure MCP Server URL:**
    *   In the Unity Editor, go to `Window > Unity Agent MCP > Settings`.
    *   In the "Server URL" field, enter the address of your running MCP Server (e.g., `http://127.0.0.1:8000/api/v1`).
    *   Click "Test Connection" to verify connectivity.
    *   Click "Save Settings" to persist the URL.

## 2. Interacting with Agents

Once the setup is complete, you can start sending prompts to the AI agents.

1.  **Open the Agent Interface:** In the Unity Editor, go to `Window > Unity Agent MCP > Agent Interface`.
2.  **Select an Agent Type:** From the "Agent Type" dropdown, choose the specialized agent you wish to interact with (e.g., "Orchestrator", "Level Architect", "Code Weaver").
3.  **Enter Your Prompt:** In the "Prompt" text area, describe the task you want the agent to perform using natural language. Be as clear and specific as possible.
    *   **Example Prompt for Orchestrator:** "Create a simple 2D platformer game with a main character, basic movement, and a few collectible items."
    *   **Example Prompt for Level Architect:** "Generate a forest level with a winding path, a small river, and a hidden cave."
    *   **Example Prompt for Code Weaver:** "Write a C# script for player movement (left, right, jump) and attach it to the main character GameObject."
4.  **Send to Agent:** Click the "Send to Agent" button. The "Response" area will update with "Processing request..." and then display the agent's response or status.

## 3. Understanding the Workflow (Behind the Scenes)

When you send a prompt:

*   The Unity Editor constructs a JSON request containing your `prompt`, a unique `task_id`, the `agent_id`, and other relevant parameters (like the current Unity scene name).
*   This request is sent to the MCP Server's `/execute_agent` endpoint.
*   The MCP Server's internal `StateManager` initializes a LangGraph task, which is a dynamic workflow designed to process your request.
*   The Orchestrator agent (if selected) or other specialized agents then interpret the prompt and execute sub-tasks, potentially collaborating with other agents or toolchains (e.g., generating code, creating assets, modifying the Unity scene).
*   The MCP Server manages the state of this task and provides updates back to the Unity Editor.

## 4. Optimizing for Local LLMs (Advanced)

To save on token usage costs and improve performance, you can configure the system to use local Large Language Models (LLMs).

1.  **Install a Local LLM Inference Server:**
    *   **LocalAI:** Recommended for its OpenAI-compatible API. Follow the instructions on the [`mudler/LocalAI`](https://github.com/mudler/LocalAI) GitHub repository to install and run it. You can use Docker for easy setup.
    *   **Ollama:** Another excellent option for running local LLMs. Visit the Ollama website for installation instructions.
2.  **Download LLM Models:** Download quantized LLM models (e.g., GGUF format) from platforms like Hugging Face. These are optimized for local inference on consumer hardware. Place them in the designated models directory for your chosen local inference server (e.g., `./models` for LocalAI).
3.  **Configure MCP Server to Use Local LLM (Future Integration):**
    *   *Note: This feature is currently under development.* The goal is to allow the MCP Server and its agents to dynamically route LLM calls to your local inference server. This will involve:
        *   Updating the MCP Server's configuration (e.g., via environment variables or a config file) to point to your local LLM server's endpoint.
        *   Modifying the agents' internal logic to check for a preferred LLM provider and use the local server if configured.
4.  **Unity Editor LLM Provider Selection (Future Integration):**
    *   *Note: This feature is currently under development.* A future update will introduce a UI element in the Unity Editor to explicitly select your desired LLM provider (e.g., "OpenAI (Cloud)", "LocalAI (Local)", "Ollama (Local)"). This selection will be passed to the MCP Server to route requests accordingly.

By leveraging local LLMs, you can significantly reduce operational costs and enhance the responsiveness of the AI agents, making your game development workflow even more efficient.