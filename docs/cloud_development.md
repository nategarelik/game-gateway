# Cloud Development Guide

This guide explains how to use the Unity Agent MCP system with cloud development environments, allowing you to access and use the project from any device.

## GitHub Codespaces

GitHub Codespaces provides a complete, configurable development environment in the cloud. You can use it to develop the Unity Agent MCP project from any device with a web browser.

### Setting Up GitHub Codespaces

1. **Create a GitHub Repository**:
   - Follow the instructions in [GitHub Setup](github_setup.md) to create a GitHub repository for the project.

2. **Create a Codespace**:
   - Navigate to your GitHub repository
   - Click the "Code" button
   - Select the "Codespaces" tab
   - Click "Create codespace on main"

3. **Configure the Codespace**:
   - The Codespace will open with a VS Code interface in your browser
   - The repository will be cloned automatically
   - Install Python dependencies:
     ```bash
     pip install -r requirements.txt
     ```

4. **Start the MCP Server**:
   - In the terminal, run:
     ```bash
     python -m src.mcp_server.main
     ```
   - The server will start on http://localhost:5001

5. **Access the Server**:
   - GitHub Codespaces will automatically forward the port
   - Click on the "Ports" tab in the bottom panel
   - Find port 5001 and click the globe icon to open it in a browser

### Using Unity with GitHub Codespaces

While you can develop the server-side components in GitHub Codespaces, Unity development requires a local Unity installation. You can:

