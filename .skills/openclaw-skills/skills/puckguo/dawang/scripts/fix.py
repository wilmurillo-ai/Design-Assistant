import re

with open('/Users/godspeed/.openclaw/skills/openclawchat-autonomous-chat/index.js', 'r') as f:
    lines = f.readlines()

# Find lines to modify
result = []
skip_next = False
for i, line in enumerate(lines):
    if skip_next:
        skip_next = False
        continue
    # After "Connecting to" log, we need to add Promise code
    if 'console.log(`[AutonomousChat] Connecting to ${wsUrl}`);' in line:
        result.append(line)
        # Check if next line is closing brace
        if i+1 < len(lines) and lines[i+1].strip() == '}':
            # Skip the closing brace - Promise code will follow
            skip_next = True
            continue
    result.append(line)

with open('/Users/godspeed/.openclaw/skills/openclawchat-autonomous-chat/index.js', 'w') as f:
    f.writelines(result)

print("Fixed closing brace")
