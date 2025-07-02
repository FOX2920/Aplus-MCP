from mcp.server.fastmcp import FastMCP
from data.wework_client import WeWorkClient
from typing import Dict, List, Optional, Any
import pandas as pd
import os
from dotenv import load_dotenv
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# Access token từ environment hoặc fallback
WEWORK_ACCESS_TOKEN = os.getenv('WEWORK_ACCESS_TOKEN', '5654-FCVE2Z8T53L7WTFKVXFP2PTM9MUABP6WRU5LCY6E365RY6TCSRYY4GTAJ48WJEMV-THT9F7ZZNPVMGBNV3FTB8P2QZF5HN2FW9HKV7J64MXDV8BQWN43SK3DUCBJP6JT2')

# Create MCP server
mcp = FastMCP("WeWork Project Management Server")

# Initialize WeWork client with error handling
try:
    wework_client = WeWorkClient(WEWORK_ACCESS_TOKEN)
    logger.info("WeWork client initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize WeWork client: {e}")
    wework_client = None

# Resource to get available projects
@mcp.resource("file://projects/available")
def get_available_projects() -> str:
    """Lấy danh sách tất cả các dự án có sẵn"""
    try:
        if not wework_client:
            return "Error: WeWork client not initialized"
        
        projects = wework_client.fetch_projects()
        result = {
            'projects': projects,
            'total_count': len(projects)
        }
        logger.info(f"Found {len(projects)} projects")
        
        # Return as formatted string for MCP resource
        if projects:
            project_list = "\n".join([f"- {p.get('name', 'Unknown')} (ID: {p.get('id', 'Unknown')})" for p in projects])
            return f"Available Projects ({len(projects)} total):\n{project_list}"
        else:
            return "No projects found or error accessing projects"
            
    except Exception as e:
        logger.error(f"Error in get_available_projects: {e}")
        return f"Error: {str(e)}"

# Tool to search projects
@mcp.tool()
def search_projects(search_text: str, limit: int = 10) -> Dict[str, Any]:
    """
    Tìm kiếm dự án theo tên
    
    Args:
        search_text: Text để tìm kiếm trong tên dự án
        limit: Số lượng kết quả tối đa (default: 10)
    
    Returns:
        Danh sách các dự án phù hợp
    """
    try:
        if not wework_client:
            return {'error': 'WeWork client not initialized'}
        
        logger.info(f"Searching projects with text: {search_text}")
        results = wework_client.search_projects(search_text=search_text, limit=limit)
        
        return {
            'success': True,
            'search_text': search_text,
            'results': results,
            'count': len(results)
        }
    except Exception as e:
        logger.error(f"Error in search_projects: {e}")
        return {'error': str(e), 'success': False}

# Tool to get project details
@mcp.tool()
def get_project_details(project_id: str) -> Dict[str, Any]:
    """
    Lấy chi tiết của một dự án
    
    Args:
        project_id: ID của dự án
    
    Returns:
        Chi tiết dự án bao gồm thông tin cơ bản
    """
    try:
        if not wework_client:
            return {'error': 'WeWork client not initialized'}
        
        logger.info(f"Getting project details for ID: {project_id}")
        project_info = wework_client.get_project_info(project_id)
        
        if project_info:
            return {
                'success': True,
                'project': project_info
            }
        else:
            return {
                'error': f'Không tìm thấy dự án với ID: {project_id}',
                'success': False
            }
    except Exception as e:
        logger.error(f"Error in get_project_details: {e}")
        return {'error': str(e), 'success': False}

