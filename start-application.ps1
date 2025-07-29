#!/usr/bin/env pwsh

Write-Host "🚀 Starting MSPR Bloc 4 Autonomous Application" -ForegroundColor Green
Write-Host "==============================================" -ForegroundColor Green

# Check if Docker is running
try {
    docker info | Out-Null
    Write-Host "✅ Docker is running" -ForegroundColor Green
} catch {
    Write-Host "❌ Error: Docker is not running. Please start Docker Desktop and try again." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if Docker Compose is available
try {
    docker-compose --version | Out-Null
    Write-Host "✅ Docker Compose is available" -ForegroundColor Green
} catch {
    Write-Host "❌ Error: docker-compose is not available. Please install Docker Desktop and try again." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "📋 Checking prerequisites..." -ForegroundColor Yellow

# Stop any existing containers
Write-Host ""
Write-Host "🧹 Cleaning up existing containers..." -ForegroundColor Yellow
docker-compose down --remove-orphans

# Build and start all services
Write-Host ""
Write-Host "🏗️  Building and starting all services..." -ForegroundColor Yellow
Write-Host "Services that will be started:" -ForegroundColor Cyan
Write-Host "  - RabbitMQ (Message Broker) - Port 5672, Management: 15672" -ForegroundColor Cyan
Write-Host "  - PostgreSQL (Clients DB) - Port 5432" -ForegroundColor Cyan
Write-Host "  - PostgreSQL (Orders DB) - Port 5431" -ForegroundColor Cyan
Write-Host "  - API Clients - Port 8002" -ForegroundColor Cyan
Write-Host "  - API Orders - Port 8000" -ForegroundColor Cyan
Write-Host "  - API Products - Port 8001" -ForegroundColor Cyan
Write-Host "  - Frontend - Port 80" -ForegroundColor Cyan
Write-Host "  - Caddy Reverse Proxy - Port 8085" -ForegroundColor Cyan
Write-Host ""

docker-compose up --build -d

# Wait for services to be healthy
Write-Host ""
Write-Host "⏳ Waiting for services to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Check service health
Write-Host ""
Write-Host "🔍 Checking service health..." -ForegroundColor Yellow

$healthyServices = 0
$services = @(
    @{Name="RabbitMQ"; Url="http://localhost:15672"},
    @{Name="API Clients"; Url="http://localhost:8002/docs"},
    @{Name="API Orders"; Url="http://localhost:8000/docs"},
    @{Name="API Products"; Url="http://localhost:8001/docs"}
)

foreach ($service in $services) {
    try {
        $response = Invoke-WebRequest -Uri $service.Url -Method Head -TimeoutSec 5 -ErrorAction Stop
        if ($response.StatusCode -eq 200) {
            Write-Host "✅ $($service.Name) is healthy" -ForegroundColor Green
            $healthyServices++
        }
    } catch {
        Write-Host "⚠️  $($service.Name) might still be starting..." -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "📊 Service Status Summary:" -ForegroundColor Magenta
Write-Host "==========================================" -ForegroundColor Magenta
Write-Host "🌐 Frontend: http://localhost" -ForegroundColor Cyan
Write-Host "🔄 Caddy Proxy: http://localhost:8085" -ForegroundColor Cyan
Write-Host "👥 API Clients: http://localhost:8002/docs" -ForegroundColor Cyan
Write-Host "📦 API Orders: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "🛍️  API Products: http://localhost:8001/docs" -ForegroundColor Cyan
Write-Host "🐰 RabbitMQ Management: http://localhost:15672 (guest/guest)" -ForegroundColor Cyan
Write-Host ""

if ($healthyServices -eq $services.Count) {
    Write-Host "🎉 All services are running successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "💡 Useful commands:" -ForegroundColor Yellow
    Write-Host "   - View logs: docker-compose logs -f" -ForegroundColor Cyan
    Write-Host "   - Stop application: docker-compose down" -ForegroundColor Cyan
    Write-Host "   - Restart application: docker-compose restart" -ForegroundColor Cyan
} else {
    Write-Host "⚠️  Some services might still be starting. Use 'docker-compose logs' to check status." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "🔗 Quick Links:" -ForegroundColor Magenta
Write-Host "   - Client Management: http://localhost:8002/docs" -ForegroundColor Cyan
Write-Host "   - Order Management: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "   - Product Catalog: http://localhost:8001/docs" -ForegroundColor Cyan
Write-Host "   - Message Queue: http://localhost:15672" -ForegroundColor Cyan
Write-Host ""
Write-Host "✨ Application is ready!" -ForegroundColor Green

# Keep window open if run from Windows Explorer
if ($Host.Name -eq "ConsoleHost") {
    Read-Host "Press Enter to continue"
}