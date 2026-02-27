@echo off
echo ===================================================
echo   UHC Agent - Local CI Simulation
echo ===================================================

echo.
echo [1/3] Installing dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt

echo.
echo [2/3] Running Pylint Static Analysis...
pylint src/
if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] Pylint found issues. Please review them before committing.
) else (
    echo [SUCCESS] Pylint passed!
)

echo.
echo [3/3] Verifying Docker Images Build...
docker-compose build
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Docker build failed!
    exit /b %ERRORLEVEL%
) else (
    echo [SUCCESS] Docker images built successfully!
)

echo.
echo ===================================================
echo   Simulation Complete!
echo ===================================================
pause
