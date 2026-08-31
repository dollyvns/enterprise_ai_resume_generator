# Security Model

## Assets
- Candidate profile and resume PII
- Authentication credentials/tokens
- LLM provider credentials
- Generated resume content
- Audit/observability data

## Primary threats and mitigations

| Threat | Mitigation |
|---|---|
| Prompt injection through resume/JD fields | Inputs serialized as untrusted JSON; every agent system prompt refuses embedded instructions |
| Hallucinated experience/skills | Writer factuality rules + Reviewer unsupported-claim checks |
| Unauthorized API use | JWT authentication + scope enforcement |
| Credential theft | Secrets supplied by environment; production recommendation is cloud secrets manager |
| PII leakage in logs | Request bodies and LLM payloads are not logged |
| Runaway agent loop | Explicit maximum review revisions |
| Resource abuse | Input field limits; production recommendation is API gateway/WAF/distributed rate limiting |
| Container privilege escalation | Non-root image, read-only filesystem, dropped capabilities, no privilege escalation |
| Excessive CORS exposure | Explicit allowlist |
| Trace/log data leakage | Application emits metadata only; profile contents are excluded |

## Production authentication

The local token issuer exists only to make the repository runnable. For enterprise
deployment, validate JWTs issued by an organization IdP such as Okta, Microsoft Entra ID,
Amazon Cognito, or Auth0 and remove the local password endpoint.
