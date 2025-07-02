#!/usr/bin/env python3
"""Test Claude Desktop configuration"""

import json
import os
import subprocess

def test_claude_config():
    """Test Claude Desktop configuration file"""
    print("🧪 Testing Claude Desktop Configuration...")
    
    config_file = "claude_desktop_config_example.json"
    
    try:
        # Check if config file exists
        if not os.path.exists(config_file):
            print(f"❌ Config file {config_file} not found")
            return False
        
        # Load and validate JSON
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        print("✅ Config file is valid JSON")
        
        # Check structure
        if 'mcpServers' not in config:
            print("❌ Missing 'mcpServers' section")
            return False
        
        if 'wework-task-analysis' not in config['mcpServers']:
            print("❌ Missing 'wework-task-analysis' server config")
            return False
        
        server_config = config['mcpServers']['wework-task-analysis']
        
        # Check command
        command = server_config.get('command')
        if not command:
            print("❌ Missing 'command' in server config")
            return False
        
        print(f"✅ Server command: {command}")
        
        # Check if command file exists
        if command.endswith('.bat'):
            if os.path.exists(command):
                print("✅ Batch file exists")
            else:
                # Try relative path
                relative_path = os.path.basename(command)
                if os.path.exists(relative_path):
                    print("✅ Batch file exists (relative path)")
                else:
                    print(f"❌ Batch file not found: {command}")
                    return False
        
        print("✅ Claude Desktop config looks good!")
        return True
        
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in config file: {e}")
        return False
    except Exception as e:
        print(f"❌ Error testing config: {e}")
        return False

def test_batch_script():
    """Test if batch script can start"""
    print("\n🧪 Testing batch script...")
    
    batch_file = "start_server.bat"
    
    try:
        if not os.path.exists(batch_file):
            print(f"❌ Batch file {batch_file} not found")
            return False
        
        print(f"✅ Batch file {batch_file} exists")
        
        # Read batch file content
        with open(batch_file, 'r') as f:
            content = f.read()
        
        print("✅ Batch file content:")
        for line in content.strip().split('\n'):
            print(f"   {line}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing batch script: {e}")
        return False

def show_setup_instructions():
    """Show setup instructions for Claude Desktop"""
    print("\n📋 SETUP INSTRUCTIONS FOR CLAUDE DESKTOP:")
    print("="*50)
    
    config_path_win = r"%APPDATA%\Claude\claude_desktop_config.json"
    config_path_mac = r"~/Library/Application Support/Claude/claude_desktop_config.json"
    
    print("1. Locate your Claude Desktop config file:")
    print(f"   Windows: {config_path_win}")
    print(f"   macOS: {config_path_mac}")
    
    print("\n2. Copy the content from 'claude_desktop_config_example.json'")
    print("   to your actual Claude Desktop config file.")
    
    print("\n3. Make sure the paths in the config are correct:")
    print("   - Update the command path if needed")
    print("   - Verify the working directory path")
    
    print("\n4. Restart Claude Desktop application")
    
    print("\n5. Test the server by asking Claude:")
    print("   'What WeWork projects are available?'")
    print("   'Search for projects containing \"test\"'")
    
    print("\n💡 If you see tools available, the setup is successful!")

def main():
    """Run configuration tests"""
    print("🚀 Testing Claude Desktop Configuration\n")
    
    # Run tests
    test1 = test_claude_config()
    test2 = test_batch_script()
    
    # Summary
    print("\n" + "="*40)
    print("📊 CONFIG TEST RESULTS:")
    print(f"   Claude Config:  {'✅ PASS' if test1 else '❌ FAIL'}")
    print(f"   Batch Script:   {'✅ PASS' if test2 else '❌ FAIL'}")
    
    if test1 and test2:
        print("\n🎯 Result: ✅ CONFIGURATION READY!")
        show_setup_instructions()
    else:
        print("\n🎯 Result: ❌ CONFIGURATION ISSUES FOUND")
        print("Please fix the issues above before proceeding.")
    
    return test1 and test2

if __name__ == "__main__":
    main() 