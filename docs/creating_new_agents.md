# Creating New Agents

This guide explains how to create new specialized agents for the Unity Agent MCP system, allowing you to extend the system with custom capabilities.

## Overview

The Unity Agent MCP system is designed to be extensible, allowing you to create new specialized agents for specific tasks. Each agent is responsible for a specific domain of game development, such as level design, code generation, or asset management.

## Agent Architecture

Each agent in the system follows a common architecture:

1. **Base Agent Class**: All agents inherit from the `BaseAgent` class, which provides common functionality
2. **Prompt Templates**: Agents define prompt templates for different tasks
3. **Task Processing**: Agents implement methods to process specific types of tasks
4. **MCP Integration**: Agents communicate with the MCP server and Unity through a standardized interface

## Creating a New Agent

### Step 1: Create the Agent Class

Create a new Python file in the `src/agents` directory with a name that reflects the agent's purpose, e.g., `sound_designer_agent.py`.

```python
# src/agents/sound_designer_agent.py

from .base_agent import BaseAgent

class SoundDesignerAgent(BaseAgent):
    def __init__(self, agent_id: str, mcp_server_url: str, config: dict = None):
        super().__init__(agent_id, mcp_server_url, capabilities=["sound_design", "audio_management"])
        self.config = config if config is not None else {}
        self.prompt_templates = {
            "create_sound_effect": SOUND_EFFECT_TEMPLATE,
            "create_music_track": MUSIC_TRACK_TEMPLATE,
            "optimize_audio": OPTIMIZE_AUDIO_TEMPLATE,
        }
        self.prompt_template_required_vars = {
            "create_sound_effect": ["description", "duration", "format"],
            "create_music_track": ["genre", "mood", "duration", "tempo"],
            "optimize_audio": ["file_path", "target_quality"],
        }

    async def process_task(self, task_details: dict) -> dict:
        task_id = task_details.get("task_id", "unknown_task")
        task_type = task_details.get("task_type_for_prompt")

        if not task_type:
            error_msg = f"'task_type_for_prompt' missing in task_details for task {task_id}."
            return {"status": "failure", "message": error_msg, "output": None}

        try:
            # Resolve prompt and simulate LLM (or use actual LLM)
            prompt_result = await self._resolve_prompt_and_simulate_llm(task_type, task_details)
            
            if prompt_result.get("status") == "error":
                return {"status": "failure", "message": prompt_result.get('error_message'), "output": None}
            
            llm_output = prompt_result.get("mock_output")
            
            # Process the task based on its type
            if task_type == "create_sound_effect":
                result = await self._create_sound_effect(llm_output, task_details)
            elif task_type == "create_music_track":
                result = await self._create_music_track(llm_output, task_details)
            elif task_type == "optimize_audio":
                result = await self._optimize_audio(llm_output, task_details)
            else:
                return {"status": "failure", "message": f"Unknown task type: {task_type}", "output": None}
            
            return {"status": "success", "message": "Task processed successfully", "output": result}
            
        except Exception as e:
            return {"status": "failure", "message": f"Error processing task: {str(e)}", "output": None}

    async def _resolve_prompt_and_simulate_llm(self, task_type: str, task_details: dict) -> dict:
        # Implementation similar to other agents
        # This would either use a mock response for testing or call an actual LLM
        pass

    async def _create_sound_effect(self, llm_output: dict, task_details: dict) -> dict:
        # Implementation for creating sound effects
        pass

    async def _create_music_track(self, llm_output: dict, task_details: dict) -> dict:
        # Implementation for creating music tracks
        pass

    async def _optimize_audio(self, llm_output: dict, task_details: dict) -> dict:
        # Implementation for optimizing audio
        pass
```

### Step 2: Define Prompt Templates

Define prompt templates for the different tasks your agent will handle.

```python
# At the top of your agent file

SOUND_EFFECT_TEMPLATE = """System: You are a sound design expert specializing in game audio.
- Create realistic and immersive sound effects
- Optimize audio for game environments
- Follow industry best practices for game audio

User Input:
{{
  "task_type": "create_sound_effect",
  "description": "{description}",
  "duration": "{duration}",
  "format": "{format}"
}}"""

MUSIC_TRACK_TEMPLATE = """System: You are a music composer specializing in game soundtracks.
- Create atmospheric and thematic music
- Adapt to different game genres and moods
- Create loopable tracks for seamless playback

User Input:
{{
  "task_type": "create_music_track",
  "genre": "{genre}",
  "mood": "{mood}",
  "duration": "{duration}",
  "tempo": "{tempo}"
}}"""

OPTIMIZE_AUDIO_TEMPLATE = """System: You are an audio optimization expert.
- Optimize audio files for game performance
- Maintain audio quality while reducing file size
- Follow platform-specific audio guidelines

User Input:
{{
  "task_type": "optimize_audio",
  "file_path": "{file_path}",
  "target_quality": "{target_quality}"
}}"""
```

