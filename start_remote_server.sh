#!/bin/bash

# Script để khởi động remote server

echo "🚀 Starting WeWork MCP HTTP Server..."

# Load environment variables if .env exists
if [ -f ".env" ]; then
    echo "📁 Loading environment variables from .env..."
    export $(cat .env | grep -v '^#' | xargs)
fi

# Set default values
export PORT=${PORT:-8000}
export HOST=${HOST:-0.0.0.0}
export SERVER_MODE=${SERVER_MODE:-http}

echo "🔧 Configuration:"
echo "   PORT: $PORT"
echo "   HOST: $HOST"
echo "   SERVER_MODE: $SERVER_MODE"
echo "   WEWORK_TOKEN: ${WEWORK_ACCESS_TOKEN:+***configured***}"

# Start the server
python wework_http_server.py 