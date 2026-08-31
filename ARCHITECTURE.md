# Architecture Notes

## Mandatory flow mapping

| Requirement | Implementation |
|---|---|
| User/API Request | `POST /api/v1/resumes/generate` |
| FastAPI Endpoint | `app/api/routes/resumes.py` |
| Authentication Layer | `app/core/security.py`, `app/api/routes/auth.py` |
| Orchestrator | `app/orchestration/graph.py` |
| Profile Analyzer Agent | `app/agents/profile_analyzer.py` |
| ATS Optimization Agent | `app/agents/ats_optimizer.py` |
| Resume Writer Agent | `app/agents/resume_writer.py` |
| Reviewer Agent | `app/agents/reviewer.py` |
| Structured JSON Response | `app/models/outputs.py` |
| Logs + Monitoring | `app/core/logging.py`, `app/core/middleware.py`, `app/core/telemetry.py` |

## Trust boundaries

```text
External client
   |
   | Untrusted HTTP
   v
FastAPI validation
   |
   | Authenticated request
   v
Application domain
   |
   | Untrusted resume/JD data serialized to JSON
   v
LLM provider
   |
   | Schema-constrained model output
   v
Pydantic validation + Reviewer quality gate
   |
   v
Client response
```

## Agent independence

Each agent has:

- one responsibility,
- one system policy,
- one structured output type,
- no direct HTTP dependency,
- no knowledge of FastAPI,
- no direct secret access,
- no arbitrary tool execution.

This separation makes the agents individually testable and replaceable.
