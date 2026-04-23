# ClawRecipes Plugin

**ClawRecipes** is a comprehensive OpenClaw plugin that enables markdown-based recipe authoring for scaffolding agents and teams.

## What it does

- **Recipe Authoring**: Create agent/team configurations using markdown templates
- **Scaffolding**: Instantly deploy agents and teams from recipes
- **Workflow Management**: Built-in workflow runners and team coordination
- **Template Library**: Pre-built recipes for common agent patterns

## Installation

```bash
openclaw skills install clawrecipes
```

## Usage

After installation, use the `openclaw recipes` command:

```bash
# List available recipes
openclaw recipes list

# Scaffold a team from a recipe
openclaw recipes scaffold-team my-team

# Create an agent from a recipe
openclaw recipes scaffold my-agent
```

## Features

- ✅ Markdown-based recipe format
- ✅ Team and individual agent scaffolding
- ✅ Workflow automation and runners
- ✅ Built-in template library
- ✅ Kitchen UI integration
- ✅ Git-friendly configuration

## Use Cases

- **Development Teams**: Scaffold coding teams with lead, dev, QA roles
- **Marketing Teams**: Create content, social, and campaign automation teams
- **Customer Support**: Deploy triage, resolution, and knowledge base teams
- **Custom Workflows**: Build specialized agent teams for your use case

## Requirements

- OpenClaw 2026.3.x or later
- Node.js 22+

## Documentation

Full documentation available at: https://github.com/JIGGAI/ClawRecipes

## Support

- GitHub Issues: https://github.com/JIGGAI/ClawRecipes/issues
- Discord: https://discord.com/invite/clawd