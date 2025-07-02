@echo off
cd /d "C:\Users\Hii\Desktop\WM_MCP-master\WM_MCP-master"

REM Set server mode to stdio for local Claude MCP
set SERVER_MODE=stdio

py wework_mcp_server.py 