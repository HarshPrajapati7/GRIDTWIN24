# Auto-push script for GRIDTWIN24
# Runs every 5 minutes (300 seconds), commits any changes, and pushes to origin/main.

$repoDir = Split-Path -Parent $PSScriptRoot
Set-Location $repoDir

Write-Host "Starting GRIDTWIN24 auto-push watcher every 5 minutes in $repoDir..." -ForegroundColor Cyan

while ($true) {
    try {
        $timestamp = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
        
        # Check for uncommitted changes
        $status = git status --porcelain
        if ($status) {
            Write-Host "[$timestamp] Changes detected. Staging and committing..." -ForegroundColor Yellow
            git add -A
            git commit -m "auto-snapshot: $timestamp"
        }

        # Check if local is ahead of remote
        $ahead = git rev-list @{u}..HEAD 2>$null
        if ($ahead -or $status) {
            Write-Host "[$timestamp] Pushing to origin main..." -ForegroundColor Green
            git push origin main
            Write-Host "[$timestamp] Push completed successfully." -ForegroundColor Green
        } else {
            Write-Host "[$timestamp] Working tree clean and up to date with remote." -ForegroundColor DarkGray
        }
    } catch {
        Write-Warning "[$((Get-Date).ToString('yyyy-MM-dd HH:mm:ss'))] Error during auto-push: $_"
    }

    Start-Sleep -Seconds 300
}
