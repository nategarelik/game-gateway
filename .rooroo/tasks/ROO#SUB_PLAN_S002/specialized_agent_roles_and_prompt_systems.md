# Specialized Agent Roles & Prompt Systems

This document outlines the structure, core responsibilities, prompt templates, and implementation components for three specialized agent types in the Unity Agent system: Level Architect, Pixel Forge, and Documentation Sentinel.

## 1. Level Architect Agent

### Core Responsibilities
- Reconstruct virtual environments from reference images with high dimensional accuracy (±2%)
- Maintain architectural coherence across all scene elements
- Generate UV maps optimized for retro pixel art pipelines
- Assemble real-time scenes using Unity Muse

### Prompt Template Structure & Role Enforcement
The Level Architect's prompt template enforces its specialized role through:

```text
System: You are a virtual environment architect specializing in residential spaces.  
- Reconstruct layouts from reference images with ±2% dimensional accuracy  
- Maintain architectural coherence across all scene elements  
- Generate UV maps optimized for retro pixel art pipelines  

User Input:  
{  
  "reference_image": "family_home_1985.jpg",  
  "style_constraints": "32-color palette (hex codes: #1A1C2C, #E6A272)",  
  "interactive_elements": ["lights", "doors", "secret_passages"]  
}  
```

**Role Enforcement Mechanisms:**
1. **Identity Framing**: Establishes the agent as a "virtual environment architect" with a specialty in "residential spaces"
2. **Precision Requirements**: Sets specific accuracy standards (±2% dimensional accuracy)
3. **Technical Constraints**: Requires optimization for "retro pixel art pipelines"
4. **Structured Input Format**: Uses JSON format with specific fields for reference images, style constraints, and interactive elements
5. **Integration Point**: "Utilizes Unity Muse for real-time scene assembly"

### Implementation Components
1. **Reference Image Processor**
   - Image analysis module for extracting dimensional data
   - Spatial relationship mapper for architectural elements

2. **Architectural Coherence Engine**
   - Style consistency validator
   - Element relationship verification system

3. **UV Map Generator**
   - Retro pixel art optimization algorithms
   - Texture mapping system for low-resolution assets

4. **Unity Muse Integration Layer**
   - API connectors for real-time scene assembly
   - Asset pipeline for transferring generated elements to Unity

5. **Input Parser & Validator**
   - JSON schema validator for user inputs
   - Error handling for malformed requests

## 2. Pixel Forge Agent

### Core Responsibilities
- Generate retro pixel art assets with specific resolution and color palette constraints
- Create animation frames for interactive elements
- Define collision meshes and hitboxes for game objects
- Maintain style consistency using FLUX architecture
- Assemble and organize sprite sheets

### Prompt Template Structure & Role Enforcement
The Pixel Forge's prompt system consists of two main components:

1. **Retro Diffusion Generation Protocol:**
```text
Prompt: Retro Pixel, Isometric view of Victorian-style door  
- 64x64 resolution  
- 8-color palette: #2D1B2E, #87758F, #E6A272  
- Animation frames: 8 (open/close cycle)  
- Collision mesh: 16x32 pixel hitbox  

Negative Prompt:  
Modern design elements, anti-aliasing, >32 colors  
```

2. **Sprite Sheet Assembly Workflow:**
```text
graph TD  
A[Concept Sketch] --> B{MCP StyleCheck}  
B -->|Approved| C[Generate 8 Directions]  
B -->|Rejected| D[Regenerate via RD_FLUX]  
C --> E[Batch Process Hitboxes]  
```

**Role Enforcement Mechanisms:**
1. **Technical Specificity**: Precise resolution, color palette, and animation frame requirements
2. **Negative Constraints**: Explicit exclusion of modern design elements and techniques
3. **Process Flow Definition**: Structured workflow with decision points and alternative paths
4. **Quality Control Integration**: MCP StyleCheck validation step
5. **Specialized Terminology**: References to "RD_FLUX" architecture and "Batch Process Hitboxes"

### Implementation Components
1. **Retro Diffusion Generator**
   - Resolution-constrained image generator
   - Color palette enforcer
   - Anti-aliasing prevention system

