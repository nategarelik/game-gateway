# documentation_sentinel_agent.py
# Agent ID: ROO#SUB_PLAN_20250518-170411_S004

import json
import time
import sys
import os

# MCPClient will be imported from the mcp_server package
try:
    from ..mcp_server.client import MCPClient
    print("INFO: Successfully imported MCPClient from mcp_client.py")
except ImportError as e:
    print(f"Warning: Failed to import MCPClient from mcp_client.py: {e}. Using MockMCPClient as fallback.")
    # Define a MockMCPClient if the real one cannot be imported.
    class MCPClient: # Mock class
        def __init__(self, server_url, agent_id): print(f"MockMCPClient initialized for agent {agent_id} targeting server {server_url}")
        def connect(self): print("MockMCPClient: connect() called."); return True
        def disconnect(self): print("MockMCPClient: disconnect() called.")
        def post_event(self, event_type, payload): print(f"MockMCPClient: post_event '{event_type}'. Payload: {json.dumps(payload, indent=1)}"); return True

# Placeholder for SonarSource AI Integration
# import sonarsource_ai_client # Example

class DocumentationMonitor:
    """
    Monitors documentation sources for updates.
    - Unity documentation scraper
    - C# specification tracker
    - Change detection system
    """
    def __init__(self, sources_config):
        self.sources_config = sources_config
        self.last_check_timestamps = {source: None for source in sources_config}
        print("DocumentationMonitor initialized.")

    def check_for_updates(self):
        """
        Checks all configured sources for updates.
        This would involve specific logic for each source (web scraping, API calls, git repo checks).
        """
        print("Checking for documentation updates...")
        updates = []
        for source_name, config in self.sources_config.items():
            print(f"Checking source: {source_name} (URL: {config.get('url', 'N/A')}, Method: {config.get('method', 'N/A')})")
            # Simulate checking and finding an update
            time.sleep(0.1) # Simulate network latency
            if True: # Simulate finding an update
                update_details = {
                    "source": source_name,
                    "type": "api_change", # e.g., api_change, deprecation, new_feature
                    "content_summary": f"New update found in {source_name} documentation.",
                    "raw_content_link": f"{config.get('url', 'N/A')}/latest_change_details.html", # Example link
                    "timestamp": time.time()
                }
                updates.append(update_details)
        if updates:
            print(f"Found {len(updates)} updates.")
        else:
            print("No new updates found.")
        return updates

class CrossReferenceEngine:
    """
    Cross-references technical documentation across multiple sources.
    - Multi-source documentation analyzer
    - Consistency checker
    - Conflict identifier
    """
    def __init__(self):
        print("CrossReferenceEngine initialized.")

    def analyze_and_cross_reference(self, updates, existing_docs_vector_db):
        """
        Analyzes updates and cross-references them with existing documentation.
        This would involve NLP, semantic comparison, etc.
        """
        print(f"Cross-referencing {len(updates)} updates...")
        cross_ref_reports = []
        for update in updates:
            # Simulate analysis
            time.sleep(0.05)
            report = {
                "original_update": update,
                "consistency_check_status": "consistent", # or "inconsistent", "conflict_detected"
                "related_documents": ["doc_id_123", "doc_id_456"], # Example IDs from vector DB
                "potential_impact_areas": ["rendering", "physics"] # Example
            }
            cross_ref_reports.append(report)
        print("Cross-referencing complete.")
        return cross_ref_reports

class SummaryGenerator:
    """
    Generates concise update summaries.
    - Token-constrained content creator
    - Key information extractor
    - Technical language optimizer
    """
    def __init__(self, max_tokens=100):
        self.max_tokens = max_tokens
        print(f"SummaryGenerator initialized with max_tokens: {self.max_tokens}.")

    def generate_summary(self, cross_ref_report):
        """
        Generates a concise summary for an update.
        """
        print(f"Generating summary for update from: {cross_ref_report['original_update']['source']}")
        # Simulate summary generation
        summary = f"Update from {cross_ref_report['original_update']['source']}: {cross_ref_report['original_update']['content_summary'][:50]}... "
        summary += f"Impact: {', '.join(cross_ref_report['potential_impact_areas'])}. "
        summary += f"Status: {cross_ref_report['consistency_check_status']}."
        
        # Enforce token limit (simplified by character limit here)
        if len(summary) > self.max_tokens * 5: # Rough estimation: 1 token ~ 5 chars
            summary = summary[:self.max_tokens*5 - 3] + "..."
        print(f"Generated summary: {summary}")
        return summary

