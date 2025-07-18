# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a microservices architecture project (MSPR Bloc 4) with three main Python FastAPI services:
- **API_Clients**: Client management service (port 8002)
- **API_Commandes**: Order management service
- **API_Produits**: Product management service

The services communicate via RabbitMQ message broker and use PostgreSQL databases.

## Common Commands

### Development Setup
```bash
# For each service (API_Clients, API_Commandes, API_Produits):
cd API_[SERVICE_NAME]
pip install -r requirements.txt
```

### Running Services
```bash
# Start individual service with Docker Compose
docker-compose up -d

# Start all services (from root directory)
docker-compose -f API_Clients/docker-compose.yml up -d
docker-compose -f API_Commandes/docker-compose.yml up -d  
docker-compose -f API_Produits/docker-compose.yml up -d
```

### Testing
```bash
# Run tests for each service
cd API_[SERVICE_NAME]
pytest test/

# Run specific test types
pytest test/unit/
pytest test/validation/
```

### Code Quality
```bash
# Run Prospector (only available in API_Clients)
cd API_Clients
prospector

# Run Pylint (available in API_Commandes and API_Produits)
pylint app/
```

## Architecture

### Service Structure
Each service follows this pattern:
- `app/main.py`: FastAPI application entry point
- `app/models.py`: SQLAlchemy database models
- `app/database.py`: Database configuration and session management
- `app/schema.py`: Pydantic schemas for API validation
- `app/routers/` or `app/router/`: API route definitions
- `app/controller/`: Business logic controllers
- `app/service/`: Data access services
- `config.yaml`: Service configuration

### Message Broker Integration
- **Producer**: `API_Clients/app/producer.py` publishes events to RabbitMQ
- **Consumer**: `API_Commandes/app/consumer.py` listens for client and product events
- **Exchange**: Uses "microservices" topic exchange
- **Events**: client.created, client.updated, client.deleted, product.created, product.updated, product.deleted

### Database Configuration
Each service uses environment-based configuration:
- `APP_ENV=test`: SQLite for testing
- `APP_ENV=prod`: PostgreSQL from DATABASE_URL environment variable
- Default (dev): PostgreSQL from config.yaml

### Authentication
- JWT tokens using python-jose
- Password hashing with bcrypt via passlib
- Configuration in config.yaml under `jwt` section

## Key Components

### API_Clients
- **Model**: Customer (clients table)
- **Auth**: JWT with password hashing
- **Events**: Publishes client lifecycle events
- **Frontend**: Basic HTML dashboard
- **Reverse Proxy**: Caddy configuration

### API_Commandes  
- **Model**: Order management
- **Integration**: Consumes client and product events
- **Monitoring**: Prometheus metrics integration
- **Threading**: RabbitMQ consumer runs in separate thread

### API_Produits
- **Model**: Product catalog
- **CORS**: Enabled for cross-origin requests
- **Data**: Includes sample product data (produits.sql)

## Configuration Files

### Environment Variables
Each service supports these environment variables:
- `DATABASE_URL`: PostgreSQL connection string
- `RABBITMQ_HOST`, `RABBITMQ_PORT`, `RABBITMQ_USER`, `RABBITMQ_PASSWORD`
- `APP_ENV`: Environment mode (test/prod/dev)

### Service Ports
- API_Clients: 8002
- Caddy proxy: 8085
- Frontend: 80
- PostgreSQL: 5432
- RabbitMQ: 5672

## Testing Strategy

### Test Structure
- `test/unit/`: Unit tests for individual components
- `test/validation/`: Integration/validation tests
- `pytest.ini`: Test configuration (API_Clients only)
- `conftest.py`: Shared test fixtures

### Test Commands
Use `pytest` with the configured test paths. Tests are designed to run with proper database isolation.