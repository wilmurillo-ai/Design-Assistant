# Publishing

## Pre-publish checklist

- confirm the slug: `google-stitch-workflow`
- confirm the release version: `1.2.0`
- confirm `SKILL.md` is self-contained enough for public readers
- confirm supporting files are intentional and minimal
- confirm you are comfortable publishing under the included MIT License

## Publish

From this repo's `publish/` directory:

```bash
cd publish
clawhub login
clawhub publish ./google-stitch-workflow --slug google-stitch-workflow --name "Google Stitch Workflow" --version 1.2.0 --tags latest --changelog "Add greenfield-app guidance: use accepted Stitch exports as translation seeds instead of rebuilding from screenshots."
```

Or, from the repo root without changing directories:

```bash
clawhub login
clawhub publish ./publish/google-stitch-workflow --slug google-stitch-workflow --name "Google Stitch Workflow" --version 1.2.0 --tags latest --changelog "Add greenfield-app guidance: use accepted Stitch exports as translation seeds instead of rebuilding from screenshots."
```

## Verify

After publishing:

```bash
clawhub search "google stitch"
```

Then check the ClawHub page and verify:

- the title and description render correctly
- the `SKILL.md` sections are readable
- the supporting reference files are included
- the changelog and version appear as expected
