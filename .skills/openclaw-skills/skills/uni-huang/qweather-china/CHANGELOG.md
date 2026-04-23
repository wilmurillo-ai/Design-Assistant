# Changelog

All notable changes to this project will be documented in this file.

## [1.3.1] - 2026-03-21

### Added
- Added ClawHub tags: weather, china, utility, qweather

## [1.3.0] - 2026-03-21

### Security
- Added `.gitignore` to prevent sensitive data from being committed
- Added `config.json.template` as a template for configuration
- Removed all hardcoded credentials

### Added
- Added MIT LICENSE file
- Added `CHANGELOG.md` for version tracking
- Added network access declaration in `skill.yaml`
- Added filesystem permission declaration in `skill.yaml`
- Added cross-platform path handling for cache and key paths

### Changed
- Updated version to 1.3.0
- Improved `skill.yaml` with detailed metadata
- Enhanced configuration documentation

### Fixed
- Fixed cross-platform cache directory path handling
- Fixed cross-platform private key path handling

## [1.2.0] - 2026-03-16

### Security
- Removed all hardcoded sensitive API information
- Changed to configuration file based credential management

### Changed
- Changed skill name to "国内天气预报 - 和风天气(QWeather)驱动"
- Changed author to uni-huang
- Unified encoding to UTF-8 without BOM

## [1.1.0] - 2026-03-15

### Added
- Cross-platform compatibility (Windows, Linux, macOS)
- Encoding auto-detection and handling
- Safe print functions for different terminals

## [1.0.0] - 2026-03-13

### Added
- Initial release
- Real-time weather query
- 3-day weather forecast
- Basic life indices
- JWT authentication integration
