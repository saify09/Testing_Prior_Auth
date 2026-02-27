# Runbook: UHC Agent System

## Deployment
### Production (Kubernetes)
1. Ensure `kubectl` is configured.
2. Update Helm charts in `deployments/kubernetes`.
3. Run:
   ```bash
   helm upgrade --install uhc-agent ./src/infrastructure/k8s/charts/uhc-agent
   ```

### Local Development (No Docker)
1. Install Python 3.10+.
2. Install dependencies:
   ```powershell
   python -m pip install -r requirements.txt
   ```
3. Start agents:
   ```powershell
   ./scripts/start_local.ps1
   ```
4. Stop agents:
   ```powershell
   ./scripts/stop_local.ps1
   ```

## Monitoring
- **Logs**: In local dev, logs are in `logs/` or stdout. In Prod, check ELK/Splunk.
- **Health**: Check `/health` endpoint of each agent.
- **Alerts**: Alerts triggered on `DenialAgent.risk_score > 0.8`.

## Incident Response
- **High Error Rate**: Check `ValidationAgent` logs for schema issues.
- **FHIR Timeout**: Verify Payer API connectivity in `FHIRAgent`.
- **Security Breach**: Rotate keys in Vault immediately. Revoke compromised JWT tokens.
