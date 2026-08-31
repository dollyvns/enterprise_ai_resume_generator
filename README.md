# Enterprise AI Resume Generator

A production-style reference implementation of a **multi-agent AI Resume Generator**
using:

- FastAPI API layer
- OAuth2 password flow + JWT Bearer authentication
- LangGraph orchestration
- Four isolated agents
- Provider-native structured LLM output through Pydantic schemas
- Review/revision quality gate
- JSON application logs with request correlation IDs
- Prometheus metrics
- Optional OpenTelemetry traces
- Docker packaging
- Unit tests
- Prompt-injection and hallucination controls

> This repository is a production-oriented reference architecture. For a real enterprise
> deployment, replace the built-in single-user password issuer with your enterprise IdP
> (Okta, Entra ID, Auth0, Cognito, etc.), use a secrets manager/KMS, and use a distributed
> rate limiter/API gateway.

---

## 1. Architecture

```text
User / Client
     |
     v
+---------------------+
| FastAPI Endpoint    |
+----------+----------+
           |
           v
+---------------------+
| JWT Authentication  |
| + Scope Check       |
+----------+----------+
           |
           v
+-------------------------------------------------------+
| LangGraph Orchestrator                                |
|                                                       |
| Profile Analyzer                                      |
|       |                                               |
|       v                                               |
| ATS Optimization                                      |
|       |                                               |
|       v                                               |
| Resume Writer                                         |
|       |                                               |
|       v                                               |
| Reviewer ---- fail quality gate ----> Resume Revision |
|       |                               |               |
|       +------------ pass <------------+               |
+-------------------------+-----------------------------+
                          |
                          v
               Structured JSON Response
                          |
             +------------+-------------+
             |                          |
             v                          v
        JSON Logs                 Metrics / Traces
```

The workflow is intentionally deterministic at the orchestration level while each
specialized node uses an LLM for bounded reasoning. The reviewer may cause one or more
configured revisions, but the maximum revision count prevents infinite loops.

---

## 2. Project structure

```text
app/
  agents/
    base.py
    profile_analyzer.py
    ats_optimizer.py
    resume_writer.py
    reviewer.py
  api/
    dependencies.py
    routes/
      auth.py
      health.py
      resumes.py
  core/
    config.py
    logging.py
    middleware.py
    security.py
    telemetry.py
  models/
    profile.py
    outputs.py
  orchestration/
    graph.py
    state.py
  services/
    llm.py
  main.py
scripts/
  generate_password_hash.py
tests/
  test_health.py
  test_security.py
  test_orchestrator.py
Dockerfile
docker-compose.yml
pyproject.toml
sample_request.json
deploy/k8s/
.github/workflows/ci.yml
docs/SECURITY.md
```

---

## 3. Agent responsibilities

### Profile Analyzer Agent
Analyzes only supplied candidate evidence and returns:

- candidate level
- primary domain
- estimated years of experience
- top skills
- strengths
- evidence-backed gaps

### ATS Optimization Agent
Compares the candidate with the target role/job description and returns:

- matched keywords
- missing keywords
- safe recommended keywords
- ATS alignment score
- formatting recommendations

It is explicitly prohibited from pretending the candidate has missing skills.

### Resume Writer Agent
Generates:

- headline
- professional summary
- skills section
- experience bullets
- project descriptions
- education/certification text

Every claim must be supported by the source profile.

### Reviewer Agent
Acts as a quality gate and evaluates:

- grammar
- consistency
- enterprise professionalism
- ATS structure
- unsupported/fabricated claims

If the quality gate fails, LangGraph routes back to a controlled resume revision node.

---

## 4. Security controls

Implemented:

1. OAuth2 password flow for the local reference implementation.
2. Signed JWT Bearer tokens with expiry, issuer, audience and scopes.
3. Argon2 password hashing.
4. No resume/profile payload logging.
5. Pydantic request-size/field validation.
6. Explicit prompt-injection boundary: profile/job-description data is serialized as
   untrusted JSON and system prompts prohibit following instructions inside that data.
