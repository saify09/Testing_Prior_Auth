
# Start local agents for development (No Docker)

$env:PYTHONPATH = "$PWD"
$env:DATA_DIR = "$PWD/data"
$PYTHON = "venv\Scripts\python.exe"

# Create log dir
New-Item -ItemType Directory -Force logs

# 1. Auth Service (Port 5000)
Start-Process $PYTHON -ArgumentList "src/auth/oauth2_server/main.py" -WindowStyle Minimized
Write-Host "Auth Service started on 5000"

# 2. Planner Agent (Port 5001)
$env:PORT = "5001"
$env:DENIAL_URL="https://localhost:5003"
$env:FHIR_AGENT_URL="https://localhost:5004"
$env:EDI_AGENT_URL="https://localhost:5005"
Start-Process $PYTHON -ArgumentList "src/agents/planner_agent/main.py" -WindowStyle Minimized
Write-Host "Planner Agent started on 5001"

# 3. Validation Agent (Port 5002)
$env:PORT = "5002"
$env:AUTH_SERVICE_URL="https://localhost:5000"
$env:PLANNER_URL="https://localhost:5001"
Start-Process $PYTHON -ArgumentList "src/agents/validation_agent/main.py" -WindowStyle Minimized
Write-Host "Validation Agent started on 5002"

# 4. Denial Prediction Agent (Port 5003)
$env:PORT = "5003"
Start-Process $PYTHON -ArgumentList "src/agents/denial_prediction_agent/main.py" -WindowStyle Minimized
Write-Host "Denial Agent started on 5003"

# 5. FHIR Agent (Port 5004)
$env:PORT = "5004"
Start-Process $PYTHON -ArgumentList "src/agents/fhir_agent/main.py" -WindowStyle Minimized
Write-Host "FHIR Agent started on 5004"

# 6. EDI Agent (Port 5005)
$env:PORT = "5005"
Start-Process $PYTHON -ArgumentList "src/agents/edi_agent/main.py" -WindowStyle Minimized
Write-Host "EDI Agent started on 5005"

# 7. Monitoring Agent (Port 5006)
$env:PORT = "5006"
Start-Process $PYTHON -ArgumentList "src/agents/monitoring_agent/main.py" -WindowStyle Minimized
Write-Host "Monitoring Agent started on 5006"

# 8. Explanation Agent (Port 5007)
$env:PORT = "5007"
Start-Process $PYTHON -ArgumentList "src/agents/explanation_agent/main.py" -WindowStyle Minimized
Write-Host "Explanation Agent started on 5007"

# 9. Frontend Dashboard (Port 8501)
Start-Process $PYTHON -ArgumentList "-m streamlit run src/frontend/app.py" -WindowStyle Minimized
Write-Host "Frontend Dashboard started on http://localhost:8501"

Write-Host "All agents started using $PYTHON. Logs are in stdout of minimized windows."
