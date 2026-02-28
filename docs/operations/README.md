# Operations

## LiteLLM Secure Mode Requirements

LiteLLM secure mode requires a PostgreSQL database. It will not run without a
valid `DATABASE_URL`.

Example:

```
export DATABASE_URL="postgresql://user:password@localhost:5432/litellm"
litellm --config litellm_config.secure.example.yaml --port 4001
```

## Deployment Targets Beyond Docker

See `docs/operations/deployment-targets.md` for non-Docker options and their
tradeoffs.
