# WeWork MCP Server

A Model Context Protocol (MCP) server that provides access to WeWork project management data through Claude and other LLM clients. This server exposes WeWork project information, task analysis, and project management tools.

## Features

🔍 **Project Search**

- Search projects by name with fuzzy matching
- Find best matching projects using cosine similarity
- Get list of all available projects

📊 **Project Analysis**

- Detailed task analysis within projects
- Completion progress statistics
- Task categorization by status and assignee
- Export data to CSV files

📋 **Information Management**

- Get detailed project information
- Track deadlines and completion dates
- Analyze task failure reasons

## Prerequisites

- Python 3.12+
- WeWork API access token
- uv package manager

## Installation

1. Clone this repository:

```bash
git clone <repository-url>
cd wework-mcp-server
```

2. Install dependencies:

```bash
uv sync
```

## Configuration

### 1. WeWork Access Token

**Option A: Environment Variable (Recommended)**

Create a `.env` file in the project root:

```env
WEWORK_ACCESS_TOKEN=your_actual_wework_token_here
```

**Option B: Direct Configuration**

Update the `WEWORK_ACCESS_TOKEN` in `wework_mcp_server.py` with your actual WeWork API token.

### 2. Claude Desktop Configuration

Add this server to your Claude Desktop configuration file:

**Windows**: `%APPDATA%/Claude/claude_desktop_config.json`
**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Linux**: `~/.config/claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "WeWork Task Analysis Server": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/wework-mcp-server",
        "run",
        "wework_mcp_server.py"
      ]
    }
  }
}
```

### 3. Restart Claude Desktop

After adding the configuration, restart Claude Desktop to apply changes.

## Usage

### Example Prompts

- "Show me all available projects"
- "Find project 'marketing campaign'"
- "Analyze tasks for project ID 12345"
- "Get statistics for the development project"
- "Export task analysis to CSV"

## Available Resources

- `file://projects/available` - List all available WeWork projects

## Available Tools

- `search_projects` - Search for projects by name
- `find_project_by_name` - Find project with similarity matching
- `get_project_details` - Get detailed information about a specific project
- `analyze_project_tasks` - Analyze tasks within a project
- `get_project_statistics` - Get comprehensive project statistics

## Development

### Run Server for Testing

```bash
# Using uv
uv run wework_mcp_server.py

# Or with Python
python wework_mcp_server.py

# Run tests
python test_wework_server.py
```

### Data Structure

#### Task Analysis DataFrame Columns

| Column             | Description                           |
| ------------------ | ------------------------------------- |
| `Loại công việc`   | Task category                         |
| `Tên công việc`    | Task name                             |
| `Công việc con`    | Subtask (if any)                      |
| `Người thực hiện`  | Assignee                              |
| `Người liên quan`  | Related people                        |
| `Mô tả công việc`  | Task description                      |
| `Trạng thái`       | Status (Completed/In Progress/Failed) |
| `Kết quả đạt được` | Achievement results                   |
| `Lí do thất bại`   | Failure reason                        |
| `Ngày bắt đầu`     | Start date                            |
| `Deadline`         | Due date                              |
| `Ngày hoàn thành`  | Completion date                       |

## Troubleshooting

### Common Issues

1. **Access token expired**: Update token in `.env` file or `wework_mcp_server.py`
2. **Dependencies not found**: Run `uv sync` to install all dependencies
3. **Claude Desktop doesn't recognize server**: Check file paths in config and restart Claude Desktop
4. **CSV encoding issues**: Files are exported with UTF-8-BOM encoding

### Debug Mode

```bash
python wework_mcp_server.py --debug
```

## Security Notes

⚠️ **Important**: For production use:

- **Always use environment variables** (`.env` file) instead of hardcoding tokens
- Add `.env` to your `.gitignore` to prevent committing sensitive data
- Do not commit access tokens to git repository
- Use only in trusted environments
- Regularly rotate your access tokens

## License

This project is licensed under the MIT License.

## Acknowledgments

- WeWork for providing the project management platform and API
- Model Context Protocol team for the MCP framework
