# Code Weaver Agent

The Code Weaver Agent is a specialized AI agent responsible for generating and implementing C# scripts for Unity game development. It focuses on programming, scripting, and code-related tasks.

## Overview

The Code Weaver Agent can:

- Generate new C# scripts based on descriptions
- Implement game mechanics and behaviors
- Refactor and optimize existing code
- Create UI interactions and systems
- Generate code documentation

## Usage in Unity

### Accessing the Agent

1. Ensure the MCP server is running
2. In Unity, open Window > Unity Agent MCP > Agent Interface
3. Select "Code Weaver" from the agent dropdown
4. Enter your prompt in the text area
5. Click "Send to Agent"

### Prompt Examples

#### Generating a New Script

```
Create a player controller script that allows WASD movement, jumping with spacebar, and a dash ability with shift. Include adjustable parameters for movement speed, jump height, and dash distance.
```

#### Implementing a Game Mechanic

```
Implement a health system with regeneration. The player should have a maximum health of 100, take damage when colliding with enemies, and regenerate 1 health point every 2 seconds when not taking damage for 5 seconds.
```

#### Refactoring Existing Code

```
Refactor the PlayerMovement.cs script to use the new Input System instead of the legacy Input manager. Maintain the same functionality but improve code organization and readability.
```

#### Creating UI Interactions

```
Create a script for an inventory system UI. It should display items in a grid, allow dragging and dropping items between slots, and show item details on hover.
```

## Technical Details

### Agent Architecture

The Code Weaver Agent follows the standard agent architecture:

1. It inherits from the `BaseAgent` class
2. It defines prompt templates for different code-related tasks
3. It processes tasks through the `process_task` method
4. It communicates with the MCP server to receive requests and send responses

### Prompt Templates

The agent uses several prompt templates for different types of code generation tasks:

- **Script Generation**: For creating new scripts from scratch
- **Feature Implementation**: For implementing specific features or mechanics
- **Code Refactoring**: For refactoring and optimizing existing code
- **UI Implementation**: For creating UI-related scripts
- **Documentation Generation**: For generating code documentation

### Code Generation Process

When the Code Weaver Agent receives a request:

1. It analyzes the prompt to understand the requirements
2. It determines the appropriate script structure and patterns to use
3. It generates the C# code, including:
   - Namespace and using directives
   - Class declaration
   - Fields and properties
   - Methods and event handlers
   - Comments and documentation
4. It validates the generated code for syntax errors and best practices
5. It returns the code along with placement instructions

### Integration with Unity

The Code Weaver Agent integrates with Unity through:

1. The Unity Editor window for submitting requests
2. The MCP server for processing requests
3. The Unity file system for creating and modifying script files

## Best Practices

### Writing Effective Prompts

For best results with the Code Weaver Agent:

1. **Be Specific**: Clearly describe the functionality you want
2. **Provide Context**: Mention relevant game objects, systems, or existing scripts
3. **Specify Requirements**: Include performance considerations, coding standards, or architectural patterns
4. **Reference Examples**: Mention similar mechanics or patterns from other games
5. **Include Parameters**: Specify adjustable parameters and their default values

### Example of a Good Prompt

```
Create an enemy AI controller script that:
- Patrols between waypoints using NavMeshAgent
- Detects the player within a 10-meter radius using Physics.OverlapSphere
- Chases the player when detected
- Attacks when within 2 meters of the player
- Returns to patrolling if the player escapes beyond detection range for 5 seconds

Include adjustable parameters for:
- Patrol speed (default: 3)
- Chase speed (default: 5)
- Detection radius (default: 10)
- Attack range (default: 2)
- Attack cooldown (default: 1.5 seconds)
- Chase timeout (default: 5 seconds)

The script should work with the existing GameManager.cs which has an "OnEnemyAttack" event.
```

### Example of a Poor Prompt

```
Make an enemy AI script.
```

## Advanced Usage

### Generating Multiple Scripts

You can request the generation of multiple related scripts in a single prompt:

