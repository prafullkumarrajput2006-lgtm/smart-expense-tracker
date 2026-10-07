# Installation Verification Script
Write-Host "==================================" -ForegroundColor Cyan
Write-Host "Smart Expense Tracker - Setup Verification" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

# Check Python
Write-Host "Checking Python..." -ForegroundColor Yellow
python --version
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Python is installed" -ForegroundColor Green
} else {
    Write-Host "✗ Python not found" -ForegroundColor Red
}
Write-Host ""

# Check Node.js
Write-Host "Checking Node.js..." -ForegroundColor Yellow
node --version
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Node.js is installed" -ForegroundColor Green
} else {
    Write-Host "✗ Node.js not found" -ForegroundColor Red
}
Write-Host ""

# Check npm
Write-Host "Checking npm..." -ForegroundColor Yellow
npm --version
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ npm is installed" -ForegroundColor Green
} else {
    Write-Host "✗ npm not found" -ForegroundColor Red
}
Write-Host ""

# Check Backend venv
Write-Host "Checking backend virtual environment..." -ForegroundColor Yellow
if (Test-Path "backend\venv\Scripts\python.exe") {
    Write-Host "✓ Virtual environment exists" -ForegroundColor Green
} else {
    Write-Host "✗ Virtual environment not found" -ForegroundColor Red
    Write-Host "  Run: cd backend; python -m venv venv" -ForegroundColor Yellow
}
Write-Host ""

# Check Frontend node_modules
Write-Host "Checking frontend dependencies..." -ForegroundColor Yellow
if (Test-Path "frontend\node_modules") {
    Write-Host "✓ Node modules installed" -ForegroundColor Green
} else {
    Write-Host "✗ Node modules not found" -ForegroundColor Red
    Write-Host "  Run: cd frontend; npm install" -ForegroundColor Yellow
}
Write-Host ""

# Check ML model files
Write-Host "Checking ML model files..." -ForegroundColor Yellow
$modelExists = Test-Path "backend\expense_categorizer_model.pkl"
$vectorizerExists = Test-Path "backend\vectorizer.pkl"
if ($modelExists -and $vectorizerExists) {
    Write-Host "✓ ML models exist" -ForegroundColor Green
} else {
    Write-Host "✗ ML models not found" -ForegroundColor Red
    Write-Host "  Run: cd backend; venv\Scripts\activate; python ml_model.py" -ForegroundColor Yellow
}
Write-Host ""

Write-Host "==================================" -ForegroundColor Cyan
Write-Host "Verification Complete!" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. cd backend; venv\Scripts\activate; pip install -r requirements.txt" -ForegroundColor White
Write-Host "2. python ml_model.py (if models don't exist)" -ForegroundColor White
Write-Host "3. cd ..\frontend; npm install" -ForegroundColor White
Write-Host "4. Use start-backend.ps1 and start-frontend.ps1 to run servers" -ForegroundColor White
Write-Host ""
