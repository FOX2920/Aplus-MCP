@echo off

REM Deploy scripts cho các cloud platforms

echo 🚀 WeWork MCP Server Deployment Script
echo ======================================

echo.
echo Chọn deployment option:
echo 1) Railway (Recommended)
echo 2) Docker Build  
echo 3) Docker Compose (Local)
echo 4) Heroku Setup
echo 5) Exit
echo.

set /p choice="Nhập lựa chọn (1-5): "

if "%choice%"=="1" goto deploy_railway
if "%choice%"=="2" goto build_docker
if "%choice%"=="3" goto deploy_docker_compose
if "%choice%"=="4" goto setup_heroku
if "%choice%"=="5" goto exit_script
goto invalid_choice

:deploy_railway
echo 📦 Deploying to Railway...

REM Check nếu Railway CLI đã cài
where railway >nul 2>&1
if errorlevel 1 (
    echo ❌ Railway CLI chưa được cài đặt
    echo Cài đặt: npm install -g @railway/cli
    pause
    goto end
)

echo 🔑 Login vào Railway...
railway login

echo 🚀 Deploying...
railway up

echo ✅ Deployment hoàn thành!
echo 🌐 Check Railway dashboard for URL
goto end

:build_docker
echo 🐳 Building Docker image...

docker build -t wework-mcp-server .

set /p dockerhub_user="Docker Hub username (để trống nếu không push): "
if not "%dockerhub_user%"=="" (
    docker tag wework-mcp-server %dockerhub_user%/wework-mcp-server:latest
    echo 🚢 Pushing to Docker Hub...
    docker push %dockerhub_user%/wework-mcp-server:latest
)

echo ✅ Docker build hoàn thành!
goto end

:deploy_docker_compose
echo 🐳 Starting with Docker Compose...

if not exist ".env" (
    echo ⚠️  File .env không tồn tại
    echo Tạo file .env với WEWORK_ACCESS_TOKEN=your_token
    pause
    goto end
)

docker-compose up -d --build

echo ✅ Services đã khởi động!
echo 🌐 Local URL: http://localhost:8000
echo 📊 Health check: http://localhost:8000/health
goto end

:setup_heroku
echo 🟣 Setting up Heroku...

where heroku >nul 2>&1
if errorlevel 1 (
    echo ❌ Heroku CLI chưa được cài đặt
    pause
    goto end
)

set /p app_name="Tên app Heroku: "
heroku create %app_name%

set /p wework_token="WeWork Access Token: "
heroku config:set WEWORK_ACCESS_TOKEN=%wework_token% --app %app_name%

git push heroku main

echo ✅ Heroku deployment hoàn thành!
echo 🌐 URL: https://%app_name%.herokuapp.com
goto end

:invalid_choice
echo ❌ Lựa chọn không hợp lệ
goto end

:exit_script
echo 👋 Goodbye!
goto end

:end
pause 