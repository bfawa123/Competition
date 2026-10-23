# Start backend (FastAPI) on http://127.0.0.1:8000
# 脚本位于 scripts/ 子目录，项目根目录是其上一级
$root = Split-Path -Parent $PSScriptRoot
$python = "C:\Users\67260\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\python\python.exe"
if (-not (Test-Path $python)) { $python = "python" }

$env:PYTHONPATH = "$root\backend\pylibs"
$env:DEBUG = "false"
Set-Location "$root\backend"
Write-Host "Starting backend: http://127.0.0.1:8000"
& $python app\main.py
