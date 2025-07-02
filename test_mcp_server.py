#!/usr/bin/env python3
"""Test script for WeWork MCP Server"""

import asyncio
import json
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_wework_client():
    """Test WeWork client directly"""
    print("🧪 Testing WeWork Client...")
    
    try:
        # Import and initialize client
        from data.wework_client import WeWorkClient
        
        token = os.getenv('WEWORK_ACCESS_TOKEN')
        client = WeWorkClient(token)
        print("✅ WeWork client initialized")
        
        # Test fetch projects
        print("\n📋 Testing fetch_projects...")
        projects = client.fetch_projects()
        print(f"✅ Found {len(projects)} projects")
        if projects:
            print(f"   First project: {projects[0]}")
        
        # Test search projects
        print("\n🔍 Testing search_projects...")
        search_results = client.search_projects("test", limit=5)
        print(f"✅ Search returned {len(search_results)} results")
        
        # Test get project info
        if projects:
            print(f"\n📄 Testing get_project_info for project {projects[0]['id']}...")
            project_info = client.get_project_info(projects[0]['id'])
            if project_info:
                print("✅ Project info retrieved successfully")
                print(f"   Project: {project_info['name']}")
            else:
                print("❌ Failed to get project info")
        
        # Test project analysis
        if projects:
            print(f"\n📊 Testing get_project_analysis for project {projects[0]['id']}...")
            df = client.get_project_analysis(projects[0]['id'])
            print(f"✅ Analysis returned {len(df)} rows")
        
        print("\n🎉 All WeWork client tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ WeWork client test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_fastmcp_import():
    """Test FastMCP import and initialization"""
    print("\n🧪 Testing FastMCP...")
    
    try:
        from mcp.server.fastmcp import FastMCP
        
        # Create MCP server
        mcp = FastMCP("Test WeWork Server")
        print("✅ FastMCP server created successfully")
        
        # Test basic decorator functionality
        @mcp.tool()
        def test_tool(message: str) -> str:
            """Test tool"""
            return f"Hello {message}!"
        
        print("✅ FastMCP tool decorator works")
        
        return True
        
    except Exception as e:
        print(f"❌ FastMCP test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_server_imports():
    """Test all server imports"""
    print("\n🧪 Testing server imports...")
    
    try:
        # Test main server file imports
        import wework_mcp_server
        print("✅ Main server module imported successfully")
        
        # Check if server was created
        if hasattr(wework_mcp_server, 'mcp'):
            print("✅ MCP server instance found")
        else:
            print("⚠️ MCP server instance not found")
        
        # Check if client was created
        if hasattr(wework_mcp_server, 'wework_client'):
            print("✅ WeWork client instance found")
        else:
            print("⚠️ WeWork client instance not found")
        
        return True
        
    except Exception as e:
        print(f"❌ Server import test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run all tests"""
    print("🚀 Starting WeWork MCP Server Tests\n")
    
    # Test 1: FastMCP import
    fastmcp_ok = await test_fastmcp_import()
    
    # Test 2: WeWork client
    client_ok = await test_wework_client()
    
    # Test 3: Server imports
    server_ok = await test_server_imports()
    
    # Summary
    print("\n" + "="*50)
    print("📊 TEST SUMMARY:")
    print(f"   FastMCP Import: {'✅ PASS' if fastmcp_ok else '❌ FAIL'}")
    print(f"   WeWork Client:  {'✅ PASS' if client_ok else '❌ FAIL'}")
    print(f"   Server Imports: {'✅ PASS' if server_ok else '❌ FAIL'}")
    
    all_passed = fastmcp_ok and client_ok and server_ok
    print(f"\n🎯 Overall Result: {'✅ ALL TESTS PASSED!' if all_passed else '❌ SOME TESTS FAILED'}")
    
    if all_passed:
        print("\n🎉 Your WeWork MCP Server is ready to use!")
        print("💡 You can now configure it in Claude Desktop using the config file:")
        print("   claude_desktop_config_example.json")
    else:
        print("\n⚠️ Please fix the failing tests before using the server.")
    
    return all_passed

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1) 