class TriggerConditionEvaluator:
    """
    Evaluates if updates meet predefined trigger conditions.
    - Commit frequency analyzer
    - Deprecation notice detector
    - Community feedback aggregator (placeholder)
    """
    def __init__(self, trigger_config):
        self.trigger_config = trigger_config # e.g., {"api_change_frequency": {"commits_per_day": 2}}
        print("TriggerConditionEvaluator initialized.")

    def evaluate_triggers(self, update_summary, cross_ref_report):
        """
        Evaluates if the update triggers further actions based on defined conditions.
        """
        print(f"Evaluating triggers for update from: {cross_ref_report['original_update']['source']}")
        triggered_actions = []
        update_data = cross_ref_report['original_update']

        # Example trigger: Deprecation notices
        if "deprecation" in update_data.get("type", "").lower() or \
           "deprecated" in update_data.get("content_summary", "").lower():
            if self.trigger_config.get("deprecation_notices", True):
                triggered_actions.append("IMMEDIATE_ALERT_DEPRECATION")
                print("Triggered: IMMEDIATE_ALERT_DEPRECATION")

        # Example trigger: API change frequency (simplified)
        # In a real system, this would involve tracking commit history.
        if update_data.get("type") == "api_change":
            # Simulate high frequency
            if self.trigger_config.get("api_change_frequency", {}).get("commits_per_day", 1) <= 2: # Simulate condition met
                 triggered_actions.append("HIGH_PRIORITY_IMPACT_ANALYSIS")
                 print("Triggered: HIGH_PRIORITY_IMPACT_ANALYSIS")
        
        if not triggered_actions:
            print("No specific triggers met for this update, standard processing.")
            triggered_actions.append("STANDARD_DOCUMENTATION_UPDATE")

        return triggered_actions

class SonarSourceAIIntegration:
    """
    Integrates with SonarSource AI for impact analysis.
    - API connector for impact analysis
    - Code change evaluator
    - Risk assessment system
    """
    def __init__(self, api_key=None):
        self.api_key = api_key
        # self.client = sonarsource_ai_client.SonarSourceClient(api_key=api_key) # Example
        print(f"SonarSourceAIIntegration initialized. API Key {'provided' if api_key else 'not provided'}.")

    def analyze_impact(self, update_details, code_context=None):
        """
        Uses SonarSource AI (or a mock) to analyze the impact of documentation changes.
        """
        print(f"Requesting SonarSource AI impact analysis for update: {update_details['source']}")
        # Simulate API call to SonarSource AI
        time.sleep(0.2) # Simulate network latency
        impact_report = {
            "estimated_risk_level": "medium", # low, medium, high
            "affected_modules": ["module_A", "module_C"], # Example
            "suggested_actions": ["Review API usage in module_A", "Update integration tests for module_C"],
            "confidence_score": 0.85
        }
        print(f"SonarSource AI Impact Analysis complete. Risk: {impact_report['estimated_risk_level']}")
        return impact_report