2. **Animation Frame Sequencer**
   - Cycle definition engine
   - Frame consistency validator
   - Animation preview renderer

3. **Collision System**
   - Hitbox generator and editor
   - Collision mesh optimizer
   - Physics interaction tester

4. **FLUX Architecture Integration**
   - Style consistency enforcement
   - Asset regeneration pipeline
   - Version control for iterative improvements

5. **Sprite Sheet Assembler**
   - Multi-directional view generator
   - Batch processing system for hitboxes
   - Export system for game engine compatibility

6. **MCP StyleCheck System**
   - Automated style validation
   - Feedback generation for rejected assets
   - Approval workflow management

## 3. Documentation Sentinel

### Core Responsibilities
- Monitor updates to Unity documentation and C# language specifications
- Cross-reference technical documentation across multiple sources
- Generate concise update summaries
- Analyze impact of changes using SonarSource AI
- Trigger updates based on specific conditions

### Prompt Template Structure & Role Enforcement
The Documentation Sentinel's prompt template enforces its specialized role through:

```text
System: You are a technical documentation curator with version control expertise.  
- Monitor updates to Unity 2025.3 LTS documentation  
- Cross-reference C# 12 language specifications  
- Generate concise update summaries (<100 tokens)  

Update Triggers:  
- API change frequency >2 commits/day  
- Deprecation notices in release notes  
- Community-reported breaking changes  
```

**Role Enforcement Mechanisms:**
1. **Expert Identity**: Positions the agent as a "technical documentation curator with version control expertise"
2. **Specific Technology Focus**: Targets "Unity 2025.3 LTS documentation" and "C# 12 language specifications"
3. **Output Constraints**: Requires "concise update summaries (<100 tokens)"
4. **Trigger Conditions**: Defines specific conditions that warrant updates
5. **Integration Point**: "Uses SonarSource AI for impact analysis"

### Implementation Components
1. **Documentation Monitor**
   - Unity documentation scraper
   - C# specification tracker
   - Change detection system

2. **Cross-Reference Engine**
   - Multi-source documentation analyzer
   - Consistency checker
   - Conflict identifier

3. **Summary Generator**
   - Token-constrained content creator
   - Key information extractor
   - Technical language optimizer

4. **Trigger Condition Evaluator**
   - Commit frequency analyzer
   - Deprecation notice detector
   - Community feedback aggregator

5. **SonarSource AI Integration**
   - API connector for impact analysis
   - Code change evaluator
   - Risk assessment system

## Integration Architecture for Prompt Systems

To effectively implement and integrate these specialized agent prompt systems, the following components are required:

### 1. Prompt Template Manager
- Storage and versioning of prompt templates
- Template validation and testing
- Dynamic template modification capabilities

### 2. Role-Based Access Control
- Agent role definition and enforcement
- Permission boundaries for different agent types
- Cross-role collaboration protocols

### 3. Input/Output Standardization
- Common data formats for inter-agent communication
- Transformation layers for specialized data types
- Validation systems for inputs and outputs

### 4. Integration Middleware
- Unity Muse connector
- FLUX architecture integration
- SonarSource AI API client

### 5. Monitoring and Evaluation System
- Agent performance metrics
- Output quality assessment
- Role adherence verification

### 6. Feedback Loop Mechanism
- User feedback collection
- Automated performance analysis
- Prompt template refinement process

## Implementation Roadmap

1. **Phase 1: Prompt Template Development**
   - Finalize core prompt templates for each agent type
   - Develop validation systems for template effectiveness
   - Create template versioning system

2. **Phase 2: Agent Core Implementation**
   - Develop specialized processing modules for each agent
   - Implement role-specific constraints and capabilities
   - Create testing framework for agent outputs

3. **Phase 3: Integration Systems**
   - Build connectors for Unity Muse, FLUX, and SonarSource AI
   - Develop inter-agent communication protocols
   - Implement shared resource management

4. **Phase 4: Validation and Refinement**
   - Test agent performance against benchmark tasks
   - Refine prompt templates based on output quality
   - Optimize integration points for efficiency

5. **Phase 5: Deployment and Monitoring**
   - Deploy agents in production environment
   - Implement monitoring systems for ongoing performance
   - Establish feedback collection and improvement processes