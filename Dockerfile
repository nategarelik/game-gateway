FROM unityci/editor:2022.3.0f1-ubuntu-1.0.0

# Install Python and pip
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Set up Python
RUN ln -s /usr/bin/python3 /usr/bin/python
RUN pip3 install --upgrade pip

# Copy package files
COPY . /project

# Set working directory
WORKDIR /project

# Install Python dependencies
RUN pip install -r requirements.txt

# Set up entry point
ENTRYPOINT ["/bin/bash"]
