# Security Configuration

## TLS/SSL
- All inter-agent communication must use mTLS in production.
- Use a service mesh (Istio/Linkerd) or manual cert loading.
- Place `server.crt` and `server.key` in this directory (will be mounted as secrets).

## Secrets Management
- Do NOT store secrets in code.
- Use HashiCorp Vault or AWS Secrets Manager.
- In Dev, use environment variables defined in `start_local.ps1`.

## Compliance
- **HIPAA**: Ensure Audit Logs (via Observability Agent) are enabled.
- **PHI**: Do not log raw patient data. Use `patient_id` references only.
