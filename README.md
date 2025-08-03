# AI Infrastructure

## Overview

This project provides Docker-based infrastructure for self-hosted AI applications, starting with OpenWebUI for local AI model interfaces.

## Features

- **OpenWebUI Stack**: Complete Docker setup for OpenWebUI with persistent data
- **Easy Management**: Makefile commands for common operations
- **Network Ready**: External Docker network for cross-stack communication
- **Production Ready**: Proper security defaults and configuration

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Make (optional, for convenient commands)

### OpenWebUI Deployment

```bash
# Create external network (run once)
docker network create llmnet

# Start OpenWebUI
make owui-up

# View logs
make owui-logs

# Stop services
make owui-down
```

## Available Stacks

### OpenWebUI
- **Location**: `stacks/openwebui/`
- **Default Port**: 3000 (configurable via OPENWEBUI_PORT)
- **Features**: Chat interface, user management, model connections
- **Commands**: `owui-up`, `owui-down`, `owui-logs`, `owui-restart`

## Configuration

- Copy `.env.sample` files to `.env` in respective stack directories
- Adjust ports and settings as needed
- Signup is disabled by default for security

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   Users     │────▶│   OpenWebUI  │────▶│ AI Models   │
│             │     │   (Port 3000)│     │ (External)  │
└─────────────┘     └──────────────┘     └─────────────┘
                           │
                    ┌──────▼──────┐
                    │ Persistent  │
                    │   Storage   │
                    └─────────────┘
```