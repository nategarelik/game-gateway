# Pixel Forge Agent Documentation

**Agent ID:** Typically `pixel_forge_agent` (or similar, e.g., `pixel_forge_001`)

**Inherits From:** [`BaseAgent`](../../src/agents/base_agent.py)

:start_line:7
-------
## Overview

The Pixel Forge Agent is a specialized component within the Autonomous AI Agent Ecosystem. While it retains capabilities for the procedural generation of game assets (like 2D images, textures, and 3D model placeholders), its primary focus has shifted to **placing and manipulating existing assets and placeholders directly within the Unity Editor**. It interacts with the Master Control Program (MCP) to receive tasks and report results, leveraging the `UnityToolchainBridge` for direct Editor control.

## Capabilities

:start_line:12
-------
*   `asset_generation_2d`: Can generate 2D assets such as images, sprites, and textures (de-prioritized).
*   `asset_generation_3d_placeholder`: Can generate placeholder 3D models or conceptual representations (de-prioritized).
*   `asset_placement`: Can place existing assets or placeholders within the Unity Editor at specified positions, rotations, and scales.

## Core Functionality

:start_line:18
-------
### Task Processing (`process_task`)

The `PixelForgeAgent` processes tasks assigned by the MCP. It supports both asset generation (de-prioritized) and asset placement.

#### 1. Asset Generation Task (`type: "generate_asset"`)

This task type is used for generating new assets.

```json
{
    "task_id": "unique_task_identifier",
    "type": "generate_asset",
    "asset_type": "image" | "texture" | "model_placeholder",
    "prompt": "A detailed natural language description of the desired asset. For example, 'A rusty metallic texture for a sci-fi crate' or 'A simple, low-poly wooden barrel model'.",
    "style_guidelines": {
        "palette": "bright_colors" | "monochromatic" | "custom_hex_list", // Example
        "theme": "fantasy" | "sci-fi" | "cartoonish", // Example
        "artistic_style": "pixel_art" | "photorealistic_concept" // Example
        // Other style parameters as defined by the Style Enforcement System
    },
    "output_path_suggestion": "project_alpha/assets/generated/textures/crate_rust.png" // Optional suggested path for saving
}
```

**Workflow for `generate_asset`:**

1.  **Task Reception:** Receives task details from the MCP.
2.  **Input Validation:** Checks for required fields (`task_id`, `asset_type`, `prompt`). If invalid, posts an `agent_task_error` event to the MCP.
3.  **Prompt Interpretation:** (Placeholder) Analyzes the `prompt` to understand the asset requirements.
4.  **Style Application:** (Placeholder) Applies `style_guidelines` using the Style Enforcement System.
5.  **Toolchain Interaction:** (Placeholder)
    *   For `asset_type` "image" or "texture": Interacts with the Retro Diffusion bridge.
    *   For `asset_type` "model_placeholder": Interacts with the Unity Muse bridge for conceptual generation.
6.  **Asset Generation:** The selected toolchain generates the asset.
7.  **Result Reporting:** Posts an `agent_task_completed` event to the MCP, including information about the generated asset (e.g., ID, path, metadata).

#### 2. Asset Placement Task (`type: "place_asset"`)

This task type is used for placing existing assets or placeholders within the Unity Editor.

```json
{
    "task_id": "unique_task_identifier",
    "type": "place_asset",
    "asset_name": "NameOfAssetPrefabOrModel", // e.g., "Tree_Pine_01", "Cube", "PlayerCharacter"
    "position": {"x": 0.0, "y": 0.0, "z": 0.0}, // World coordinates
    "rotation": {"x": 0.0, "y": 0.0, "z": 0.0}, // Euler angles (optional, defaults to 0,0,0)
    "scale": {"x": 1.0, "y": 1.0, "z": 1.0} // Scale factors (optional, defaults to 1,1,1)
}
```

**Workflow for `place_asset`:**

1.  **Task Reception:** Receives task details from the MCP.
2.  **Input Validation:** Checks for required fields (`task_id`, `asset_name`, `position`). If invalid, posts an `agent_task_error` event to the MCP.
3.  **Unity Interaction:** Calls the internal `place_asset_in_unity` method, which uses the `UnityToolchainBridge` to send `manipulate_scene` commands to the Unity Editor.
4.  **Result Reporting:** Posts an `agent_task_completed` event to the MCP, including the Unity Editor's response.

