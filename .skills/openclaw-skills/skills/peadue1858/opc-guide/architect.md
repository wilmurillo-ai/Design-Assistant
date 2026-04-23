# Phase 2: Architect

Use this phase when the person has validated their idea and needs to make technical decisions before building.

## Core Principles

Apply these to every recommendation:

1. **Boring by default.** Use proven technology for 90% of what you build. Save novelty for your actual differentiation.
2. **Ship the smallest version first.** What is the one thing users need to get value? Build that. Everything else is deferred.
3. **Reversibility matters more than optimality.** Feature flags, incremental rollouts, data models that can evolve.
4. **Every integration point is a failure point.** External APIs go down. Databases fill up. Networks partition. Design for failure.
5. **DX is product quality.** Slow builds, bad tooling → worse software.
6. **Essential vs accidental complexity.** Before adding anything: "Is this solving a real problem, or one we created?"
7. **Make the change easy, then make the easy change.** Never structural and behavioral changes at the same time.

## Architecture Review

Work through four dimensions:

### 1. Component Design

For each major component:
- **What is its single responsibility?** If you can't describe it in one sentence, it's doing too much.
- **What does it depend on?** What does it NOT depend on?
- **How does data flow in and out?** Draw a simple ASCII diagram.
- **What happens when it fails?** What does the user see? Can they recover?

### 2. Data Model

- **What data do you need to store?** What is the source of truth?
- **What happens to data you don't store?** (Analytics, logs — can these be eventual consistency?)
- **What is the schema evolution strategy?** How do you add fields without breaking existing users?
- **What happens to data on deletion?** (Compliance, backups, cascade.)

### 3. Edge Cases & Failure Modes

- **External API down?** Error? Cached result? Nothing?
- **No network?** Offline support? Graceful degradation?
- **Duplicate data?** Race conditions? Double-submit?
- **Maximum-length input?** 10,000 records? Empty dataset?
- **Concurrent users?** 100 users? 10,000 users?
- **Schema migration without downtime?** Can you deploy changes without breaking users?

**Ask:** "What is the one production incident that will teach you the most? Design for that."

### 4. Testing Strategy

- **Unit level:** Pure logic, transformations, validation.
- **Integration level:** API calls, database operations, queue processing.
- **End-to-end level:** Critical user flows (signup → payment, submit → receive).
- **Error paths:** Every error path needs a test that triggers it.
- **Regression strategy:** If this breaks something that worked yesterday, how do you catch it?

**Minimum bar:** Every new function has a unit test. Every integration has an integration test. Critical flows have E2E tests.

## Distribution Architecture

Answer these — even if the answer is "defer":

1. **How will users access this?** Binary download, package manager, web service, app store?
2. **What is the CI/CD pipeline?** How does code get from your laptop to production?
3. **What platforms?** OS, architecture — x64? ARM? Browser only?
4. **Environment configuration?** Secrets, API keys, feature flags.
5. **How will you deploy updates?** Auto-update? Manual release? Rolling deployment?

**Flag explicitly if deferred.** Write: "DISTRIBUTION: DEFERRED — this will need to be addressed before launch."

## Architecture Decision Record

```markdown
# Architecture Decision: [title]

Date: [date]

## Problem
{One sentence.}

## Key Decisions

### Decision 1: [Name]
**Chosen:** [what you chose]
**Alternatives:** [what else was possible]
**Why:** [one sentence]
**Reversibility:** [easy/medium/hard — how expensive is it to change?]

## Data Flow
```
[ASCII diagram: components, data flow, failure points]
```

## Failure Modes & Mitigations
| Failure | Impact | Mitigation |
|---------|--------|-----------|
| [what fails] | [user impact] | [what you do] |

## Testing Strategy
- Unit: [what]
- Integration: [what]
- E2E: [what]

## Distribution
[How users get this, CI/CD, platforms]

## Open Questions
1. [question]

## Deferred Decisions
1. [what you're deferring] — revisit when [trigger]
```

## Closing

- **The one thing to watch most carefully in production:** The failure mode that would teach you the most
- **The one thing to add first if you have more time:** The deferred decision that pays off fastest
- **The one thing that would make you rethink this entirely:** The assumption that, if wrong, invalidates the whole approach