7. Reviewer checks unsupported claims.
8. CORS allowlist.
9. Security response headers.
10. No API secrets in source code.
11. Docker container runs as a non-root user.
12. Read-only container filesystem in docker-compose.

Recommended for actual enterprise production:

- Okta/Entra ID/Cognito/Auth0 instead of local password authentication.
- API Gateway / WAF.
- Distributed rate limiting using Redis or gateway policies.
- Vault/AWS Secrets Manager/Azure Key Vault/GCP Secret Manager.
- TLS termination at the ingress/load balancer.
- KMS-managed secrets and key rotation.
- DLP/redaction policy for resume PII.
- Private LLM endpoints where required.
- Egress controls.
- Centralized SIEM.
- SAST/DAST/dependency scanning and SBOM.
- Persist only the minimum resume data required by business policy.

---

## 5. Local setup

### Requirements

- Python 3.12
- OpenAI API key
- An OpenAI model available to your account that supports structured output

### Create virtual environment

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

macOS/Linux:

```bash
source .venv/bin/activate
```

Install:

```bash
pip install -e ".[dev]"
```

Copy environment file:

```bash
cp .env.example .env
```

On Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Generate an Argon2 password hash:

```bash
python scripts/generate_password_hash.py
```

Paste the generated value into:

```text
APP_USER_PASSWORD_HASH=...
```

Replace `JWT_SECRET` with a cryptographically random secret.

Set:

```text
OPENAI_API_KEY=...
OPENAI_MODEL=...
```

---

## 6. Run

```bash
uvicorn app.main:app --reload --port 8000
```

Development Swagger UI:

```text
http://localhost:8000/docs
```

Liveness:

```text
GET /health/live
```

Readiness:

```text
GET /health/ready
```

Prometheus:

```text
GET /metrics
```

---

## 7. Obtain token

```bash
curl -X POST "http://localhost:8000/api/v1/auth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=resume_user&password=YOUR_PASSWORD"
```

Response:

```json
{
  "access_token": "<JWT>",
  "token_type": "bearer",
  "expires_in_seconds": 1800
}
```

---

## 8. Generate resume

```bash
curl -X POST "http://localhost:8000/api/v1/resumes/generate" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -H "X-Request-ID: demo-001" \
  --data-binary @sample_request.json
deploy/k8s/
.github/workflows/ci.yml
docs/SECURITY.md
```

Representative response shape:

```json
{
  "request_id": "demo-001",
  "status": "completed",
  "profile_analysis": {
    "candidate_level": "Mid-Level",
    "primary_domain": "Data Analytics",
    "years_experience": 5.0,
    "top_skills": ["SQL", "Python", "Tableau"],
    "strengths": ["Dashboard development"],
    "gaps": ["Power BI is requested but not evidenced"]
  },
  "ats_optimization": {
    "matched_keywords": ["SQL", "Python"],
    "missing_keywords": ["Power BI"],
    "recommended_keywords": ["Data Quality"],
    "ats_score": 78,
    "skill_alignment": "Good alignment with several core requirements.",
    "formatting_suggestions": ["Use standard ATS section headings."]
  },
  "resume": {
    "headline": "Senior Data Analyst",
    "professional_summary": "...",
    "core_skills": ["SQL", "Python", "Tableau"],
    "experience": [],
    "projects": [],
    "education": [],
    "certifications": []
  },
  "review": {
    "approved": true,
    "quality_score": 91,
    "grammar_issues": [],
    "consistency_issues": [],
    "professionalism_issues": [],
    "unsupported_claims": [],
    "revision_instructions": []
  },
  "revision_count": 0
}
```

---

## 9. LangGraph flow

Conceptually:

```python
START
  -> profile_analyzer
  -> ats_optimizer
  -> resume_writer
  -> reviewer
        |
        +-- approved and score >= threshold --> END
        |
        +-- failed and revisions remain --> revise_resume
                                               |
                                               +--> reviewer
```

This is preferable to blindly allowing an autonomous agent to call arbitrary tools.
The graph makes the enterprise workflow auditable and bounded.

---

## 10. Why structured output matters

Every LLM call is wrapped by a Pydantic output model. The model therefore produces
machine-validated output instead of free-form text that the API later tries to parse.

