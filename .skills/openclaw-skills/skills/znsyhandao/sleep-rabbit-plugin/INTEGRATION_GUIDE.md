# Sleep Rabbit OpenClaw Integration Guide

## Integration Methods

### Method 1: Copy to OpenClaw Skills Directory (Recommended)

#### Step 1: Find OpenClaw Skills Directory
```bash
# Typical location on Windows
C:\Users\<YourUsername>\.openclaw\skills\

# Typical location on Linux/macOS
~/.openclaw/skills/
```

#### Step 2: Copy Skill Directory
```bash
# Copy the entire AISleepGen directory
cp -r AISleepGen/ ~/.openclaw/skills/
```

#### Step 3: Verify Installation
```bash
# List installed skills
openclaw skill list

# Should show: Sleep Rabbit Sleep Health (v1.0.6)
```

### Method 2: Use OpenClaw Skill Install Command

#### Step 1: Extract Skill Package
```bash
# Extract the ZIP package
unzip AISleepGen-v1.0.6.zip
```

#### Step 2: Install from Directory
```bash
# Navigate to extracted directory
cd AISleepGen

# Install the skill
openclaw skill install .
```

#### Step 3: Test Installation
```bash
# Test basic functionality
/file-info README.md

# Should return file information
```

## Configuration

### Skill Configuration (config.yaml)
The skill includes a complete configuration file with:

#### Security Settings
```yaml
security:
  network_access: false      # No network access
  local_only: true          # 100% local operation
  no_shell_commands: true   # No shell command execution
  python_stdlib_only: true  # Standard library only
```

#### Performance Settings
```yaml
performance:
  cache_enabled: true       # Enable caching
  max_cache_size_mb: 100    # Cache size limit
  request_timeout_seconds: 300  # Request timeout
```

#### Compatibility Settings
```yaml
compatibility:
  openclaw_min_version: "2026.3.0"
  python_min_version: "3.8"
  supported_platforms: ["windows", "linux", "macos"]
```

### Environment Configuration

#### Python Environment
```bash
# Verify Python version
python --version
# Should be 3.8 or higher

# Install optional dependencies for advanced features
pip install mne numpy scipy
```

#### OpenClaw Configuration
```bash
# Check OpenClaw version
openclaw --version
# Should be 2026.3.0 or higher

# Verify skill is loaded
openclaw skill status Sleep Rabbit
```

## Usage Examples

### Basic Testing
```bash
# Test file information command
/file-info examples/sample_config.json

# Test environment check
/env-check

# Test meditation guidance
/meditation-guide --duration 5 --type relaxation
```

### Advanced Usage (with MNE)
```bash
# Test EDF file analysis (requires MNE)
/sleep-analyze examples/sample.edf

# Test comprehensive analysis
/sleep-report examples/sample.edf --hr-data 70,72,75,68,80
```

### Integration Testing
```bash
# Test skill response time
time /file-info README.md

# Test error handling
/file-info non_existent_file.edf

# Test input validation
/stress-check invalid_data
```

## Troubleshooting

### Common Issues

#### Issue 1: Skill Not Found
```bash
# Solution: Reinstall skill
openclaw skill remove "Sleep Rabbit"
openclaw skill install ./AISleepGen
```

#### Issue 2: Missing Dependencies
```bash
# Solution: Check environment
/env-check

# Install missing dependencies
pip install mne numpy scipy
```

#### Issue 3: Permission Errors
```bash
# Solution: Check file permissions
/file-info <problem-file>

# Fix permissions if needed
chmod +r <problem-file>
```

### Debug Mode
```bash
# Enable debug logging
export OPENCLAW_LOG_LEVEL=debug

# Run skill with debug output
/file-info README.md
```

## Performance Optimization

### Cache Configuration
```yaml
# In config.yaml
performance:
  cache_enabled: true
  cache_dir: "./cache"
  max_cache_size_mb: 100
  cache_ttl_hours: 24
```

### Memory Management
- Default max file size: 100MB
- Cache size limit: 100MB
- Concurrent requests: 5 maximum

### Resource Limits
```yaml
validation:
  edf_files:
    max_file_size_mb: 100
    max_duration_seconds: 3600
    
  hr_data:
    max_samples: 1000
    max_value: 200
```

## Security Considerations

### Path Security
- All file access restricted to skill directory
- Input validation for all file paths
- No arbitrary file system access

### Privacy Protection
- 100% local processing
- No data transmission
- No external API calls

### Compliance
- Meets ClawHub security standards
- Complete security declarations
- No prohibited code patterns

## Monitoring and Maintenance

### Health Checks
```bash
# Run skill health check
/health-check

# Check environment status
/env-status
```

### Logging
```yaml
logging:
  level: "INFO"  # DEBUG, INFO, WARNING, ERROR
  file: "./logs/sleep_rabbit.log"
  max_size_mb: 10
  backup_count: 5
```

### Updates
- Check CHANGELOG.md for version updates
- Backup configuration before updates
- Test after updates with basic commands

## Support

### Documentation
- README.md - Overview and quick start
- SKILL.md - Detailed skill documentation
- examples/ - Usage examples
- CHANGELOG.md - Version history

### Testing
- Run all example commands
- Test error conditions
- Verify security compliance

### Issues
- Check environment with /env-check
- Review logs in ./logs/
- Verify file permissions and paths

---

**Integration Complete When:**
1. Skill appears in `openclaw skill list`
2. Basic commands work (`/file-info`, `/env-check`)
3. No permission or dependency errors
4. Security compliance verified

**Last Updated**: 2026-03-29  
**Version**: 1.0.6