class DocumentationSentinelAgent:
    """
    The Documentation Sentinel agent core logic.
    Monitors documentation, analyzes changes, generates summaries, and triggers updates.
    """
    AGENT_NAME = "Documentation Sentinel"
    AGENT_ID = "ROO#SUB_PLAN_20250518-170411_S004"

    # Prompt template structure (as per specialized_agent_roles_and_prompt_systems.md)
    PROMPT_TEMPLATE = """
System: You are a technical documentation curator with version control expertise.
- Monitor updates to Unity 2025.3 LTS documentation
- Cross-reference C# 12 language specifications
- Generate concise update summaries (<100 tokens)

Update Triggers:
- API change frequency >2 commits/day
- Deprecation notices in release notes
- Community-reported breaking changes
"""

    def __init__(self, role=None, prompt_template=None, mcp_client_instance=None, config_file_path=None, **kwargs): # Added role, prompt_template, **kwargs
        # role and prompt_template are passed by mcp_server_core during generic instantiation.
        # This agent uses its class-defined AGENT_ID and PROMPT_TEMPLATE.
        # We accept them here to prevent TypeError during server instantiation.
        self.passed_role = role
        self.passed_prompt_template = prompt_template

        print(f"Initializing {self.AGENT_NAME} (ID: {self.AGENT_ID})...")
        
        # Load configuration (e.g., sources to monitor, trigger conditions)
        self.config = self._load_config(config_file_path)

        if mcp_client_instance:
            self.mcp_client = mcp_client_instance
            print(f"MCP Client: Provided externally.")
        else:
            # MCPClient should be available from the module-level import now
            # or it's the MockMCPClient if the import failed.
            mcp_server_url = self.config.get("mcp_server_url", "http://localhost:5001/mcp") # Default if not in config
            try:
                self.mcp_client = MCPClient(server_url=mcp_server_url, agent_id=self.AGENT_ID)
                print(f"MCP Client: Instantiated {type(self.mcp_client).__name__} for {mcp_server_url}.")
                if hasattr(self.mcp_client, 'connect') and callable(self.mcp_client.connect):
                    if not self.mcp_client.connect():
                        print(f"Warning: MCPClient connection failed for {self.AGENT_ID}.")
                else: # This case implies MockMCPClient might not have connect, or MCPClient is None
                    print(f"Warning: Instantiated MCP client of type {type(self.mcp_client).__name__} may not have a connect method or is None.")
            except NameError: # MCPClient was not imported successfully and no mock was defined
                print(f"CRITICAL: MCPClient class not found. MCP communications will fail.")
                self.mcp_client = None
            except Exception as e:
                print(f"Error instantiating or connecting MCPClient for {self.AGENT_ID}: {e}")
                self.mcp_client = None # Ensure it's None if instantiation/connection fails badly
        
        # Initialize components based on design documents
        self.monitor = DocumentationMonitor(self.config.get("documentation_sources", {}))
        self.cross_referencer = CrossReferenceEngine() # Needs vector DB access in a real system
        self.summarizer = SummaryGenerator(max_tokens=self.config.get("summary_max_tokens", 100))
        self.trigger_evaluator = TriggerConditionEvaluator(self.config.get("trigger_conditions", {}))
        self.impact_analyzer = SonarSourceAIIntegration(api_key=self.config.get("sonarsource_api_key"))
        
        # Placeholder for vector database for existing documentation
        self.vector_db = {} # In a real system, this would be a connection to a vector DB
        print(f"{self.AGENT_NAME} initialized successfully.")

    def _load_config(self, config_file_path):
        """Loads agent configuration from a file or uses defaults."""
        default_config = {
            "documentation_sources": {
                "unity_docs": {
                    "url": "https://docs.unity3d.com/2025.3/Documentation/ScriptReference",
                    "method": "rss_feed_and_scraper",
                    "interval_minutes": 15
                },
                "csharp_spec": {
                    "url": "https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/specifications",
                    "method": "git_diff_and_site_check",
                    "interval_minutes": 1440 # Daily
                }
            },
            "mcp_server_url": "http://localhost:5001/mcp", # Default MCP server URL
            "summary_max_tokens": 100,
            "trigger_conditions": {
                "api_change_frequency": {"commits_per_day": 2, "enabled": True},
                "deprecation_notices": True,
                "community_breaking_changes_threshold": 5 # e.g., 5 reports
            },
            "sonarsource_api_key": None, # "YOUR_API_KEY_HERE"
            "main_loop_interval_seconds": 60 # Default interval for the run loop
        }
        if config_file_path:
            try:
                with open(config_file_path, 'r') as f:
                    # Basic merge, real system might need deep merge
                    loaded_config = json.load(f)
                    default_config.update(loaded_config)
                    print(f"Loaded configuration from {config_file_path}")
                    return default_config
            except Exception as e:
                print(f"Warning: Could not load config from {config_file_path}: {e}. Using default config.")
                return default_config
        print("Using default configuration.")
        return default_config

    def get_agent_role_prompt(self):
        """Returns the agent's role-defining prompt."""
        return self.PROMPT_TEMPLATE

    def perform_monitoring_cycle(self):
        """
        Executes one full cycle of monitoring, processing, and reporting.
        """
        print(f"\n--- Starting new monitoring cycle for {self.AGENT_NAME} at {time.ctime()} ---")
        
        # 1. Monitor for updates
        raw_updates = self.monitor.check_for_updates()
        if not raw_updates:
            print("No raw updates found in this cycle.")
            print(f"--- Monitoring cycle for {self.AGENT_NAME} complete ---")
            return []

        # 2. Cross-reference updates
        # In a real system, vector_db would be populated and used
        cross_referenced_reports = self.cross_referencer.analyze_and_cross_reference(raw_updates, self.vector_db)

        processed_notifications = []
        for report in cross_referenced_reports:
            # 3. Generate summary
            summary = self.summarizer.generate_summary(report)
            
            # 4. Evaluate trigger conditions
            triggered_actions = self.trigger_evaluator.evaluate_triggers(summary, report)
            
            # 5. Analyze impact (e.g., if triggered or as part of standard processing)
            impact_analysis_report = None
            if "HIGH_PRIORITY_IMPACT_ANALYSIS" in triggered_actions or \
               self.config.get("always_analyze_impact", False): # Example config flag
                impact_analysis_report = self.impact_analyzer.analyze_impact(report['original_update'])

            # 6. Prepare notification/task for MCP or other systems
            notification = {
                "agent_id": self.AGENT_ID,
                "timestamp": time.time(),
                "source_update": report['original_update'],
                "summary": summary,
                "cross_reference_info": {
                    "status": report["consistency_check_status"],
                    "related_docs": report["related_documents"]
                },
                "triggered_actions": triggered_actions,
                "impact_analysis": impact_analysis_report,
                "priority": "high" if "IMMEDIATE_ALERT_DEPRECATION" in triggered_actions or "HIGH_PRIORITY_IMPACT_ANALYSIS" in triggered_actions else "medium"
            }
            processed_notifications.append(notification)
            
            # 7. Interface with MCP Server
            if self.mcp_client:
                try:
                    success = self.mcp_client.post_event(
                        event_type="documentation_update_notification",
                        payload=notification
                    )
                    if success:
                        print(f"MCP Interaction: Successfully posted 'documentation_update_notification' for {report['original_update']['source']}.")
                    else:
                        print(f"MCP Interaction: Failed to post 'documentation_update_notification' for {report['original_update']['source']}.")
                except Exception as e:
                    print(f"MCP Interaction Error: Could not post event for {report['original_update']['source']}: {e}")
            else:
                print(f"MCP Interaction (No Client): Notification for {report['original_update']['source']} (priority: {notification['priority']}) was prepared but no MCP client is active.")

        print(f"--- Monitoring cycle for {self.AGENT_NAME} complete. Processed {len(processed_notifications)} notifications. ---")
        return processed_notifications

    def handle_direct_request(self, parameters: dict) -> dict:
        """
        Handles a direct API request to the Documentation Sentinel agent.
        Expected parameters: "text" (str), "format" (str, e.g., "markdown").
        """
        print(f"{self.AGENT_NAME}: Handling direct request with parameters: {parameters}")
        input_text = parameters.get("text")
        output_format = parameters.get("format", "markdown") # Default to markdown

        if not input_text:
            print(f"{self.AGENT_NAME}: Error - 'text' parameter is missing.")
            return {"status": "error", "message": "Missing 'text' parameter."}

        # Simulate documentation generation using existing components if applicable,
        # or a simplified direct processing.
        # For this example, let's use a simplified approach.
        # A more complete implementation might use self.summarizer or other components.

        generated_documentation = f"## Documentation ({output_format})\n\n```\n{input_text}\n```\n\nThis documentation was generated by {self.AGENT_NAME}."
        
        if output_format == "plaintext":
            generated_documentation = f"Documentation:\n{input_text}\n\nGenerated by {self.AGENT_NAME}."

        print(f"{self.AGENT_NAME}: Generated documentation for direct request.")
        return {"status": "success", "documentation_text": generated_documentation, "format_requested": output_format}

    def shutdown(self):
        """Gracefully shuts down the agent, disconnecting the MCP client."""
        print(f"Shutting down {self.AGENT_NAME}...")
        if self.mcp_client and hasattr(self.mcp_client, 'disconnect'):
            try:
                self.mcp_client.disconnect()
            except Exception as e:
                print(f"Error during MCPClient disconnect: {e}")
        print(f"{self.AGENT_NAME} shutdown complete.")

    def run(self, single_cycle=False):
        """
        Main loop for the agent.
        """
        print(f"{self.AGENT_NAME} is now running...")
        if single_cycle:
            return self.perform_monitoring_cycle()
        else:
            # In a real deployment, this would be a persistent loop, possibly event-driven
            # or scheduled (e.g., via cron or a scheduler service).
            # For this example, we'll just run a few cycles.
            for i in range(3): # Run 3 cycles for demonstration
                self.perform_monitoring_cycle()
                main_loop_interval = self.config.get('main_loop_interval_seconds', 60)
                print(f"Waiting for next cycle (simulated {main_loop_interval}s)...")
                time.sleep(main_loop_interval) # Use configured interval
            print(f"{self.AGENT_NAME} finished its demonstration run.")