```
Create a weapon system with the following scripts:
1. Weapon.cs - A base class for all weapons
2. Gun.cs - Inherits from Weapon, implements shooting mechanics
3. Melee.cs - Inherits from Weapon, implements melee attack mechanics
4. WeaponManager.cs - Manages weapon switching and inventory

Each script should follow the component-based design pattern and integrate with the existing PlayerController.cs.
```

### Modifying Existing Scripts

To modify an existing script, provide the script name and describe the changes:

```
Modify the PlayerController.cs script to add a crouch mechanic. The player should move at half speed while crouching and have a reduced collider height. Crouching should be toggled with the C key.
```

### Generating Editor Scripts

You can request the generation of Unity Editor scripts:

```
Create a custom editor script for the LevelGenerator.cs class. The editor should display a button to generate a random level, sliders for room size and count parameters, and a preview of the generated level in the scene view.
```

## Troubleshooting

### Common Issues

#### Script Doesn't Compile

If the generated script doesn't compile:

1. Check the Unity Console for specific error messages
2. Request a fix from the Code Weaver Agent by describing the error
3. Ensure all referenced scripts and components exist in your project

#### Script Doesn't Work as Expected

If the script compiles but doesn't work as expected:

1. Check that the script is attached to the correct GameObject
2. Verify that all required components are present
3. Check the Unity Console for runtime errors
4. Request a modification from the Code Weaver Agent

#### Agent Doesn't Understand the Request

If the agent doesn't understand your request:

1. Rephrase your prompt to be more specific
2. Break down complex requests into smaller, more focused requests
3. Provide more context about your project and requirements

## Examples

### Player Controller Script

Request:
```
Create a first-person controller script with smooth movement, camera look controls, and the ability to sprint and jump.
```

Response:
```csharp
using UnityEngine;

public class FirstPersonController : MonoBehaviour
{
    [Header("Movement Settings")]
    [SerializeField] private float walkSpeed = 5f;
    [SerializeField] private float sprintSpeed = 10f;
    [SerializeField] private float jumpForce = 5f;
    [SerializeField] private float gravity = -9.81f;
    
    [Header("Look Settings")]
    [SerializeField] private float mouseSensitivity = 2f;
    [SerializeField] private float lookXLimit = 90f;
    
    [Header("References")]
    [SerializeField] private Transform cameraTransform;
    
    private CharacterController characterController;
    private Vector3 moveDirection = Vector3.zero;
    private float rotationX = 0f;
    private bool canMove = true;
    
    private void Awake()
    {
        characterController = GetComponent<CharacterController>();
        
        // Lock and hide cursor
        Cursor.lockState = CursorLockMode.Locked;
        Cursor.visible = false;
    }
    
    private void Update()
    {
        if (!canMove) return;
        
        // Handle movement
        HandleMovement();
        
        // Handle camera rotation
        HandleCameraRotation();
    }
    
    private void HandleMovement()
    {
        // Calculate movement direction
        Vector3 forward = transform.TransformDirection(Vector3.forward);
        Vector3 right = transform.TransformDirection(Vector3.right);
        
        // Determine if sprinting
        bool isSprinting = Input.GetKey(KeyCode.LeftShift);
        float speed = isSprinting ? sprintSpeed : walkSpeed;
        
        // Calculate input direction
        float verticalInput = Input.GetAxis("Vertical");
        float horizontalInput = Input.GetAxis("Horizontal");
        
        // Calculate movement
        float moveDirectionY = moveDirection.y;
        moveDirection = (forward * verticalInput + right * horizontalInput).normalized;
        
        // Apply speed
        moveDirection *= speed;
        
        // Handle jumping
        if (characterController.isGrounded)
        {
            moveDirection.y = 0f;
            
            if (Input.GetButtonDown("Jump"))
            {
                moveDirection.y = jumpForce;
            }
        }
        
        // Apply gravity
        moveDirection.y += gravity * Time.deltaTime;
        
        // Move the controller
        characterController.Move(moveDirection * Time.deltaTime);
    }
    
    private void HandleCameraRotation()
    {
        // Get mouse input
        float mouseX = Input.GetAxis("Mouse X") * mouseSensitivity;
        float mouseY = Input.GetAxis("Mouse Y") * mouseSensitivity;
        
        // Rotate camera up/down
        rotationX -= mouseY;
        rotationX = Mathf.Clamp(rotationX, -lookXLimit, lookXLimit);
        cameraTransform.localRotation = Quaternion.Euler(rotationX, 0f, 0f);
        
        // Rotate player left/right
        transform.rotation *= Quaternion.Euler(0f, mouseX, 0f);
    }
    
    public void SetCanMove(bool value)
    {
        canMove = value;
        
        if (!canMove)
        {
            moveDirection = Vector3.zero;
        }
    }
}
```