### Step 3: Implement Task Processing Methods

Implement the methods that will process each type of task.

```python
async def _create_sound_effect(self, llm_output: dict, task_details: dict) -> dict:
    """
    Creates a sound effect based on the LLM output and task details.
    
    Args:
        llm_output: The output from the LLM
        task_details: The original task details
        
    Returns:
        A dictionary containing the created sound effect details
    """
    # Extract parameters
    description = task_details.get("description", "")
    duration = task_details.get("duration", "1.0")
    format = task_details.get("format", "wav")
    
    # In a real implementation, you would:
    # 1. Use an audio generation API or tool
    # 2. Process the generated audio
    # 3. Save the file to the appropriate location
    # 4. Return the file path and metadata
    
    # For this example, we'll return mock data
    return {
        "file_name": f"sound_effect_{task_details.get('task_id')}.{format}",
        "duration": duration,
        "description": description,
        "file_path": f"Assets/Audio/SoundEffects/sound_effect_{task_details.get('task_id')}.{format}"
    }
```

### Step 4: Create a Test File

Create a test file for your agent in the `tests/agents` directory.

```python
# tests/agents/test_sound_designer_agent.py

import pytest
import asyncio
from unittest.mock import patch, MagicMock
from src.agents.sound_designer_agent import SoundDesignerAgent

@pytest.fixture
def sound_designer_agent():
    return SoundDesignerAgent("sound_designer", "http://localhost:5001")

@pytest.mark.asyncio
async def test_process_task_create_sound_effect(sound_designer_agent):
    # Mock the _resolve_prompt_and_simulate_llm method
    sound_designer_agent._resolve_prompt_and_simulate_llm = MagicMock(
        return_value=asyncio.Future()
    )
    sound_designer_agent._resolve_prompt_and_simulate_llm.return_value.set_result({
        "status": "success",
        "mock_output": {
            "sound_type": "footstep",
            "material": "wood",
            "characteristics": ["creaky", "hollow"]
        }
    })
    
    # Mock the _create_sound_effect method
    sound_designer_agent._create_sound_effect = MagicMock(
        return_value=asyncio.Future()
    )
    sound_designer_agent._create_sound_effect.return_value.set_result({
        "file_name": "footstep_wood_001.wav",
        "duration": "0.5",
        "description": "Wooden footstep sound",
        "file_path": "Assets/Audio/SoundEffects/footstep_wood_001.wav"
    })
    
    # Create a task
    task = {
        "task_id": "test_task_001",
        "task_type_for_prompt": "create_sound_effect",
        "description": "Wooden footstep sound",
        "duration": "0.5",
        "format": "wav"
    }
    
    # Process the task
    result = await sound_designer_agent.process_task(task)
    
    # Check the result
    assert result["status"] == "success"
    assert "file_name" in result["output"]
    assert result["output"]["file_name"] == "footstep_wood_001.wav"
```

### Step 5: Register the Agent with the MCP Server

Modify the `src/mcp_server/server_core.py` file to import and register your new agent.

```python
# In the import section
try:
    from sound_designer_agent import SoundDesignerAgent
    _agent_classes["sound_designer"] = SoundDesignerAgent
    print("[INFO] Successfully imported SoundDesignerAgent.")
except ImportError as e:
    print(f"[Warning] Failed to import SoundDesignerAgent: {e}. This agent will not be available.")
```

### Step 6: Create Unity Integration

Create a Unity Editor script to interact with your new agent.

```csharp
// In unity-package/Editor/SoundDesignerWindow.cs

using UnityEngine;
using UnityEditor;
using System;
using System.Net.Http;
using System.Text;
using System.Threading.Tasks;

namespace UnityAgentMCP.Editor
{
    public class SoundDesignerWindow : EditorWindow
    {
        private string description = "";
        private string duration = "1.0";
        private string format = "wav";
        private string response = "";
        private bool isProcessing = false;

        [MenuItem("Window/Unity Agent MCP/Sound Designer")]
        public static void ShowWindow()
        {
            GetWindow<SoundDesignerWindow>("Sound Designer");
        }

        void OnGUI()
        {
            GUILayout.Label("Sound Designer Agent", EditorStyles.boldLabel);

            EditorGUILayout.Space();

            EditorGUILayout.LabelField("Description");
            description = EditorGUILayout.TextArea(description, GUILayout.Height(100));

            EditorGUILayout.BeginHorizontal();
            EditorGUILayout.PrefixLabel("Duration (seconds)");
            duration = EditorGUILayout.TextField(duration);
            EditorGUILayout.EndHorizontal();

            EditorGUILayout.BeginHorizontal();
            EditorGUILayout.PrefixLabel("Format");
            format = EditorGUILayout.TextField(format);
            EditorGUILayout.EndHorizontal();

            EditorGUILayout.Space();

            GUI.enabled = !isProcessing && !string.IsNullOrEmpty(description);
            if (GUILayout.Button("Create Sound Effect"))
            {
                CreateSoundEffect();
            }
            GUI.enabled = true;

            EditorGUILayout.Space();

            EditorGUILayout.LabelField("Response");
            EditorGUILayout.TextArea(response, GUILayout.Height(200));
        }

        private async void CreateSoundEffect()
        {
            // Implementation similar to other agent windows
        }
    }
}
```

