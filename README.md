# HIPAA-Compliant AI Prior Authorization System

## Overview
This project implements a production-ready agentic AI prior authorization platform supporting UnitedHealthcare, Cigna, and Aetna. It leverages a multi-agent architecture to handle validation, planning, denial prediction, and payer integration via FHIR R4 and X12 EDI 278.

## Architecture
The system consists of several specialized microservices ("agents"):
- **Validation Agent**: Validates incoming requests and authentication.
- **Planner Agent**: Orchestrates the workflow.
- **Denial Prediction Agent**: ML-based risk scoring.
- **FHIR Agent**: Interfaces with FHIR-enabled payers.
- **EDI Agent**: Handles legacy X12 EDI transactions.
- **Monitoring Agent**: Tracks authorization status.
- **Explanation Agent**: Provides rationale for decisions.

## Tech Stack
- **Language**: Python 3.10+
- **Orchestration**: Kubernetes / Docker Compose (Dev)
- **Communication**: REST / gRPC / Message Queues
- **Security**: OAuth2, JWT, TLS, Secrets Management

## Setup
1. **Prerequisites**: Python 3.10+, Docker, Kubernetes (optional for local dev).
2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Run Locally**:
   ```bash
   docker-compose up --build
   ```

## Folder Structure
- `src/agents/`: Agent source code.
- `src/infrastructure/`: Dockerfiles, K8s manifests.
- `src/auth/`: OAuth2 service.
- `src/config/`: Configuration files.
