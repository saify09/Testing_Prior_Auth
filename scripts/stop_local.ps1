
# Stop local python agents
# WARNING: This kills all python processes started from this folder location pattern
# A more robust way is to track PIDs, but for dev this suffices if careful.

Write-Host "Stopping UHC Agent services..."
Get-Process python | Where-Object {$_.MainWindowTitle -like "*main.py*"} | Stop-Process -Name "python" -Force -ErrorAction SilentlyContinue
Stop-Process -Name "streamlit" -Force -ErrorAction SilentlyContinue 
Write-Host "Stopped."
