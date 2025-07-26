@echo off
echo 🚀 Starting MSPR Bloc 4 Autonomous Application
echo ==============================================

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: Docker is not running. Please start Docker Desktop and try again.
    pause
    exit /b 1
)

REM Check if Docker Compose is available
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: docker-compose is not available. Please install Docker Desktop and try again.
    pause
    exit /b 1
)

echo 📋 Checking prerequisites...
echo ✅ Docker is running
echo ✅ Docker Compose is available

REM Stop any existing containers
echo.
echo 🧹 Cleaning up existing containers...
docker-compose down --remove-orphans

REM Build and start all services
echo.
echo 🏗️  Building and starting all services...
echo Services that will be started:
echo   - RabbitMQ (Message Broker) - Port 5672, Management: 15672
echo   - PostgreSQL (Clients DB) - Port 5432
echo   - PostgreSQL (Orders DB) - Port 5431
echo   - API Clients - Port 8002
echo   - API Orders - Port 8000
echo   - API Products - Port 8001
echo   - Frontend - Port 80
echo   - Caddy Reverse Proxy - Port 8085
echo.

docker-compose up --build -d

REM Wait for services to be healthy
echo.
echo ⏳ Waiting for services to start...
timeout /t 10 /nobreak >nul

REM Check service health
echo.
echo 🔍 Checking service health...

set healthy_services=0
set total_services=4

REM Check each service
curl -f http://localhost:15672 >nul 2>&1
if not errorlevel 1 (
    echo ✅ RabbitMQ is healthy
    set /a healthy_services+=1
) else (
    echo ⚠️  RabbitMQ might still be starting...
)

curl -f http://localhost:8002/docs >nul 2>&1
if not errorlevel 1 (
    echo ✅ API Clients is healthy
    set /a healthy_services+=1
) else (
    echo ⚠️  API Clients might still be starting...
)

curl -f http://localhost:8000/docs >nul 2>&1
if not errorlevel 1 (
    echo ✅ API Orders is healthy
    set /a healthy_services+=1
) else (
    echo ⚠️  API Orders might still be starting...
)

curl -f http://localhost:8001/docs >nul 2>&1
if not errorlevel 1 (
    echo ✅ API Products is healthy
    set /a healthy_services+=1
) else (
    echo ⚠️  API Products might still be starting...
)

echo.
echo 📊 Service Status Summary:
echo ==========================================
echo 🌐 Frontend: http://localhost
echo 🔄 Caddy Proxy: http://localhost:8085
echo 👥 API Clients: http://localhost:8002/docs
echo 📦 API Orders: http://localhost:8000/docs
echo 🛍️  API Products: http://localhost:8001/docs
echo 🐰 RabbitMQ Management: http://localhost:15672 (guest/guest)
echo.

if %healthy_services% equ %total_services% (
    echo 🎉 All services are running successfully!
    echo.
    echo 💡 Useful commands:
    echo    - View logs: docker-compose logs -f
    echo    - Stop application: docker-compose down
    echo    - Restart application: docker-compose restart
) else (
    echo ⚠️  Some services might still be starting. Use 'docker-compose logs' to check status.
)

echo.
echo 🔗 Quick Links:
echo    - Client Management: http://localhost:8002/docs
echo    - Order Management: http://localhost:8000/docs
echo    - Product Catalog: http://localhost:8001/docs
echo    - Message Queue: http://localhost:15672
echo.
echo ✨ Application is ready!
echo.
echo Press any key to continue...
pause >nul