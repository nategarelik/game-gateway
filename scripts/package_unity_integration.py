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
        
        # Read package.json to get the package name and version
        with open(unity_package_dir / 'package.json', 'r') as f:
            package_json = json.load(f)
        
        package_name = package_json.get('name', 'com.unity-agent-mcp')
        version = package_json.get('version', '1.0.0')
        
        # Create the final package name
        package_filename = f"{package_name}-{version}.unitypackage"
        output_path = unity_package_dir / package_filename
        
        # Check if we're running in GitHub Actions
        is_ci = os.environ.get('CI') == 'true'
        
        # In CI, we'll use the docker image's Unity
        if is_ci:
            print("Running in CI environment. Using Unity from path...")
            unity_exe = Path('/opt/unity/Editor/Unity')
            if not unity_exe.exists():
                print("Unity not found at /opt/unity/Editor/Unity. Trying to find Unity...")
                # Try to find Unity in the default installation path
                unity_exe = Path('/Applications/Unity/Hub/Editor/2022.3.0f1/Unity.app/Contents/MacOS/Unity')
        else:
            # Local development - try to find Unity
            unity_exe = None
            if sys.platform == 'win32':
                # Default Unity installation path on Windows
                program_files = os.environ.get('ProgramW6432', 'C:\\Program Files')
                unity_exe = Path(program_files) / 'Unity' / 'Hub' / 'Editor' / '2022.3.0f1' / 'Editor' / 'Unity.exe'
                if not unity_exe.exists():
                    # Try to find the latest Unity version
                    hub_path = Path(program_files) / 'Unity' / 'Hub' / 'Editor'
                    if hub_path.exists():
                        versions = sorted([v for v in hub_path.iterdir() if v.is_dir()], reverse=True)
                        if versions:
                            unity_exe = versions[0] / 'Editor' / 'Unity.exe'
            elif sys.platform == 'darwin':
                # Default Unity installation path on macOS
                unity_exe = Path('/Applications/Unity/Hub/Editor/2022.3.0f1/Unity.app/Contents/MacOS/Unity')
            
            if not unity_exe or not unity_exe.exists():
                print(f"Error: Could not find Unity executable. Please ensure Unity Hub is installed.")
                print(f"Searched at: {unity_exe}" if unity_exe else "Unity Hub not found in default location.")
                print("Creating a .zip archive instead...")
                
                # Fallback to creating a zip file
                import zipfile
                zip_path = output_path.with_suffix('.zip')
                with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    for root, dirs, files in os.walk(temp_dir):
                        for file in files:
                            file_path = os.path.join(root, file)
                            arcname = os.path.relpath(file_path, temp_dir)
                            zipf.write(file_path, arcname)
                print(f"Created zip archive at: {zip_path}")
                return True
        
        # If we found Unity, create a proper .unitypackage
        print(f"Found Unity at: {unity_exe}")
        print("Creating Unity package...")
        
        # Create a temporary project for exporting the package
        temp_project = project_root / 'temp_unity_project'
        if temp_project.exists():
            shutil.rmtree(temp_project)
        temp_project.mkdir()
        
        try:
            # Copy assets to the Assets folder
            assets_dir = temp_project / 'Assets'
            shutil.copytree(temp_dir, assets_dir / package_name)
            
            # Export the package
            export_cmd = [
                str(unity_exe),
                '-batchmode',
                '-nographics',
                '-logFile', str(project_root / 'unity_export.log'),
                '-projectPath', str(temp_project),
                '-exportPackage', f'Assets/{package_name}', str(output_path),
                '-quit'
            ]
            
            result = subprocess.run(
                export_cmd,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                print(f"Error creating Unity package: {result.stderr}")
                return False
                
        finally:
            # Clean up temporary project
            shutil.rmtree(temp_project, ignore_errors=True)
        
        if not output_path.exists():
            print("Warning: Unity package was not created. Check unity_export.log for details.")
            return False
        
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