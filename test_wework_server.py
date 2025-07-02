#!/usr/bin/env python3
"""
Test script để kiểm tra WeWork MCP Server
"""

import asyncio
from data.wework_client import WeWorkClient

# Access token
WEWORK_ACCESS_TOKEN = '5654-FCVE2Z8T53L7WTFKVXFP2PTM9MUABP6WRU5LCY6E365RY6TCSRYY4GTAJ48WJEMV-THT9F7ZZNPVMGBNV3FTB8P2QZF5HN2FW9HKV7J64MXDV8BQWN43SK3DUCBJP6JT2'

def test_wework_client():
    """Test WeWork client functionality"""
    print("🧪 Testing WeWork Client...")
    
    # Initialize client
    client = WeWorkClient(WEWORK_ACCESS_TOKEN)
    
    try:
        # Test 1: Fetch projects
        print("\n📋 Test 1: Lấy danh sách dự án...")
        projects = client.fetch_projects()
        print(f"✅ Tìm thấy {len(projects)} dự án")
        
        if projects:
            print("📝 Một số dự án:")
            for i, project in enumerate(projects[:3]):
                print(f"   {i+1}. {project['name']} (ID: {project['id']})")
        
        # Test 2: Search projects
        print("\n🔍 Test 2: Tìm kiếm dự án...")
        search_results = client.search_projects("thống", limit=3)
        print(f"✅ Tìm thấy {len(search_results)} dự án phù hợp với 'thống'")
        
        for project in search_results:
            print(f"   - {project['name']} (ID: {project['id']})")
        
        # Test 3: Find best match
        if projects:
            print("\n🎯 Test 3: Tìm dự án bằng similarity...")
            best_project, score = client.find_best_project_match("thống lĩnh", projects)
            if best_project:
                print(f"✅ Tìm thấy: {best_project['name']} (Điểm: {score:.3f})")
            else:
                print("❌ Không tìm thấy dự án phù hợp")
        
        # Test 4: Analyze tasks (nếu có dự án)
        if projects:
            project_id = projects[0]['id']
            project_name = projects[0]['name']
            print(f"\n📊 Test 4: Phân tích tasks của dự án '{project_name}'...")
            
            df = client.get_project_analysis(project_id)
            if not df.empty:
                print(f"✅ Đã phân tích {len(df)} tasks")
                print(f"📈 Thống kê trạng thái:")
                status_counts = df['Trạng thái'].value_counts()
                for status, count in status_counts.items():
                    print(f"   - {status}: {count}")
            else:
                print("⚠️ Không có tasks trong dự án này")
                
        print("\n🎉 Tất cả tests đã hoàn thành!")
        return True
        
    except Exception as e:
        print(f"❌ Lỗi trong quá trình test: {str(e)}")
        return False

def test_mcp_server():
    """Test MCP server functions"""
    print("\n🔧 Testing MCP Server functions...")
    
    try:
        # Import server functions
        from wework_mcp_server import (
            search_projects, 
            get_project_details, 
            find_project_by_name,
            get_project_statistics
        )
        
        # Test search_projects
        print("\n🔍 Test MCP search_projects...")
        results = search_projects("thống", 3)
        if isinstance(results, list) and len(results) > 0:
            print(f"✅ search_projects hoạt động - tìm thấy {len(results)} dự án")
        else:
            print("⚠️ search_projects không trả về kết quả")
        
        # Test find_project_by_name
        print("\n🎯 Test MCP find_project_by_name...")
        result = find_project_by_name("thống lĩnh đức chinh phục mỹ")
        if result.get('found'):
            project = result['project']
            print(f"✅ find_project_by_name hoạt động - tìm thấy: {project['name']}")
            
            # Test get_project_details with found project
            project_id = project['id']
            print(f"\n📋 Test MCP get_project_details cho ID: {project_id}...")
            details = get_project_details(project_id)
            if 'error' not in details:
                print(f"✅ get_project_details hoạt động - {details['name']}")
            else:
                print(f"❌ get_project_details lỗi: {details['error']}")
                
            # Test get_project_statistics
            print(f"\n📊 Test MCP get_project_statistics...")
            stats = get_project_statistics(project_id)
            if 'error' not in stats:
                total_tasks = stats['statistics']['total_tasks']
                completion_rate = stats['statistics']['completion_rate']
                print(f"✅ get_project_statistics hoạt động - {total_tasks} tasks, {completion_rate}% hoàn thành")
            else:
                print(f"❌ get_project_statistics lỗi: {stats['error']}")
        else:
            print(f"⚠️ find_project_by_name không tìm thấy dự án: {result.get('message', 'Unknown error')}")
        
        print("\n🎉 MCP Server tests hoàn thành!")
        return True
        
    except Exception as e:
        print(f"❌ Lỗi trong MCP server test: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Bắt đầu testing WeWork MCP Server")
    print("=" * 50)
    
    # Test WeWork client
    client_ok = test_wework_client()
    
    # Test MCP server functions
    server_ok = test_mcp_server()
    
    print("\n" + "=" * 50)
    if client_ok and server_ok:
        print("🎉 Tất cả tests PASSED! WeWork MCP Server sẵn sàng sử dụng.")
    else:
        print("❌ Một số tests FAILED. Vui lòng kiểm tra lại.") 