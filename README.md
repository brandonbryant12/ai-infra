# AI Infrastructure - LiteLLM Proxy Gateway

## Overview

This project provides infrastructure for managing AI model connections through LiteLLM proxy gateway. It includes scripts and Helm charts to streamline the deployment and configuration of LiteLLM proxy instances.

## Purpose

- **Centralized AI Connection Management**: Manage multiple AI provider connections (OpenAI, Anthropic, etc.) through a single gateway
- **Easy Configuration**: Simplified scripts for adding new AI connections
- **Kubernetes Deployment**: Helm charts for deploying LiteLLM proxy to Kubernetes clusters
- **Single Master Key**: Initial implementation uses a single master key for authentication
- **No Database**: Lightweight deployment without database dependencies

## Features

- LiteLLM proxy gateway deployment
- Helm chart configuration for Kubernetes
- Scripts for managing AI provider connections
- Single master key authentication
- Support for multiple AI providers through unified interface

## Getting Started

### Prerequisites

- Kubernetes cluster
- Helm 3.x
- kubectl configured for your cluster

### Deployment

```bash
# Deploy LiteLLM proxy using Helm
helm install litellm-proxy ./helm/litellm-proxy

# Configure AI connections
./scripts/add-connection.sh
```

## Configuration

The LiteLLM proxy is configured through:
- Environment variables for API keys
- Configuration files for model mappings
- Helm values for deployment customization

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   Client    │────▶│   LiteLLM    │────▶│ AI Providers│
│Applications │     │    Proxy     │     │  (OpenAI,   │
└─────────────┘     └──────────────┘     │  Anthropic) │
                           │              └─────────────┘
                           │
                    ┌──────▼──────┐
                    │ Master Key  │
                    │   Auth      │
                    └─────────────┘
```

## Roadmap

- [ ] Multi-key authentication support
- [ ] Database integration for usage tracking
- [ ] Advanced load balancing
- [ ] Monitoring and observability


  curl -X POST "${OPENWEBUI_API_URL}/api/chat/completions" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer ${OPENQWEBUI_TOKEN}" \
    -d '{
      "model": "gpt-3.5-turbo",
      "messages": [{"role": "user", "content": "test"}],
      "stream": false
    }' \
    -v