1. **Use the MCP Server in Codespaces with a Local Unity Installation**:
   - Start the MCP server in Codespaces
   - Note the forwarded URL (e.g., https://yourcodespace-5001.preview.app.github.dev)
   - In your local Unity project, configure the MCP connection to use this URL

2. **Export the Unity Package**:
   - In Codespaces, run:
     ```bash
     python scripts/package_unity_integration.py
     ```
   - Download the generated package from the Codespaces file explorer
   - Import it into your local Unity project

## GitPod

GitPod is another cloud development environment that you can use with the Unity Agent MCP project.

### Setting Up GitPod

1. **Create a GitPod Account**:
   - Go to [GitPod](https://www.gitpod.io/) and sign up

2. **Create a GitPod Workspace**:
   - Navigate to your GitHub repository
   - Add `gitpod.io/#` to the beginning of the URL
   - For example: `gitpod.io/#https://github.com/YOUR_USERNAME/unity-agent-mcp`

3. **Configure the Workspace**:
   - GitPod will open with a VS Code interface in your browser
   - The repository will be cloned automatically
   - Install Python dependencies:
     ```bash
     pip install -r requirements.txt
     ```

4. **Start the MCP Server**:
   - In the terminal, run:
     ```bash
     python -m src.mcp_server.main
     ```
   - The server will start on http://localhost:5001

5. **Access the Server**:
   - GitPod will automatically forward the port
   - Click on the "Remote Explorer" icon in the sidebar
   - Find port 5001 and click the globe icon to open it in a browser

## Visual Studio Code Remote Development

Visual Studio Code Remote Development allows you to use a remote machine, container, or WSL as a full development environment.

### Using VS Code Remote - SSH

1. **Set Up a Remote Machine**:
   - Set up a remote machine with SSH access
   - Install Python 3.8+ on the remote machine

2. **Install VS Code Remote - SSH Extension**:
   - In VS Code, install the "Remote - SSH" extension

3. **Connect to the Remote Machine**:
   - Press F1 and select "Remote-SSH: Connect to Host..."
   - Enter your SSH connection details

4. **Clone the Repository**:
   - In the remote VS Code window, clone your GitHub repository
   - Install Python dependencies:
     ```bash
     pip install -r requirements.txt
     ```

5. **Start the MCP Server**:
   - In the terminal, run:
     ```bash
     python -m src.mcp_server.main
     ```
   - The server will start on http://localhost:5001

6. **Access the Server**:
   - VS Code will automatically forward the port
   - Click on the "Ports" tab in the bottom panel
   - Find port 5001 and click the globe icon to open it in a browser

## Docker

You can use Docker to containerize the Unity Agent MCP server, making it easy to run on any device with Docker installed.

### Creating a Docker Container

1. **Create a Dockerfile**:
   ```dockerfile
   FROM python:3.10-slim
   
   WORKDIR /app
   
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt
   
   COPY . .
   
   EXPOSE 5001
   
   CMD ["python", "-m", "src.mcp_server.main"]
   ```

2. **Build the Docker Image**:
   ```bash
   docker build -t unity-agent-mcp .
   ```

3. **Run the Docker Container**:
   ```bash
   docker run -p 5001:5001 unity-agent-mcp
   ```

4. **Access the Server**:
   - The server will be available at http://localhost:5001

### Using Docker Compose

For a more complete setup, you can use Docker Compose:

1. **Create a docker-compose.yml File**:
   ```yaml
   version: '3'
   services:
     mcp-server:
       build: .
       ports:
         - "5001:5001"
       volumes:
         - ./src:/app/src
         - ./docs:/app/docs
         - ./tests:/app/tests
       environment:
         - MCP_SERVER_HOST=0.0.0.0
         - MCP_SERVER_PORT=5001
   ```

2. **Start the Services**:
   ```bash
   docker-compose up
   ```

3. **Access the Server**:
   - The server will be available at http://localhost:5001

## Cloud Hosting Options

For a more permanent solution, you can host the MCP server on a cloud platform.

### Heroku

1. **Create a Heroku Account**:
   - Go to [Heroku](https://www.heroku.com/) and sign up

2. **Install the Heroku CLI**:
   - Follow the instructions at [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli)

3. **Create a Procfile**:
   ```
   web: python -m src.mcp_server.main
   ```

4. **Create a runtime.txt File**:
   ```
   python-3.10.0
   ```

5. **Deploy to Heroku**:
   ```bash
   heroku create unity-agent-mcp
   git push heroku main
   ```

6. **Configure the Unity Integration**:
   - In Unity, set the MCP server URL to your Heroku app URL

### AWS Elastic Beanstalk

1. **Create an AWS Account**:
   - Go to [AWS](https://aws.amazon.com/) and sign up

2. **Install the AWS CLI and EB CLI**:
   - Follow the instructions at [AWS CLI](https://aws.amazon.com/cli/) and [EB CLI](https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/eb-cli3-install.html)

3. **Initialize EB CLI**:
   ```bash
   eb init
   ```

4. **Create an Application**:
   ```bash
   eb create unity-agent-mcp
   ```

5. **Deploy the Application**:
   ```bash
   eb deploy
   ```

6. **Configure the Unity Integration**:
   - In Unity, set the MCP server URL to your Elastic Beanstalk environment URL

## Best Practices for Cloud Development

1. **Use Environment Variables**:
   - Store configuration in environment variables
   - Avoid hardcoding sensitive information

2. **Implement Authentication**:
   - Add authentication to the MCP server API
   - Use API keys or OAuth for secure access

3. **Set Up Continuous Integration**:
   - Use GitHub Actions or other CI/CD tools
   - Automatically run tests and build packages

4. **Monitor Performance**:
   - Set up logging and monitoring
   - Track server performance and usage

5. **Implement Backup and Recovery**:
   - Regularly back up your data
   - Have a recovery plan in case of failures

## Troubleshooting

### Common Issues

#### Port Forwarding Issues

If you're having trouble accessing the MCP server from a cloud environment:

1. Ensure the server is listening on all interfaces:
   ```python
   app.run(host='0.0.0.0', port=5001)
   ```

2. Check that the port is properly forwarded:
   - In GitHub Codespaces, check the "Ports" tab
   - In GitPod, check the "Remote Explorer"
   - In VS Code Remote, check the "Ports" tab

#### Connection Issues from Unity

If Unity can't connect to the cloud-hosted MCP server:

1. Ensure the server URL is correct
2. Check that the server is running
3. Verify that there are no firewall or CORS issues
4. Try using HTTPS instead of HTTP

#### Docker Issues

If you're having trouble with Docker:

1. Ensure Docker is properly installed
2. Check that the container is running:
   ```bash
   docker ps
   ```
3. Check the container logs:
   ```bash
   docker logs <container_id>
   ```

## Conclusion

Using cloud development environments with the Unity Agent MCP system allows you to access and use the project from any device. Whether you're using GitHub Codespaces, GitPod, VS Code Remote, Docker, or a cloud hosting platform, you can develop and run the MCP server from anywhere.

For the Unity side of development, you'll still need a local Unity installation, but you can connect it to your cloud-hosted MCP server for a flexible development workflow.