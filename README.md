# AI Infrastructure

## Overview

This project provides Docker-based infrastructure for self-hosted AI applications, including OpenWebUI for local AI model interfaces and LiteLLM gateway for unified API access.

## Features

- **OpenWebUI Stack**: Complete Docker setup for OpenWebUI with persistent data and user header forwarding
- **LiteLLM Gateway**: OpenAI-compatible API gateway with OpenRouter integration
- **Easy Management**: Makefile commands for common operations
- **Network Ready**: External Docker network for cross-stack communication
- **Production Ready**: Proper security defaults and configuration

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Make (optional, for convenient commands)

### Quick Start

```bash
# Create external network (run once)
docker network create llmnet

# Start OpenWebUI
make owui-up

# Start LiteLLM Gateway (requires OpenRouter API key)
cp stacks/litellm/.env.sample stacks/litellm/.env
# Edit .env with your OpenRouter API key
make litellm-up

# View logs
make owui-logs
make litellm-logs
```

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