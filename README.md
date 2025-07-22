# MSPR Bloc 4 - Microservices E-commerce Application

A complete microservices-based e-commerce application built with Python FastAPI, featuring client management, product catalog, order processing, and message queuing.

## 🏗️ Architecture Overview

This application consists of multiple microservices:

- **API Clients** (Port 8002) - Client management service
- **API Commandes** (Port 8000) - Order processing service  
- **API Produits** (Port 8001) - Product catalog service
- **Frontend** (Port 80) - Web interface
- **RabbitMQ** (Port 5672/15672) - Message broker
- **PostgreSQL** - Database services (Ports 5432, 5431)
- **Caddy** (Port 8085) - Reverse proxy

## 🚀 Quick Start

### Prerequisites

Before running the application, ensure you have:

- **Docker** (version 20.0 or higher)
- **Docker Compose** (version 2.0 or higher)
- **Git** (for cloning the repository)

### Installation Steps

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd MSPR_Bloc4
   ```

2. **Start the application**
   ```bash
   chmod +x start-application.sh
   ./start-application.sh
   ```

   The script will:
   - Check Docker prerequisites
   - Clean up existing containers
   - Build all services
   - Start the complete application stack
   - Verify service health

3. **Stop the application**
   ```bash
   chmod +x stop-application.sh
   ./stop-application.sh
   ```

## 🌐 Service Endpoints

Once the application is running, you can access:

| Service | URL | Description |
|---------|-----|-------------|
| Frontend | http://localhost | Main web interface |
| Caddy Proxy | http://localhost:8085 | Reverse proxy |
| API Clients | http://localhost:8002/docs | Client management API docs |
| API Orders | http://localhost:8000/docs | Order processing API docs |
| API Products | http://localhost:8001/docs | Product catalog API docs |
| RabbitMQ Management | http://localhost:15672 | Message queue admin (guest/guest) |

## 🔧 Manual Docker Commands

If you prefer to run Docker commands manually:

```bash
# Start all services
docker-compose up --build -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down

# Stop and remove all data
docker-compose down -v

# Restart specific service
docker-compose restart api-clients
```

## 📦 Dependencies

Each microservice uses Python with the following key dependencies:

- **FastAPI** - Web framework
- **SQLAlchemy** - ORM
- **PostgreSQL** - Database
- **RabbitMQ** - Message queuing
- **Pydantic** - Data validation
- **Uvicorn** - ASGI server

Full dependency lists are available in each service's `requirements.txt` file.

## 🔍 Service Health Checks

The application includes health checks for all services:

- APIs respond on `/docs` endpoints
- Databases use `pg_isready` checks
- RabbitMQ uses `rabbitmq-diagnostics ping`

## 🐛 Troubleshooting

### Common Issues

1. **Docker not running**
   ```bash
   # Start Docker service
   sudo systemctl start docker
   ```

2. **Port conflicts**
   - Ensure ports 80, 5432, 5431, 5672, 8000, 8001, 8002, 8085, 15672 are available
   - Check with: `netstat -tulpn | grep :<port>`

3. **Services not starting**
   ```bash
   # Check logs
   docker-compose logs <service-name>
   
   # Rebuild specific service
   docker-compose build <service-name>
   ```

4. **Database connection issues**
   ```bash
   # Reset databases
   docker-compose down -v
   docker-compose up -d
   ```

### Debug Commands

```bash
# View all containers
docker-compose ps

# Enter a container
docker exec -it <container-name> bash

# View specific service logs
docker-compose logs -f api-clients

# Check network connectivity
docker network ls
```

## 📁 Project Structure

```
MSPR_Bloc4/
├── API_Clients/           # Client management service
│   ├── app/              # Application code
│   ├── frontend/         # Web interface
│   ├── Dockerfile        # Container definition
│   └── requirements.txt  # Python dependencies
├── API_Commandes/        # Order processing service
├── API_Produits/         # Product catalog service
├── docker-compose.yml    # Service orchestration
├── start-application.sh  # Startup script
└── stop-application.sh   # Shutdown script
```

## 🔐 Security Notes

- Default credentials are used for development (guest/guest for RabbitMQ)
- Database passwords are hardcoded for development environments
- For production deployment, use environment-specific configurations

## 🛠️ Development

To develop individual services:

1. Start dependencies only:
   ```bash
   docker-compose up rabbitmq clients-db commandes-db -d
   ```

2. Run service locally:
   ```bash
   cd API_Clients
   pip install -r requirements.txt
   uvicorn app.main:app --reload --port 8002
   ```

## 📊 Monitoring

- RabbitMQ Management UI: http://localhost:15672
- API documentation is available at each service's `/docs` endpoint
- Health checks are configured for all services

---

**Need help?** Check the logs with `docker-compose logs -f` or refer to the troubleshooting section above.