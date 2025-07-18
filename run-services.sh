#!/bin/bash

# Universal service runner for Docker and Podman
# Usage: ./run-services.sh [up|down|build|logs] [service-name]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMPOSE_CMD="$SCRIPT_DIR/container-compose"

# Make wrapper executable
chmod +x "$COMPOSE_CMD"

# Function to ensure shared network exists
ensure_shared_network() {
    local network_name="microservices-network"
    echo "Ensuring shared network '$network_name' exists..."
    
    # Check if network exists, create if it doesn't
    if ! $SCRIPT_DIR/container network ls --format "{{.Name}}" | grep -q "^${network_name}$"; then
        echo "Creating shared network: $network_name"
        $SCRIPT_DIR/container network create "$network_name"
    else
        echo "Shared network '$network_name' already exists"
    fi
}

# Function to run compose command in a service directory
run_compose() {
    local service_dir=$1
    local compose_args="${@:2}"
    
    if [ -d "$service_dir" ] && [ -f "$service_dir/docker-compose.yml" ]; then
        echo "Running in $service_dir: $COMPOSE_CMD $compose_args"
        cd "$service_dir"
        $COMPOSE_CMD $compose_args
        cd "$SCRIPT_DIR"
    else
        echo "ERROR: $service_dir not found or missing docker-compose.yml"
        exit 1
    fi
}

# Main command handling
case "${1:-up}" in
    "up")
        # Always ensure shared network exists before starting services
        ensure_shared_network
        
        case "${2:-all}" in
            "all")
                echo "Starting all services..."
                run_compose "API_Clients" up -d
                run_compose "API_Commandes" up -d
                run_compose "API_Produits" up -d
                ;;
            "clients")
                run_compose "API_Clients" up -d
                ;;
            "orders"|"commandes")
                run_compose "API_Commandes" up -d
                ;;
            "products"|"produits")
                run_compose "API_Produits" up -d
                ;;
            *)
                echo "Usage: $0 up [all|clients|orders|products]"
                exit 1
                ;;
        esac
        ;;
    "down")
        case "${2:-all}" in
            "all")
                echo "Stopping all services..."
                run_compose "API_Clients" down
                run_compose "API_Commandes" down
                run_compose "API_Produits" down
                ;;
            "clients")
                run_compose "API_Clients" down
                ;;
            "orders"|"commandes")
                run_compose "API_Commandes" down
                ;;
            "products"|"produits")
                run_compose "API_Produits" down
                ;;
            *)
                echo "Usage: $0 down [all|clients|orders|products]"
                exit 1
                ;;
        esac
        ;;
    "build")
        case "${2:-all}" in
            "all")
                echo "Building all services..."
                run_compose "API_Clients" build
                run_compose "API_Commandes" build
                run_compose "API_Produits" build
                ;;
            "clients")
                run_compose "API_Clients" build
                ;;
            "orders"|"commandes")
                run_compose "API_Commandes" build
                ;;
            "products"|"produits")
                run_compose "API_Produits" build
                ;;
            *)
                echo "Usage: $0 build [all|clients|orders|products]"
                exit 1
                ;;
        esac
        ;;
    "logs")
        if [ -n "$2" ]; then
            case "$2" in
                "clients")
                    run_compose "API_Clients" logs -f
                    ;;
                "orders"|"commandes")
                    run_compose "API_Commandes" logs -f
                    ;;
                "products"|"produits")
                    run_compose "API_Produits" logs -f
                    ;;
                *)
                    echo "Usage: $0 logs [clients|orders|products]"
                    exit 1
                    ;;
            esac
        else
            echo "Usage: $0 logs [clients|orders|products]"
            exit 1
        fi
        ;;
    "help"|"-h"|"--help")
        echo "Universal Service Runner for Docker/Podman"
        echo ""
        echo "Usage: $0 [command] [service]"
        echo ""
        echo "Commands:"
        echo "  up [all|clients|orders|products]    - Start services"
        echo "  down [all|clients|orders|products]  - Stop services"
        echo "  build [all|clients|orders|products] - Build services"
        echo "  logs [clients|orders|products]      - Show service logs"
        echo "  help                                 - Show this help"
        echo ""
        echo "Examples:"
        echo "  $0 up all                           - Start all services"
        echo "  $0 up clients                       - Start only client service"
        echo "  $0 down all                         - Stop all services"
        echo "  $0 logs clients                     - Show client service logs"
        ;;
    *)
        echo "Unknown command: $1"
        echo "Run '$0 help' for usage information"
        exit 1
        ;;
esac