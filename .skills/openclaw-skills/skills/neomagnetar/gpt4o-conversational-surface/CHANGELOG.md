# Changelog

## 1.1.1
- Fixed `SKILL.md` frontmatter for current OpenClaw parser compatibility
- Converted `metadata` to single-line JSON
- Added `user-invocable: true`
- Added `disable-model-invocation: true` to keep the skill explicit instead of ambient
- Aligned the internal skill name with `/gpt4o` slash activation
- Kept published slug as `gpt4o-conversational-surface`

## 1.1.0
- Renamed and finalized package as `gpt4o-conversational-surface`
- Added explicit `/gpt4o` activation behavior
- Added explicit stop / revert behavior for returning to normal tone
- Tightened anti-override boundaries for technical and domain-specific outputs
- Added uncertainty behavior guidance for quick acknowledgment and soft confidence modulation
- Clarified this is a GPT4o-like conversational surface layer, not model replacement

## 1.0.0
- Initial release
- Added GPT4o-inspired conversational surface profile
- Defined tone, mirroring, readability, and continuity rules
- Tuned for adaptive, polished, readability-first output
- Packaged for ClawHub / OpenClaw skill publishing
