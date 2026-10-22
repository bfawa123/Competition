# Start frontend (Vite) on http://127.0.0.1:5173
$root = $PSScriptRoot
$node = "C:\Users\67260\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\node\bin\node.exe"
if (-not (Test-Path $node)) { $node = "node" }

Set-Location "$root\frontend"
Write-Host "Starting frontend: http://127.0.0.1:5173"
& $node node_modules\vite\bin\vite.js --host 127.0.0.1 --port 5173
