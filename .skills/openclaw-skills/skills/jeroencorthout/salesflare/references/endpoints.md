# Salesflare API endpoint usage notes

This file is intentionally practical and short. For full coverage, use:

```bash
scripts/sf discover --format table
scripts/sf discover --format markdown > references/endpoints-generated.md
```

## Auth

```bash
export SALESFLARE_API_KEY='YOUR_KEY'
```

## Read examples

### Me / users

```bash
scripts/sf get --path /me
scripts/sf get --path /users --query limit=20
```

### Accounts

```bash
scripts/sf get --path /accounts --query limit=20
scripts/sf get --path /accounts --query search=acme --query limit=10
```

### Contacts

```bash
scripts/sf get --path /contacts --query limit=20
scripts/sf get --path /contacts --query email=someone@example.com
```

### Opportunities

```bash
scripts/sf get --path /opportunities --query limit=20
scripts/sf get --path /opportunities --query search=renewal --query closed=false
```

### Tasks

```bash
scripts/sf get --path /tasks --query limit=20
```

### Tags / pipelines

```bash
scripts/sf get --path /tags --query limit=50
scripts/sf get --path /pipelines
```

## Write examples

### Create account

```bash
scripts/sf post --path /accounts --data-json '{
  "name": "Acme BV",
  "domain": "acme.com"
}'
```

### Create contact

```bash
scripts/sf post --path /contacts --data-json '{
  "email": "john@acme.com",
  "firstname": "John",
  "lastname": "Doe",
  "account": 123
}'
```

### Create opportunity

```bash
scripts/sf post --path /opportunities --data-json '{
  "account": 123,
  "name": "Acme Expansion",
  "value": 12000
}'
```

### Create task

```bash
scripts/sf post --path /tasks --data-json '{
  "description": "Follow up on proposal",
  "account": 123
}'
```

## Pagination

Use `--paginate` for GET list endpoints:

```bash
scripts/sf get --path /accounts --paginate --page-limit 100 --max-pages 10
```

## Discover all endpoints by tag

```bash
scripts/sf discover --tag Accounts
scripts/sf discover --tag Contacts
scripts/sf discover --tag Opportunities
scripts/sf discover --tag Tasks
scripts/sf discover --tag Workflows
```

## Notes

- API docs include legacy/deprecated query-builder filter shapes (`q`, `rules` variants). Prefer simple filters first.
- For complex filtering, test with a read request before using write calls.
- Script retries 429/5xx with exponential backoff.
- Advanced filtering support is raw/pass-through: you can send `q` payloads manually, but this skill does not provide a high-level query-builder abstraction.
- Use `sf_smoketest.py` for re-validation in your own environment. By default it skips DELETE operations unless you pass `--allow-delete`.

## Endpoint-specific caveats (from live tests)

### Persons
- Bare `GET /persons` can return 500.
- Prefer `GET /persons?search=...` or `GET /persons?id=...`.

### Tags
- Treat `GET /tags/{tag_id}` as unsupported in this skill (reproduced 500 with valid IDs).
- Use `GET /tags` and `GET /tags/{tag_id}/usage`.

### Calls and meetings
- `POST /calls` and `POST /meetings` require at least `date` and `participants`.
- Minimal working payload:
  - `{"date":"<ISO8601>","participants":[<contact_id>]}`

### Custom fields
- For `GET /customfields/{itemClass}/{customFieldApiField}/options`, `itemClass` must be plural (`accounts|contacts|opportunities`).
- `POST /customfields/{itemClass}` expects schema-specific payloads, and `type` is numeric in practice. Use `GET /customfields/types` to map valid type IDs.

### Filter fields
- `GET /filterfields/{entity}` works for `contact`, `account`, `opportunity`, `task`, `workflow`, `lead`.
- `person` returned 400 in tests.

### Account relationship update routes
- `POST /accounts/{account_id}/contacts` and `POST /accounts/{account_id}/users` expect an array body like `[{"id": <id>}]`.

### Message feedback
- `POST /messages/{message_id}/feedback` works with a valid accessible message ID and body `{"feedback":"helpful"}`.
- Singular alias `/message/{id}/feedback` also worked in this workspace.

### Fixture dependencies
- Some endpoints require existing resource IDs (groups, meetings, messages). If no such records exist, failures can be fixture/context related instead of endpoint incompatibility.
