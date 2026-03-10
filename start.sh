#!/bin/bash
export PYTHONPATH=/app

echo "Starting microservices..."

# Start background services
python -m src.auth.main &
python -m src.agents.planner_agent.main &
python -m src.agents.validation_agent.main &
python -m src.agents.denial_prediction_agent.main &
python -m src.agents.fhir_agent.main &
python -m src.agents.edi_agent.main &
python -m src.agents.monitoring_agent.main &
python -m src.agents.explanation_agent.main &

echo "Starting Frontend Bridge on port 7860..."
# Start the bridge service (Flask) on port 7860
python src/frontend/bridge.py
