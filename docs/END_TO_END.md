# End-to-End Flow: OpenWebUI → LiteLLM → OpenRouter (+ Langfuse Tracing)

## Architecture

```
┌─────────────┐     ┌──────────────┐      ┌─────────────┐       ┌─────────────┐
│   Users     │ ──▶ │  OpenWebUI   │ ───▶ │   LiteLLM   │ ────▶ │  OpenRouter │
│             │     │  (3000)      │      │  (4000)     │       │  API        │
└─────────────┘     └──────────────┘      └─────────────┘       └─────────────┘
                              │
                              └──────▶  Langfuse (Traces, 3100)
```

## User Identification (Headers)

* OpenWebUI (with `ENABLE_FORWARD_USER_INFO_HEADERS=true`) forwards:

  * `X-OpenWebUI-User-Id`, `X-OpenWebUI-User-Email`, `X-OpenWebUI-User-Name`, `X-OpenWebUI-User-Role`, `X-OpenWebUI-Chat-Id`.
* LiteLLM is configured to read a single header for user attribution. **Keep using your chosen header (`X-OpenWebUI-User-Id`)** so spend/metrics/traces are attributed per-user.

---

## LiteLLM ↔ Langfuse Integration (Specifics)

**What enables traces?**

* In `stacks/litellm/config.yaml.j2`:

  ```yaml
  litellm_settings:
    success_callback: ["langfuse"]
    failure_callback: ["langfuse"]
  ```

  This activates LiteLLM's built-in Langfuse callback for every successful/failed request.

**Environment variables (set in `stacks/litellm/.env`):**

* `LANGFUSE_HOST` — Your Langfuse URL (e.g., `https://langfuse.brandonbryant.io`)
* `LANGFUSE_PUBLIC_KEY` — Project public key (from Langfuse UI or auto-init)
* `LANGFUSE_SECRET_KEY` — Project secret key
* Optional: `LANGFUSE_DEBUG=true` for verbose callback logs

**How are traces attributed?**

* LiteLLM attaches the request's user id (from your selected header) to the trace/observation metadata.
* OpenWebUI forwards user headers automatically to LiteLLM via `OPENAI_API_BASE_URL` requests (in Docker network).

**Data flow & mapping**

1. **OpenWebUI** sends a Chat Completions request to **LiteLLM**.

   * Headers include `X-OpenWebUI-User-Id` and related fields.
2. **LiteLLM** proxies to **OpenRouter** (`openrouter/*` models in your config), receives the response, and

   * emits a **Langfuse trace** (success or failure) using the environment keys.
3. **Langfuse** stores:

   * Request/response metadata, timing, costs (if available), model name, and the user id captured by LiteLLM.

**Verifying traces**

* Open the Langfuse UI → Project dashboard → Traces should appear shortly after any request via LiteLLM.

**Common pitfalls**

* Missing keys: ensure `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY`, `LANGFUSE_HOST` are set and non-empty.
* Networking: LiteLLM must be able to reach `LANGFUSE_HOST`.
* TLS: if using a private CA/self-signed cert, confirm the Docker image trusts it or use a valid cert.

---

## Nginx

* `ai.brandonbryant.io` → OpenWebUI (port 3000)
* `litellm.brandonbryant.io` → LiteLLM (port 4000)
* `langfuse.brandonbryant.io` → Langfuse web (port 3100)

## One-Command Deploy

1. First-time setup:

   ```bash
   ./scripts/setup.sh
   # edit:
   # - stacks/openwebui/.env (WEBUI_SECRET_KEY, WEBUI_URL)
   # - stacks/langfuse/.env (POSTGRES_PASSWORD, NEXTAUTH_SECRET, LANGFUSE_SALT, LANGFUSE_URL; optional LANGFUSE_INIT_* to auto-provision keys)
   # - stacks/litellm/.env (OPENROUTER_API_KEY; add LANGFUSE_PUBLIC_KEY/SECRET_KEY/HOST after Langfuse boots)
   ```
2. Start everything:

   ```bash
   make start
   ```
3. Verify:

   ```bash
   make status
   scripts/e2e-check.sh
   ```

## Troubleshooting

* **No traces in Langfuse**:

  * Check LiteLLM logs for "langfuse" entries.
  * Verify `LANGFUSE_*` envs in `stacks/litellm/.env`.
  * Confirm Langfuse UI is reachable (`curl -I https://langfuse.brandonbryant.io/`).
* **Headers missing**: Ensure `ENABLE_FORWARD_USER_INFO_HEADERS=true` in OpenWebUI `.env`.
* **Models not listed**: Ensure `OPENROUTER_API_KEY` is valid; `update-models.py` runs at container start.
  \