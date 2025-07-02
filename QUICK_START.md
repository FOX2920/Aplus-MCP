# 🚀 Quick Start - WeWork MCP Server

## 📝 Tóm tắt

WeWork MCP Server cho phép Claude truy cập và phân tích dữ liệu dự án WeWork. Hỗ trợ cả local và remote deployment.

## ⚡ 1-Click Setup

### Option 1: Local (Windows)

```bash
# 1. Double-click start_server.bat
# 2. Copy nội dung claude_desktop_config.json vào %APPDATA%\Claude\claude_desktop_config.json
# 3. Restart Claude Desktop
```

### Option 2: Remote (Cloud)

```bash
# 1. Install Railway CLI
npm install -g @railway/cli

# 2. Deploy
./deploy_scripts.sh
# Choose option 1

# 3. Set environment variable trên Railway:
# WEWORK_ACCESS_TOKEN=your_token

# 4. Update Claude config với remote URL
```

## 🔧 Files quan trọng

| File                         | Mục đích                 |
| ---------------------------- | ------------------------ |
| `claude_desktop_config.json` | Config cho local Claude  |
| `claude_remote_config.json`  | Config cho remote Claude |
| `deploy_scripts.sh`          | Script deploy tự động    |
| `DEPLOY_GUIDE.md`            | Hướng dẫn chi tiết       |
| `wework_mcp_server.py`       | Local MCP server         |
| `wework_http_server.py`      | Remote HTTP server       |

## 📊 Test ngay

Sau khi setup, test trong Claude:

```
# Local
"Hãy kiểm tra kết nối WeWork của tôi"
"Tìm kiếm dự án có tên 'marketing'"

# Remote
Visit: https://your-app.railway.app/health
```

## ⚠️ Lưu ý quan trọng

1. **Token WeWork**: Thay `your_wework_access_token_here` bằng token thật
2. **Local vs Remote**:
   - Local: Dùng `wework_mcp_server.py` với stdio
   - Remote: Dùng `wework_http_server.py` với HTTP
3. **Security**: Không commit token vào Git

## 📞 Hỗ trợ

- Lỗi local: Check `start_server.bat` và Claude config
- Lỗi remote: Check `/health` endpoint và platform logs
- Token issues: Verify WeWork API access
