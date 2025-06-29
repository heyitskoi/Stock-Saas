# Use Ubuntu as the base image
FROM ubuntu:22.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive

# Install essential development tools
RUN apt-get update && apt-get install -y \
    git \
    curl \
    wget \
    build-essential \
    python3 \
    python3-pip \
    vim \
    nano \
    && rm -rf /var/lib/apt/lists/*

# Install latest Node.js LTS version
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && npm install -g npm@latest

# Upgrade pip to latest version
RUN python3 -m pip install --upgrade pip

# Create a non-root user
RUN useradd -m -s /bin/bash ubuntu

# Set the working directory
WORKDIR /home/ubuntu

# Switch to the non-root user
USER ubuntu

# Set default command
CMD ["/bin/bash"]
