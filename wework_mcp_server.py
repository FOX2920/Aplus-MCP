from mcp.server.fastmcp import FastMCP
from data.wework_client import WeWorkClient
from typing import Dict, List, Optional
import pandas as pd
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Access token từ environment hoặc fallback
WEWORK_ACCESS_TOKEN = os.getenv('WEWORK_ACCESS_TOKEN', '5654-FCVE2Z8T53L7WTFKVXFP2PTM9MUABP6WRU5LCY6E365RY6TCSRYY4GTAJ48WJEMV-THT9F7ZZNPVMGBNV3FTB8P2QZF5HN2FW9HKV7J64MXDV8BQWN43SK3DUCBJP6JT2')

# Create MCP server
mcp = FastMCP("WeWork Project Management Server")

# Initialize WeWork client
wework_client = WeWorkClient(WEWORK_ACCESS_TOKEN)

# Resource to get available projects
@mcp.resource("file://projects/available")
def get_available_projects() -> Dict:
    """Lấy danh sách tất cả các dự án có sẵn"""
    try:
        projects = wework_client.fetch_projects()
        return {
            'projects': projects,
            'total_count': len(projects)
        }
    except Exception as e:
        return {
            'error': str(e),
            'projects': [],
            'total_count': 0
        }

# Tool to search projects
@mcp.tool()
def search_projects(search_text: str, limit: int = 10) -> List[Dict]:
    """
    Tìm kiếm dự án theo tên
    
    Args:
        search_text: Text để tìm kiếm trong tên dự án
        limit: Số lượng kết quả tối đa (default: 10)
    
    Returns:
        Danh sách các dự án phù hợp
    """
    try:
        results = wework_client.search_projects(search_text=search_text, limit=limit)
        return results
    except Exception as e:
        return [{'error': str(e)}]

# Tool to get project details
@mcp.tool()
def get_project_details(project_id: str) -> Dict:
    """
    Lấy chi tiết của một dự án
    
    Args:
        project_id: ID của dự án
    
    Returns:
        Chi tiết dự án bao gồm thông tin cơ bản
    """
    try:
        project_info = wework_client.get_project_info(project_id)
        if project_info:
            return project_info
        else:
            return {'error': f'Không tìm thấy dự án với ID: {project_id}'}
    except Exception as e:
        return {'error': str(e)}

# Tool to analyze project tasks
@mcp.tool()
def analyze_project_tasks(project_id: str, export_csv: bool = False) -> Dict:
    """
    Phân tích các tasks trong dự án
    
    Args:
        project_id: ID của dự án
        export_csv: Có xuất file CSV không (default: False)
    
    Returns:
        Phân tích tasks dưới dạng dictionary
    """
    try:
        # Lấy thông tin dự án
        project_info = wework_client.get_project_info(project_id)
        if not project_info:
            return {'error': f'Không tìm thấy dự án với ID: {project_id}'}
        
        # Phân tích tasks
        df = wework_client.get_project_analysis(project_id)
        
        if df.empty:
            return {
                'project_name': project_info['name'],
                'project_id': project_id,
                'tasks': [],
                'summary': {
                    'total_tasks': 0,
                    'completed_tasks': 0,
                    'in_progress_tasks': 0,
                    'failed_tasks': 0
                }
            }
        
        # Tính thống kê
        status_counts = df['Trạng thái'].value_counts().to_dict()
        
        # Chuyển DataFrame thành dictionary
        tasks_data = df.to_dict(orient='records')
        
        # Xuất CSV nếu được yêu cầu
        csv_filename = None
        if export_csv:
            csv_filename = f"{project_info['name']}_tasks_analysis.csv"
            df.to_csv(csv_filename, index=False, encoding='utf-8-sig')
        
        result = {
            'project_name': project_info['name'],
            'project_id': project_id,
            'tasks': tasks_data,
            'summary': {
                'total_tasks': len(df),
                'completed_tasks': status_counts.get('Hoàn thành', 0),
                'in_progress_tasks': status_counts.get('Đang thực hiện', 0),
                'failed_tasks': status_counts.get('Thất bại', 0),
                'status_breakdown': status_counts
            }
        }
        
        if csv_filename:
            result['csv_file'] = csv_filename
            
        return result
        
    except Exception as e:
        return {'error': str(e)}

# Tool to find project by name
@mcp.tool()
def find_project_by_name(project_name: str, threshold: float = 0.3) -> Dict:
    """
    Tìm dự án theo tên với độ tương đồng
    
    Args:
        project_name: Tên dự án cần tìm
        threshold: Ngưỡng tương đồng tối thiểu (default: 0.3)
    
    Returns:
        Thông tin dự án phù hợp nhất
    """
    try:
        projects = wework_client.fetch_projects()
        best_project, similarity_score = wework_client.find_best_project_match(
            project_name, projects, threshold
        )
        
        if best_project:
            return {
                'found': True,
                'project': best_project,
                'similarity_score': similarity_score,
                'search_term': project_name
            }
        else:
            return {
                'found': False,
                'similarity_score': similarity_score,
                'search_term': project_name,
                'message': f'Không tìm thấy dự án phù hợp với "{project_name}" (ngưỡng: {threshold})'
            }
            
    except Exception as e:
        return {'error': str(e)}

# Tool to get project statistics
@mcp.tool()
def get_project_statistics(project_id: str) -> Dict:
    """
    Lấy thống kê tổng quan về dự án
    
    Args:
        project_id: ID của dự án
    
    Returns:
        Thống kê chi tiết về dự án
    """
    try:
        # Lấy thông tin dự án
        project_info = wework_client.get_project_info(project_id)
        if not project_info:
            return {'error': f'Không tìm thấy dự án với ID: {project_id}'}
        
        # Phân tích tasks
        df = wework_client.get_project_analysis(project_id)
        
        if df.empty:
            return {
                'project_name': project_info['name'],
                'project_id': project_id,
                'statistics': {
                    'total_tasks': 0,
                    'task_breakdown': {},
                    'assignee_breakdown': {},
                    'completion_rate': 0
                }
            }
        
        # Tính các thống kê
        total_tasks = len(df)
        status_counts = df['Trạng thái'].value_counts().to_dict()
        assignee_counts = df['Người thực hiện'].value_counts().to_dict()
        
        # Tính completion rate
        completed = status_counts.get('Hoàn thành', 0)
        completion_rate = (completed / total_tasks * 100) if total_tasks > 0 else 0
        
        # Thống kê theo loại công việc
        task_type_counts = df['Loại công việc'].value_counts().to_dict()
        
        return {
            'project_name': project_info['name'],
            'project_id': project_id,
            'statistics': {
                'total_tasks': total_tasks,
                'task_breakdown': status_counts,
                'assignee_breakdown': assignee_counts,
                'task_type_breakdown': task_type_counts,
                'completion_rate': round(completion_rate, 2),
                'summary': {
                    'completed': status_counts.get('Hoàn thành', 0),
                    'in_progress': status_counts.get('Đang thực hiện', 0),
                    'failed': status_counts.get('Thất bại', 0)
                }
            }
        }
        
    except Exception as e:
        return {'error': str(e)}

if __name__ == "__main__":
    # For development/testing
    mcp.run("stdio")
