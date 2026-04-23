# Facebook Page Posting Skill

A command-line skill for posting to Facebook Pages via the Graph API.

## Overview

This skill provides CLI commands to:
- Post text and images to Facebook Pages
- Schedule posts for later publication
- Manage scheduled posts
- Test connections and verify credentials

## Installation

The skill is installed as an npm package:

```bash
npm install -g clawhub
clawhub install facebookadvanced
```
```bash
cd .\facebook-advanced
npm install
npm link
```

Or run directly from the workspace:

```bash
node C:\Users\OS\.openclaw\workspace\skills\facebook-advanced\index.js <command>
```

## Usage
**OPTIONAL - create facebook-config.json in the same directory as the skill**:
```json
{
  "page_id": "",
  "access_token":"",
  "page_name": "",
}
```
### Setup

First, configure your Facebook Page credentials:

```bash
openclaw-facebook-posting fb-post-setup <page_id> <access_token> [page_name]
```

**Getting a Page Access Token:**
1. Go to [Facebook Developer Console](https://developers.facebook.com/)
2. Create an app (if needed)
3. Add "Graph API" product
4. Generate a Page Access Token with permissions:
   - `pages_manage_posts` - Create and manage posts
   - `pages_read_engagement` - Read page content

### Posting

**Text Post:**
```bash
openclaw-facebook-posting fb-post "Your message here"
```

**Image Post:**
```bash
openclaw-facebook-posting fb-post-image "Caption" "https://example.com/image.jpg"
```

### Scheduling

**Schedule a Post:**
```bash
openclaw-facebook-posting fb-post-schedule "Tomorrow's post!" "2024-04-20T10:00:00Z"
```

**List Scheduled Posts:**
```bash
openclaw-facebook-posting fb-post-schedule-list
```

**Delete Scheduled Post:**
```bash
openclaw-facebook-posting fb-post-schedule-delete <post_id>
```

### Testing

**Test Connection:**
```bash
openclaw-facebook-posting fb-post-test
```

**Show Configuration:**
```bash
openclaw-facebook-posting fb-config-show
```

### Help

```bash
openclaw-facebook-posting --help
```

## Configuration

Configuration is stored in:
```
C:\Users\OS\.openclaw\workspace\facebook-config.json
```

**Security Note:** This file contains your access token. Keep it secure.

## Commands Reference

| Command | Description |
|---------|-------------|
| `fb-post-setup` | Configure Facebook Page credentials |
| `fb-post` | Post text to your Page |
| `fb-post-image` | Post image with caption |
| `fb-post-schedule` | Schedule a post for later |
| `fb-post-schedule-list` | List scheduled posts |
| `fb-post-schedule-delete` | Delete a scheduled post |
| `fb-post-test` | Test connection and permissions |
| `fb-config-show` | Show current configuration |
| `--help` | Show help message |

## Troubleshooting

### Common Issues

**Invalid Access Token:**
- Token expired. Generate a new one and re-run setup.
- Check token permissions.

**Page Not Found:**
- Verify page_id is correct.
- Ensure token has access to the page.

**Permission Denied:**
- Token needs `pages_manage_posts` permission.
- Re-generate token with correct permissions.

## API References

- [Facebook Graph API](https://developers.facebook.com/docs/graph-api/)
- [Page Posts API](https://developers.facebook.com/docs/graph-api/reference/page/posts/)
- [Page Photos API](https://developers.facebook.com/docs/graph-api/reference/page/photos/)

## Security Considerations

- Access tokens are stored in plain text in the config file
- Do not share your config file
- Revoke tokens when no longer needed
- Use environment variables for sensitive data in production

## Development

### Project Structure

```
example-posting/
├── index.js              # Main CLI entry point
├── package.json          # npm package config
├── README.md             # User documentation
├── SKILL.md              # Skill documentation
├── commands/
│   ├── setup.js          # Configuration setup
│   ├── post.js           # Text posting
│   ├── post-image.js     # Image posting
│   ├── post-schedule.js  # Schedule posts
│   ├── post-schedule-list.js  # List scheduled posts
│   ├── post-schedule-delete.js  # Delete scheduled posts
│   ├── post-test.js      # Connection testing
│   ├── config-show.js    # Show configuration
│   └── help.js           # Help message
└── facebook-config.json  # User configuration (created on setup)
```

### Adding New Commands

1. Create a new file in `commands/` directory
2. Export a function that handles the command logic
3. Add the command to `index.js` commands mapping
4. Update `help.js` with documentation

### Testing

```bash
# Test connection
node commands/post-test.js

# Test specific command
node commands/post.js "Test message"
```

## License

MIT
