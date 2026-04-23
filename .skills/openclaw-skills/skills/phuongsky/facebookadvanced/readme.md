# Facebook Page Posting CLI

A command-line tool for posting to Facebook Pages via the Graph API, designed for OpenClaw.

## Features

- **Text Posts**: Post text messages to your Facebook Page
- **Image Posts**: Post images with captions
- **Scheduled Posts**: Schedule posts for later publication
- **Connection Testing**: Verify your credentials and permissions
- **Configuration Management**: Easy setup and configuration display

## Installation

```bash
npm install -g openclaw-facebook-posting
```

Or run directly from the workspace:

```bash
node C:\Users\OS\.openclaw\workspace\skills\example-posting\index.js <command>
```

## Quick Start

### 1. Get a Page Access Token

1. Go to [Facebook Developer Console](https://developers.facebook.com/)
2. Create an app (if you don't have one)
3. Add "Graph API" product
4. Generate a Page Access Token with these permissions:
   - `pages_manage_posts` - Create and manage posts
   - `pages_read_engagement` - Read page content

### 2. Setup Configuration

```bash
openclaw-facebook-posting fb-post-setup <page_id> <access_token> [page_name]
```

Example:
```bash
openclaw-facebook-posting fb-post-setup 123456789 "EAAB..." "My Page Name"
```

### 3. Test Connection

```bash
openclaw-facebook-posting fb-post-test
```

### 4. Start Posting

```bash
# Post text
openclaw-facebook-posting fb-post "Hello, Facebook!"

# Post image
openclaw-facebook-posting fb-post-image "Check this out!" "https://example.com/image.jpg"

# Schedule a post
openclaw-facebook-posting fb-post-schedule "Tomorrow's post!" "2024-04-20T10:00:00Z"
```

## Commands

### Setup & Configuration

- `fb-post-setup <page_id> <access_token> [page_name]` - Configure credentials
- `fb-config-show` - Show current configuration
- `fb-post-test` - Test connection and permissions

### Posting

- `fb-post "<message>"` - Post text to your Page
- `fb-post-image "<caption>" "<image_url>"` - Post image with caption

### Scheduling

- `fb-post-schedule "<message>" "<scheduled_time>"` - Schedule a post
- `fb-post-schedule-list` - List all scheduled posts
- `fb-post-schedule-delete <post_id>` - Delete a scheduled post

### Help

- `--help`, `-h`, `help` - Show help message

## Configuration File

The CLI stores configuration in:
```
C:\Users\OS\.openclaw\workspace\facebook-config.json
```

**⚠️ Security Note**: This file contains your access token. Keep it secure and don't share it.

## Troubleshooting

### "Invalid Access Token"
- Token may have expired. Generate a new one and run `fb-post-setup` again.
- Check that the token has the required permissions.

### "Page Not Found"
- Verify the page_id is correct.
- Ensure the access token has access to the page.

### "Permission Denied"
- Your token needs `pages_manage_posts` permission.
- Re-generate the token with the correct permissions.

## API Reference

- [Facebook Graph API](https://developers.facebook.com/docs/graph-api/)
- [Page Posts](https://developers.facebook.com/docs/graph-api/reference/page/posts/)
- [Page Photos](https://developers.facebook.com/docs/graph-api/reference/page/photos/)

## License

MIT
