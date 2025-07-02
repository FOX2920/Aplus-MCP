import asyncio
import json
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading
from mcp.server.fastmcp import FastMCP
from data.wework_client import WeWorkClient
from typing import Dict, List, Optional, Any
import pandas as pd
from dotenv import load_dotenv
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Access token từ environment
WEWORK_ACCESS_TOKEN = os.getenv('WEWORK_ACCESS_TOKEN', '5654-FCVE2Z8T53L7WTFKVXFP2PTM9MUABP6WRU5LCY6E365RY6TCSRYY4GTAJ48WJEMV-THT9F7ZZNPVMGBNV3FTB8P2QZF5HN2FW9HKV7J64MXDV8BQWN43SK3DUCBJP6JT2')
PORT = int(os.getenv('PORT', 8000))
HOST = os.getenv('HOST', '0.0.0.0')

# Create MCP server
mcp = FastMCP("WeWork Project Management Server")

# Initialize WeWork client
try:
    wework_client = WeWorkClient(WEWORK_ACCESS_TOKEN)
    logger.info("WeWork client initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize WeWork client: {e}")
    wework_client = None

# Import all MCP tools from original server
from wework_mcp_server import (
    search_projects, get_project_details, analyze_project_tasks,
    find_project_by_name, get_project_statistics, test_connection
)

class MCPHTTPHandler(BaseHTTPRequestHandler):
    """HTTP Handler cho MCP server"""
    
    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        if path == '/health':
            self.send_health_check()
        elif path == '/api/test':
            self.send_test_connection()
        elif path == '/api/projects':
            query_params = parse_qs(parsed_path.query)
            search_text = query_params.get('search', [''])[0]
            if search_text:
                self.send_search_projects(search_text)
            else:
                self.send_error_response("Missing search parameter")
        else:
            self.send_error_response("Endpoint not found", 404)
    
    def do_POST(self):
        """Handle POST requests"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8')) if post_data else {}
            
            if path == '/api/project/details':
                project_id = data.get('project_id')
                if project_id:
                    self.send_project_details(project_id)
                else:
                    self.send_error_response("Missing project_id")
            elif path == '/api/project/analyze':
                project_id = data.get('project_id')
                export_csv = data.get('export_csv', False)
                if project_id:
                    self.send_project_analysis(project_id, export_csv)
                else:
                    self.send_error_response("Missing project_id")
            else:
                self.send_error_response("Endpoint not found", 404)
                
        except json.JSONDecodeError:
            self.send_error_response("Invalid JSON data")
        except Exception as e:
            self.send_error_response(f"Server error: {str(e)}", 500)
    
    def send_health_check(self):
        """Health check endpoint"""
        response = {
            "status": "healthy",
            "service": "WeWork MCP Server",
            "wework_client": wework_client is not None,
            "timestamp": pd.Timestamp.now().isoformat()
        }
        self.send_json_response(response)
    
    def send_test_connection(self):
        """Test WeWork connection"""
        try:
            result = test_connection()
            self.send_json_response(result)
        except Exception as e:
            self.send_error_response(f"Connection test failed: {str(e)}")
    
    def send_search_projects(self, search_text: str):
        """Search projects endpoint"""
        try:
            result = search_projects(search_text)
            self.send_json_response(result)
        except Exception as e:
            self.send_error_response(f"Search failed: {str(e)}")
    
    def send_project_details(self, project_id: str):
        """Get project details endpoint"""
        try:
            result = get_project_details(project_id)
            self.send_json_response(result)
        except Exception as e:
            self.send_error_response(f"Failed to get project details: {str(e)}")
    
    def send_project_analysis(self, project_id: str, export_csv: bool = False):
        """Analyze project tasks endpoint"""
        try:
            result = analyze_project_tasks(project_id, export_csv)
            self.send_json_response(result)
        except Exception as e:
            self.send_error_response(f"Analysis failed: {str(e)}")
    
    def send_json_response(self, data: dict, status_code: int = 200):
        """Send JSON response"""
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False, default=str).encode('utf-8'))
    
    def send_error_response(self, message: str, status_code: int = 400):
        """Send error response"""
        error_data = {
            "error": message,
            "status_code": status_code,
            "timestamp": pd.Timestamp.now().isoformat()
        }
        self.send_json_response(error_data, status_code)
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

def run_http_server():
    """Chạy HTTP server"""
    server_address = (HOST, PORT)
    httpd = HTTPServer(server_address, MCPHTTPHandler)
    logger.info(f"HTTP Server starting on http://{HOST}:{PORT}")
    logger.info("Available endpoints:")
    logger.info("  GET  /health - Health check")
    logger.info("  GET  /api/test - Test WeWork connection")
    logger.info("  GET  /api/projects?search=<text> - Search projects")
    logger.info("  POST /api/project/details - Get project details")
    logger.info("  POST /api/project/analyze - Analyze project tasks")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info("Shutting down HTTP server...")
        httpd.shutdown()

def run_mcp_server():
    """Chạy MCP server trong stdio mode"""
    logger.info("Starting MCP Server in stdio mode...")
    mcp.run("stdio")

if __name__ == "__main__":
    mode = os.getenv('SERVER_MODE', 'http').lower()
    
    if mode == 'stdio':
        # Chạy MCP server cho local Claude
        run_mcp_server()
    else:
        # Chạy HTTP server cho cloud deployment
        run_http_server() 