# GRIDTWIN-24 — development launcher (hot reload).
# Starts the FastAPI backend on :8000 and the Vite dev server on :5173.
# The dev server proxies /api -> :8000, so open http://localhost:5173
#
# Usage:  powershell -ExecutionPolicy Bypass -File run_web_dev.ps1

$ErrorActionPreference = "Stop"
$root = $PSScriptRoot

Write-Host "Starting GRIDTWIN-24 backend on http://localhost:8000 ..." -ForegroundColor Yellow
Start-Process -FilePath "py" -ArgumentList "-3.13","-m","uvicorn","backend.main:app","--host","127.0.0.1","--port","8000","--reload" -WorkingDirectory $root

Start-Sleep -Seconds 2
Write-Host "Starting Vite dev server on http://localhost:5173 ..." -ForegroundColor Yellow
Start-Process -FilePath "npm" -ArgumentList "run","dev" -WorkingDirectory (Join-Path $root "frontend")

Write-Host ""
Write-Host "GRIDTWIN-24 is starting. Open http://localhost:5173 in your browser." -ForegroundColor Green
Write-Host "(The first forecast trains the model and takes ~20-30s; a spinner is shown.)" -ForegroundColor DarkGray
