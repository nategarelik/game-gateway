import requests
import json
import uuid

url = "http://127.0.0.1:8000/api/v1/execute_agent"
task_id = str(uuid.uuid4())
agent_id = "orchestrator"
prompt = "Create a simple 2D platformer game with a main character, basic movement, and a few collectible items."
scene_name = "MyUnityScene" # Placeholder, as Unity's scene_name is dynamic

payload = {
    "task_id": task_id,
    "agent_id": agent_id,
    "parameters": {
        "prompt": prompt,
        "scene_name": scene_name
    }
}

headers = {
    "Content-Type": "application/json"
}

print(f"Sending request to: {url}")
print(f"Payload: {json.dumps(payload, indent=2)}")

try:
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    response.raise_for_status() # Raise an exception for HTTP errors (4xx or 5xx)
    print("Response Status Code:", response.status_code)
    print("Response Body:", response.json())
except requests.exceptions.RequestException as e:
    print(f"Request failed: {e}")
    if hasattr(e, 'response') and e.response is not None:
        print("Response Status Code:", e.response.status_code)
        print("Response Body:", e.response.text)

