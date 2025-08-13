#!/bin/bash

echo "Starting MSPR Bloc 4 Autonomous Application"
echo "============================================="
echo

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    echo "Error: Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if Docker Compose is available
if ! command -v docker-compose >/dev/null 2>&1; then
    echo "Error: docker-compose is not available. Please install Docker Compose and try again."
    exit 1
fi

echo "Checking prerequisites..."
echo "Docker is running"
echo "Docker Compose is available"
echo

# Fix line endings for startup.sh files if dos2unix is available
if command -v dos2unix >/dev/null 2>&1; then
    echo "Converting line endings for startup.sh files..."
    find . -name "startup.sh" -exec dos2unix {} \; 2>/dev/null || true
    echo "Line endings converted"
    echo
fi

# Stop any existing containers
echo "Cleaning up existing containers..."
docker-compose down --remove-orphans

# Build and start all services
echo
echo "Building and starting all services..."
echo "Services that will be started:"
echo "  - RabbitMQ (Message Broker) - Port 5672, Management: 15672"
echo "  - PostgreSQL (Clients DB) - Port 5432"
echo "  - PostgreSQL (Orders DB) - Port 5431"
echo "  - PostgreSQL (Products DB) - Port 5433"
echo "  - API Clients - Port 8002"
echo "  - API Orders - Port 8000"
echo "  - API Products - Port 8001"
echo "  - Frontend - Port 80"
echo "  - Caddy Reverse Proxy - Port 8085"
echo "  - PgAdmin - Port 5050"
echo

docker-compose up --build -d

# Wait for services to be healthy
echo
echo "Waiting for services to start..."
sleep 10

# Check service health
echo
echo "Checking service health..."
echo

healthy_services=0
total_services=4

# Check each service
if curl -f http://localhost:15672 >/dev/null 2>&1; then
    echo "RabbitMQ is healthy"
    ((healthy_services++))
else
    echo "RabbitMQ might still be starting..."
fi

if curl -f http://localhost:8002/docs >/dev/null 2>&1; then
    echo "API Clients is healthy"
    ((healthy_services++))
else
    echo "API Clients might still be starting..."
fi

if curl -f http://localhost:8000/docs >/dev/null 2>&1; then
    echo "API Orders is healthy"
    ((healthy_services++))
else
    echo "API Orders might still be starting..."
fi

if curl -f http://localhost:8001/docs >/dev/null 2>&1; then
    echo "API Products is healthy"
    ((healthy_services++))
else
    echo "API Products might still be starting..."
fi

echo
echo "Service Status Summary:"
echo "=========================================="
echo "Frontend: http://localhost"
echo "Caddy Proxy: http://localhost:8085"
echo "API Clients: http://localhost:8002/docs"
echo "API Orders: http://localhost:8000/docs"
echo "API Products: http://localhost:8001/docs"
echo "RabbitMQ Management: http://localhost:15672 (guest/guest)"
echo "PgAdmin: http://localhost:5050 (admin@pgadmin.com/admin)"
echo

if [ $healthy_services -eq $total_services ]; then
    echo "All services are running successfully!"
    echo
    echo "Useful commands:"
    echo "  - View logs: docker-compose logs -f"
    echo "  - Stop application: ./stop-application.sh"
    echo "  - Restart application: docker-compose restart"
else
    echo "Some services might still be starting. Use 'docker-compose logs' to check status."
fi

echo
echo "Quick Links:"
echo "  - Client Management: http://localhost:8002/docs"
echo "  - Order Management: http://localhost:8000/docs"
echo "  - Product Catalog: http://localhost:8001/docs"
echo "  - Message Queue: http://localhost:15672"
echo "  - Database Admin: http://localhost:5050"
echo
echo "Application is ready!"