# Git Ignore Template

This document provides a recommended `.gitignore` file template for the Unity Agent MCP project. Since the Architect mode can only edit Markdown files, this template is provided as a Markdown document. You should create a `.gitignore` file in the root of your repository with this content.

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
.pytest_cache/
.coverage
htmlcov/
.tox/
.nox/
.hypothesis/
.pytest_cache/
venv/
ENV/

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
*.apk
*.aab
*.unitypackage
*.app
*.exe
*.dll
*.so
*.dylib
*.pdb
*.mdb
*.opendb
*.VC.db
*.pidb
*.booproj
*.svd
*.userprefs
*.csproj
*.sln
*.suo
*.tmp
*.user
*.userosscache
*.dbmdl
*.dbproj.schemaview
*.jfm
*.pfx
*.publishsettings
orleans.codegen.cs

# IDE
.idea/
.vscode/
*.swp
*.swo
.vs/
*.sublime-workspace
*.sublime-project

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Project specific
generated_assets/
temp_package/
.rooroo/
```

## Usage

1. Create a file named `.gitignore` in the root of your repository
2. Copy the content above into the file
3. Commit the file to your repository

This will ensure that temporary files, build artifacts, and other unnecessary files are not included in your Git repository.

## Customization

You may need to customize the `.gitignore` file based on your specific project needs:

- Add additional file patterns specific to your development environment
- Remove patterns that you want to include in your repository
- Add patterns for additional tools or frameworks you're using

## Additional Resources

- [GitHub's collection of .gitignore templates](https://github.com/github/gitignore)
- [Git documentation on .gitignore](https://git-scm.com/docs/gitignore)