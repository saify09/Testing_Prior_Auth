# Agentic AI Connector for UHC Prior Authorization API

## Objective

Design an agentic AI connector that integrates with the UnitedHealthcare (UHC) Prior Authorization API to automate, assist, and monitor prior authorization workflows in a secure, explainable, and compliant manner.

The system aims to:
*   **Reduce manual effort for providers**
*   **Improve prior authorization turnaround time**
*   **Ensure data completeness before submission**
*   **Provide transparent explanations for approval/denial outcomes**
*   **Maintain HIPAA-aligned handling of PHI**

## Features

- **Web Interface**: A user-friendly, responsive frontend for non-technical users (`http://localhost:8001/`).
- **Autonomous Orchestration**: A multi-agent system coordinated by a Planner Agent to execute the Discovery -> Validation -> Submission loop.
- **HIPAA Compliance**: Built-in **PHI Redaction** in server logs to ensure patient data is never exposed in the backend console.
- **Mock UHC API**: Simulates FHIR-compliant endpoints for OAuth, Coverage Requirements Discovery (CRD), and Prior Authorization Support (PAS).
- **Clinical Validation**: A Validation Agent (Compliance Officer) performs "Gap Analysis" on clinical notes before submission.
- **Human-Readable Feedback**: An Explanation Agent provides transparent reasons for approvals (e.g., "Medical necessity demonstrated") and clear next steps.

## Architecture

The system is built with Python (FastAPI/AsyncIO) and follows the Agentic Loop:
1.  **Discovery**: Checks if Prior Auth is required (CRD).
2.  **Validation**: Ensures data completeness (DTR).
3.  **Submission**: Submits the request if valid (PAS).

## Repository Structure
```
.
├── agents/                 # Autonomous Agent Modules
│   ├── base_agent.py       # Base class with HIPAA-compliant logging
│   ├── validation_agent.py # Logic for CPT/Clinical Data checks
│   ├── planner_agent.py    # Workflow orchestration logic
│   ├── uhc_api_agent.py    # API connector (Auth, PAS)
│   └── explanation_agent.py# User-facing summary generation
├── static/                 # Frontend Assets
│   ├── index.html          # Web Interface
│   ├── script.js           # Frontend Logic
│   └── styles.css          # Styling
├── mock_uhc_api.py         # Mock FHIR Server (FastAPI)
├── orchestrator.py         # Main Agentic Loop
└── requirements.txt        # Dependencies
```

## API Reference (Mock)
The prototype simulates these key UHC/FHIR endpoints:
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/oauth/token` | Generates Mock OAuth2 Bearer Token |
| `POST` | `/crd/coverage-requirement` | Checks if Prior Auth is required (CRD) |
| `POST` | `/pas/submit` | Submits the Prior Authorization Request |
| `GET`  | `/eligibility/coverage` | Checks Member Eligibility |
| `POST` | `/agent/run` | **Agentic Endpoint** - Triggers the agent workflow |

## Technical Implementation: Integration Logic

The system uses a **Single-Server Architecture** to ensure seamless communication between the Agent Logic and the User Interface.

1.  **Backend (`mock_uhc_api.py`)**:
    *   Initializes a `FastAPI` application.
    *   **Mounts** the `static/` directory to serve the HTML/CSS/JS frontend on the root path (`/`).
    *   **Exposes** the `/agent/run` endpoint, which wraps the `run_orchestrator` async function.
    *   **Enables CORS** to allow flexible access methods.

2.  **Frontend (`static/script.js`)**:
    *   Collects user input from `index.html`.
    *   Sends an asynchronous `POST` request to `http://localhost:8001/agent/run`.
    *   Receives the `AgentState` JSON object and dynamically updates the UI based on `final_explanation`.

## Setup & Usage

### Prerequisites
- Python 3.8+
- `pip`

### Quick Start (Windows)
Simply double-click the **`start_prototype.bat`** file. 
*   It will install dependencies.
*   Start the server.
*   Automatically open the Web Interface in your default browser.

### Manual Installation
1.  Clone the repository.
2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

### Running the Prototype (Manual)

**Step 1: Start the Server**
```bash
python mock_uhc_api.py
```
*The server will run on `http://localhost:8001`*

**Step 2: Use the Agent**

#### Option A: Web Interface
1.  Open [http://localhost:8001/](http://localhost:8001/).
2.  Enter Member ID, CPT Code (e.g., `70450`), and Notes.
3.  Click **Run Agent Analysis**.

#### Option B: Command Line (CLI)
```bash
python orchestrator.py --cpt "70450" --notes "Patient has chronic migraines. CT Head required."
```

## Agent Roles
- **Validation Agent**: Compliance Officer ensuring data integrity.
    - *New*: **Specificity Rule** - Rejects generic notes (e.g., "abdomen pain") unless they include severity, duration, or prior history (e.g., "severe abdomen pain", "unresponsive to medication").
    - *New*: **Gibberish Detector** - Filters out non-clinical text input.
- **Planner Agent**: Strategist for workflow execution.
- **UHC API Agent**: Secure connector for API transactions.
- **Explanation Agent**: Clinical Liaison for user-friendly communication.