### Enemy AI Script

Request:
```
Create an enemy AI that patrols between waypoints and chases the player when detected.
```

Response:
```csharp
using System.Collections;
using UnityEngine;
using UnityEngine.AI;

public class EnemyAI : MonoBehaviour
{
    [Header("Patrol Settings")]
    [SerializeField] private Transform[] waypoints;
    [SerializeField] private float patrolSpeed = 3f;
    [SerializeField] private float waypointWaitTime = 1f;
    
    [Header("Detection Settings")]
    [SerializeField] private float detectionRadius = 10f;
    [SerializeField] private LayerMask playerLayer;
    [SerializeField] private float chaseSpeed = 5f;
    [SerializeField] private float losePlayerTimeout = 5f;
    
    [Header("Attack Settings")]
    [SerializeField] private float attackRange = 2f;
    [SerializeField] private float attackCooldown = 1.5f;
    [SerializeField] private int attackDamage = 10;
    
    private NavMeshAgent agent;
    private Transform player;
    private int currentWaypointIndex = 0;
    private bool isChasing = false;
    private bool isAttacking = false;
    private float losePlayerTimer = 0f;
    private float lastAttackTime = 0f;
    
    private enum EnemyState
    {
        Patrolling,
        Chasing,
        Attacking
    }
    
    private EnemyState currentState;
    
    private void Awake()
    {
        agent = GetComponent<NavMeshAgent>();
        player = GameObject.FindGameObjectWithTag("Player").transform;
        currentState = EnemyState.Patrolling;
    }
    
    private void Start()
    {
        if (waypoints.Length > 0)
        {
            agent.SetDestination(waypoints[currentWaypointIndex].position);
        }
        else
        {
            Debug.LogWarning("No waypoints assigned to enemy AI.");
        }
    }
    
    private void Update()
    {
        switch (currentState)
        {
            case EnemyState.Patrolling:
                Patrol();
                DetectPlayer();
                break;
                
            case EnemyState.Chasing:
                ChasePlayer();
                CheckAttackRange();
                CheckLosePlayer();
                break;
                
            case EnemyState.Attacking:
                Attack();
                break;
        }
    }
    
    private void Patrol()
    {
        if (waypoints.Length == 0) return;
        
        agent.speed = patrolSpeed;
        
        // Check if we've reached the waypoint
        if (!agent.pathPending && agent.remainingDistance < 0.5f)
        {
            StartCoroutine(WaitAtWaypoint());
        }
    }
    
    private IEnumerator WaitAtWaypoint()
    {
        agent.isStopped = true;
        yield return new WaitForSeconds(waypointWaitTime);
        agent.isStopped = false;
        
        // Move to next waypoint
        currentWaypointIndex = (currentWaypointIndex + 1) % waypoints.Length;
        agent.SetDestination(waypoints[currentWaypointIndex].position);
    }
    
    private void DetectPlayer()
    {
        Collider[] hitColliders = Physics.OverlapSphere(transform.position, detectionRadius, playerLayer);
        
        if (hitColliders.Length > 0)
        {
            // Player detected
            currentState = EnemyState.Chasing;
            isChasing = true;
        }
    }
    
    private void ChasePlayer()
    {
        agent.speed = chaseSpeed;
        agent.SetDestination(player.position);
    }
    
    private void CheckAttackRange()
    {
        float distanceToPlayer = Vector3.Distance(transform.position, player.position);
        
        if (distanceToPlayer <= attackRange)
        {
            currentState = EnemyState.Attacking;
            agent.isStopped = true;
        }
    }
    
    private void CheckLosePlayer()
    {
        Collider[] hitColliders = Physics.OverlapSphere(transform.position, detectionRadius, playerLayer);
        
        if (hitColliders.Length == 0)
        {
            // Player not in detection radius
            losePlayerTimer += Time.deltaTime;
            
            if (losePlayerTimer >= losePlayerTimeout)
            {
                // Lost the player
                losePlayerTimer = 0f;
                isChasing = false;
                currentState = EnemyState.Patrolling;
                
                // Return to nearest waypoint
                if (waypoints.Length > 0)
                {
                    float minDistance = float.MaxValue;
                    int nearestWaypointIndex = 0;
                    
                    for (int i = 0; i < waypoints.Length; i++)
                    {
                        float distance = Vector3.Distance(transform.position, waypoints[i].position);
                        if (distance < minDistance)
                        {
                            minDistance = distance;
                            nearestWaypointIndex = i;
                        }
                    }
                    
                    currentWaypointIndex = nearestWaypointIndex;
                    agent.SetDestination(waypoints[currentWaypointIndex].position);
                }
            }
        }
        else
        {
            // Player still in detection radius
            losePlayerTimer = 0f;
        }
    }
    
    private void Attack()
    {
        transform.LookAt(new Vector3(player.position.x, transform.position.y, player.position.z));
        
        float distanceToPlayer = Vector3.Distance(transform.position, player.position);
        
        if (distanceToPlayer > attackRange)
        {
            // Player moved out of attack range
            agent.isStopped = false;
            currentState = EnemyState.Chasing;
            return;
        }
        
        // Attack logic
        if (Time.time >= lastAttackTime + attackCooldown)
        {
            lastAttackTime = Time.time;
            
            // Perform attack
            PlayerHealth playerHealth = player.GetComponent<PlayerHealth>();
            if (playerHealth != null)
            {
                playerHealth.TakeDamage(attackDamage);
            }
            
            // Notify game manager
            if (GameManager.Instance != null)
            {
                GameManager.Instance.OnEnemyAttack(gameObject, player.gameObject);
            }
        }
    }
    
    private void OnDrawGizmosSelected()
    {
        // Draw detection radius
        Gizmos.color = Color.yellow;
        Gizmos.DrawWireSphere(transform.position, detectionRadius);
        
        // Draw attack range
        Gizmos.color = Color.red;
        Gizmos.DrawWireSphere(transform.position, attackRange);
        
        // Draw waypoint connections
        if (waypoints.Length > 0)
        {
            Gizmos.color = Color.blue;
            for (int i = 0; i < waypoints.Length; i++)
            {
                if (waypoints[i] != null)
                {
                    Vector3 position = waypoints[i].position;
                    Gizmos.DrawSphere(position, 0.3f);
                    
                    // Draw line to next waypoint
                    if (i < waypoints.Length - 1 && waypoints[i + 1] != null)
                    {
                        Gizmos.DrawLine(position, waypoints[i + 1].position);
                    }
                    else if (i == waypoints.Length - 1 && waypoints[0] != null)
                    {
                        Gizmos.DrawLine(position, waypoints[0].position);
                    }
                }
            }
        }
    }
}
```

## Integration with Other Agents

The Code Weaver Agent works well with other agents in the system:

- **Level Architect**: The Level Architect can create scenes, and the Code Weaver can implement the behavior for objects in those scenes.
- **Documentation Sentinel**: The Documentation Sentinel can generate documentation for scripts created by the Code Weaver.
- **Pixel Forge**: The Code Weaver can create scripts that interact with assets placed by the Pixel Forge.

## Conclusion

The Code Weaver Agent is a powerful tool for generating and implementing C# scripts for Unity game development. By providing clear, specific prompts, you can leverage its capabilities to accelerate your game development process and implement complex game mechanics with ease.