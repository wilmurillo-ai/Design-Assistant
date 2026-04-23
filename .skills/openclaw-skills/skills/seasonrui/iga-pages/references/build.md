# Build

## Basic Usage

```bash
iga pages build             # build to .iga/ (default output dir)
iga pages build -o dist     # build to custom output directory
```

The CLI auto-detects the framework and runs the appropriate build. Next.js projects get SSR/SSG support; all others produce static output.

## Output Directory

Default output: `.iga/`

## Configuration Override

In `iga.json` you can override build settings:

```json
{
  "installCommand": "pnpm install",
  "buildCommand": "npm run build:prod",
  "outputDirectory": "my-dist"
}
```

| Field             | Description                         |
| ----------------- | ----------------------------------- |
| `installCommand`  | Override the install command        |
| `buildCommand`    | Override the build command          |
| `outputDirectory` | Override the build output directory |

`iga.json` takes priority over Console settings and framework defaults.

## Package Manager

Supported package managers:

| Package Manager | Supported Versions |
| --------------- | ------------------ |
| npm             | 10                 |
| pnpm            | 7, 8, 9, 10        |
| yarn            | 1, 2               |
