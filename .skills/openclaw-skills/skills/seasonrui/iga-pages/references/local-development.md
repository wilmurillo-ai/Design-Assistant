# Local Development

## Basic Usage

```bash
iga pages dev               # start on default port 3000
iga pages dev -p 8080       # start on port 8080
iga pages dev --port 8080   # same as above
```

If your `package.json` dev script already specifies a port, the CLI uses that instead.

## Serverless Functions

The dev server also handles serverless functions placed in the `api/` directory, routing requests to them locally. See `references/functions.md` for handler styles and route patterns.