if __name__ == "__main__":
    print("Documentation Sentinel Agent - Standalone Test Run")
    
    # Define task-specific output directory for artifacts like dummy config
    task_artifact_dir = os.path.dirname(__file__) # This script's directory
    if not os.path.exists(task_artifact_dir):
        os.makedirs(task_artifact_dir)

    dummy_config_path = os.path.join(task_artifact_dir, "dummy_sentinel_config.json")

    default_mcp_url = "http://localhost:5001/mcp" # Default for test

    with open(dummy_config_path, 'w') as f:
        json.dump({
            "documentation_sources": {
                "unity_docs_test": {
                    "url": "https://example.com/unity",
                    "method": "test_scraper",
                    "interval_minutes": 1
                },
                "csharp_spec_test": {
                    "url": "https://example.com/csharp",
                    "method": "test_git_check",
                    "interval_minutes": 5
                }
            },
            "mcp_server_url": default_mcp_url,
            "summary_max_tokens": 80,
            "trigger_conditions": {
                "api_change_frequency": {"commits_per_day": 1, "enabled": True},
                "deprecation_notices": True
            },
            "sonarsource_api_key": "TEST_KEY_123",
            "main_loop_interval_seconds": 3 # For quick demo cycles
        }, f, indent=2)

    # Initialize the agent. It will create its own MCPClient if MCPClient is available.
    # No need to pass mcp_client_instance for this test if we want the agent to manage it.
    sentinel_agent = DocumentationSentinelAgent(config_file_path=dummy_config_path)
    
    try:
        # Print role prompt
        print("\nAgent Role Prompt:")
        print(sentinel_agent.get_agent_role_prompt())
        
        # Run a few cycles as per agent's run() method
        sentinel_agent.run(single_cycle=False)
        
        # Example of running a single explicit cycle and getting results
        # print("\n--- Running a single explicit cycle ---")
        # single_cycle_results = sentinel_agent.perform_monitoring_cycle()
        # if single_cycle_results:
        #     print(f"\nResults from single cycle ({len(single_cycle_results)} notifications):")
        #     for res_idx, res_item in enumerate(single_cycle_results):
        #         print(f"Notification {res_idx + 1}:")
        #         print(json.dumps(res_item, indent=2))
        # else:
        #     print("No notifications from the single cycle.")

    except KeyboardInterrupt:
        print("\nUser interrupted execution.")
    finally:
        if sentinel_agent:
            sentinel_agent.shutdown()

    print("\nDocumentation Sentinel Agent - Standalone Test Run Complete.")