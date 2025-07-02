import requests
import pandas as pd
from datetime import datetime
import time
import re
from bs4 import BeautifulSoup
from collections import defaultdict
from typing import Dict, List, Optional, Tuple, Any

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    import numpy as np
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

class TaskAnalyzer:
    """Phân tích và xử lý dữ liệu task từ WeWork"""
    
    @staticmethod
    def convert_timestamp(timestamp) -> Optional[str]:
        """Chuyển đổi timestamp thành định dạng ngày"""
        try:
            if timestamp and str(timestamp).strip() and int(timestamp) != 0:
                return datetime.fromtimestamp(int(timestamp)).strftime('%Y-%m-%d')
        except (ValueError, TypeError):
            pass
        return None

    @staticmethod
    def clean_html_content(content) -> str:
        """Loại bỏ HTML tags và định dạng nội dung"""
        if not isinstance(content, str):
            return ""
        
        # Use BeautifulSoup to remove all HTML/CSS styling
        soup = BeautifulSoup(content, 'html.parser')
        
        # Remove all style attributes
        for tag in soup.find_all(style=True):
            del tag['style']
        
        # Convert specific HTML elements to plain text
        text = str(soup)
        replacements = {
            '<p>': '', '</p>': '\n',
            '<ul>': '', '</ul>': '',
            '<li>': '- ', '</li>': '\n',
            '<br>': '\n', '<br/>': '\n',
            '<ol>': '', '</ol>': '',
            '<span>': '', '</span>': '',
            '<strong>': '', '</strong>': '',
            '&nbsp;': ' '
        }
        for old, new in replacements.items():
            text = text.replace(old, new)
        
        # Remove any remaining HTML tags
        text = re.sub('<[^<]+?>', '', text)
        
        # Clean up extra whitespace
        text = ' '.join(text.split())
        return text.strip()

    def parse_tasks(self, tasks: List[Dict], is_subtask: bool = False) -> pd.DataFrame:
        """Parse tasks data thành DataFrame"""
        if not tasks:
            return pd.DataFrame()
        
        parsed_data = []
        for task in tasks:
            try:
                content = self.clean_html_content(task.get('content', ''))
                
                # Handle tasklist name
                origin_task_name = ''
                if isinstance(task.get('tasklist'), dict):
                    origin_task_name = task['tasklist'].get('name', '')
                
                # Handle origin export name
                origin_task = ''
                if isinstance(task.get('origin_export'), dict):
                    origin_task = task['origin_export'].get('name', '')
                    
                # Handle result content
                result = ''
                if isinstance(task.get('result'), dict):
                    result = task['result'].get('content', '')
                
                # Fix for failed reason extraction
                failed_reason = ''
                if isinstance(task.get('data'), dict):
                    data_dict = task['data']
                    if isinstance(data_dict.get('failed_reason'), dict):
                        failed_reason = data_dict['failed_reason'].get('reason', '')
                    elif isinstance(data_dict.get('failed_reason'), str):
                        failed_reason = data_dict['failed_reason']
    
                # Handle deadline date
                deadline = ''
                if int(task.get('has_deadline', '0')) == 1:
                    deadline = self.convert_timestamp(task.get('deadline'))
                
                # Handle completion date
                completion_date = ''
                if task.get('completed_time') and int(task.get('completed_time', 0)) != 0:
                    completion_date = self.convert_timestamp(task.get('completed_time'))
                
                # Determine status based on completion and failed_reason
                status = 'Thất bại' if failed_reason else ('Hoàn thành' if task.get('complete') == '100.00' else 'Đang thực hiện')
                
                # Creation date
                created_date = self.convert_timestamp(task.get('start_time'))
                
                task_data = {
                    'Loại công việc': origin_task_name,
                    'Tên công việc': origin_task if is_subtask else task.get('name', ''),
                    'Công việc con': task.get('name', '') if is_subtask else "",
                    'Người thực hiện': task.get('username', ''),
                    'Người liên quan': ', '.join([follower.get('username', '') for follower in task.get('followers', [])]),
                    'Mô tả công việc': content,
                    'Trạng thái': status,
                    'Kết quả đạt được': result,
                    'Lí do thất bại': failed_reason,
                    'Ngày bắt đầu': created_date,
                    'Deadline': deadline,
                    'Ngày hoàn thành': completion_date,
                    'Metatype': task.get('metatype', ''),
                }
                
                parsed_data.append(task_data)
                
            except Exception as e:
                print(f"Error parsing task: {str(e)}")
                continue
        
        return pd.DataFrame(parsed_data)

    def analyze_tasks(self, response_data: Dict) -> pd.DataFrame:
        """Phân tích dữ liệu tasks và trả về DataFrame"""
        try:
            df = self.parse_tasks(response_data.get('tasks', []))
            df_sub = self.parse_tasks(response_data.get('subtasks', []), is_subtask=True)
            
            if df.empty and df_sub.empty:
                return pd.DataFrame()
            
            final_df = pd.concat([df, df_sub], ignore_index=True)
            final_df = final_df.map(lambda x: str(x).strip() if isinstance(x, str) else x)
            final_df = final_df.dropna(axis=1, how='all')
            final_df = final_df.loc[:, (final_df != "").any(axis=0)]
            
            if not final_df.empty and 'Tên công việc' in final_df.columns:
                final_df = final_df.sort_values(by='Tên công việc').reset_index(drop=True)
            
            return final_df
        except Exception as e:
            print(f"Error analyzing tasks: {str(e)}")
            return pd.DataFrame()


