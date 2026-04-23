# PHP Demo Suite

Use this reference when the user wants runnable PHP demo files instead of only a single client class.

## Bundled demo scripts

- `scripts/config.php` — centralized config
- `scripts/moderation_support.php` — object-oriented support classes
- `scripts/php_xai_client_example.php` — shared moderation client class
- `scripts/pull_pending_posts.php` — pull pending post list from business API
- `scripts/audit_posts.php` — pull -> audit -> callback full flow
- `scripts/callback_audit_result.php` — callback one moderation result from stdin JSON
- `scripts/audit_comment.php` — moderate one comment from stdin JSON

## Code style

This version follows these conventions:
- PHP 7.3 compatible syntax
- arrays use `[]`
- prefer object-oriented structure over procedural helpers
- keep entry scripts thin
- keep config and support logic separate
- add small infrastructure-style utility classes for maintainability
- add DTO-style wrappers for migration friendliness
- add service layer so command files stop owning business orchestration

## Main classes

### Constants

- `ModerationConst`

### Exceptions

- `ModerationException`
- `ModerationConfigException`
- `ModerationHttpException`
- `ModerationValidationException`

### Interfaces

- `ModerationLoggerInterface`
- `ModerationRuleProviderInterface`
- `ModerationMediaInspectorInterface`

### Utility / support classes

- `ModerationLogger`
- `ModerationTraceIdBuilder`
- `ModerationRetry`
- `ModerationCallbackRetryPolicy`
- `ModerationConfig`
- `ModerationRuleLoader`
- `ModerationHttpClient`
- `ModerationInput`
- `ModerationMediaInspectorPlaceholder`
- `ModerationResultBuilder`
- `ModerationResultFormatter`
- `ModerationAppContext`

### DTOs

- `ModerationPostDto`
- `ModerationCommentDto`
- `ModerationAuditResultDto`

### Services

- `PostModerationService`
- `CommentModerationService`

### Business client

- `PostContentModerationClient`

### Command classes

- `PullPendingPostsCommand`
- `AuditPostsCommand`
- `CallbackAuditResultCommand`
- `AuditCommentCommand`

## What became more engineered

Compared with the previous round, this version adds:
- service layer between commands and the moderation client
- command files that focus on IO instead of moderation orchestration
- a clearer split between transport/client logic and moderation workflow logic

## Suggested next migration path

When moving into a real Yaf project, map these parts like this:
- `ModerationConst` -> library/constants
- DTOs -> library/dto
- interfaces -> library/contracts
- `PostContentModerationClient` -> library/client
- services -> library/service
- `ModerationRuleProviderInterface` + implementation -> library/service or model-backed provider
- `AuditPostsCommand` -> cron/task entry
- `AuditCommentCommand` -> controller/service action
