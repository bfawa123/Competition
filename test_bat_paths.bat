@echo off
chcp 65001 >nul
echo ============================================================
echo   测试 start.bat 路径计算
echo ============================================================
echo.
echo 当前脚本位置: %~dp0
echo.
echo 检查路径:
echo   setup.py:       %~dp0..\setup.py
echo   frontend:       %~dp0..\frontend
echo   backend:        %~dp0..\backend
echo   venv:           %~dp0..\backend\.venv\Scripts\python.exe
echo.
echo 实际路径:
if exist "%~dp0..\setup.py" (echo   [OK] setup.py 存在) else (echo   [MISS] setup.py 不存在)
if exist "%~dp0..\frontend" (echo   [OK] frontend/ 存在) else (echo   [MISS] frontend/ 不存在)
if exist "%~dp0..\frontend\node_modules" (echo   [OK] frontend\node_modules 存在) else (echo   [WARN] frontend\node_modules 不存在)
if exist "%~dp0..\backend" (echo   [OK] backend/ 存在) else (echo   [MISS] backend/ 不存在)
if exist "%~dp0..\backend\.venv" (echo   [OK] backend\.venv 存在) else (echo   [WARN] backend\.venv 不存在)
if exist "%~dp0..\backend\.venv\Scripts\python.exe" (echo   [OK] venv python.exe 存在) else (echo   [WARN] venv python.exe 不存在)
if exist "%~dp0..\backend\app\main.py" (echo   [OK] backend\app\main.py 存在) else (echo   [MISS] backend\app\main.py 不存在)
echo.
pause
