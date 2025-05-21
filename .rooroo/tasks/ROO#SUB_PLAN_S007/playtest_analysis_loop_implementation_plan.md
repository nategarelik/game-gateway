# Playtest Analysis Loop Implementation Plan

## Overview

The Playtest Analysis Loop is a critical component of the Autonomous Iteration Workflow, enabling AI agents to collect metrics, analyze playtest data, and trigger optimization actions without human intervention. This document outlines the implementation plan for creating a closed-loop optimization system that continuously improves game performance and quality.

## Core Components

### 1. QA Commander Agent

**Purpose:** Orchestrates the playtest process, schedules tests, and coordinates with other agents.

**Implementation Details:**
- **Agent Class:** `QACommanderAgent` extending the base `Agent` class
- **Prompt Template:**
  ```python
  QA_COMMANDER_PROMPT = """
  System: You are QA_Commander, an expert in automated game testing and performance analysis.
  
  Your responsibilities:
  - Schedule and execute automated playtests
  - Collect and analyze performance metrics
  - Identify optimization opportunities
  - Trigger appropriate optimization actions
  - Maintain test case repository
  - Report critical issues that require human intervention
  
  Current Project Context:
  - Game Style: {{game_style}}
  - Target Performance: {{performance_targets}}
  - Current Test Suite: {{test_suite_summary}}
  
  Task: {{task_description}}
  """
  ```

- **Registration with MCP:**
  ```python
  mcp_server.register_agent(QACommanderAgent(
      role="QA_Commander",
      prompt_template=QA_COMMANDER_PROMPT,
      tools=["test_runner", "metric_collector", "optimization_trigger"]
  ))
  ```

### 2. Test Case Repository

**Purpose:** Maintains a structured database of test cases, scenarios, and expected outcomes.

**Implementation Details:**
- **Data Structure:**
  ```python
  class TestCase:
      def __init__(self, id, name, description, scene, steps, expected_results, 
                   performance_thresholds, priority):
          self.id = id
          self.name = name
          self.description = description
          self.scene = scene
          self.steps = steps  # List of actions to perform
          self.expected_results = expected_results
          self.performance_thresholds = performance_thresholds
          self.priority = priority
          self.history = []  # Track test results over time
  ```

- **Repository Class:**
  ```python
  class TestCaseRepository:
      def __init__(self):
          self.test_cases = {}
          
      def add_test_case(self, test_case):
          self.test_cases[test_case.id] = test_case
          
      def get_test_case(self, id):
          return self.test_cases.get(id)
          
      def get_test_cases_by_scene(self, scene):
          return [tc for tc in self.test_cases.values() if tc.scene == scene]
          
      def get_test_cases_by_priority(self, min_priority):
          return [tc for tc in self.test_cases.values() if tc.priority >= min_priority]
  ```

### 3. Metric Collection System

**Purpose:** Captures and processes performance data during playtests.

**Implementation Details:**
- **Metrics to Collect:**
  - Frame time/FPS
  - Memory usage and leaks
  - Collision checks per frame
  - Draw calls
  - Texture memory usage
  - Physics calculations
  - Load times
  - Input response time

- **Collection Class:**
  ```python
  class MetricCollector:
      def __init__(self):
          self.metrics = {}
          self.thresholds = {}
          
      def register_metric(self, name, collection_method, threshold=None):
          self.metrics[name] = collection_method
          if threshold:
              self.thresholds[name] = threshold
              
      def collect_metrics(self, test_case):
          results = {}
          for name, method in self.metrics.items():
              results[name] = method(test_case)
          return results
          
      def analyze_metrics(self, results):
          issues = []
          for name, value in results.items():
              if name in self.thresholds and value > self.thresholds[name]:
                  issues.append({
                      "metric": name,
                      "value": value,
                      "threshold": self.thresholds[name],
                      "severity": (value / self.thresholds[name]) - 1
                  })
          return sorted(issues, key=lambda x: x["severity"], reverse=True)
  ```

