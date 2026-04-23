# github-readme-maker

Generate a polished GitHub profile README from a simple config.

## Usage

```
Generate a GitHub README for [description of you/your project]
```

The agent reads the user's intent and generates a complete `README.md` with:
- Profile header with name, badges, and tagline
- GitHub stats (streak, top languages, contributions)
- Sections: About, Skills/Tech Stack, Projects, Contact
- Social links
- Minimal, modern, or classic style variants

## Input Fields

| Field | Description | Default |
|-------|-------------|---------|
| name | Your name or project name | — |
| description | What you're about | — |
| style | minimal / modern / classic | modern |
| github_username | For stats widgets | — |
| skills | Comma-separated tech stack | — |
| projects | List of projects with repo URLs | — |
| social | Links (twitter, linkedin, website) | — |

## Output

Writes a complete `README.md` to the current directory.

## Examples

- "Generate a GitHub README for me: name=Alex Chen, full-stack dev, knows React/Python/Go, my projects are https://github.com/alex/myapp and https://github.com/alex/cli-tool"
- "Make a minimal README for my open source project called FastAPI Boilerplate"

## Notes

- Uses shields.io for badges
- GitHub stats from github-readme-stats
- No API key required
- Suitable for both personal profiles and project repos