class WeWorkClient:
    """
    Client để tương tác với WeWork API
    """
    
    BASE_URL = "https://wework.base.vn/extapi/v3"
    
    def __init__(self, access_token: str):
        """
        Khởi tạo WeWork client
        
        Args:
            access_token (str): Access token để truy cập WeWork API
        """
        self.access_token = access_token
        self.task_analyzer = TaskAnalyzer()
        
    def _fetch_data_with_retry(self, url: str, payload: Dict, max_retries: int = 3) -> Optional[Dict]:
        """Gửi request với retry logic"""
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        
        for attempt in range(max_retries):
            try:
                response = requests.post(url, headers=headers, data=payload, timeout=30)
                response.raise_for_status()
                return response.json()
            except requests.exceptions.RequestException as e:
                if attempt < max_retries - 1:
                    time.sleep(2)
                    continue
                else:
                    print(f"Error fetching data: {str(e)}")
                    return None
        return None

    def fetch_projects(self) -> List[Dict]:
        """Lấy danh sách tất cả projects"""
        url = f"{self.BASE_URL}/project/list"
        data = self._fetch_data_with_retry(url, {'access_token': self.access_token})
        return data.get('projects', []) if data else []

    def fetch_project_details(self, project_id: str) -> Optional[Dict]:
        """Lấy chi tiết của một project"""
        url = f"{self.BASE_URL}/project/get.full"
        return self._fetch_data_with_retry(url, {
            'access_token': self.access_token,
            'id': project_id
        })

    def find_best_project_match(self, target_name: str, projects: List[Dict], threshold: float = 0.3) -> Tuple[Optional[Dict], float]:
        """
        Tìm dự án phù hợp nhất bằng cosine similarity (nếu sklearn có sẵn)
        hoặc simple string matching
        """
        if not projects:
            return None, 0
        
        # Tạo danh sách tên dự án
        project_names = [project['name'].lower() for project in projects]
        target_name_lower = target_name.lower()
        
        # Kiểm tra khớp chính xác trước
        for i, name in enumerate(project_names):
            if target_name_lower in name or name in target_name_lower:
                return projects[i], 1.0
        
        # Sử dụng TF-IDF và cosine similarity nếu sklearn có sẵn
        if SKLEARN_AVAILABLE:
            try:
                vectorizer = TfidfVectorizer(analyzer='char', ngram_range=(2, 3))
                all_names = project_names + [target_name_lower]
                tfidf_matrix = vectorizer.fit_transform(all_names)
                
                # Tính cosine similarity giữa target và tất cả project names
                target_vector = tfidf_matrix[-1]
                project_vectors = tfidf_matrix[:-1]
                similarities = cosine_similarity(target_vector, project_vectors).flatten()
                
                # Tìm similarity cao nhất
                best_idx = np.argmax(similarities)
                best_similarity = similarities[best_idx]
                
                if best_similarity >= threshold:
                    return projects[best_idx], best_similarity
                else:
                    return None, best_similarity
                    
            except Exception as e:
                print(f"Lỗi khi tính cosine similarity: {e}")
        
        # Fallback: Simple string similarity
        best_match = None
        best_score = 0
        
        for project in projects:
            name_lower = project['name'].lower()
            # Simple similarity based on common characters
            common_chars = len(set(target_name_lower) & set(name_lower))
            total_chars = len(set(target_name_lower) | set(name_lower))
            similarity = common_chars / total_chars if total_chars > 0 else 0
            
            if similarity > best_score and similarity >= threshold:
                best_match = project
                best_score = similarity
        
        return best_match, best_score

    def search_projects(self, search_text: str, limit: int = 10) -> List[Dict]:
        """
        Tìm kiếm projects theo tên
        """
        projects = self.fetch_projects()
        if not projects:
            return []
        
        # Tìm projects phù hợp
        matches = []
        for project in projects:
            project_name = project['name'].lower()
            search_lower = search_text.lower()
            
            # Exact match hoặc partial match
            if search_lower in project_name or project_name in search_lower:
                matches.append({
                    'project': project,
                    'similarity': 1.0 if search_lower == project_name else 0.8
                })
            else:
                # Sử dụng find_best_project_match
                _, similarity = self.find_best_project_match(search_text, [project])
                if similarity > 0.3:
                    matches.append({
                        'project': project,
                        'similarity': similarity
                    })
        
        # Sắp xếp theo similarity và giới hạn kết quả
        matches.sort(key=lambda x: x['similarity'], reverse=True)
        return [match['project'] for match in matches[:limit]]

    def get_project_analysis(self, project_id: str) -> pd.DataFrame:
        """
        Lấy và phân tích dữ liệu project
        """
        project_data = self.fetch_project_details(project_id)
        
        if project_data:
            return self.task_analyzer.analyze_tasks(project_data)
        else:
            return pd.DataFrame()

    def get_project_info(self, project_id: str) -> Optional[Dict]:
        """Lấy thông tin cơ bản của project"""
        projects = self.fetch_projects()
        for project in projects:
            if project['id'] == project_id:
                return project
        return None