- **Unity Integration:**
  ```csharp
  public class MetricsReporter : MonoBehaviour
  {
      private Dictionary<string, float> metrics = new Dictionary<string, float>();
      
      void Update()
      {
          // Collect frame time
          metrics["frameTime"] = Time.deltaTime * 1000; // Convert to ms
          
          // Collect memory usage
          metrics["memoryUsage"] = System.GC.GetTotalMemory(false) / (1024 * 1024); // MB
          
          // Report metrics every N frames
          if (Time.frameCount % 60 == 0)
          {
              ReportMetrics();
          }
      }
      
      void ReportMetrics()
      {
          string json = JsonUtility.ToJson(metrics);
          // Send to MCP server via REST API or WebSocket
          StartCoroutine(SendMetrics(json));
      }
      
      IEnumerator SendMetrics(string json)
      {
          using (UnityWebRequest request = UnityWebRequest.Post("http://localhost:8000/metrics", json))
          {
              yield return request.SendWebRequest();
          }
      }
  }
  ```

### 4. Analysis Engine

**Purpose:** Processes collected metrics, identifies patterns, and determines optimization needs.

**Implementation Details:**
- **Analysis Class:**
  ```python
  class PlaytestAnalysisEngine:
      def __init__(self, metric_collector, test_repository):
          self.metric_collector = metric_collector
          self.test_repository = test_repository
          self.optimization_rules = []
          
      def register_optimization_rule(self, metric_pattern, optimization_action):
          self.optimization_rules.append({
              "pattern": metric_pattern,
              "action": optimization_action
          })
          
      def analyze_test_results(self, test_id, metrics_data):
          test_case = self.test_repository.get_test_case(test_id)
          if not test_case:
              return {"error": "Test case not found"}
              
          # Store results in history
          test_case.history.append({
              "timestamp": datetime.now(),
              "metrics": metrics_data
          })
          
          # Analyze metrics against thresholds
          issues = self.metric_collector.analyze_metrics(metrics_data)
          
          # Determine optimization actions
          optimizations = []
          for issue in issues:
              for rule in self.optimization_rules:
                  if self._matches_pattern(issue, rule["pattern"]):
                      optimizations.append({
                          "issue": issue,
                          "action": rule["action"],
                          "priority": issue["severity"]
                      })
                      
          return {
              "test_id": test_id,
              "issues": issues,
              "optimizations": optimizations
          }
          
      def _matches_pattern(self, issue, pattern):
          # Pattern matching logic
          # e.g., check if metric name matches and value exceeds pattern threshold
          return (issue["metric"] == pattern["metric"] and 
                  issue["value"] > pattern.get("min_value", float("-inf")) and
                  issue["value"] < pattern.get("max_value", float("inf")))
  ```

### 5. Optimization Trigger System

**Purpose:** Executes optimization actions based on analysis results.

**Implementation Details:**
- **Optimization Registry:**
  ```python
  class OptimizationRegistry:
      def __init__(self):
          self.optimizations = {}
          
      def register_optimization(self, name, action_function, required_params):
          self.optimizations[name] = {
              "function": action_function,
              "params": required_params
          }
          
      def get_optimization(self, name):
          return self.optimizations.get(name)
          
      def execute_optimization(self, name, params):
          opt = self.get_optimization(name)
          if not opt:
              return {"error": f"Optimization {name} not found"}
              
          # Validate parameters
          for param in opt["params"]:
              if param not in params:
                  return {"error": f"Missing required parameter: {param}"}
                  
          # Execute optimization
          return opt["function"](params)
  ```

