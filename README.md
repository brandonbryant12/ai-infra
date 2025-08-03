# AI Infrastructure

## Overview

This project provides Docker-based infrastructure for self-hosted AI applications, including OpenWebUI for local AI model interfaces and LiteLLM gateway for unified API access.

## Features

- **OpenWebUI Stack**: Complete Docker setup for OpenWebUI with persistent data and user header forwarding
- **LiteLLM Gateway**: OpenAI-compatible API gateway with dynamic OpenRouter integration (295+ models)
- **Central Management**: Unified Makefile for managing all services
- **Automatic Updates**: Pull latest code and restart with one command
- **Jinja2 Templating**: Dynamic configuration with environment variables
- **Network Ready**: External Docker network for cross-stack communication
- **Production Ready**: Proper security defaults and configuration

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Git (for updates)

### Quick Start

```bash
# Clone the repository
git clone https://github.com/brandonbryant12/ai-infra.git
cd ai-infra

# Run setup script (first time only)
./scripts/setup.sh

# Edit environment files
vim stacks/openwebui/.env    # Set WEBUI_SECRET_KEY
vim stacks/litellm/.env      # Set OPENROUTER_API_KEY

# Start all services
make start

# Check status
make status
```

## Central Management Commands

The repository includes a central Makefile for managing all services:

```bash
# Core Commands
make help          # Show all available commands
make update        # Pull latest code and restart all services
make start         # Start all services
make stop          # Stop all services
make restart       # Restart all services
make status        # Show status of all services
make logs          # Stream logs from all services

# Maintenance Commands
make pull          # Pull latest Docker images
make rebuild       # Rebuild all services from scratch
make clean         # Clean up containers and unused resources
make check-env     # Check environment setup

# Individual Service Commands
make owui-*        # OpenWebUI-specific commands
make litellm-*     # LiteLLM-specific commands
```

### Automatic Updates

To update your deployment with the latest changes:

```bash
make update
```

This command will:
1. Pull the latest code from the main branch
2. Restart all services with the new configuration
3. Show the status of all services

## Available Stacks

### OpenWebUI
- **Location**: `stacks/openwebui/`
- **Default Port**: 3000 (configurable via OPENWEBUI_PORT)
- **Features**: Chat interface, user management, model connections, user header forwarding
- **Commands**: `owui-up`, `owui-down`, `owui-logs`, `owui-restart`

### LiteLLM Gateway
- **Location**: `stacks/litellm/`
- **Default Port**: 4000 (configurable via LITELLM_PORT)
- **Features**: OpenAI-compatible API, OpenRouter integration, user tracking via headers
- **Commands**: `litellm-up`, `litellm-down`, `litellm-logs`, `litellm-restart`
- **Models**: GPT-4o, GPT-4o-mini, Claude 3.5 Sonnet, Claude 3 Haiku

## Configuration

- Copy `.env.sample` files to `.env` in respective stack directories
- **OpenWebUI**: Signup disabled by default, user info headers enabled for downstream APIs
- **LiteLLM**: Requires OpenRouter API key, configured for user tracking via X-OpenWebUI-User-Id headers
- Adjust ports and settings as needed

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐     ┌─────────────┐
│   Users     │────▶│   OpenWebUI  │────▶│ LiteLLM     │────▶│ OpenRouter  │
│             │     │   (Port 3000)│     │ Gateway     │     │ AI Models   │
└─────────────┘     └──────────────┘     │ (Port 4000) │     └─────────────┘
                           │              └─────────────┘
                    ┌──────▼──────┐
                    │ Persistent  │
                    │   Storage   │
                    └─────────────┘
```

### User Header Flow
- OpenWebUI forwards user info as `X-OpenWebUI-User-*` headers
- LiteLLM Gateway receives and tracks users via `X-OpenWebUI-User-Id`
- Both services share the `llmnet` Docker network for communication