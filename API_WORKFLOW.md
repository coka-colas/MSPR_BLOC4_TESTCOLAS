# API Workflow - Client Order Management

This document describes the complete workflow for the three APIs communication system.

## Workflow Overview

1. **Client Profile Creation** (API_Clients)
2. **Product Listing** (API_Produits - requires authentication)
3. **Order Creation** (API_Commandes - with stock validation)
4. **Stock Management** (API_Produits - automatic stock updates)
5. **Order History** (API_Commandes - client-specific)

## Step-by-Step Testing Guide

### 1. Start All Services

```bash
# Using the universal container scripts (works with Docker or Podman)
./run-services.sh up all

# Or start individual services
./run-services.sh up clients
./run-services.sh up orders
./run-services.sh up products

# Alternative: Start each service manually
cd API_Clients && ./container-compose up -d
cd API_Commandes && ./container-compose up -d
cd API_Produits && ./container-compose up -d
```

### 2. Create a Client Profile

```bash
# POST /api/clients/
curl -X POST "http://localhost:8002/api/clients/" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "name": "John Doe",
    "first_name": "John",
    "last_name": "Doe",
    "postal_code": "12345",
    "city": "Paris",
    "profile_first_name": "John",
    "profile_last_name": "Doe",
    "company_name": "ACME Corp",
    "email": "john.doe@example.com",
    "phone": "0123456789",
    "actif": true,
    "password": "secure_password123"
  }'
```

### 3. Login to Get JWT Token

```bash
# POST /api/clients/login
curl -X POST "http://localhost:8002/api/clients/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "password": "secure_password123"
  }'
```

Save the returned `access_token` for subsequent requests.

### 4. View Products (Authentication Required)

```bash
# GET /produits/
curl -X GET "http://localhost:8001/produits/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### 5. Create an Order (with Stock Validation)

```bash
# POST /orders/
curl -X POST "http://localhost:8003/orders/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "customer_id": 1,
    "items": [
      {
        "product_id": 1,
        "quantity": 2
      },
      {
        "product_id": 2,
        "quantity": 1
      }
    ]
  }'
```

**Note**: The system will automatically:
- Validate that products exist
- Check stock availability
- Update product stock levels
- Create the order only if all validations pass

### 6. View Order History

```bash
# GET /orders/my-orders
curl -X GET "http://localhost:8003/orders/my-orders" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## API Endpoints Summary

### API_Clients (Port 8002)
- `POST /api/clients/` - Create client profile
- `POST /api/clients/login` - Login and get JWT token
- `GET /api/clients/me` - Get current user profile

### API_Produits (Port 8001)
- `GET /produits/` - List products (requires authentication)
- `GET /produits/{id}` - Get product details
- `PATCH /produits/{id}/stock` - Update stock (internal use)

### API_Commandes (Port 8003)
- `POST /orders/` - Create order (with stock validation)
- `GET /orders/my-orders` - Get user's order history
- `GET /orders/{id}` - Get order details

## Inter-Service Communication

### Authentication Flow
1. Client logs in via API_Clients
2. API_Clients returns JWT token
3. API_Produits validates token by calling API_Clients `/api/clients/me`
4. API_Commandes validates token by calling API_Clients `/api/clients/me`

### Order Creation Flow
1. Client sends order request to API_Commandes
2. API_Commandes validates JWT token with API_Clients
3. For each product in order:
   - API_Commandes calls API_Produits to get product details
   - API_Commandes calls API_Produits to check and update stock
4. If all validations pass, order is created
5. If any validation fails, order is rejected and stock is not modified

## Error Handling

- **401 Unauthorized**: Invalid or expired JWT token
- **403 Forbidden**: User trying to create order for another user
- **404 Not Found**: Product or client not found
- **400 Bad Request**: Insufficient stock or validation errors

## Configuration

Each service can be configured with environment variables:

```bash
# Service URLs
export CLIENTS_SERVICE_URL="http://localhost:8002"
export PRODUCTS_SERVICE_URL="http://localhost:8001"
export ORDERS_SERVICE_URL="http://localhost:8003"

# Database URLs
export DATABASE_URL="postgresql://postgres:root@localhost:5432/dbname"
```

## Container Engine Support

The project supports both Docker and Podman through universal wrapper scripts:

### Available Scripts

- **`container-compose`** - Auto-detects and uses `podman-compose`, `docker-compose`, or `docker compose`
- **`container`** - Auto-detects and uses `podman` or `docker`
- **`run-services.sh`** - High-level service manager

### Universal Commands

```bash
# Service management
./run-services.sh up all           # Start all services
./run-services.sh down all         # Stop all services
./run-services.sh build all        # Build all services
./run-services.sh logs clients     # View client service logs

# Individual service control
./run-services.sh up clients       # Start only clients service
./run-services.sh up orders        # Start only orders service
./run-services.sh up products      # Start only products service

# Direct container commands
./container-compose --version      # Check compose version
./container ps                     # List running containers
```

### Engine Detection

The scripts automatically detect your container engine:
- **Podman**: Uses `podman-compose` and `podman`
- **Docker**: Uses `docker-compose` or `docker compose`
- **Mixed environments**: Works seamlessly across team members using different engines

## Message Broker Integration

The system uses RabbitMQ for event-driven communication:

- **Client Events**: `client.created`, `client.updated`, `client.deleted`
- **Product Events**: `product.created`, `product.updated`, `product.deleted`
- **Order Events**: Order creation triggers stock updates

## Security Features

- JWT-based authentication
- Password hashing with bcrypt
- Cross-service token validation
- User authorization (users can only access their own orders)
- API key support (configurable)

## Testing Considerations

1. **Database Isolation**: Each service should have its own database
2. **Message Broker**: RabbitMQ should be running and accessible
3. **Service Dependencies**: Services communicate via HTTP, ensure all are running
4. **Token Expiration**: JWT tokens have a 30-minute expiration by default
5. **Stock Consistency**: Stock levels are updated atomically during order creation