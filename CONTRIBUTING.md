# Contributing to SentinelFlow SOAR

SentinelFlow is a defensive security engineering demonstration. Contributions should improve reliability, clarity, testability, or safe automation.

## Before submitting a change

- Keep changes focused and explain the security impact.
- Never commit credentials, tokens, production logs, or real incident evidence.
- Add tests for changed backend behavior where practical.
- Run the backend suite with:

```bash
cd backend
python -m pytest -v
```

## Automation changes

Document new playbook steps and clearly identify actions that require human approval. Destructive integrations should remain simulated or explicitly gated unless their safety controls are documented.

## Pull requests

Include what changed, how it was tested, and any migration, API, authentication, or authorization implications.
