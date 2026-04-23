# Stress Sleep AI Skill

## Overview

The Stress Sleep AI Skill is an OpenClaw plugin that provides scientific stress analysis, sleep optimization, audio therapy, breathing exercises, and mindfulness practices. Based on the AISleepGen autonomous meditation AI agent architecture, this skill focuses on evidence-based techniques for mental wellness.

## Features

### 1. Stress Analysis System
- **Real-time stress assessment**: Analysis based on user-provided physiological data
- **Personalized recommendations**: Customized suggestions based on stress patterns
- **Progress tracking**: Long-term stress trend monitoring

### 2. Sleep Analysis System
- **Sleep quality assessment**: Analysis of sleep duration, quality, and patterns
- **Optimization suggestions**: Evidence-based recommendations for better sleep
- **Sleep hygiene guidance**: Practical tips for improving sleep environment

### 3. Audio Therapy System
- **Scientific audio protocols**: Alpha waves, theta waves, white noise, pink noise
- **Brainwave entrainment**: Audio stimulation for relaxation and focus
- **Customizable sessions**: Different durations and intensity levels

### 4. Breathing Exercise System
- **Multiple techniques**: Box breathing, 4-7-8 breathing, diaphragmatic breathing
- **Step-by-step guidance**: Clear instructions for each technique
- **Physiological benefits**: Stress reduction, anxiety management, focus improvement

### 5. Mindfulness Practice System
- **Evidence-based practices**: Body scan, breath awareness, loving-kindness meditation
- **Guided sessions**: Structured practice guidance
- **Scientific foundation**: Based on Mindfulness-Based Stress Reduction (MBSR) research

### 6. Autonomous Intervention System
- **Real-time monitoring**: 7x24 user state monitoring (based on user-provided data)
- **Intelligent intervention**: Data analysis-based intervention decisions
- **Multiple intervention types**: Micro-meditation, breathing reminders, rest suggestions
- **Effect tracking**: Intervention effect recording and assessment
- **Data source clarification**: Monitoring uses only user-provided inputs via command arguments or configuration. No automatic system sensor access.
- **Data storage**: All monitoring data is stored in memory during session and not persisted to disk. No file writing occurs.
- **Privacy assurance**: 100% local processing, no external data transmission, no disk persistence.

## Security Declaration

### Core Security Principles
1. **100% local operation**: Skill performs no network access, all processing done locally
2. **No dangerous functions**: No use of `subprocess`, `eval`, `exec`, `__import__` or other dangerous functions
3. **Path restrictions**: File access limited to skill directory only
4. **Input validation**: Strict validation of all input data
5. **Privacy protection**: No collection or upload of user data

### Security Implementation
- **No network calls**: No socket, requests, urllib, or http.client usage
- **No external dependencies**: Uses only Python standard library
- **Memory-only storage**: Session data stored in memory, not written to disk
- **Transparent code**: All source code available for review

## Scientific Basis

### Evidence-Based Techniques
1. **Cognitive Behavioral Therapy (CBT)**: For stress and sleep management
2. **Mindfulness-Based Stress Reduction (MBSR)**: For mindfulness practices
3. **Biofeedback technology**: For physiological regulation
4. **Progressive muscle relaxation**: For physical tension release
5. **Guided imagery**: For mental relaxation
6. **Breathing regulation techniques**: For autonomic nervous system balance

### Excluded Content
- ❌ No Buddhist-related content or terminology
- ❌ No religious therapy techniques
- ❌ No traditional culture-specific methods
- ❌ No non-scientifically validated techniques

## Commands

### Basic Commands
1. **Stress analysis**
   ```
   /stress-sleep analyze-stress
   ```
   Analyze current stress level and get recommendations

2. **Sleep analysis**
   ```
   /stress-sleep analyze-sleep
   ```
   Analyze sleep quality and get optimization suggestions

3. **Audio therapy**
   ```
   /stress-sleep audio-therapy [protocol]
   ```
   Start audio therapy session (alpha_wave, theta_wave, white_noise, pink_noise)

4. **Breathing exercise**
   ```
   /stress-sleep breathing-exercise [technique]
   ```
   Guide breathing exercise (box_breathing, 4-7-8_breathing, diaphragmatic_breathing)

5. **Mindfulness practice**
   ```
   /stress-sleep mindfulness-practice [practice]
   ```
   Guide mindfulness practice (body_scan, breath_awareness, loving_kindness)

### Advanced Commands
6. **Start autonomous mode**
   ```
   /stress-sleep start-autonomous
   ```
   Start 7x24 monitoring and intelligent intervention

7. **Stop autonomous mode**
   ```
   /stress-sleep stop-autonomous
   ```
   Stop autonomous monitoring

8. **Get status**
   ```
   /stress-sleep status
   ```
   Check skill status and version

## Installation

### OpenClaw Installation
```bash
# Install via ClawHub
npx clawhub install stress-sleep-ai
```

### Manual Installation
1. Download the skill package
2. Extract to OpenClaw skills directory
3. Restart OpenClaw

## Configuration

### Basic Configuration
Edit `config.yaml` to customize:
- Feature enable/disable
- Default protocols and techniques
- Performance settings

### Environment Variables
No environment variables required. The skill operates entirely locally.

## Performance

### Response Times
- Command response: < 100ms
- Stress analysis: < 500ms
- Sleep analysis: < 1000ms
- Audio generation: < 200ms

### Resource Usage
- Memory usage: < 50MB
- CPU usage: < 5%
- Disk usage: Minimal (configuration files only)

## Compatibility

### Supported Platforms
- **Operating Systems**: Windows, macOS, Linux
- **Python Versions**: 3.8+
- **OpenClaw Versions**: 2026.3+
- **Architectures**: x86_64, arm64

### Dependencies
- **Required**: None (uses Python standard library only)
- **Optional**: None

## Development

### Code Structure
```
skill.py              # Main skill implementation
config.yaml          # Configuration file
SKILL.md            # This documentation
README.md           # User guide
CHANGELOG.md        # Version history
requirements.txt    # Dependency list (empty)
```

### Testing
```bash
# Run basic tests
python -c "from skill import StressSleepAISkill; skill = StressSleepAISkill(); print(skill.handle_command('status'))"
```

## Troubleshooting

### Common Issues
1. **Command not recognized**: Ensure skill is properly installed
2. **No response**: Check OpenClaw logs for errors
3. **Performance issues**: Verify system meets minimum requirements

### Logs
Check OpenClaw logs for detailed error information:
- Installation logs
- Runtime logs
- Error logs

## Support

### Documentation
- Full documentation: This file (SKILL.md)
- User guide: README.md
- Configuration: config.yaml
- Changelog: CHANGELOG.md

### Issues
Report issues via:
- GitHub repository (if available)
- OpenClaw community support
- Direct contact with maintainer

## License

MIT License - See LICENSE file for details

## Version

Current version: 5.0.3

## Contact

- **Maintainer**: OpenClaw Assistant
- **Community**: OpenClaw Discord community
- **Updates**: Check ClawHub for latest version