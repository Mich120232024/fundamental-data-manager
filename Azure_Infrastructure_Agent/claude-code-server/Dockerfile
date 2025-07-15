# Claude Code Server Dockerfile
FROM node:18-alpine

# Install dependencies
RUN apk add --no-cache \
    git \
    bash \
    curl \
    ca-certificates \
    openssl \
    python3 \
    py3-pip

# Create virtual environment and install Python dependencies
RUN python3 -m venv /app/venv
ENV PATH="/app/venv/bin:$PATH"
RUN pip install --no-cache-dir \
    mcp \
    fastapi==0.115.0 \
    uvicorn==0.34.0 \
    pydantic==2.10.1 \
    httpx==0.28.1 \
    websockets==14.2

# Install Claude Code CLI
RUN npm install -g @anthropic-ai/claude-code@1.0.34

# Create app directory
WORKDIR /app

# Create workspace directory for code operations
RUN mkdir -p /workspace && chmod 755 /workspace

# Copy application files
COPY mcp-config.json /app/
COPY claude_code_mcp_server.py /app/
COPY mcp_http_bridge.py /app/
COPY entrypoint.sh /app/
RUN chmod +x /app/entrypoint.sh

# Create non-root user for security
RUN addgroup -g 1001 claude && \
    adduser -D -u 1001 -G claude claude && \
    chown -R claude:claude /app /workspace

# Switch to non-root user
USER claude

# Expose MCP server port
EXPOSE 8080

# Health check endpoint
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8080/health || exit 1

# Run Claude Code in server mode
CMD ["/app/entrypoint.sh"]