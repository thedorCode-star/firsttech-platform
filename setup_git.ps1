# Git Setup Script for FinTech Project
# Run this in PowerShell: .\setup_git.ps1

Write-Host "=== Git Setup for FinTech Platform ===" -ForegroundColor Green
Write-Host ""

# Check if Git is installed
Write-Host "Checking Git installation..." -ForegroundColor Yellow
try {
    $gitVersion = git --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Git found: $gitVersion" -ForegroundColor Green
    } else {
        throw "Git not found"
    }
} catch {
    Write-Host "✗ Git is not installed!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install Git first:" -ForegroundColor Yellow
    Write-Host "1. Download from: https://git-scm.com/download/win" -ForegroundColor Cyan
    Write-Host "2. Or see: INSTALL_GIT.md" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "After installation, restart PowerShell and run this script again." -ForegroundColor Yellow
    exit 1
}

# Check if already a git repository
Write-Host ""
Write-Host "Checking if repository is initialized..." -ForegroundColor Yellow
if (Test-Path ".git") {
    Write-Host "✓ Git repository already initialized" -ForegroundColor Green
} else {
    Write-Host "Initializing Git repository..." -ForegroundColor Yellow
    git init
    Write-Host "✓ Repository initialized" -ForegroundColor Green
}

# Check Git configuration
Write-Host ""
Write-Host "Checking Git configuration..." -ForegroundColor Yellow
$userName = git config user.name
$userEmail = git config user.email

if ($userName -and $userEmail) {
    Write-Host "✓ Git configured:" -ForegroundColor Green
    Write-Host "  Name: $userName" -ForegroundColor White
    Write-Host "  Email: $userEmail" -ForegroundColor White
} else {
    Write-Host "⚠ Git not configured. Please set your name and email:" -ForegroundColor Yellow
    Write-Host ""
    $name = Read-Host "Enter your name"
    $email = Read-Host "Enter your email"
    
    git config --global user.name $name
    git config --global user.email $email
    Write-Host "✓ Git configured" -ForegroundColor Green
}

# Set default branch to main
Write-Host ""
Write-Host "Setting default branch to 'main'..." -ForegroundColor Yellow
git config --global init.defaultBranch main
Write-Host "✓ Default branch set to 'main'" -ForegroundColor Green

# Check .gitignore
Write-Host ""
Write-Host "Checking .gitignore..." -ForegroundColor Yellow
if (Test-Path ".gitignore") {
    Write-Host "✓ .gitignore exists" -ForegroundColor Green
    
    # Check if .env is ignored
    $envIgnored = git check-ignore .env 2>&1
    if ($envIgnored) {
        Write-Host "✓ .env file is properly ignored" -ForegroundColor Green
    } else {
        Write-Host "⚠ .env file is NOT ignored - check .gitignore" -ForegroundColor Yellow
    }
} else {
    Write-Host "⚠ .gitignore not found!" -ForegroundColor Yellow
}

# Check for .env file
Write-Host ""
Write-Host "Checking for .env file..." -ForegroundColor Yellow
if (Test-Path ".env") {
    $envIgnored = git check-ignore .env 2>&1
    if ($envIgnored) {
        Write-Host "✓ .env file exists and is ignored (good!)" -ForegroundColor Green
    } else {
        Write-Host "⚠ WARNING: .env file exists but is NOT ignored!" -ForegroundColor Red
        Write-Host "  Make sure .env is in .gitignore before committing!" -ForegroundColor Red
    }
} else {
    Write-Host "ℹ No .env file found (will be created from env.example)" -ForegroundColor Cyan
}

# Show status
Write-Host ""
Write-Host "Current Git status:" -ForegroundColor Yellow
git status --short

# Ask if user wants to make initial commit
Write-Host ""
$makeCommit = Read-Host "Do you want to make an initial commit? (y/n)"
if ($makeCommit -eq "y" -or $makeCommit -eq "Y") {
    Write-Host ""
    Write-Host "Adding all files..." -ForegroundColor Yellow
    git add .
    
    Write-Host "Creating initial commit..." -ForegroundColor Yellow
    git commit -m "Initial commit: FinTech platform with POPIA compliance and HA architecture"
    
    Write-Host "✓ Initial commit created!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Commit hash:" -ForegroundColor Cyan
    git log --oneline -1
} else {
    Write-Host ""
    Write-Host "Skipped initial commit. You can commit later with:" -ForegroundColor Yellow
    Write-Host "  git add ." -ForegroundColor Cyan
    Write-Host "  git commit -m 'Your commit message'" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "=== Git Setup Complete! ===" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Review your changes: git status" -ForegroundColor White
Write-Host "2. Make commits as you work: git add . && git commit -m 'message'" -ForegroundColor White
Write-Host "3. (Optional) Connect to GitHub/GitLab: See GIT_SETUP.md" -ForegroundColor White
Write-Host ""
Write-Host "For more Git commands, see: GIT_SETUP.md" -ForegroundColor Cyan

