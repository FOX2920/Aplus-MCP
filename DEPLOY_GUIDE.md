# 🚀 Hướng dẫn Deploy WeWork MCP Server

## 📋 Tổng quan

Tài liệu này hướng dẫn cách deploy WeWork MCP Server lên các cloud platforms để Claude có thể kết nối từ xa.

## ⚡ Quick Start với Railway (Khuyến nghị)

### Bước 1: Chuẩn bị

```bash
# Cài Railway CLI
npm install -g @railway/cli

# Login
railway login
```

### Bước 2: Deploy

```bash
# Chạy script deploy
chmod +x deploy_scripts.sh
./deploy_scripts.sh
# Chọn option 1 (Railway)
```

### Bước 3: Cấu hình Environment

Trên Railway Dashboard:

1. Vào project vừa tạo
2. Variables → Add Variable
3. Thêm: `WEWORK_ACCESS_TOKEN=your_actual_token`
4. Deploy lại

### Bước 4: Cấu hình Claude

```json
{
  "mcpServers": {
    "wework-remote": {
      "command": "curl",
      "args": [
        "-X",
        "POST",
        "https://your-app.railway.app/api/test",
        "-H",
        "Content-Type: application/json"
      ]
    }
  }
}
```

## 🐳 Deploy với Docker

### Local Testing

```bash
# Build và test
docker build -t wework-mcp .
docker run -p 8000:8000 -e WEWORK_ACCESS_TOKEN=your_token wework-mcp

# Hoặc với docker-compose
docker-compose up --build
```

### Deploy lên Cloud

```bash
# Tag và push
docker tag wework-mcp your-username/wework-mcp
docker push your-username/wework-mcp
```

## 🌐 Platform-specific Instructions

### Railway

- ✅ Dockerfile tự động detect
- ✅ Environment variables easy setup
- ✅ Custom domain miễn phí
- ✅ Auto-deploy từ Git

**URL format**: `https://your-app.railway.app`

### Render

1. Connect GitHub repo
2. Environment: Docker
3. Thêm environment variables
4. Deploy

**URL format**: `https://your-app.onrender.com`

### Heroku

```bash
# Setup
heroku create your-app-name
heroku config:set WEWORK_ACCESS_TOKEN=your_token
git push heroku main
```

**URL format**: `https://your-app.herokuapp.com`

### DigitalOcean App Platform

1. Import từ GitHub
2. Chọn Dockerfile
3. Thêm environment variables
4. Deploy

## 🔧 Endpoints có sẵn

### Health Check

```
GET /health
```

### Test Connection

```
GET /api/test
```

### Search Projects

```
GET /api/projects?search=project_name
```

### Project Details

```
POST /api/project/details
{
  "project_id": "12345"
}
```

### Analyze Tasks

```
POST /api/project/analyze
{
  "project_id": "12345",
  "export_csv": false
}
```

## 🔐 Security & Environment Variables

### Required Variables

- `WEWORK_ACCESS_TOKEN`: WeWork API token
- `PORT`: Server port (mặc định: 8000)
- `HOST`: Bind address (mặc định: 0.0.0.0)

### Optional Variables

- `LOG_LEVEL`: Logging level (INFO/DEBUG/ERROR)
- `SERVER_MODE`: http hoặc stdio

## 🐛 Troubleshooting

### Common Issues

**1. Health check fails**

```bash
curl https://your-app.railway.app/health
```

**2. WeWork connection fails**

- Kiểm tra WEWORK_ACCESS_TOKEN
- Test với `/api/test` endpoint

**3. CORS errors**

- Server đã cấu hình CORS headers
- Kiểm tra browser console

**4. Port binding errors**

- Đảm bảo PORT environment variable đúng
- Railway/Render tự động assign port

### Logs

```bash
# Railway
railway logs

# Docker
docker logs container_name

# Heroku
heroku logs --tail
```

## 📱 Monitoring

### Health Checks

Tất cả platforms đều có endpoint `/health` để monitor:

```json
{
  "status": "healthy",
  "service": "WeWork MCP Server",
  "wework_client": true,
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### Performance

- Response time: < 2s cho most endpoints
- Memory usage: ~100-200MB
- CPU: Low usage khi idle

## 🆘 Support

Nếu gặp vấn đề:

1. Check logs của platform
2. Test `/health` endpoint
3. Verify environment variables
4. Check WEWORK_ACCESS_TOKEN validity

## 🎯 Next Steps

Sau khi deploy thành công:

1. ✅ Test tất cả endpoints
2. ✅ Cấu hình Claude với remote URL
3. ✅ Setup monitoring/alerts
4. ✅ Document API cho team
