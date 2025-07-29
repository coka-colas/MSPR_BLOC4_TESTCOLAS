#!/bin/bash

echo "🚀 Starting MSPR Bloc 4 Autonomous Application"
echo "=============================================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if Docker Compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Error: docker-compose is not installed. Please install Docker Compose and try again."
    exit 1
fi

echo "📋 Checking prerequisites..."
echo "✅ Docker is running"
echo "✅ Docker Compose is available"

# Stop any existing containers
echo ""
echo "🧹 Cleaning up existing containers..."
docker-compose down --remove-orphans

# Build and start all services
echo ""
echo "🏗️  Building and starting all services..."
echo "Services that will be started:"
echo "  - RabbitMQ (Message Broker) - Port 5672, Management: 15672"
echo "  - PostgreSQL (Clients DB) - Port 5432"
echo "  - PostgreSQL (Orders DB) - Port 5431"
echo "  - API Clients - Port 8002"
echo "  - API Orders - Port 8000"
echo "  - API Products - Port 8001"
echo "  - Frontend - Port 80"
echo "  - Caddy Reverse Proxy - Port 8085"
echo ""

docker-compose up --build -d

# Wait for services to be healthy
echo ""
echo "⏳ Waiting for services to start..."
sleep 10

# Check service health
echo ""
echo "🔍 Checking service health..."

services=("rabbitmq-shared:15672" "client-api:8002/docs" "commande-api:8000/docs" "produit-api:8001/docs")
healthy_services=0

for service in "${services[@]}"; do
    IFS=':' read -r container port <<< "$service"
    if docker exec "$container" curl -f "http://localhost:$port" > /dev/null 2>&1; then
        echo "✅ $container is healthy"
        ((healthy_services++))
    else
        echo "⚠️  $container might still be starting..."
    fi
done

echo ""
echo "📊 Service Status Summary:"
echo "=========================================="
echo "🌐 Frontend: http://localhost"
echo "🔄 Caddy Proxy: http://localhost:8085"
echo "👥 API Clients: http://localhost:8002/docs"
echo "📦 API Orders: http://localhost:8000/docs"
echo "🛍️  API Products: http://localhost:8001/docs"
echo "🐰 RabbitMQ Management: http://localhost:15672 (guest/guest)"
echo ""

if [ $healthy_services -eq ${#services[@]} ]; then
    echo "🎉 All services are running successfully!"
    echo ""
    echo "💡 Useful commands:"
    echo "   - View logs: docker-compose logs -f"
    echo "   - Stop application: docker-compose down"
    echo "   - Restart application: docker-compose restart"
else
    echo "⚠️  Some services might still be starting. Use 'docker-compose logs' to check status."
fi

echo ""
echo "🔗 Quick Links:"
echo "   - Client Management: http://localhost:8002/docs"
echo "   - Order Management: http://localhost:8000/docs"
echo "   - Product Catalog: http://localhost:8001/docs"
echo "   - Message Queue: http://localhost:15672"
echo ""
echo "✨ Application is ready!"