### Step 7: Document Your Agent

Create documentation for your agent in the `docs/agents` directory.

```markdown
# Sound Designer Agent

The Sound Designer Agent is responsible for creating and managing audio assets for your Unity project.

## Capabilities

- Creating sound effects based on descriptions
- Composing music tracks based on genre, mood, and tempo
- Optimizing audio files for game performance

## Usage

### Creating Sound Effects

1. Open Window > Unity Agent MCP > Sound Designer
2. Enter a description of the sound effect
3. Specify the duration and format
4. Click "Create Sound Effect"

Example description:
```
A creaky wooden footstep sound, as if someone is walking on an old wooden floor.
```

### Composing Music Tracks

1. Open Window > Unity Agent MCP > Sound Designer
2. Select "Music Track" from the task dropdown
3. Specify the genre, mood, duration, and tempo
4. Click "Create Music Track"

Example parameters:
- Genre: Fantasy
- Mood: Mysterious
- Duration: 60.0
- Tempo: 80

### Optimizing Audio

1. Open Window > Unity Agent MCP > Sound Designer
2. Select "Optimize Audio" from the task dropdown
3. Specify the file path and target quality
4. Click "Optimize Audio"

## Integration with Other Agents

The Sound Designer Agent can work with other agents:

- **Level Architect**: Add ambient sounds to scenes
- **Code Weaver**: Generate audio manager scripts
- **Documentation Sentinel**: Document audio assets
```

## Best Practices for Agent Development

1. **Follow the Common Architecture**: Inherit from `BaseAgent` and follow the established patterns
2. **Use Clear Prompt Templates**: Design clear and specific prompt templates for each task
3. **Implement Robust Error Handling**: Handle errors gracefully and provide helpful error messages
4. **Write Comprehensive Tests**: Test all aspects of your agent's functionality
5. **Document Your Agent**: Create clear documentation for users of your agent
6. **Consider Integration Points**: Think about how your agent will interact with other agents and Unity
7. **Optimize Performance**: Ensure your agent performs well, especially for resource-intensive tasks
8. **Provide Feedback**: Include progress updates and feedback in your agent's responses

## Advanced Agent Features

### Agent State Management

Agents can maintain state across multiple requests using the `agent_states` field in the `GameDevState` class.

```python
async def process_task(self, task_details: dict) -> dict:
    # Get the current state for this agent
    agent_id = self.agent_id
    state_manager = self.get_state_manager()
    current_state = state_manager.get_agent_state(agent_id)
    
    # Update the state
    current_state["last_task"] = task_details.get("task_id")
    current_state["task_count"] = current_state.get("task_count", 0) + 1
    
    # Save the updated state
    state_manager.set_agent_state(agent_id, current_state)
    
    # Process the task...
```

### Multi-Agent Collaboration

Agents can collaborate with other agents by sending requests to the MCP server.

```python
async def _create_sound_effect(self, llm_output: dict, task_details: dict) -> dict:
    # Create the sound effect...
    
    # Request documentation from the Documentation Sentinel
    doc_request = {
        "task_id": f"{task_details.get('task_id')}_doc",
        "agent_id": "documentation_sentinel",
        "parameters": {
            "asset_type": "sound_effect",
            "asset_name": sound_effect_name,
            "asset_description": description,
            "asset_metadata": metadata
        }
    }
    
    doc_response = await self.send_request_to_mcp(doc_request)
    
    # Return the result with documentation
    return {
        "file_name": sound_effect_name,
        "duration": duration,
        "description": description,
        "file_path": file_path,
        "documentation": doc_response.get("result", {}).get("documentation", "")
    }
```

### Custom LLM Integration

Agents can integrate with custom LLM providers by implementing the `_resolve_prompt_and_call_llm` method.

```python
async def _resolve_prompt_and_call_llm(self, task_type: str, task_details: dict) -> dict:
    template_string = self._get_prompt_template_for_task(task_type)
    if not template_string:
        return {"status": "error", "error_message": f"No prompt template found for task_type: {task_type}"}
    
    # Resolve the prompt template
    resolved_prompt = template_string.format(**task_details)
    
    # Call your custom LLM API
    llm_response = await self._call_custom_llm_api(resolved_prompt)
    
    return {"status": "success", "llm_output": llm_response}

async def _call_custom_llm_api(self, prompt: str) -> dict:
    # Implement your custom LLM API call here
    pass
```

## Conclusion

Creating new agents allows you to extend the Unity Agent MCP system with custom capabilities tailored to your specific game development needs. By following the common architecture and best practices, you can create agents that integrate seamlessly with the existing system and provide valuable functionality to Unity developers.