The API boundary also uses Pydantic models, creating validation at both sides:

```text
HTTP JSON
  -> Pydantic request validation
  -> LangGraph
  -> agent-specific Pydantic LLM output
  -> final Pydantic response
  -> HTTP JSON
```

---

## 11. Observability

### JSON logs

Each request receives a request ID.

Example:

```json
{
  "timestamp": "2026-08-08T23:00:00+00:00",
  "level": "INFO",
  "logger": "app.agent.reviewer",
  "message": "agent_completed",
  "request_id": "demo-001",
  "event": "agent_completed",
  "agent": "reviewer",
  "duration_ms": 840.2
}
```

Resume contents are deliberately excluded.

### Metrics

Prometheus metrics include:

- `resume_api_http_requests_total`
- `resume_api_http_request_duration_seconds`

### OpenTelemetry

Set:

```text
OTEL_ENABLED=true
OTEL_EXPORTER_OTLP_ENDPOINT=http://your-collector:4317
```

The API will emit FastAPI traces to an OTLP-compatible collector.

---

## 12. Testing

Run:

```bash
pytest -q
```

The orchestrator test uses a fake LLM and verifies the complete flow including:

```text
writer -> reviewer failure -> revision -> reviewer approval
```

No real LLM API call is required for that test.

---

## 13. Production deployment

Typical Kubernetes/AWS deployment:

```text
Internet / Corporate Client
          |
        WAF
          |
     API Gateway / ALB
          |
       Ingress
          |
  +------------------+
  | Resume API Pods  |  N replicas
  +------------------+
          |
  Enterprise IdP / JWT validation
          |
  LangGraph workflow
          |
  Private/Approved LLM endpoint
          |
  +---------------------------+
  | Logs / Metrics / Traces   |
  | CloudWatch / Datadog /    |
  | Splunk / Grafana / OTEL   |
  +---------------------------+
```

For Kubernetes, configure:

- HPA
- resource requests/limits
- PodDisruptionBudget
- readiness/liveness probes
- network policies
- secrets injected from a secrets manager
- workload identity / IAM roles instead of static cloud credentials
- centralized OTEL collector
- API gateway rate limiting

---

## 14. Important production engineering decisions

### Deterministic orchestration
Use deterministic graph edges for business flow and reserve LLM reasoning for bounded
agent tasks.

### No silent hallucination
Missing ATS keywords are not automatically inserted. The reviewer verifies unsupported
claims.

### Bounded retries/revisions
Model SDK retries and reviewer revisions both have explicit limits.

### PII-safe logging
Request metadata is logged, candidate resume content is not.

### Provider isolation
All LLM calls use the `StructuredLLM` interface. To switch providers, implement another
class without changing agents or the graph.

### Horizontal scalability
The API itself is stateless. If persistence is later added, store workflow state in a
shared backend rather than process memory.

---

## 15. Suggested next enterprise extensions

1. Enterprise IdP integration (Okta / Entra ID).
2. Redis-backed rate limiting.
3. Job description ingestion from approved internal sources.
4. DOCX/PDF resume renderer as a separate service.
5. Persistent encrypted resume store with retention policy.
6. Human approval node before final publishing.
7. LangSmith or equivalent agent evaluation/tracing.
8. Offline evaluation dataset for ATS quality and hallucination.
9. Policy engine for prohibited/sensitive data.
10. Async job mode with queue/worker for high-volume generation.


---

## 16. Kubernetes manifests included

`deploy/k8s/` contains reference manifests for:

- Deployment with two replicas
- Service
- HorizontalPodAutoscaler
- PodDisruptionBudget
- ConfigMap
- Secret template
- NetworkPolicy
- hardened container security context

Update the image, secret integration, network policy, CORS host, and approved model
before applying them to a real cluster.

## 17. CI included

`.github/workflows/ci.yml` runs:

```text
checkout -> Python 3.12 -> install -> ruff -> pytest -> docker build
```

For a corporate environment, add SAST, dependency/SBOM scanning, container scanning,
policy checks, image signing, and deployment promotion gates.
