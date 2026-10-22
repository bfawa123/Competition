@echo off
chcp 65001 >nul
echo ============================================================
echo   知遇 AI 馆员 - 一键启动（同事版）
echo ============================================================
echo.

REM 检查环境是否就绪（后端 venv + 前端 node_modules 缺一不可）
set "NEED_SETUP=0"
if not exist "%~dp0..\frontend\node_modules" set "NEED_SETUP=1"

REM 检测 .venv 是否存在且可用（跨电脑拷贝时 pyvenv.cfg 可能指向不存在的 Python）
if exist "%~dp0..\backend\.venv\Scripts\python.exe" (
    "%~dp0..\backend\.venv\Scripts\python.exe" --version >nul 2>&1
    if errorlevel 1 (
        echo 检测到 backend\.venv 已损坏，正在删除并重建...
        rmdir /s /q "%~dp0..\backend\.venv"
        set "NEED_SETUP=1"
    )
) else (
    set "NEED_SETUP=1"
)

if "%NEED_SETUP%"=="1" (
    echo 首次运行或环境不完整，正在自动安装依赖...
    python "%~dp0..\setup.py"
    if errorlevel 1 (
        echo 环境安装失败，请查看上方报错。
        pause
        exit /b 1
    )
)

REM 启动后端
echo [BACKEND] 启动 FastAPI 后端 (端口 8000)...
start "知遇AI馆员-后端" cmd /k "cd /d "%~dp0..\backend" && .venv\Scripts\python.exe app\main.py"

REM 等待 3 秒后启动前端
timeout /t 3 /nobreak >nul

REM 启动前端
echo [FRONTEND] 启动 Vite 前端 (端口 5173)...
start "知遇AI馆员-前端" cmd /k "cd /d "%~dp0..\frontend" && npm run dev"

echo.
echo ============================================================
echo   后端 API:  http://localhost:8000/docs
echo   前端页面:  http://127.0.0.1:5173
echo ============================================================
echo.
echo   两个窗口已分别打开，关闭窗口即可停止对应服务。
echo.
pause
