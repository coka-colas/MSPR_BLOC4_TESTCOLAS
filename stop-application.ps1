#!/usr/bin/env pwsh

Write-Host "🛑 Stopping MSPR Bloc 4 Autonomous Application" -ForegroundColor Red
Write-Host "==============================================" -ForegroundColor Red

# Stop all services
Write-Host "⏹️  Stopping all services..." -ForegroundColor Yellow
docker-compose down --remove-orphans

# Optional: Remove volumes (uncomment if you want to clean data)
# Write-Host "🗑️  Removing volumes..." -ForegroundColor Yellow
# docker-compose down -v

Write-Host ""
Write-Host "✅ Application stopped successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "💡 To remove all data (databases, etc.), run:" -ForegroundColor Yellow
Write-Host "   docker-compose down -v" -ForegroundColor Cyan
Write-Host ""
Write-Host "🔄 To start again, run:" -ForegroundColor Yellow
Write-Host "   .\start-application.ps1" -ForegroundColor Cyan

# Keep window open if run from Windows Explorer
if ($Host.Name -eq "ConsoleHost") {
    Read-Host "Press Enter to continue"
}