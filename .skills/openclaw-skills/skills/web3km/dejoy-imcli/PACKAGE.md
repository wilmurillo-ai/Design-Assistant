# Publishing notes

## Purpose

Zip the entire **`dejoy-imcli`** directory (or upload that folder as required) and submit it to ClawHub as the skill package.

## Upstream source

The Go source for `imcli` lives in the Synapse/DeJoy project repository under:

- `tools/imcli/` (includes `cmd/imcli`, `internal/dejoy`, `go.mod`)

This upload bundle **intentionally excludes** source code to avoid duplicating the main repo; users clone upstream and run `go build` locally.

## Versioning

Record in ClawHub or a changelog:

- Skill document version (e.g. date of the bundled `SKILL.md`)
- Compatible `imcli` behavior version (e.g. git tag when you publish releases)

## Release changelog template

Copy this section into your release notes and replace placeholders:

```md
## dejoy-imcli skill release - <YYYY-MM-DD>

### Summary
- <1-line summary of why this release exists>

### Added
- <new capability 1>
- <new capability 2>

### Changed
- <behavior or docs update 1>
- <behavior or docs update 2>

### Fixed
- <bug fix 1>
- <bug fix 2>

### Compatibility
- Skill package version: <vX.Y or date tag>
- Expected imcli behavior baseline: <git tag / commit / release>
- Matrix API scope: `/_matrix/client/v3`

### Notes for operators
- <migration note, if any>
- <known limitation, if any>
```

## Compatibility matrix template

Use this table in release docs when needed:

| Skill package version | Tested `imcli` build | Notable capabilities |
|---|---|---|
| `<vX.Y>` | `<tag-or-commit>` | `<e.g. create-room --space-id, set-topic --clear, set-avatar --clear>` |

## Publishing checklist

- [ ] `SKILL.md` reflects current command flags and examples
- [ ] `SKILL.md` frontmatter declares credentials consistently:
  - `primaryEnv: DEJOY_ACCESS_TOKEN`
  - `requiredEnv: [DEJOY_HOMESERVER, DEJOY_ACCESS_TOKEN]`
- [ ] `README.md` quick start is updated and runnable
- [ ] `README.md` includes credential supply method and safety notes
- [ ] No secrets or environment-specific tokens are present
- [ ] Bundle contains only `SKILL.md`, `README.md`, `PACKAGE.md`
- [ ] Slug and display name match ClawHub submission (`dejoy-imcli` / `DeJoy IM CLI`)
