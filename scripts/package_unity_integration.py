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