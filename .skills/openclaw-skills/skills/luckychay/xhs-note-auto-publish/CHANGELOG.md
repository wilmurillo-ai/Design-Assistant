# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-04-08

### Added
- Initial release of xhs-auto-publish skill
- Support for two publishing modes:
  - External topic mode (manual topic specification)
  - Auto topic mode (automatic hot topic detection)
- Idempotency protection to prevent duplicate execution
- Standardized cover generation using ImageMagick
- Mandatory hashtags: #留学新加坡 #新加坡私立大学
- One-time publishing strategy (publish once regardless of success)
- Complete skill documentation and installation scripts

### Features
- Automatic detection of running tasks to avoid conflicts
- Integration with existing xhs skill for content publishing
- Support for cron job scheduling
- Comprehensive error handling and user feedback