# Release Notes - v1.0.3

## 🔧 ClawHub Metadata Fix

This release fixes the ClawHub security scan warning about missing credential declaration by adding proper frontmatter metadata to SKILL.md and README.md.

## What's Fixed

### ClawHub Metadata
- ✅ **Added SKILL.md frontmatter** with clawdbot metadata
- ✅ **Added README.md frontmatter** with clawdbot metadata
- ✅ **Declared GPROPHET_API_KEY** in metadata.clawdbot.requires.env
- ✅ **Resolved security scan warning** about missing credential declaration

## Why This Matters

ClawHub's security scanner looks for environment variable declarations in the SKILL.md and README.md frontmatter (metadata.clawdbot section), not in _meta.json. This release ensures the credential requirement is properly declared where ClawHub expects it.

## Breaking Changes

None. This is a metadata fix only.

## Migration Guide

If you're upgrading from v1.0.2:

1. **No action required** - The skill functionality remains unchanged
2. **Security warning should disappear** - ClawHub will now recognize the credential requirement
3. **Installation experience improves** - Users will see proper credential warnings

## Files Changed

- `SKILL.md`: Added frontmatter with clawdbot metadata
- `README.md`: Added frontmatter with clawdbot metadata
- `_meta.json`: Updated version to 1.0.3
- `CHANGELOG.md`: Updated with v1.0.3 changes
- `RELEASE_NOTES.md`: Updated with v1.0.3 info

## Verification

To verify the fix:

```bash
# Check SKILL.md frontmatter
head -15 SKILL.md | grep -A 10 "metadata:"

# Check README.md frontmatter
head -15 README.md | grep -A 10 "metadata:"

# Both should show:
# metadata:
#   clawdbot:
#     requires:
#       env: ["GPROPHET_API_KEY"]
```

## Next Steps

1. Review the updated documentation
2. Verify ClawHub security scan passes
3. Install and test the skill
4. Provide feedback on improvements

## Support

- Documentation: https://www.gprophet.com/docs
- ClawHub: https://clawhub.ai
- General Support: support@gprophet.com

---

**Release Date**: 2026-03-04  
**Version**: 1.0.3  
**Previous Version**: 1.0.2
