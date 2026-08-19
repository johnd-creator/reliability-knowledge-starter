# AGENTS.md — PI Knowledge

## Mission

Discover and maintain authorized PI Web API knowledge for operational and reliability use without altering PI production configuration or data.

## Mandatory Safety Rules

1. READ ONLY.
2. Never perform state-changing calls.
3. Never create/delete/update PI Points, AF Elements, Attributes, analyses, event frames, or configuration.
4. Never brute-force WebIds, tag names, or authentication.
5. Prefer system navigation endpoints and documented API relations.
6. Respect server rate limits.
7. Never commit credentials, cookies, NTLM/Kerberos artifacts, tokens, or session data.
8. Save sanitized samples only.
9. Record units of measure and data type whenever discovered.
10. Record business meaning separately from technical tag names.
11. Never push directly to `main` unless explicitly instructed.

## Preferred Discovery Order

1. PI Web API root / system information
2. Data Servers
3. PI Points
4. Asset Servers
5. AF Databases
6. Elements
7. Attributes
8. Streams
9. Recorded values
10. Interpolated values
11. Summaries

## Git Rules

Use a dedicated branch:

```bash
git switch -c discovery/<short-topic>
```

Keep commits focused:

```text
feat(pi): catalog data servers
feat(pi): map BFP temperature tags
docs(pi): document stream query behavior
```

Do not merge, reset, force-push, or rewrite history unless explicitly authorized.
