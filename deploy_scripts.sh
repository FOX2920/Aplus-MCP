#!/bin/bash

# Deploy scripts cho các cloud platforms

echo "🚀 WeWork MCP Server Deployment Script"
echo "======================================"

# Function để deploy lên Railway
deploy_railway() {
    echo "📦 Deploying to Railway..."
    
    # Check nếu Railway CLI đã cài
    if ! command -v railway &> /dev/null; then
        echo "❌ Railway CLI chưa được cài đặt"
        echo "Cài đặt: npm install -g @railway/cli"
        return 1
    fi
    
    # Login và deploy
    echo "🔑 Login vào Railway..."
    railway login
    
    echo "🚀 Deploying..."
    railway up
    
    echo "✅ Deployment hoàn thành!"
    echo "🌐 URL: https://$(railway domain).railway.app"
}

# Function để build Docker image
build_docker() {
    echo "🐳 Building Docker image..."
    
    # Build image
    docker build -t wework-mcp-server .
    
    # Tag cho Docker Hub (nếu cần)
    read -p "Docker Hub username (để trống nếu không push): " dockerhub_user
    if [ ! -z "$dockerhub_user" ]; then
        docker tag wework-mcp-server $dockerhub_user/wework-mcp-server:latest
        echo "🚢 Pushing to Docker Hub..."
        docker push $dockerhub_user/wework-mcp-server:latest
    fi
    
    echo "✅ Docker build hoàn thành!"
}

# Function để deploy với docker-compose
deploy_docker_compose() {
    echo "🐳 Starting with Docker Compose..."
    
    # Kiểm tra .env file
    if [ ! -f ".env" ]; then
        echo "⚠️  File .env không tồn tại"
        echo "Tạo file .env với WEWORK_ACCESS_TOKEN=your_token"
        return 1
    fi
    
    # Start services
    docker-compose up -d --build
    
    echo "✅ Services đã khởi động!"
    echo "🌐 Local URL: http://localhost:8000"
    echo "📊 Health check: http://localhost:8000/health"
}

# Function để setup Heroku
setup_heroku() {
    echo "🟣 Setting up Heroku..."
    
    # Check Heroku CLI
    if ! command -v heroku &> /dev/null; then
        echo "❌ Heroku CLI chưa được cài đặt"
        return 1
    fi
    
    # Tạo app
    read -p "Tên app Heroku: " app_name
    heroku create $app_name
    
    # Set environment variables
    read -p "WeWork Access Token: " wework_token
    heroku config:set WEWORK_ACCESS_TOKEN=$wework_token --app $app_name
    
    # Deploy
    git push heroku main
    
    echo "✅ Heroku deployment hoàn thành!"
    echo "🌐 URL: https://$app_name.herokuapp.com"
}

# Menu chính
echo ""
echo "Chọn deployment option:"
echo "1) Railway (Recommended)"
echo "2) Docker Build"
echo "3) Docker Compose (Local)"
echo "4) Heroku Setup"
echo "5) Exit"
echo ""

read -p "Nhập lựa chọn (1-5): " choice

case $choice in
    1)
        deploy_railway
        ;;
    2)
        build_docker
        ;;
    3)
        deploy_docker_compose
        ;;
    4)
        setup_heroku
        ;;
    5)
        echo "👋 Goodbye!"
        exit 0
        ;;
    *)
        echo "❌ Lựa chọn không hợp lệ"
        exit 1
        ;;
esac 