# Tool to analyze project tasks
@mcp.tool()
def analyze_project_tasks(project_id: str, export_csv: bool = False) -> Dict[str, Any]:
    """
    Phân tích các tasks trong dự án
    
    Args:
        project_id: ID của dự án
        export_csv: Có xuất file CSV không (default: False)
    
    Returns:
        Phân tích tasks dưới dạng dictionary
    """
    try:
        if not wework_client:
            return {'error': 'WeWork client not initialized'}
        
        logger.info(f"Analyzing tasks for project ID: {project_id}")
        
        # Lấy thông tin dự án
        project_info = wework_client.get_project_info(project_id)
        if not project_info:
            return {
                'error': f'Không tìm thấy dự án với ID: {project_id}',
                'success': False
            }
        
        # Phân tích tasks
        df = wework_client.get_project_analysis(project_id)
        
        if df.empty:
            return {
                'success': True,
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
        status_counts = df['Trạng thái'].value_counts().to_dict() if 'Trạng thái' in df.columns else {}
        
        # Chuyển DataFrame thành dictionary
        tasks_data = df.to_dict(orient='records')
        
        # Xuất CSV nếu được yêu cầu
        csv_filename = None
        if export_csv:
            csv_filename = f"{project_info['name']}_tasks_analysis.csv"
            try:
                df.to_csv(csv_filename, index=False, encoding='utf-8-sig')
                logger.info(f"CSV exported to: {csv_filename}")
            except Exception as csv_error:
                logger.error(f"Failed to export CSV: {csv_error}")
        
        result = {
            'success': True,
            'project_name': project_info['name'],
            'project_id': project_id,
            'tasks': tasks_data,
            'total_tasks': len(df),
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
        logger.error(f"Error in analyze_project_tasks: {e}")
        return {'error': str(e), 'success': False}

# Tool to find project by name
@mcp.tool()
def find_project_by_name(project_name: str, threshold: float = 0.3) -> Dict[str, Any]:
    """
    Tìm dự án theo tên với độ tương đồng
    
    Args:
        project_name: Tên dự án cần tìm
        threshold: Ngưỡng tương đồng tối thiểu (default: 0.3)
    
    Returns:
        Thông tin dự án phù hợp nhất
    """
    try:
        if not wework_client:
            return {'error': 'WeWork client not initialized'}
        
        logger.info(f"Finding project by name: {project_name}")
        projects = wework_client.fetch_projects()
        
        if not projects:
            return {
                'error': 'No projects available or failed to fetch projects',
                'success': False
            }
        
        best_project, similarity_score = wework_client.find_best_project_match(
            project_name, projects, threshold
        )
        
        if best_project:
            return {
                'success': True,
                'found': True,
                'project': best_project,
                'similarity_score': similarity_score,
                'search_term': project_name
            }
        else:
            return {
                'success': True,
                'found': False,
                'similarity_score': similarity_score,
                'search_term': project_name,
                'message': f'Không tìm thấy dự án phù hợp với "{project_name}" (ngưỡng: {threshold})',
                'available_projects': [p.get('name', 'Unknown') for p in projects[:5]]  # Show first 5 for reference
            }
            
    except Exception as e:
        logger.error(f"Error in find_project_by_name: {e}")
        return {'error': str(e), 'success': False}

# Tool to get project statistics
@mcp.tool()
def get_project_statistics(project_id: str) -> Dict[str, Any]:
    """
    Lấy thống kê tổng quan về dự án
    
    Args:
        project_id: ID của dự án
    
    Returns:
        Thống kê chi tiết về dự án
    """
    try:
        if not wework_client:
            return {'error': 'WeWork client not initialized'}
        
        logger.info(f"Getting statistics for project ID: {project_id}")
        
        # Lấy thông tin dự án
        project_info = wework_client.get_project_info(project_id)
        if not project_info:
            return {
                'error': f'Không tìm thấy dự án với ID: {project_id}',
                'success': False
            }
        
        # Phân tích tasks
        df = wework_client.get_project_analysis(project_id)
        
        if df.empty:
            return {
                'success': True,
                'project_name': project_info['name'],
                'project_id': project_id,
                'statistics': {
                    'total_tasks': 0,
                    'task_breakdown': {},
                    'assignee_breakdown': {},
                    'completion_rate': 0
                }
            }
        
        # Tính các thống kê với kiểm tra column tồn tại
        total_tasks = len(df)
        status_counts = df['Trạng thái'].value_counts().to_dict() if 'Trạng thái' in df.columns else {}
        assignee_counts = df['Người thực hiện'].value_counts().to_dict() if 'Người thực hiện' in df.columns else {}
        task_type_counts = df['Loại công việc'].value_counts().to_dict() if 'Loại công việc' in df.columns else {}
        
        # Tính completion rate
        completed = status_counts.get('Hoàn thành', 0)
        completion_rate = (completed / total_tasks * 100) if total_tasks > 0 else 0
        
        return {
            'success': True,
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
        logger.error(f"Error in get_project_statistics: {e}")
        return {'error': str(e), 'success': False}

# Tool to test connection
@mcp.tool()
def test_connection() -> Dict[str, Any]:
    """
    Test kết nối với WeWork API
    
    Returns:
        Thông tin về trạng thái kết nối
    """
    try:
        if not wework_client:
            return {
                'success': False,
                'error': 'WeWork client not initialized',
                'token_available': bool(WEWORK_ACCESS_TOKEN)
            }
        
        logger.info("Testing WeWork API connection")
        projects = wework_client.fetch_projects()
        
        return {
            'success': True,
            'connection_status': 'Connected',
            'projects_count': len(projects) if projects else 0,
            'token_available': bool(WEWORK_ACCESS_TOKEN),
            'sample_projects': [p.get('name', 'Unknown') for p in (projects[:3] if projects else [])]
        }
        
    except Exception as e:
        logger.error(f"Error in test_connection: {e}")
        return {
            'success': False,
            'error': str(e),
            'token_available': bool(WEWORK_ACCESS_TOKEN)
        }

if __name__ == "__main__":
    # For development/testing
    mcp.run("stdio")