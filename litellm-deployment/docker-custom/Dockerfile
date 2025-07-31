# ---- Base image ----
FROM python:3.11-slim

# ---- Working directory ----
WORKDIR /app

# ---- Install LiteLLM proxy (no-cache) ----
RUN pip install --no-cache-dir "litellm[proxy]" && \
    pip cache purge && \
    rm -rf /root/.cache/pip && \
    # Remove .pyc & __pycache__ to save space
    find /usr/local/lib/python3.11 -name '__pycache__' -type d -exec rm -rf {} + && \
    find /usr/local/lib/python3.11 -name '*.pyc' -delete

# ---- Non-root for security ----
RUN useradd -m -u 1000 litellm && chown -R litellm:litellm /app
USER litellm

# ---- Expose default port ----
EXPOSE 4000

# ---- Entrypoint ----
ENTRYPOINT ["litellm"]
CMD ["--port", "4000"]