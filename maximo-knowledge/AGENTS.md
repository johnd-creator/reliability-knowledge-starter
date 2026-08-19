# AGENTS.md — Maximo Knowledge

## Mission

Discover, verify, document, and maintain the Maximo API knowledge available to this organization without changing production data.

## Mandatory Safety Rules

1. READ ONLY.
2. Never execute POST, PUT, PATCH, DELETE, MERGE, or any state-changing request against production.
3. Never brute-force paths, IDs, object names, or credentials.
4. Prefer OpenAPI/OAS metadata and documented resources before probing.
5. Respect server-side rate limits and add delays when enumerating large collections.
6. Never store credentials, passwords, tokens, cookies, API keys, session identifiers, or Authorization headers.
7. Sanitize all saved response examples.
8. Do not commit personal data unless explicitly approved and required.
9. Do not infer business meaning without evidence.
10. If access behavior is uncertain, stop and record the endpoint as `unknown`.
11. Never change remote Git history.
12. Never push directly to `main` unless explicitly instructed.

## Discovery Procedure

For every resource:

1. Identify the documented endpoint.
2. Record HTTP method.
3. Record required/optional parameters.
4. Test the smallest safe read request.
5. Record status and access result.
6. Record response structure only.
7. Map relevant fields to business meaning.
8. Record pagination/filter/sort capabilities.
9. Store sanitized sample.
10. Update `verified_at`.

## Required Metadata Per Endpoint

- system
- resource
- endpoint
- method
- status
- access
- description
- parameters
- important_fields
- relationships
- use_cases
- notes
- verified_at

## Git Working Rules

Before modifying files:

```bash
git status
git branch --show-current
git fetch --all --prune
```

Create a dedicated branch:

```bash
git switch -c discovery/<short-topic>
```

Use small commits:

```text
docs(maximo): document workorder endpoint
feat(discovery): add asset object structure
docs(mapping): map failure fields
```

Before handoff:

```bash
git diff --check
git status
```

Do not merge, rebase, reset, force-push, or delete branches unless explicitly instructed.
