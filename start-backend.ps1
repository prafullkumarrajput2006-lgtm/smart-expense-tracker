# Start Backend Server
Write-Host "Starting Backend Server..." -ForegroundColor Green
cd backend
& venv\Scripts\Activate.ps1
python app.py
