# ClawHub Publish Checklist

## 1. Metadata & Packaging
- [ ] Skill name: `aivideo-api-executor`
- [ ] Description includes trigger terms: API, generate, status, cancel, polling
- [ ] Version is bumped (SemVer)
- [ ] `SKILL.md` line count is under 500
- [ ] References are one-level deep (`reference.md`, `examples.md`)

## 2. Security
- [ ] API key loaded only from environment variable
- [ ] Logs never print full API key
- [ ] URL query params are sanitized in logs
- [ ] No secrets committed to repository

## 3. Runtime Reliability
- [ ] Timeout enabled (`AIVIDEO_TIMEOUT_MS`)
- [ ] Idempotent retries enabled for GET endpoints
- [ ] 429 handling reads `Retry-After`
- [ ] Exponential backoff with jitter is active
- [ ] Errors mapped to stable `errorCode`

## 4. Smoke Validation (Sandbox Key)
- [ ] `t2v` create test passed
- [ ] `i2v` create test passed
- [ ] `t2v_v3` create test passed
- [ ] Cancel task behavior verified (`SUBMITTED` only)
- [ ] 429 behavior verified (or replayed in test env)

## 5. ClawHub Release
- [ ] Upload skill package
- [ ] Verify render of `SKILL.md`, `reference.md`, `examples.md`
- [ ] Verify command examples run in runtime environment
- [ ] Tag release notes with breaking changes (if any)

## 6. Post-release Monitoring
- [ ] Track first 24h failure rate
- [ ] Track average completion time
- [ ] Track 429 ratio and retry success
- [ ] Prepare rollback to previous stable version
