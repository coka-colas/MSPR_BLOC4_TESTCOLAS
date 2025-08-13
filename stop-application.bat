@echo off
echo Stopping MSPR Bloc 4 Autonomous Application
echo ==============================================

REM Stop all services
echo Stopping all services...
docker-compose down --remove-orphans

REM Optional: Remove volumes (uncomment if you want to clean data)
REM echo Removing volumes...
REM docker-compose down -v

echo.
echo Application stopped successfully!
echo.
echo To remove all data (databases, etc.), run:
echo   docker-compose down -v
echo.
echo To start again, run:
echo   start-application.bat
echo.
echo Press any key to continue...
pause >nul