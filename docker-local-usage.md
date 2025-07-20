# Docker Local Usage Guide

## Quick Start

### 1. Build the Docker image
```bash
docker build -t mcp-financial .
```

### 2. Run with environment variable (Recommended)
```bash
docker run -e FMP_API_KEY=your_api_key_here -p 8000:8000 mcp-financial
```

### 3. Test the server
```bash
# Health check
curl http://localhost:8000/health

# Server info
curl http://localhost:8000/info
```

## Usage Options

### Option 1: Environment Variable (Recommended for Security)
```bash
# HTTP transport (default)
docker run -e FMP_API_KEY=your_key -p 8000:8000 mcp-financial

# Custom host/port
docker run -e FMP_API_KEY=your_key -p 9000:9000 mcp-financial \
  python -m mcp_financial_modeling_prep.server --transport http --host 0.0.0.0 --port 9000

# stdio transport (for subprocess usage)
docker run -e FMP_API_KEY=your_key mcp-financial \
  python -m mcp_financial_modeling_prep.server --transport stdio
```

### Option 2: Bind Mount .env File
```bash
# Create .env file with FMP_API_KEY=your_key_here
echo "FMP_API_KEY=your_api_key_here" > .env

# Run with bind-mounted .env
docker run -v $(pwd)/.env:/app/.env -p 8000:8000 mcp-financial
```

### Option 3: Built-in .env (Development Only)
```bash
# If .env exists during build, it will be copied into the image
# This is convenient for development but NOT recommended for production
docker build -t mcp-financial .
docker run -p 8000:8000 mcp-financial
```

## Security Notes

- **Default binding**: Container binds to `127.0.0.1:8000` for security
- **External access**: Use `--host 0.0.0.0` only when needed for external connections
- **Environment variables**: Take precedence over .env files
- **Non-root user**: Container runs as user `mcp` for security

## Transport Selection

### HTTP Transport (Default)
- Best for: Web applications, REST APIs, containerized deployment
- Endpoints: `/health`, `/info`, `/mcp`
- Port: 8000 (configurable)

### stdio Transport  
- Best for: Subprocess usage, Claude Desktop integration
- No network ports required
- Communicates via stdin/stdout

## Examples

### MCP Client Usage
```bash
# Start server
docker run -e FMP_API_KEY=your_key -p 8000:8000 mcp-financial

# Test MCP endpoint (in another terminal)
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -H "MCP-Protocol-Version: 2025-06-18" \
  -d '{"jsonrpc": "2.0", "method": "initialize", "id": 1, "params": {}}'
```

### Development with Hot Reload
```bash
# Bind mount source code for development
docker run -e FMP_API_KEY=your_key \
  -v $(pwd)/src:/app/src \
  -p 8000:8000 \
  mcp-financial
```