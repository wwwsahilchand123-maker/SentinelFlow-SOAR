# Response Safety Verification

SentinelFlow is designed for controlled security-response workflows. Before enabling an external connector or automated action, verify the following.

## Pre-flight checks
- Credentials come from environment variables or a secret manager.
- The target environment is explicitly authorized.
- The action has a documented scope and rollback path.
- High-impact actions require human approval.
- Simulation mode is used during initial integration testing.

## Audit requirements
Record the incident or alert identifier, selected playbook, requested action, approval decision, execution result, timestamp, and actor/service identity. Do not store passwords, API keys, access tokens, or unnecessary full payloads in audit records.

## Integration test sequence
1. Run the connector against a test target.
2. Confirm the expected approval gate.
3. Verify the action appears in the audit trail.
4. Verify failure handling does not trigger an unintended fallback action.
5. Test rollback or disable the connector before production use.

Recommended default: observe, simulate, approve, then execute.