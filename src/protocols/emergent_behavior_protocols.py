# src/protocols/emergent_behavior_protocols.py
import logging
from typing import List, Dict, Any, Optional, Callable

logger = logging.getLogger(__name__)

# --- Conceptual Data Structures ---

class DesignProposal:
    """Represents a design proposal from an agent."""
    def __init__(self, proposal_id: str, agent_id: str, target_element_id: str, proposed_design: Dict[str, Any], confidence: float = 1.0, priority: int = 0):
        self.proposal_id = proposal_id
        self.agent_id = agent_id
        self.target_element_id = target_element_id # e.g., "level_01_puzzle_area", "character_enemy_grunt_texture"
        self.proposed_design = proposed_design # e.g., {"layout_type": "open", "difficulty": "medium"} or {"color_palette": ["#..."]}
        self.confidence = confidence # Agent's confidence in this proposal (0.0 to 1.0)
        self.priority = priority # Agent-assigned priority (higher means more important)

class Tool:
    """Represents an available tool or capability an agent can use."""
    def __init__(self, tool_id: str, name: str, capabilities: List[str], parameters: Dict[str, Any]):
        self.tool_id = tool_id
        self.name = name
        self.capabilities = capabilities # e.g., ["generate_texture", "analyze_layout"]
        self.parameters = parameters # Describes parameters the tool accepts

    async def execute(self, execution_params: Dict[str, Any], agent_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Placeholder for tool execution. Returns a mock result."""
        logger.info(f"Tool '{self.name}' (ID: {self.tool_id}) conceptually executing with params: {execution_params}")
        await asyncio.sleep(0.1) # Simulate work
        return {"status": "success_mock", "tool_id": self.tool_id, "result_summary": f"Mock result for {self.name}."}

# --- Core Protocol Components (Conceptual Implementations) ---

class CreativeConflictResolver:
    """
    Handles conflicts when multiple agents propose different designs for the same element.
    """
    def __init__(self, mcp_event_notifier: Optional[Callable] = None):
        """
        Args:
            mcp_event_notifier: A (conceptual) callable to notify MCP/human about unresolved conflicts.
                                e.g., async def notify(event_type: str, data: dict)
        """
        self.mcp_event_notifier = mcp_event_notifier
        logger.info("CreativeConflictResolver initialized.")

    async def resolve_conflicting_proposals(self, proposals: List[DesignProposal], target_element_id: str) -> Optional[DesignProposal]:
        """
        Resolves conflicts between multiple design proposals for the same target element.

        Args:
            proposals: A list of DesignProposal objects for the same target_element_id.
            target_element_id: The ID of the element being designed.

        Returns:
            The winning DesignProposal, or None if conflict cannot be resolved automatically
            (in which case an event might be flagged for human review).
        """
        if not proposals:
            logger.warning(f"No proposals provided for conflict resolution on element '{target_element_id}'.")
            return None
        if len(proposals) == 1:
            return proposals[0]

        logger.info(f"Resolving {len(proposals)} conflicting proposals for element '{target_element_id}'.")

        # Simple Priority-based Resolution (Placeholder)
        # Sort by priority (descending), then by confidence (descending)
        # In a real system, this could involve voting, merging, or more complex logic.
        sorted_proposals = sorted(proposals, key=lambda p: (p.priority, p.confidence), reverse=True)
        
        winning_proposal = sorted_proposals[0]
        logger.info(f"Winning proposal for '{target_element_id}' is '{winning_proposal.proposal_id}' from agent '{winning_proposal.agent_id}' (Priority: {winning_proposal.priority}, Confidence: {winning_proposal.confidence}).")

        # Check if there's a significant tie or low confidence that might need human review
        if len(sorted_proposals) > 1:
            runner_up = sorted_proposals[1]
            if winning_proposal.priority == runner_up.priority and \
               abs(winning_proposal.confidence - runner_up.confidence) < 0.1: # Arbitrary small confidence diff
                logger.warning(f"Close conflict between proposals '{winning_proposal.proposal_id}' and '{runner_up.proposal_id}' for '{target_element_id}'. Flagging for review.")
                if self.mcp_event_notifier:
                    await self.mcp_event_notifier(
                        event_type="creative_conflict_review_needed",
                        data={
                            "target_element_id": target_element_id,
                            "proposals": [p.__dict__ for p in sorted_proposals[:2]], # Send top 2 for review
                            "resolution_method": "priority_confidence_tie"
                        }
                    )
                # Depending on policy, could return None or still return the top one. For now, return top.
        
        return winning_proposal


class DynamicToolComposer:
    """
    Conceptually allows an agent to decide a sequence of tools to use based on task state.
    This is a highly simplified placeholder. A real implementation would involve
    planning, state representation, and a more robust tool interaction model.
    """
    def __init__(self, available_tools: List[Tool]):
        self.available_tools_map: Dict[str, Tool] = {tool.tool_id: tool for tool in available_tools}
        logger.info(f"DynamicToolComposer initialized with {len(self.available_tools_map)} tools.")

    async def compose_and_execute_tool_sequence(self, task_goal: str, initial_state: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Placeholder for composing and executing a sequence of tools.

        Args:
            task_goal: A description of the overall goal (e.g., "generate_detailed_forest_texture").
            initial_state: Current state relevant to the task.

        Returns:
            A list of results from each tool executed in the sequence.
        """
        logger.info(f"DynamicToolComposer attempting to achieve goal: '{task_goal}' from state: {initial_state}")
        results_sequence = []
        current_state = initial_state.copy()

        # --- Highly Simplified Placeholder Logic ---
        # If goal is "generate_detailed_forest_texture":
        # 1. Use a "concept_generator_tool" (if available) to get keywords.
        # 2. Use a "texture_generator_tool" with those keywords.
        # 3. Use a "detail_enhancer_tool" on the generated texture.

        if "generate_detailed_forest_texture" in task_goal.lower():
            # Step 1: Conceptualize (mock)
            concept_tool_id = next((tid for tid, t in self.available_tools_map.items() if "concept_generation" in t.capabilities), None)
            if concept_tool_id:
                concept_tool = self.available_tools_map[concept_tool_id]
                concept_params = {"prompt": "forest texture elements", "num_keywords": 3}
                logger.info(f"DTC Step 1: Using tool '{concept_tool.name}' for conceptualization.")
                concept_result = await concept_tool.execute(concept_params)
                results_sequence.append(concept_result)
                # Mock: Assume result contains keywords
                current_state["keywords"] = concept_result.get("keywords", ["mossy", "bark", "dappled_light"]) 
            else:
                logger.warning("DTC: Concept generation tool not found for forest texture goal.")
                current_state["keywords"] = ["generic_forest", "green", "brown"] # Fallback

            # Step 2: Generate Texture (mock)
            texture_tool_id = next((tid for tid, t in self.available_tools_map.items() if "generate_texture" in t.capabilities), None)
            if texture_tool_id:
                texture_tool = self.available_tools_map[texture_tool_id]
                texture_params = {"prompt": f"{', '.join(current_state['keywords'])} texture", "resolution": "512x512"}
                logger.info(f"DTC Step 2: Using tool '{texture_tool.name}' for texture generation.")
                texture_result = await texture_tool.execute(texture_params)
                results_sequence.append(texture_result)
                current_state["base_texture_id"] = texture_result.get("asset_id", "mock_texture_123")
            else:
                logger.error("DTC: Texture generation tool not found! Cannot proceed with forest texture goal.")
                return results_sequence # Abort

            # Step 3: Enhance Detail (mock)
            enhancer_tool_id = next((tid for tid, t in self.available_tools_map.items() if "enhance_detail" in t.capabilities), None)
            if enhancer_tool_id:
                enhancer_tool = self.available_tools_map[enhancer_tool_id]
                enhancer_params = {"source_asset_id": current_state["base_texture_id"], "enhancement_level": "high"}
                logger.info(f"DTC Step 3: Using tool '{enhancer_tool.name}' for detail enhancement.")
                enhancer_result = await enhancer_tool.execute(enhancer_params)
                results_sequence.append(enhancer_result)
            else:
                logger.warning("DTC: Detail enhancement tool not found for forest texture goal.")
        else:
            logger.warning(f"DTC: No specific tool composition logic for goal: '{task_goal}'.")

        logger.info(f"DynamicToolComposer finished for goal '{task_goal}'. Executed {len(results_sequence)} tools.")
        return results_sequence


# --- Example Usage ---
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    async def mock_mcp_notify(event_type: str, data: dict):
        logger.info(f"[MockMCPNotifier] Event: {event_type}, Data: {data}")

    # Creative Conflict Resolution Example
    resolver = CreativeConflictResolver(mcp_event_notifier=mock_mcp_notify)
    proposals = [
        DesignProposal("propA1", "AgentAlpha", "puzzle_01", {"difficulty": "hard", "theme": "crystal"}, priority=1, confidence=0.9),
        DesignProposal("propB1", "AgentBeta", "puzzle_01", {"difficulty": "medium", "theme": "crystal", "hint_system": True}, priority=2, confidence=0.85),
        DesignProposal("propC1", "AgentGamma", "puzzle_01", {"difficulty": "medium", "theme": "ancient_crystal", "hint_system": True}, priority=2, confidence=0.82), # Close to B1
    ]
    
    async def run_conflict_resolution():
        print("\n--- Creative Conflict Resolution Example ---")
        winning = await resolver.resolve_conflicting_proposals(proposals, "puzzle_01")
        if winning:
            print(f"Resolved winning proposal for puzzle_01: {winning.proposal_id} from {winning.agent_id}")
        else:
            print("Conflict resolution for puzzle_01 resulted in no single winner (or needs review).")

    # Dynamic Tool Composition Example
    mock_tools = [
        Tool("tool_concept", "Concept Generator", ["concept_generation"], {"prompt": "str", "num_keywords": "int"}),
        Tool("tool_texture", "Texture Generator", ["generate_texture"], {"prompt": "str", "resolution": "str"}),
        Tool("tool_detail", "Detail Enhancer", ["enhance_detail"], {"source_asset_id": "str", "enhancement_level": "str"}),
        Tool("tool_analyze", "Layout Analyzer", ["analyze_layout"], {"layout_data": "dict"}),
    ]
    composer = DynamicToolComposer(available_tools=mock_tools)

    async def run_tool_composition():
        print("\n--- Dynamic Tool Composition Example ---")
        goal = "generate_detailed_forest_texture"
        initial_state = {"project_style": "fantasy_realistic"}
        tool_results = await composer.compose_and_execute_tool_sequence(goal, initial_state)
        print(f"Tool composition for '{goal}' yielded {len(tool_results)} results:")
        for i, res in enumerate(tool_results):
            print(f"  Result {i+1}: {res.get('result_summary', 'No summary')}")

    async def main_demo():
        await run_conflict_resolution()
        await run_tool_composition()

    asyncio.run(main_demo())