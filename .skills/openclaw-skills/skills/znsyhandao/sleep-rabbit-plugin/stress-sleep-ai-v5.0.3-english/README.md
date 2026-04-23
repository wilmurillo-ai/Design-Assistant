# Stress Sleep AI Skill

A scientific stress and sleep analysis skill for OpenClaw, based on AISleepGen autonomous meditation AI agent architecture.

## Features

### 🧠 Stress Analysis
- Real-time stress level assessment
- Personalized recommendations
- Progress tracking

### 😴 Sleep Optimization  
- Sleep quality analysis
- Evidence-based suggestions
- Sleep hygiene guidance

### 🔊 Audio Therapy
- Alpha/theta wave stimulation
- White/pink noise generation
- Brainwave entrainment

### 🌬️ Breathing Exercises
- Box breathing technique
- 4-7-8 breathing pattern
- Diaphragmatic breathing

### 🧘 Mindfulness Practices
- Body scan meditation
- Breath awareness
- Loving-kindness practice

### 🤖 Autonomous Mode
- 7x24 intelligent monitoring
- Data-driven interventions
- In-memory processing only

## Quick Start

### Installation
```bash
# Install from ClawHub
npx clawhub install stress-sleep-ai
```

### Basic Usage
```bash
# Analyze stress
/stress-sleep analyze-stress

# Analyze sleep  
/stress-sleep analyze-sleep

# Start audio therapy
/stress-sleep audio-therapy alpha_wave

# Practice breathing
/stress-sleep breathing-exercise box_breathing

# Mindfulness practice
/stress-sleep mindfulness-practice body_scan
```

## Security & Privacy

### Core Principles
- ✅ **100% local operation** - No network access
- ✅ **No dangerous functions** - No eval, exec, subprocess
- ✅ **Memory-only storage** - No disk persistence
- ✅ **Transparent code** - Full source available

### Data Handling
- All processing done locally on your device
- Session data stored in memory only
- No data collection or transmission
- No file system access outside skill directory

## Scientific Basis

### Evidence-Based Techniques
- Cognitive Behavioral Therapy (CBT)
- Mindfulness-Based Stress Reduction (MBSR)
- Biofeedback technology
- Progressive muscle relaxation
- Guided imagery
- Breathing regulation

### Excluded Content
- ❌ No religious or spiritual content
- ❌ No traditional culture-specific methods  
- ❌ No non-scientifically validated techniques

## Performance

### System Requirements
- **Python**: 3.8+
- **OpenClaw**: 2026.3+
- **Memory**: < 50MB
- **Storage**: Minimal

### Response Times
- Command response: < 100ms
- Analysis completion: < 1000ms
- Audio generation: < 200ms

## Configuration

### Basic Settings
Edit `config.yaml` to customize:
- Enable/disable features
- Set default protocols
- Adjust performance parameters

### No External Dependencies
The skill uses only Python standard library modules:
- `os`, `sys`, `json`, `random`
- `datetime`, `typing`

## Advanced Usage

### Autonomous Monitoring
```bash
# Start 7x24 monitoring
/stress-sleep start-autonomous

# Check monitoring status
/stress-sleep status

# Stop monitoring
/stress-sleep stop-autonomous
```

### Custom Data Input
Provide your own data for analysis:
```bash
# Stress analysis with custom data
/stress-sleep analyze-stress heart_rate=85 sleep_hours=6.5 mood="stressed"

# Sleep analysis with custom data  
/stress-sleep analyze-sleep duration_hours=7.5 quality_rating=4 wakeups=2
```

## Troubleshooting

### Common Issues

**Command not working?**
- Verify installation: `npx clawhub list | grep stress-sleep`
- Check OpenClaw logs for errors
- Ensure correct command syntax

**No response from skill?**
- Check skill status: `/stress-sleep status`
- Verify OpenClaw is running
- Restart OpenClaw if needed

**Performance issues?**
- Check system resource usage
- Verify Python version compatibility
- Review configuration settings

### Getting Help
- Check full documentation in `SKILL.md`
- Review configuration in `config.yaml`
- Check version history in `CHANGELOG.md`
- Contact maintainer for support

## Development

### Code Structure
- `skill.py` - Main implementation
- `config.yaml` - Configuration
- `SKILL.md` - Full documentation
- `README.md` - User guide
- `CHANGELOG.md` - Version history
- `requirements.txt` - Dependencies (empty)

### Testing
```python
# Quick test
from skill import StressSleepAISkill
skill = StressSleepAISkill()
result = skill.handle_command('status')
print(result)
```

## License

MIT License - Free to use, modify, and distribute.

## Version

**Current**: 5.0.3  
**Status**: Production ready  
**Security**: Benign (OpenClaw security scan)

## Support

- **Documentation**: This file and `SKILL.md`
- **Community**: OpenClaw Discord
- **Updates**: Via ClawHub registry
- **Issues**: Report through appropriate channels

---

**Note**: This skill is designed for educational and self-improvement purposes only. It is not a substitute for professional medical advice, diagnosis, or treatment.