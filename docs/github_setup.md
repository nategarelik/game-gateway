# GitHub Repository Setup

This document provides instructions for setting up and publishing the Unity Agent MCP project on GitHub, making it accessible from any device and easily applicable to any Unity project.

## Repository Structure

The recommended repository structure is:

```
unity-agent-mcp/
├── .github/
│   └── workflows/
│       └── build.yml
├── docs/
│   ├── agents/
│   ├── mcp_server/
│   ├── protocols/
│   ├── systems/
│   ├── toolchains/
│   ├── workflows/
│   ├── github_setup.md
│   └── unity_package_structure.md
├── scripts/
│   ├── package_unity_integration.py
│   ├── run_end_to_end_scenario_01.py
│   └── run_level_architect_scenario.py
├── src/
│   ├── agents/
│   ├── mcp_server/
│   ├── protocols/
│   ├── systems/
│   ├── toolchains/
│   └── workflows/
├── tests/
│   ├── agents/
│   ├── mcp_server/
│   └── ...
├── unity-package/
│   ├── Editor/
│   ├── Runtime/
│   ├── package.json
│   └── README.md
├── .gitignore
├── CONTRIBUTING.md
├── LICENSE
├── pyproject.toml
├── README.md
└── requirements.txt
```

## Setting Up the GitHub Repository

### 1. Create a New Repository on GitHub

1. Go to [GitHub](https://github.com/) and sign in to your account
2. Click the "+" icon in the top-right corner and select "New repository"
3. Enter "unity-agent-mcp" (or your preferred name) as the Repository name
4. Add a description: "An Autonomous AI Agent Ecosystem for Unity Game Development"
5. Choose Public or Private visibility as desired
6. Do NOT initialize the repository with a README, .gitignore, or license file
7. Click "Create repository"

### 2. Initialize the Local Repository

1. Open a terminal or command prompt in your project directory
2. Run the following commands:

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/unity-agent-mcp.git
git push -u origin main
```

Replace `YOUR_USERNAME` with your GitHub username.

### 3. Set Up GitHub Actions for CI/CD

Create a `.github/workflows/build.yml` file with the following content:

```yaml
name: Build and Package

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        if [ -f requirements.txt ]; then pip install -r requirements.txt; fi
    
    - name: Run tests
      run: |
        python -m pytest tests/
    
    - name: Create Unity package
      run: |
        python scripts/package_unity_integration.py
    
    - name: Upload Unity package
      uses: actions/upload-artifact@v3
      with:
        name: unity-package
        path: unity-package/com.unity-agent-mcp.tgz
```

This workflow will:
- Run on every push to the main branch and on pull requests
- Set up Python
- Install dependencies
- Run tests
- Create the Unity package
- Upload the Unity package as an artifact

### 4. Create a .gitignore File

Create a `.gitignore` file with the following content:

```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
*.egg-info/
.installed.cfg
*.egg

# Unity
/[Ll]ibrary/
/[Tt]emp/
/[Oo]bj/
/[Bb]uild/
/[Bb]uilds/
/[Ll]ogs/
/[Uu]ser[Ss]ettings/
*.pidb.meta
*.pdb.meta
*.mdb.meta
*.unitypackage
*.tgz

# IDE
.idea/
.vscode/
*.swp
*.swo
.vs/

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db
```

### 5. Create a Package Script

Create a `scripts/package_unity_integration.py` file that will package the Unity integration files into a format that can be imported into Unity projects:

```python
#!/usr/bin/env python

import os
import shutil
import subprocess
import sys
import json
from pathlib import Path

def create_unity_package():
    """Create a Unity package from the unity-package directory"""
    # Get the project root directory
    project_root = Path(__file__).parent.parent.absolute()
    unity_package_dir = project_root / 'unity-package'
    
    # Check if the unity-package directory exists
    if not unity_package_dir.exists():
        print(f"Error: {unity_package_dir} does not exist")
        return False
    
    # Create a temporary directory for packaging
    temp_dir = project_root / 'temp_package'
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    temp_dir.mkdir()
    
    try:
        # Copy the unity-package contents to the temp directory
        for item in unity_package_dir.iterdir():
            if item.is_dir():
                shutil.copytree(item, temp_dir / item.name)
            else:
                shutil.copy2(item, temp_dir / item.name)
        
        # Create the tgz package
        package_name = 'com.unity-agent-mcp.tgz'
        output_path = unity_package_dir / package_name
        
        # Use npm pack to create the package
        result = subprocess.run(
            ['npm', 'pack'], 
            cwd=temp_dir, 
            capture_output=True, 
            text=True
        )
        
        if result.returncode != 0:
            print(f"Error creating package: {result.stderr}")
            return False
        
        # Move the created package to the unity-package directory
        created_package = list(temp_dir.glob('*.tgz'))[0]
        if output_path.exists():
            output_path.unlink()
        shutil.move(created_package, output_path)
        
        print(f"Successfully created Unity package: {output_path}")
        return True
    
    except Exception as e:
        print(f"Error creating Unity package: {e}")
        return False
    
    finally:
        # Clean up the temporary directory
        if temp_dir.exists():
            shutil.rmtree(temp_dir)

if __name__ == "__main__":
    success = create_unity_package()
    sys.exit(0 if success else 1)
```

## Making the Project Accessible from Any Device

Once your repository is set up on GitHub, you can access it from any device by:

1. Cloning the repository:
   ```bash
   git clone https://github.com/YOUR_USERNAME/unity-agent-mcp.git
   ```

2. Installing dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Running the MCP server:
   ```bash
   python -m src.mcp_server.main
   ```

## Applying to Any Unity Project

To apply the tool to any Unity project:

1. Download the Unity package from the GitHub repository (either from the releases page or from the GitHub Actions artifacts)
2. In Unity, go to Window > Package Manager
3. Click '+' > Add package from disk
4. Select the `com.unity-agent-mcp.tgz` file
5. Configure the MCP server connection in Window > Unity Agent MCP > Settings
6. Use the agent interface in Window > Unity Agent MCP > Agent Interface

## Continuous Integration and Deployment

The GitHub Actions workflow will automatically:

1. Run tests to ensure the code is working correctly
2. Build the Unity package
3. Make the package available as an artifact

For a more complete CI/CD pipeline, consider:

1. Adding a release workflow that creates GitHub releases
2. Setting up automatic versioning
3. Adding code quality checks
4. Implementing automatic documentation generation

## Best Practices for Collaboration

1. Use branches for new features and bug fixes
2. Create pull requests for code review
3. Write tests for new functionality
4. Keep documentation up to date
5. Follow the contribution guidelines in CONTRIBUTING.md