### Direct Generation Methods (Retained for internal use)

### Direct Generation Methods

The agent also exposes (or will expose) more direct methods for asset generation, which might be called internally or by other tightly coupled services:

*   `generate_image(prompt: str, style_guidelines: dict = None) -> dict`: Generates an image.
*   `generate_texture(prompt: str, style_guidelines: dict = None) -> dict`: Generates a texture.
*   `generate_model_placeholder(prompt: str, style_guidelines: dict = None) -> dict`: Generates a 3D model placeholder.

These currently have placeholder implementations.

## MCP Interaction

*   **Registration:** Registers with the MCP upon initialization, providing its `agent_id` and `capabilities`.
*   **Event Posting:**
    *   `agent_task_completed`: Sent when an asset generation task is successfully completed.
        *   Payload includes `task_id`, `agent_id`, `result` (asset info), and a `message`.
    *   `agent_task_error`: Sent if an error occurs during task processing.
        *   Payload includes `task_id`, `error` message, and original `details` of the task.

:start_line:110
-------
## Integration with Other Systems

*   **MCP Server:** For tasking, eventing, and overall orchestration.
*   **Unity Toolchain:** For direct interaction with the Unity Editor (scene manipulation, asset placement). (Interface via [`UnityToolchainBridge`](../../src/toolchains/unity_bridge.py))
*   **Retro Diffusion Toolchain:** For 2D asset generation (de-prioritized). (Interface via [`RetroDiffusionBridge`](../../src/toolchains/retro_diffusion_bridge.py))
*   **Unity Muse Toolchain:** For conceptual 3D asset generation (de-prioritized). (Interface via [`MuseBridge`](../../src/toolchains/muse_bridge.py))
*   **Style Enforcement System:** To ensure generated assets adhere to defined artistic styles and palettes. (Details TBD, likely involves passing style guidelines and validation steps).

## Configuration

*   `agent_id`: Unique identifier for the agent instance.
*   `mcp_server_url`: URL of the MCP server.
*   `capabilities`: List of capabilities this agent offers.

## Future Enhancements

*   Full implementation of Retro Diffusion and Muse bridge interactions.
*   Integration with the Style Enforcement System.
*   More sophisticated prompt understanding and parameterization for toolchains.
*   Support for asset modification tasks.
*   Batch generation capabilities.

:start_line:117
-------
## Example `if __name__ == '__main__':` Usage

The agent includes a basic `if __name__ == '__main__':` block for standalone testing or demonstration (requires a running or mocked MCP server). It shows how to instantiate the agent and process example tasks, including both asset generation and placement.

The agent includes a basic `if __name__ == '__main__':` block for standalone testing or demonstration (requires a running or mocked MCP server). It shows how to instantiate the agent and process an example task.

```python
# src/agents/pixel_forge_agent.py
# ... (class definition) ...

if __name__ == '__main__':
    async def main():
        mcp_url = "http://localhost:8000/mcp" # Example MCP URL
        agent = PixelForgeAgent(agent_id="pixel_forge_001", mcp_server_url=mcp_url)
        
:start_line:125
-------
        # Example task: Place an asset
        example_place_task = {
            "task_id": "pf_place_task_123",
            "type": "place_asset",
            "asset_name": "Prefab_Tree_01",
            "position": {"x": 10, "y": 0, "z": 5},
            "rotation": {"x": 0, "y": 45, "z": 0},
            "scale": {"x": 2, "y": 2, "z": 2}
        }
        result_place = await agent.process_task(example_place_task)
        logger.info(f"Asset placement task result: {result_place}")

        # Example task: Generate an asset (de-prioritized but still functional)
        example_generate_task = {
            "task_id": "pf_generate_task_456",
            "type": "generate_asset",
            "asset_type": "image",
            "prompt": "A stylized rock texture",
            "style_guidelines": {"resolution": "512x512"},
            "output_path_suggestion": "project_x/assets/textures/"
        }
        result_generate = await agent.process_task(example_generate_task)
        logger.info(f"Asset generation task result: {result_generate}")

        await agent.shutdown()

    asyncio.run(main())