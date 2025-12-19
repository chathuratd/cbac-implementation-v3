# Quick Start Script for CBIE MVP
# Run this script to set up and start the application

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  CBIE MVP - Quick Start" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Check Python
Write-Host "Checking Python installation..." -ForegroundColor Yellow
python --version
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Python not found. Please install Python 3.9+ first." -ForegroundColor Red
    exit 1
}
Write-Host "✓ Python found" -ForegroundColor Green
Write-Host ""

# Check Docker (optional)
Write-Host "Checking Docker (optional)..." -ForegroundColor Yellow
docker --version 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Docker found" -ForegroundColor Green
    
    $useDocker = Read-Host "Do you want to start MongoDB and Qdrant using Docker? (y/n)"
    if ($useDocker -eq 'y') {
        Write-Host ""
        Write-Host "Starting Docker services..." -ForegroundColor Yellow
        docker-compose up -d
        Write-Host "✓ Docker services started" -ForegroundColor Green
        Write-Host ""
        Start-Sleep -Seconds 5
    }
} else {
    Write-Host "⚠ Docker not found. Make sure MongoDB and Qdrant are running manually." -ForegroundColor Yellow
}
Write-Host ""

# Create virtual environment
Write-Host "Setting up Python virtual environment..." -ForegroundColor Yellow
if (-not (Test-Path "venv")) {
    python -m venv venv
    Write-Host "✓ Virtual environment created" -ForegroundColor Green
} else {
    Write-Host "✓ Virtual environment already exists" -ForegroundColor Green
}
Write-Host ""

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1
Write-Host "✓ Virtual environment activated" -ForegroundColor Green
Write-Host ""

# Install dependencies
Write-Host "Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt --quiet
Write-Host "✓ Dependencies installed" -ForegroundColor Green
Write-Host ""

# Check .env file
Write-Host "Checking configuration..." -ForegroundColor Yellow
if (Test-Path ".env") {
    Write-Host "✓ .env file found" -ForegroundColor Green
} else {
    Write-Host "⚠ .env file not found. Please create one based on the documentation." -ForegroundColor Yellow
}
Write-Host ""

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  Setup Complete!" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "To start the CBIE API server, run:" -ForegroundColor Yellow
Write-Host "  python main.py" -ForegroundColor White
Write-Host ""
Write-Host "API will be available at:" -ForegroundColor Yellow
Write-Host "  http://localhost:8000" -ForegroundColor White
Write-Host "  http://localhost:8000/docs (API documentation)" -ForegroundColor White
Write-Host ""

$startNow = Read-Host "Do you want to start the API server now? (y/n)"
if ($startNow -eq 'y') {
    Write-Host ""
    Write-Host "Starting CBIE API server..." -ForegroundColor Green
    Write-Host ""
    python main.py
}