- **Example Optimizations:**
  ```python
  # Pathfinding grid refinement
  def refine_pathfinding_grid(params):
      grid_resolution = params.get("resolution", 1.0)
      scene_path = params["scene_path"]
      
      # Implementation to adjust pathfinding grid resolution
      # This would interact with Unity's NavMesh system
      
      return {
          "status": "success",
          "message": f"Pathfinding grid refined to {grid_resolution} in {scene_path}"
      }
      
  # LOD bias adjustment
  def adjust_lod_bias(params):
      bias = params.get("bias", 1.0)
      
      # Implementation to adjust LOD bias
      # This would modify QualitySettings.lodBias in Unity
      
      return {
          "status": "success",
          "message": f"LOD bias adjusted to {bias}"
      }
      
  # Texture mipmap regeneration
  def regenerate_mipmaps(params):
      textures = params.get("textures", [])
      
      # Implementation to regenerate mipmaps for specified textures
      # This would call texture.GenerateMipMaps() in Unity
      
      return {
          "status": "success",
          "message": f"Regenerated mipmaps for {len(textures)} textures"
      }
  ```

### 6. Feedback Loop System

**Purpose:** Ensures optimizations are effective by re-testing after changes.

**Implementation Details:**
- **Workflow Class:**
  ```python
  class PlaytestFeedbackLoop:
      def __init__(self, test_repository, analysis_engine, optimization_registry):
          self.test_repository = test_repository
          self.analysis_engine = analysis_engine
          self.optimization_registry = optimization_registry
          self.active_loops = {}
          
      def start_feedback_loop(self, test_id):
          test_case = self.test_repository.get_test_case(test_id)
          if not test_case:
              return {"error": "Test case not found"}
              
          loop_id = str(uuid.uuid4())
          self.active_loops[loop_id] = {
              "test_id": test_id,
              "status": "running",
              "iterations": 0,
              "max_iterations": 5,  # Prevent infinite loops
              "history": []
          }
          
          # Start the loop
          self._run_iteration(loop_id)
          
          return {"loop_id": loop_id}
          
      def _run_iteration(self, loop_id):
          loop = self.active_loops.get(loop_id)
          if not loop or loop["status"] != "running":
              return
              
          # Increment iteration counter
          loop["iterations"] += 1
          
          # Run the test
          test_id = loop["test_id"]
          # ... code to execute test ...
          
          # Collect and analyze metrics
          metrics_data = {}  # This would be populated with actual metrics
          analysis = self.analysis_engine.analyze_test_results(test_id, metrics_data)
          
          # Store results
          loop["history"].append({
              "iteration": loop["iterations"],
              "metrics": metrics_data,
              "analysis": analysis
          })
          
          # Check if optimizations are needed
          if analysis["optimizations"]:
              # Execute highest priority optimization
              opt = analysis["optimizations"][0]
              result = self.optimization_registry.execute_optimization(
                  opt["action"]["name"], 
                  opt["action"]["params"]
              )
              
              # Store optimization result
              loop["history"][-1]["optimization"] = {
                  "action": opt["action"]["name"],
                  "result": result
              }
              
              # Continue the loop if we haven't reached max iterations
              if loop["iterations"] < loop["max_iterations"]:
                  # Schedule next iteration
                  # In a real implementation, this would be async
                  self._run_iteration(loop_id)
              else:
                  loop["status"] = "completed_max_iterations"
          else:
              # No more optimizations needed
              loop["status"] = "completed_optimized"
  ```

## Integration with MCP Server

### 1. API Endpoints

```python
@app.route("/api/playtest/start", methods=["POST"])
def start_playtest():
    data = request.json
    test_id = data.get("test_id")
    
    # Validate test exists
    test_case = test_repository.get_test_case(test_id)
    if not test_case:
        return jsonify({"error": "Test case not found"}), 404
        
    # Start feedback loop
    result = feedback_loop.start_feedback_loop(test_id)
    return jsonify(result)

@app.route("/api/playtest/status/<loop_id>", methods=["GET"])
def get_playtest_status(loop_id):
    loop = feedback_loop.active_loops.get(loop_id)
    if not loop:
        return jsonify({"error": "Feedback loop not found"}), 404
        
    return jsonify({
        "loop_id": loop_id,
        "status": loop["status"],
        "iterations": loop["iterations"],
        "test_id": loop["test_id"]
    })

@app.route("/api/metrics", methods=["POST"])
def receive_metrics():
    data = request.json
    test_id = data.get("test_id")
    metrics = data.get("metrics")
    
    # Process metrics
    analysis = analysis_engine.analyze_test_results(test_id, metrics)
    
    # Trigger optimizations if needed
    for opt in analysis["optimizations"]:
        optimization_registry.execute_optimization(
            opt["action"]["name"],
            opt["action"]["params"]
        )
        
    return jsonify({"status": "received"})
```

