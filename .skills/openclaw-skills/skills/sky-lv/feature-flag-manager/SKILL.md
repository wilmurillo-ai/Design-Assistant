---
description: Feature flag management for AI agents — toggle features, A/B testing, gradual rollouts
keywords: openclaw, skill, automation, ai-agent, feature-toggle, ab-testing, gradual-rollout
name: feature-flag-manager
triggers: feature flag, feature toggle, A/B testing, gradual rollout, release management
---

# feature-flag-manager

> Manage feature flags for AI agents — enable/disable features, A/B testing, gradual rollouts, and percentage-based releases.

## Skill Metadata

- **Slug**: feature-flag-manager
- **Version**: 1.0.0
- **Description**: Feature flag management system for AI agents. Toggle features on/off, run A/B tests, gradual percentage rollouts, and control feature visibility without deploying new code.
- **Category**: automation
- **Trigger Keywords**: `feature flag`, `feature toggle`, `A/B testing`, `gradual rollout`, `release management`, `canary release`, `percentage rollout`

---

## Capabilities

### 1. Create Feature Flag
```bash
# Create a simple on/off flag
node flag.js create my-feature --description "New dashboard"

# Create percentage rollout (initially 10%)
node flag.js create dark-mode --percentage 10 --description "Dark theme"

# Create A/B test variant
node flag.js create pricing-page --variants control,v1,v2 --weights 50,25,25
```
- Stores flags in `.featureflags/` JSON config
- Supports percentage-based rollout (0-100%)
- Multi-variant A/B testing with custom weight distribution

### 2. Check Flag Status
```bash
# Check if feature is enabled
node flag.js enabled my-feature

# Get variant for current user (for A/B)
node flag.js variant pricing-page --user-id user123

# Get rollout percentage
node flag.js percentage dark-mode
```
- Returns boolean for simple flags
- Returns variant name for A/B tests
- Returns rollout percentage

### 3. Update Flag
```bash
# Enable/disable immediately
node flag.js toggle my-feature

# Update rollout percentage (gradual increase)
node flag.js update dark-mode --percentage 50

# Pause a flag
node flag.js pause pricing-page
```
- Instant toggle for emergency rollback
- Percentage updates for gradual rollout
- Pause preserves configuration

### 4. List & Monitor
```bash
# List all flags with status
node flag.js list

# Show flag history
node flag.js history my-feature

# Export flags for reporting
node flag.js export --format json
```
- Real-time overview of all flags
- Change history with timestamps
- Export for analytics integration

---

## Configuration

```json
// .featureflags/config.json
{
  "flags": {
    "new-dashboard": {
      "enabled": true,
      "percentage": 100,
      "variants": null,
      "description": "Redesigned dashboard UI"
    },
    "dark-mode": {
      "enabled": true,
      "percentage": 25,
      "variants": null,
      "description": "Dark theme support"
    },
    "pricing-page": {
      "enabled": true,
      "percentage": 100,
      "variants": ["control", "v1", "v2"],
      "weights": [50, 25, 25]
    }
  }
}
```

## Use Cases

1. **Gradual Rollout**: Start with 5% users, increase to 100% over time
2. **A/B Testing**: Test different UX variants and measure conversion
3. **Kill Switch**: Instantly disable buggy feature without deployment
4. **User Segmentation**: Target specific user groups
5. **Remote Configuration**: Change behavior without code changes

## Integration Example

```javascript
// In your agent code
const flag = require('./flag.js');

async function handleRequest(req) {
  // Check if new feature is enabled
  if (await flag.enabled('new-dashboard', { userId: req.userId })) {
    return renderNewDashboard(req);
  }
  return renderLegacyDashboard(req);
}
```
