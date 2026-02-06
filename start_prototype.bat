@echo off
echo ============================================================
echo   Agentic AI Connector for UHC Prior Authorization API
echo ============================================================
echo.
echo [1/2] Installing/Verifying Dependencies...
pip install -r requirements.txt
echo.
echo [2/2] Starting Mock UHC API & Agent Frontend...
echo.
echo    - Backend: http://localhost:8001
echo    - Frontend: http://localhost:8001/ (Opening in browser...)
echo.
echo Press Ctrl+C to stop the server.
echo.

start "" "http://localhost:8001/"
python mock_uhc_api.py
pause