### 2. WebSocket for Real-time Updates

```python
@socketio.on("connect")
def handle_connect():
    print("Client connected")

@socketio.on("subscribe_playtest")
def handle_subscribe(data):
    loop_id = data.get("loop_id")
    if loop_id in feedback_loop.active_loops:
        join_room(f"playtest_{loop_id}")
        emit("playtest_update", feedback_loop.active_loops[loop_id])

# Emit updates when loop status changes
def emit_loop_update(loop_id):
    loop = feedback_loop.active_loops.get(loop_id)
    if loop:
        socketio.emit("playtest_update", loop, room=f"playtest_{loop_id}")
```

## Unity Integration

### 1. Automated Test Runner

```csharp
public class AutomatedTestRunner : MonoBehaviour
{
    [SerializeField] private string mcpServerUrl = "http://localhost:8000";
    
    public async Task RunTest(string testId)
    {
        // Fetch test case details from MCP
        TestCase testCase = await FetchTestCase(testId);
        
        // Set up scene
        await LoadScene(testCase.scene);
        
        // Attach metrics reporter
        var reporter = gameObject.AddComponent<MetricsReporter>();
        reporter.testId = testId;
        
        // Execute test steps
        foreach (var step in testCase.steps)
        {
            await ExecuteStep(step);
        }
        
        // Verify expected results
        bool success = await VerifyResults(testCase.expectedResults);
        
        // Report test completion
        await ReportTestCompletion(testId, success);
    }
    
    private async Task ExecuteStep(TestStep step)
    {
        switch (step.type)
        {
            case "navigate":
                // Navigate agent to position
                var agent = FindObjectOfType<NavigationAgent>();
                await agent.NavigateTo(step.position);
                break;
                
            case "interact":
                // Interact with object
                var interactable = GameObject.Find(step.targetName)?.GetComponent<IInteractable>();
                if (interactable != null)
                {
                    interactable.Interact();
                }
                break;
                
            // Other step types...
        }
        
        // Wait for specified duration
        await Task.Delay((int)(step.waitTime * 1000));
    }
}
```

### 2. Optimization Receiver

```csharp
public class OptimizationReceiver : MonoBehaviour
{
    [SerializeField] private string mcpServerUrl = "http://localhost:8000";
    private WebSocket webSocket;
    
    void Start()
    {
        ConnectToMCP();
    }
    
    async void ConnectToMCP()
    {
        webSocket = new WebSocket($"{mcpServerUrl}/ws");
        webSocket.OnMessage += HandleMessage;
        await webSocket.Connect();
        
        // Subscribe to optimization channel
        webSocket.Send(JsonUtility.ToJson(new { 
            action = "subscribe", 
            channel = "optimizations" 
        }));
    }
    
    void HandleMessage(string message)
    {
        var data = JsonUtility.FromJson<OptimizationMessage>(message);
        
        switch (data.action)
        {
            case "refine_pathfinding_grid":
                RefinePathfindingGrid(data.parameters);
                break;
                
            case "adjust_lod_bias":
                AdjustLODBias(data.parameters);
                break;
                
            case "regenerate_mipmaps":
                RegenerateMipmaps(data.parameters);
                break;
                
            // Other optimization types...
        }
        
        // Report completion
        ReportOptimizationComplete(data.id);
    }
    
    void RefinePathfindingGrid(OptimizationParameters parameters)
    {
        float resolution = parameters.GetFloat("resolution", 1.0f);
        
        // Adjust NavMesh settings
        NavMesh.pathfindingIterationsPerFrame = Mathf.RoundToInt(100 * resolution);
        
        // Rebuild affected areas
        NavMeshBuilder.BuildNavMesh();
    }
    
    void AdjustLODBias(OptimizationParameters parameters)
    {
        float bias = parameters.GetFloat("bias", 1.0f);
        QualitySettings.lodBias = bias;
    }
    
    void RegenerateMipmaps(OptimizationParameters parameters)
    {
        string[] textureNames = parameters.GetStringArray("textures");
        
        foreach (string textureName in textureNames)
        {
            // Find texture in resources or loaded assets
            Texture2D texture = Resources.Load<Texture2D>(textureName);
            if (texture != null)
            {
                texture.GenerateMipMaps();
                texture.Apply(true);
            }
        }
    }
}
```

