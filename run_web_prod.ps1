# GRIDTWIN-24 — production launcher (single origin).
# Builds the React app, then serves BOTH the UI and the API from FastAPI on
# http://localhost:8000  (no separate frontend server, no CORS).
#
# Usage:  powershell -ExecutionPolicy Bypass -File run_web_prod.ps1

$ErrorActionPreference = "Stop"
$root = $PSScriptRoot

Write-Host "Building the React frontend ..." -ForegroundColor Yellow
Push-Location (Join-Path $root "frontend")
npm install
npm run build
Pop-Location

Write-Host ""
Write-Host "Serving GRIDTWIN-24 on http://localhost:8000 (UI + API) ..." -ForegroundColor Green
py -3.13 -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
