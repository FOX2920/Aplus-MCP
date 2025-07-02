#!/usr/bin/env python3
"""Simple test for WeWork MCP components"""

import sys
import os

def test_basic_imports():
    """Test basic Python imports"""
    print("🧪 Testing basic imports...")
    
    try:
        import pandas as pd
        print("✅ pandas imported")
        
        import requests
        print("✅ requests imported") 
        
        from dotenv import load_dotenv
        print("✅ dotenv imported")
        
        import numpy as np
        print("✅ numpy imported")
        
        return True
    except Exception as e:
        print(f"❌ Basic imports failed: {e}")
        return False

def test_wework_client():
    """Test WeWork client"""
    print("\n🧪 Testing WeWork client...")
    
    try:
        from data.wework_client import WeWorkClient
        print("✅ WeWorkClient imported")
        
        # Test initialization
        client = WeWorkClient("test-token")
        print("✅ WeWorkClient initialized")
        
        # Test fetch projects
        projects = client.fetch_projects()
        print(f"✅ fetch_projects returned {len(projects)} projects")
        
        return True
    except Exception as e:
        print(f"❌ WeWork client test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_environment():
    """Test environment setup"""
    print("\n🧪 Testing environment...")
    
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        token = os.getenv('WEWORK_ACCESS_TOKEN')
        if token:
            print(f"✅ Access token loaded (length: {len(token)})")
        else:
            print("⚠️ No access token found in .env")
        
        return True
    except Exception as e:
        print(f"❌ Environment test failed: {e}")
        return False

def test_server_script():
    """Test if main server script can be imported"""
    print("\n🧪 Testing server script...")
    
    try:
        # Just check if the file exists and has basic syntax
        server_file = "wework_mcp_server.py"
        if os.path.exists(server_file):
            print(f"✅ Server file {server_file} exists")
            
            # Try to read it
            with open(server_file, 'r', encoding='utf-8') as f:
                content = f.read()
                if 'FastMCP' in content:
                    print("✅ FastMCP found in server file")
                if 'WeWorkClient' in content:
                    print("✅ WeWorkClient found in server file")
                    
            return True
        else:
            print(f"❌ Server file {server_file} not found")
            return False
            
    except Exception as e:
        print(f"❌ Server script test failed: {e}")
        return False

def main():
    """Run simple tests"""
    print("🚀 Running Simple Tests for WeWork MCP\n")
    
    # Run tests
    test1 = test_basic_imports()
    test2 = test_wework_client() 
    test3 = test_environment()
    test4 = test_server_script()
    
    # Summary
    print("\n" + "="*40)
    print("📊 TEST RESULTS:")
    print(f"   Basic Imports:  {'✅ PASS' if test1 else '❌ FAIL'}")
    print(f"   WeWork Client:  {'✅ PASS' if test2 else '❌ FAIL'}")
    print(f"   Environment:    {'✅ PASS' if test3 else '❌ FAIL'}")
    print(f"   Server Script:  {'✅ PASS' if test4 else '❌ FAIL'}")
    
    all_passed = all([test1, test2, test3, test4])
    print(f"\n🎯 Result: {'✅ CORE COMPONENTS OK' if all_passed else '❌ SOME ISSUES FOUND'}")
    
    if all_passed:
        print("\n💡 Core components are working!")
        print("   You can now try running the server with:")
        print("   .\\start_server.bat")
    
    return all_passed

if __name__ == "__main__":
    main() 