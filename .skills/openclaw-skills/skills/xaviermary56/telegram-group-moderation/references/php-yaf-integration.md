# PHP / Yaf Integration Notes

Use this when integrating Telegram moderation into a PHP 7.3 + Yaf project.

## Suggested placement

- webhook entry -> controller action or dedicated callback entry
- normalization -> library/service layer
- moderation core client -> library/client or service
- Telegram action client -> library/client
- offense tracking -> model layer

## Suggested flow in Yaf

1. webhook controller receives Telegram update JSON
2. validate secret / source / allowed chat
3. normalize update to internal moderation DTO
4. call moderation policy service
5. map result to Telegram action
6. persist moderation log
7. return fast HTTP 200 to Telegram

## Performance advice

- avoid heavy synchronous media downloads in webhook request path
- if media processing is needed, push to queue and return quickly
- rate-limit delete/mute/ban actions
- separate Telegram API failure logs from moderation decision logs

## Security advice

- never hardcode bot token
- restrict webhook route exposure
- verify allowed chat ids before action execution
- keep timeout and connect_timeout explicit for all outbound HTTP calls
