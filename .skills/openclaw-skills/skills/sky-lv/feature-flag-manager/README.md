# feature-flag-manager

Feature flag management for AI agents — toggle features, A/B testing, gradual rollouts.

## Quick Start

```bash
# Create a flag
node flag.js create dark-mode --percentage 10

# Check if enabled
node flag.js enabled dark-mode

# Toggle
node flag.js toggle dark-mode

# List all
node flag.js list
```

## Use Cases

- **Gradual Rollout**: Start with 5% → increase to 100%
- **A/B Testing**: Test different UX variants
- **Kill Switch**: Instantly disable buggy features
- **Remote Config**: Change behavior without deploying
