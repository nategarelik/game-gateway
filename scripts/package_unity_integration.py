#!/usr/bin/env python

import os
import shutil
import subprocess
import sys
import json
import uuid
from pathlib import Path

# Add this import to read the package.json
import json

def generate_meta_file(file_path: Path):
    """Generates a basic .meta file for a given file or directory path."""
    meta_path = file_path.with_suffix(file_path.suffix + '.meta')
    if not meta_path.exists():
        guid = uuid.uuid4().hex
        content = f"""fileFormatVersion: 2
guid: {guid}
folderAsset: yes
DefaultImporter:
  externalObjects: {{}}
  userData:
  assetBundleName:
  assetBundleVariant:
""" if file_path.is_dir() else f"""fileFormatVersion: 2
guid: {guid}
DefaultImporter:
  externalObjects: {{}}
  userData:
  assetBundleName:
  assetBundleVariant:
"""
        meta_path.write_text(content)
        print(f"Generated .meta for: {file_path}")

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
        
        # Generate .meta files for all relevant assets in the temp directory
        for root, dirs, files in os.walk(temp_dir):
            for d in dirs:
                generate_meta_file(Path(root) / d)
            for f in files:
                file_path = Path(root) / f
                if file_path.suffix in ['.cs', '.asmdef', '.md', '.json']: # Include common asset types
                    generate_meta_file(file_path)
        
        # Read package.json to get the package name
        with open(unity_package_dir / 'package.json', 'r') as f:
            package_json = json.load(f)
        package_name_from_json = package_json.get('name', 'com.unity-agent-mcp') # Default if name not found

        # Create the tgz package
        package_name = f"{package_name_from_json}.tgz"
        output_path = unity_package_dir / package_name
        
        # Use npm pack to create the package
        result = subprocess.run(
            ['npm', 'pack'],
            cwd=temp_dir,
            capture_output=True,
            text=True,
            env=os.environ,
            shell=True
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