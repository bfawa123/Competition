# Prepare demo: backup + clear memories, clear cache, check backend
# 脚本位于 scripts/ 子目录，项目根目录是其上一级
$root = Split-Path -Parent $PSScriptRoot
$data = "$root\backend\data"

Write-Host "=== Preparing demo ==="

$memFile = "$data\memories.json"
if (Test-Path $memFile) {
    $stamp = Get-Date -Format "yyyyMMdd-HHmmss"
    Copy-Item $memFile "$data\memories.backup-$stamp.json" -Force
    Set-Content -Path $memFile -Value "{}" -Encoding ascii
    Write-Host "[OK] memories cleared (backup: memories.backup-$stamp.json)"
} else {
    Set-Content -Path $memFile -Value "{}" -Encoding ascii
    Write-Host "[OK] created empty memories.json"
}

$cache = "$data\embeddings_cache.json"
if (Test-Path $cache) {
    Remove-Item $cache -Force
    Write-Host "[OK] cleared embeddings cache"
}

try {
    $r = Invoke-WebRequest -Uri "http://127.0.0.1:8000/health" -TimeoutSec 5 -UseBasicParsing
    Write-Host "[OK] backend is running (HTTP $($r.StatusCode))"
} catch {
    Write-Host "[!] backend not running - run scripts\start-backend.bat first"
}

Write-Host ""
Write-Host "Next:"
Write-Host "  1) double-click scripts\start-backend.bat (if not running)"
Write-Host "  2) double-click scripts\start-frontend.bat"
Write-Host "  3) open http://127.0.0.1:5173"
