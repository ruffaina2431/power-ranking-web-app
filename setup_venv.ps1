# PowerShell script to set up Python virtual environment and install dependencies
Write-Host "Setting up E-Sports Tournament Hub development environment..." -ForegroundColor Green
Write-Host "=================================================" -ForegroundColor Green

# Check if Python is installed
try {
    $pythonVersion = python --version
    Write-Host "Found Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "Error: Python not found. Please install Python 3.8 or later." -ForegroundColor Red
    Write-Host "Download from: https://www.python.org/downloads/" -ForegroundColor Yellow
    exit 1
}

# Create .venv directory if it doesn't exist
Write-Host "`nStep 1: Creating virtual environment..." -ForegroundColor Cyan
if (-not (Test-Path .venv)) {
    python -m venv .venv
    Write-Host "Virtual environment created successfully!" -ForegroundColor Green
} else {
    Write-Host "Virtual environment already exists." -ForegroundColor Yellow
}

# Activate the virtual environment
Write-Host "`nStep 2: Activating virtual environment..." -ForegroundColor Cyan
.\.venv\Scripts\Activate.ps1

# Install requirements
Write-Host "`nStep 3: Installing required packages..." -ForegroundColor Cyan
pip install -r requirements.txt

# Setup complete
Write-Host "`nSetup complete! 🎮" -ForegroundColor Green
Write-Host "------------------------------------------------" -ForegroundColor White
Write-Host "To start development:" -ForegroundColor Cyan
Write-Host "1. The virtual environment is now activated (you'll see (.venv) in your prompt)" -ForegroundColor White
Write-Host "2. Run the app: python main.py" -ForegroundColor White
Write-Host "3. Visit: http://127.0.0.1:5000" -ForegroundColor White
Write-Host "`nIn the future, just run:" -ForegroundColor Cyan
Write-Host ".\.venv\Scripts\Activate.ps1" -ForegroundColor Yellow
Write-Host "to activate the environment before development." -ForegroundColor White
Write-Host "------------------------------------------------" -ForegroundColor White

# Check if MySQL is needed
Write-Host "`nDatabase Setup:" -ForegroundColor Cyan
Write-Host "This project uses MySQL by default. Make sure you:" -ForegroundColor White
Write-Host "1. Have MySQL installed" -ForegroundColor White
Write-Host "2. Create a database named 'esports_tournament'" -ForegroundColor White
Write-Host "3. Or edit website/__init__.py to use SQLite instead" -ForegroundColor White