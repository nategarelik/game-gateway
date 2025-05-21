# Muse Bridge Documentation

The [`MuseBridge`](../../src/toolchains/muse_bridge.py) class serves as an interface to (a conceptual or mocked) Unity Muse service. It is designed to facilitate interactions for tasks such as generating scene concepts, material concepts, 3D model concepts, and obtaining animation advice.

It inherits from [`BaseToolchainBridge`](../../src/toolchains/base_toolchain_bridge.py), utilizing its asynchronous request queuing and processing capabilities via a worker thread. This ensures that interactions with the (potentially slow) external Muse service do not block the main application or agent logic.

## Purpose

The primary goal of the `MuseBridge` is to allow agents within the Autonomous AI Agent Ecosystem (e.g., `LevelArchitectAgent`, `PixelForgeAgent`) to leverage Muse's conceptual generation capabilities without needing to handle the direct communication complexities. The bridge abstracts these interactions, providing a clear Python API.

## Core Functionality

### Initialization (`__init__`)

```python
class MuseBridge(BaseToolchainBridge):
    def __init__(self, mcp_server, api_key: str = None, muse_endpoint: str = None):
        # ...
```

*   `mcp_server`: An instance of the Master Control Program server (or a mock), primarily for context.
*   `api_key` (optional): The API key for accessing the Unity Muse service. For the current mock implementation, this is not used for actual authentication.
*   `muse_endpoint` (optional): The API endpoint URL for Unity Muse. Defaults to a mock URL: `https://api.unity.com/v1/muse/mock`.

### Request Handling (`_handle_specific_request`)

This internal method is invoked by the `BaseToolchainBridge`'s worker thread to process queued requests.
For the `MuseBridge`, it currently simulates interaction with Muse:
1.  Logs the request details.
2.  Simulates a network delay and processing time (partially based on prompt length).
3.  Based on the `request_type`, it constructs a mock JSON response.
4.  Supported `request_type` values:
    *   `GENERATE_SCENE_CONCEPT`
    *   `GENERATE_MATERIAL_CONCEPT`
    *   `GET_ANIMATION_ADVICE`
    *   `GENERATE_3D_MODEL_CONCEPT` (useful for `PixelForgeAgent`)
5.  If an unsupported `request_type` is received, it raises a `ValueError`.

### Public Interface Methods

The `MuseBridge` provides the following public methods for agents to submit requests. Each method returns a `concurrent.futures.Future` object, which will eventually contain the result (a dictionary) or an exception if the request processing failed.

*   **`generate_scene_concept(self, prompt: str, mood: str = "neutral", lighting: str = "daylight", agent_id: str = None) -> Future`**
    *   Payload sent: `{"prompt": prompt, "mood": mood, "lighting": lighting}`
    *   Mocked Response Example:
        ```json
        {
            "request_id": "...",
            "status": "success_mock",
            "concept_type": "scene",
            "description": "Conceptual scene based on: 'A mystical forest clearing at twilight'. Includes elements like [element1, element2].",
            "mood": "twilight",
            "elements_suggested": ["mock_tree_01", "mock_rock_02", "mock_lighting_twilight"]
        }
        ```

*   **`generate_material_concept(self, prompt: str, base_color: str = None, texture_style: str = None, agent_id: str = None) -> Future`**
    *   Payload sent: `{"prompt": prompt, "base_color": base_color, "texture_style": texture_style}`
    *   Mocked Response Example:
        ```json
        {
            "request_id": "...",
            "status": "success_mock",
            "concept_type": "material",
            "description": "Conceptual material for: 'Ancient runic stone texture'. Properties: [color, texture_idea].",
            "base_color_idea": "#5A5A5A",
            "texture_style_idea": "smooth_metallic"
        }
        ```

*   **`get_animation_advice(self, query: str, character_type: str = None, agent_id: str = None) -> Future`**
    *   Payload sent: `{"query": query, "character_type": character_type}`
    *   Mocked Response Example:
        ```json
        {
            "request_id": "...",
            "status": "success_mock",
            "advice_type": "animation",
            "query": "A heavy two-handed sword swing",
            "suggestion": "For 'A heavy two-handed sword swing', consider using [technique A] and focus on [keyframe principle B].",
            "estimated_complexity": "medium"
        }
        ```

*   **`generate_3d_model_concept(self, prompt: str, complexity: str = "low_poly", agent_id: str = None) -> Future`**
    *   Payload sent: `{"prompt": prompt, "complexity": complexity}`
    *   Mocked Response Example:
        ```json
        {
            "request_id": "...",
            "status": "success_mock",
            "concept_type": "3d_model",
            "description": "Conceptual 3D model for: 'A simple wooden crate' (low_poly). Key features: [feature1, feature2].",
            "suggested_primitives": ["cube", "sphere"],
            "estimated_polycount_category": "low_poly"
        }
        ```

## Interaction Flow

1.  An agent (e.g., `PixelForgeAgent`) needs a concept from Muse.
2.  The agent calls one of the public methods on a `MuseBridge` instance (e.g., `muse_bridge.generate_3d_model_concept(...)`).
3.  The `MuseBridge` wraps the request and puts it onto its internal queue via `_submit_request`. A `Future` object is returned to the agent.
4.  The `MuseBridge`'s worker thread picks up the request from the queue.
5.  `_handle_specific_request` is called, which (currently) simulates the interaction and generates a mock response.
6.  The result (or an exception) is set on the `Future` object.
7.  The agent can then get the result from the `Future` (e.g., by calling `future.result()` in a synchronous context, or `await future` in an asynchronous context).

## Example Usage (from `if __name__ == '__main__':`)

The script includes a synchronous example in its `if __name__ == '__main__':` block:

```python
# In src/toolchains/muse_bridge.py

class MockMCPServer:
    def __init__(self):
        self.name = "MockMCPServer"

# ... (inside if __name__ == '__main__')
mock_mcp_sync = MockMCPServer()
muse_bridge_sync = MuseBridge(mcp_server=mock_mcp_sync, api_key="FAKE_API_KEY_SYNC")

logger.info("SYNC: Submitting requests to MuseBridge...")
f1 = muse_bridge_sync.generate_scene_concept(prompt="A cyberpunk city alley", agent_id="LA02")
f2 = muse_bridge_sync.generate_3d_model_concept(prompt="Sci-fi drone", complexity="medium_poly", agent_id="PF02")

# .result() is blocking and will wait for the worker thread to process
logger.info(f"SYNC: Scene concept result: {f1.result(timeout=5)}")
logger.info(f"SYNC: 3D model concept result: {f2.result(timeout=5)}")

muse_bridge_sync.shutdown()
logger.info("SYNC: MuseBridge demo finished.")
```

This demonstrates how requests are submitted and how their results can be retrieved. In a real multi-agent, asynchronous environment, agents would typically `await` the futures.

## Future Enhancements

*   Integration with a live Unity Muse API endpoint.
*   Actual HTTP request/response handling instead of mock logic.
*   More detailed error handling and reporting.
*   Support for more advanced Muse features as they become available.