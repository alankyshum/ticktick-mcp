#!/bin/bash
# Setup script for TickTick authentication with custom dotenv directory

DOTENV_DIR="/Users/kshum/Documents/gitproj/dotfiles/ai-agent/mcp-ticktick/config"

echo "=========================================="
echo "TickTick MCP Authentication Setup"
echo "=========================================="
echo ""
echo "This will:"
echo "1. Open your browser for TickTick authorization"
echo "2. Prompt you to paste the redirect URL"
echo "3. Cache your authentication token"
echo ""
echo "Dotenv directory: $DOTENV_DIR"
echo ""

# Run the setup with the custom dotenv directory
uv run --directory /Users/kshum/Documents/gitproj/ticktick-mcp python -c "
import sys
sys.argv = ['setup', '--dotenv-dir', '$DOTENV_DIR']
from ticktick_mcp.client import setup_auth
from ticktick_mcp.config import parser
args = parser.parse_args()
setup_auth()
"

