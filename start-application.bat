REM =====================================================================
REM SCRIPT DE DEMARRAGE DE L'APPLICATION E-COMMERCE (Windows Batch)
REM =====================================================================
REM Ce script démarre automatiquement tous les services de l'application
REM Il vérifie que Docker fonctionne, nettoie les anciens conteneurs,
REM puis démarre tous les services nécessaires (bases de données, APIs, frontend)

@echo off
echo Starting MSPR Bloc 4 Autonomous Application
echo ==============================================

REM Vérifier si Docker Desktop est en cours d'exécution
REM La commande 'docker info' retourne une erreur si Docker n'est pas démarré
docker info >nul 2>&1
if errorlevel 1 (
    echo Error: Docker is not running. Please start Docker Desktop and try again.
    pause
    exit /b 1
)

REM Vérifier si Docker Compose est disponible sur le système
REM Docker Compose est nécessaire pour gérer plusieurs conteneurs
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo Error: docker-compose is not available. Please install Docker Desktop and try again.
    pause
    exit /b 1
)

echo Checking prerequisites...
echo Docker is running
echo Docker Compose is available

REM Arrêter et supprimer tous les conteneurs existants pour repartir proprement
REM --remove-orphans supprime les conteneurs qui ne sont plus dans docker-compose.yml
echo.
echo Cleaning up existing containers...
docker-compose down --remove-orphans

REM Construire et démarrer tous les services définis dans docker-compose.yml
REM --build force la reconstruction des images Docker
REM -d lance les conteneurs en arrière-plan (mode détaché)
echo.
echo Building and starting all services...
echo Services that will be started:
echo   - RabbitMQ (Message Broker) - Port 5672, Management: 15672
echo   - PostgreSQL (Clients DB) - Port 5432
echo   - PostgreSQL (Orders DB) - Port 5431
echo   - PostgreSQL (Products DB) - Port 5433
echo   - API Clients - Port 8002
echo   - API Orders - Port 8000
echo   - API Products - Port 8001
echo   - Frontend - Port 80
echo   - Caddy Reverse Proxy - Port 8085
echo   - PgAdmin - Port 5050
echo.

docker-compose up --build -d

REM Attendre que les services aient le temps de démarrer
REM Les services ont besoin de temps pour initialiser leurs bases de données
echo.
echo Waiting for services to start...
timeout /t 10 /nobreak >nul

REM Vérifier l'état de santé de chaque service en testant leurs endpoints HTTP
REM Cette section utilise curl pour tester si les APIs répondent correctement
echo.
echo Checking service health...

REM Variables pour compter les services fonctionnels
set healthy_services=0
set total_services=4

REM Tester chaque service individuellement
REM curl -f fait échouer la commande si le serveur retourne une erreur HTTP

REM Test de RabbitMQ (interface de gestion web)
curl -f http://localhost:15672 >nul 2>&1
if not errorlevel 1 (
    echo RabbitMQ is healthy
    set /a healthy_services+=1
) else (
    echo RabbitMQ might still be starting...
)

REM Test de l'API Clients (page de documentation Swagger)
curl -f http://localhost:8002/docs >nul 2>&1
if not errorlevel 1 (
    echo API Clients is healthy
    set /a healthy_services+=1
) else (
    echo API Clients might still be starting...
)

REM Test de l'API Commandes (page de documentation Swagger)
curl -f http://localhost:8000/docs >nul 2>&1
if not errorlevel 1 (
    echo API Orders is healthy
    set /a healthy_services+=1
) else (
    echo API Orders might still be starting...
)

REM Test de l'API Produits (page de documentation Swagger)
curl -f http://localhost:8001/docs >nul 2>&1
if not errorlevel 1 (
    echo API Products is healthy
    set /a healthy_services+=1
) else (
    echo API Products might still be starting...
)

echo.
REM Résumé de tous les services et leurs URLs d'accès
echo Service Status Summary:
echo ==========================================
echo Frontend: http://localhost
echo Caddy Proxy: http://localhost:8085
echo API Clients: http://localhost:8002/docs
echo API Orders: http://localhost:8000/docs
echo API Products: http://localhost:8001/docs
echo RabbitMQ Management: http://localhost:15672 (guest/guest)
echo PgAdmin: http://localhost:5050 (admin@pgadmin.com/admin)
echo.

REM Vérifier si tous les services ont démarré avec succès
if %healthy_services% equ %total_services% (
    echo All services are running successfully!
    echo.
    echo Useful commands:
    echo   - View logs: docker-compose logs -f
    echo   - Stop application: stop-application.bat
    echo   - Restart application: docker-compose restart
) else (
    echo Some services might still be starting. Use 'docker-compose logs' to check status.
)

REM Afficher les liens rapides pour accéder aux différentes interfaces
echo.
echo Quick Links:
echo   - Client Management: http://localhost:8002/docs
echo   - Order Management: http://localhost:8000/docs
echo   - Product Catalog: http://localhost:8001/docs
echo   - Message Queue: http://localhost:15672
echo   - Database Admin: http://localhost:5050
echo.
echo Application is ready!
echo.
echo Press any key to continue...
REM Attendre que l'utilisateur appuie sur une touche avant de fermer
pause >nul