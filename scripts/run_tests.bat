@echo off
setlocal
echo ========================================================
echo Running NexoraNet Full Test Suite
echo ========================================================

echo [1/3] Running Backend Ruff Lint Check...
cd /d "%~dp0..\backend"
call .venv\Scripts\activate.bat
python -m ruff check app tests
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Backend ruff check failed!
    exit /b %ERRORLEVEL%
)

echo [2/3] Running Backend Pytest Suite...
python -m pytest tests -v
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Backend tests failed!
    exit /b %ERRORLEVEL%
)

echo [3/3] Running Frontend Vitest Suite...
cd /d "%~dp0..\frontend"
call npm test
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Frontend tests failed!
    exit /b %ERRORLEVEL%
)

echo ========================================================
echo All NexoraNet tests passed successfully!
echo ========================================================
endlocal
