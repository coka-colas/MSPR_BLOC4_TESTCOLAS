#!/bin/bash

echo "Stopping MSPR Bloc 4 Autonomous Application"
echo "============================================="
echo

# Stop all services
echo "Stopping all services..."
docker-compose down --remove-orphans

# Optional: Remove volumes (uncomment if you want to clean data)
# echo "Removing volumes..."
# docker-compose down -v

echo
echo "Application stopped successfully!"
echo
echo "To remove all data (databases, etc.), run:"
echo "  docker-compose down -v"
echo
echo "To start again, run:"
echo "  ./start-application.sh"
echo