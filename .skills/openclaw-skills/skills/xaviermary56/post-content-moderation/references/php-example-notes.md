# PHP Example Notes

Use this reference when the user wants to adapt the bundled PHP example to their own backend.

## Bundled files

- `scripts/config.php`
- `scripts/moderation_support.php`
- `scripts/php_xai_client_example.php`

## Style direction

This demo intentionally uses:
- PHP 7.3 compatible syntax
- short array syntax `[]`
- object-oriented structure
- small command entry files
- separated config and support classes
- a migration-friendly engineering skeleton
- DTO-style wrappers for post/comment/result data
- service layer between command and client

## Structure

### `config.php`

Keep configuration in one place:
- x.ai endpoint
- api key
- model name
- pull interface url
- callback url
- timeout settings
- host allowlists
- dry-run switch
- whitelist
- custom rules

### `moderation_support.php`

Keep shared support code in classes:
- constants
- custom exceptions
- logger interface + implementation
- trace id builder
- retry and callback retry policy
- config loader
- URL host allowlist validation
- rule provider interface + loader
- HTTP client
- stdin input reader
- media inspector interface + placeholder
- DTO classes
- result builder and formatter
- post/comment moderation services
- app context

### `php_xai_client_example.php`

Keep moderation transport responsibilities in one class:
- post moderation request
- comment moderation request
- callback request
- model response parsing

## Production advice

- do not store real API keys in git
- keep `temperature = 0`
- log raw model failures separately from content rejections
- if full-auto strict mode is enabled, fail closed on model/network/media errors
- if callback fails, retry with backoff instead of dropping the result silently
- replace placeholder media inspection with real image/video preprocessing
- keep outbound destinations on a strict allowlist
- use `dry_run` while testing pull/audit pipelines before enabling result callbacks
- if moving into Yaf, split current support file into constants, dto, contracts, client, formatter, provider, and service directories

## Important limitation

The current bundled media inspector is only a placeholder. It can count attached media and return a simple status object, but it does **not** actually inspect image or video content. If you need real media moderation, implement OCR, QR detection, frame extraction, and ASR in your own pipeline before using the result for automatic production decisions.