## Workflow Sequence

1. **Test Scheduling:**
   - QA_Commander agent schedules tests based on priority and recent changes
   - Tests are queued in the MCP server

2. **Test Execution:**
   - Unity client connects to MCP server and requests test details
   - Test runner executes test steps and collects metrics
   - Metrics are sent to MCP server in real-time

3. **Analysis:**
   - Analysis engine processes metrics and identifies issues
   - Issues are ranked by severity

4. **Optimization:**
   - Optimization actions are triggered based on analysis
   - Unity client receives optimization commands and applies them

5. **Verification:**
   - After optimizations, tests are re-run to verify improvements
   - Process continues until performance meets targets or max iterations reached

6. **Reporting:**
   - Results and optimizations are logged
   - Critical issues that couldn't be automatically resolved are flagged for human review

## Data Flow Diagram

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│             │     │             │     │             │
│    Unity    │◄────┤  MCP Server │◄────┤     QA      │
│   Client    │     │             │     │  Commander  │
│             │─────►             │─────►             │
└─────────────┘     └─────────────┘     └─────────────┘
       │                   │                   │
       │                   │                   │
       ▼                   ▼                   ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│             │     │             │     │             │
│   Metrics   │─────►  Analysis   │─────►Optimization │
│ Collection  │     │   Engine    │     │   Trigger   │
│             │     │             │     │             │
└─────────────┘     └─────────────┘     └─────────────┘
                                               │
                                               │
                                               ▼
                                        ┌─────────────┐
                                        │             │
                                        │  Feedback   │
                                        │    Loop     │
                                        │             │
                                        └─────────────┘
```

## Implementation Timeline

1. **Phase 1: Core Infrastructure**
   - Implement MCP server endpoints for playtest management
   - Create test case repository and data structures
   - Develop basic metric collection system

2. **Phase 2: Analysis Engine**
   - Implement metric analysis algorithms
   - Create optimization rule system
   - Develop pattern matching for issue identification

3. **Phase 3: Unity Integration**
   - Create Unity client for test execution
   - Implement metric reporting from Unity
   - Develop optimization receivers

4. **Phase 4: Feedback Loop**
   - Implement closed-loop testing system
   - Create verification mechanisms
   - Develop adaptive optimization strategies

5. **Phase 5: QA Commander Agent**
   - Implement agent prompt and behavior
   - Create test scheduling algorithms
   - Develop reporting and notification systems

## Conclusion

The Playtest Analysis Loop provides a robust framework for autonomous game optimization without human intervention. By continuously collecting metrics, analyzing performance, and applying targeted optimizations, the system ensures that games maintain optimal performance while adhering to style and quality standards.

This implementation plan outlines the core components, integration points, and workflow sequences needed to create a fully functional autonomous iteration system. The modular design allows for easy extension with new metrics, analysis techniques, and optimization strategies as the project evolves.