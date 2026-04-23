# Sleep Rabbit Plugin Usage Guide

## Quick Start

### Basic Commands
```bash
# Check file information
/file-info <file-path>

# Stress assessment from heart rate
/stress-check <heart-rate-values>

# Meditation guidance
/meditation-guide

# Environment diagnostics
/env-check
```

### Advanced Commands (with MNE)
```bash
# EDF sleep analysis
/sleep-analyze <edf-file>

# Comprehensive health report
/sleep-report <edf-file> --hr-data <heart-rate-values>
```

## Command Reference

### 1. File Information (`/file-info`)
Analyzes file properties and validates format.

**Usage:**
```bash
/file-info <file-path>
```

**Examples:**
```bash
# Check EDF file
/file-info data/sleep_recording.edf

# Check configuration file
/file-info config.yaml

# Check data file
/file-info data/heart_rate.csv
```

**Output:**
- File existence and type
- Size and encoding
- Readability and format
- Validation results

### 2. Stress Check (`/stress-check`)
Performs stress assessment from heart rate data.

**Usage:**
```bash
# Direct input
/stress-check 70,72,75,68,80,78,76,74,72,70

# From file
/stress-check data/heart_rate.txt
```

**Input Formats:**
- Comma-separated values: `70,72,75,68,80`
- Space-separated values: `70 72 75 68 80`
- File with one value per line
- JSON array: `[70, 72, 75, 68, 80]`

**Output:**
- Average heart rate
- Heart rate variability (HRV)
- Stress score (0-100)
- Recommendations

### 3. Meditation Guide (`/meditation-guide`)
Provides personalized meditation techniques.

**Usage:**
```bash
# Basic meditation
/meditation-guide

# Specific type and duration
/meditation-guide --type relaxation --duration 10

# Sleep-focused meditation
/meditation-guide --type sleep --duration 15
```

**Options:**
- `--type`: relaxation, focus, sleep, stress-relief
- `--duration`: minutes (default: 10)
- `--level`: beginner, intermediate, advanced

**Output:**
- Step-by-step instructions
- Breathing techniques
- Duration guidance
- Tips and recommendations

### 4. Environment Check (`/env-check`)
Diagnoses environment and dependencies.

**Usage:**
```bash
/env-check
```

**Checks:**
- Python version and environment
- Library availability (MNE, NumPy, SciPy)
- File permissions and access
- System resources

**Output:**
- Environment status
- Missing dependencies
- Recommendations
- Capability level

### 5. Sleep Analyze (`/sleep-analyze`)
Analyzes EDF sleep data files (requires MNE).

**Usage:**
```bash
/sleep-analyze <edf-file>
```

**Requirements:**
- MNE-Python installed: `pip install mne numpy scipy`
- Valid EDF file with EEG/EOG/EMG channels
- File size < 100MB

**Output:**
- Sleep stage analysis
- Sleep quality score
- Recommendations
- Visualization data

### 6. Sleep Report (`/sleep-report`)
Generates comprehensive health reports.

**Usage:**
```bash
# Basic report
/sleep-report <edf-file>

# With heart rate data
/sleep-report <edf-file> --hr-data <heart-rate-values>

# Custom output format
/sleep-report <edf-file> --format json
```

**Options:**
- `--hr-data`: Heart rate values for stress assessment
- `--format`: Output format (markdown, json, text)
- `--detailed`: Include detailed analysis

**Output:**
- Sleep analysis results
- Stress assessment
- Health recommendations
- Actionable insights

## Examples

### Example 1: Basic Health Check
```bash
# Check environment
/env-check

# Verify a data file
/file-info data/sample.edf

# Quick stress check
/stress-check 72,74,76,78,80,82,80,78,76,74

# Get meditation guidance
/meditation-guide --duration 5
```

### Example 2: Professional Sleep Analysis
```bash
# First, check environment and dependencies
/env-check

# Install MNE if needed
# pip install mne numpy scipy

# Analyze sleep data
/sleep-analyze data/night_sleep.edf

# Generate comprehensive report
/sleep-report data/night_sleep.edf --hr-data 65,67,69,71,73,75,73,71,69,67
```

### Example 3: Batch Processing
```bash
# Check multiple files
for file in data/*.edf; do
    /file-info "$file"
done

# Process heart rate data from file
/stress-check data/heart_rate_log.txt

# Generate JSON report
/sleep-report data/sleep_study.edf --format json > report.json
```

## Input Validation

### File Requirements
- **EDF files**: Must contain EEG, EOG, EMG channels
- **Size limit**: Maximum 100MB per file
- **Encoding**: UTF-8 preferred, auto-detected
- **Permissions**: Read access required

### Data Requirements
- **Heart rate**: 40-200 BPM, minimum 10 samples
- **Sleep data**: 30-3600 seconds duration
- **Meditation**: 1-60 minutes duration

### Error Handling
- Invalid files: Clear error messages
- Missing data: Suggestions for correction
- Permission issues: Guidance for resolution

## Output Formats

### Markdown (Default)
```markdown
# Sleep Analysis Report

## Summary
- Sleep Quality: 85/100
- Stress Level: 42/100
- Recommendations: 5 items

## Details
...
```

### JSON
```json
{
  "sleep_quality": 85,
  "stress_level": 42,
  "recommendations": [...],
  "analysis_details": {...}
}
```

### Text
```
Sleep Analysis Report
=====================

Summary:
- Sleep Quality: 85/100
- Stress Level: 42/100

Details:
...
```

## Performance Tips

### Caching
- Results are cached for 24 hours
- Cache size limited to 100MB
- Clear cache if needed: Delete `./cache/` directory

### Resource Management
- Large files processed in chunks
- Memory usage optimized
- Concurrent requests limited to 5

### Optimization
- Use appropriate file formats
- Pre-process large datasets
- Schedule intensive analyses

## Troubleshooting

### Common Errors

#### "File not found"
- Verify file path and permissions
- Use `/file-info` to check file
- Ensure file is in allowed directory

#### "MNE not installed"
- Run `/env-check` to verify
- Install: `pip install mne numpy scipy`
- Check Python environment

#### "Invalid data format"
- Check input format requirements
- Use `/file-info` to validate files
- Convert data to supported format

### Debug Mode
```bash
# Enable detailed logging
export OPENCLAW_LOG_LEVEL=debug

# Run command with debug output
/file-info data/sample.edf
```

### Support
- Check `README.md` for overview
- Review `SKILL.md` for details
- See `examples/` for usage examples
- Run `/env-check` for diagnostics

---

**Quick Reference:**
- Basic: `/file-info`, `/stress-check`, `/meditation-guide`, `/env-check`
- Advanced: `/sleep-analyze`, `/sleep-report` (requires MNE)
- Help: Check documentation, run `/env-check` for diagnostics

**Last Updated**: 2026-03-29  
**Version**: 1.0.6