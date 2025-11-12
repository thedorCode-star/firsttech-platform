# Quick Local Setup Script for Windows
# Run this in PowerShell: .\setup_local.ps1

Write-Host "=== FinTech Platform - Local Setup ===" -ForegroundColor Green
Write-Host ""

# Check Python
Write-Host "Checking Python..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Python found: $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "✗ Python not found. Please install Python 3.9+" -ForegroundColor Red
    exit 1
}

# Create virtual environment
Write-Host ""
Write-Host "Creating virtual environment..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Write-Host "✓ Virtual environment already exists" -ForegroundColor Green
} else {
    python -m venv venv
    Write-Host "✓ Virtual environment created" -ForegroundColor Green
}

# Activate virtual environment
Write-Host ""
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1

# Upgrade pip
Write-Host ""
Write-Host "Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip

# Install dependencies
Write-Host ""
Write-Host "Installing dependencies (this may take a few minutes)..." -ForegroundColor Yellow
pip install -r requirements.txt

# Create .env file if it doesn't exist
Write-Host ""
Write-Host "Setting up environment file..." -ForegroundColor Yellow
if (-not (Test-Path ".env")) {
    Copy-Item env.example .env
    Write-Host "✓ Created .env file from env.example" -ForegroundColor Green
    Write-Host ""
    Write-Host "⚠ IMPORTANT: Edit .env file and set:" -ForegroundColor Yellow
    Write-Host "  - SECRET_KEY (random string, min 32 chars)" -ForegroundColor Yellow
    Write-Host "  - ENCRYPTION_KEY (random string, 32 chars)" -ForegroundColor Yellow
    Write-Host "  - DATABASE_URL (if using local PostgreSQL)" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "You can generate keys with:" -ForegroundColor Cyan
    Write-Host "  python -c `"import secrets; print(secrets.token_urlsafe(32))`"" -ForegroundColor Cyan
} else {
    Write-Host "✓ .env file already exists" -ForegroundColor Green
}

Write-Host ""
Write-Host "=== Setup Complete! ===" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Edit .env file with your configuration" -ForegroundColor White
Write-Host "2. Make sure PostgreSQL is running and database 'fintech_db' exists" -ForegroundColor White
Write-Host "3. Run migrations: alembic upgrade head" -ForegroundColor White
Write-Host "4. Start the server: uvicorn app.main:app --reload" -ForegroundColor White
Write-Host ""
Write-Host "Or install Docker and use: docker compose up -d" -ForegroundColor Cyan

