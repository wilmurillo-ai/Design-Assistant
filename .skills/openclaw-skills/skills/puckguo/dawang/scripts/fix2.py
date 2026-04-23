import re

with open('/Users/godspeed/.openclaw/skills/openclawchat-autonomous-chat/index.js', 'r') as f:
    content = f.read()

# The issue: connect() method is missing its body (the Promise code)
# and Promise code is placed after buildWsUrl() 
# We need to move Promise code inside connect() and remove duplicate buildWsUrl

# Find the structure and fix it
# Pattern: after "Connecting to ${wsUrl}" should come Promise, not closing brace

lines = content.split('\n')
result = []
in_connect = False
connect_brace_count = 0
found_connecting_log = False

for i, line in enumerate(lines):
    # Detect connect method start
    if 'connect(room)' in line and '{' in line:
        in_connect = True
        connect_brace_count = 1
        result.append(line)
        continue
    
    if in_connect:
        connect_brace_count += line.count('{') - line.count('}')
        
        # Check if this is the line with console.log Connecting to
        if 'console.log(`[AutonomousChat] Connecting to ${wsUrl}`);' in line:
            found_connecting_log = True
            result.append(line)
            continue
        
        # If we found the log and now hit a closing brace, skip it
        # The Promise code should come after
        if found_connecting_log and line.strip() == '}' and connect_brace_count == 0:
            # Skip this closing brace
            in_connect = False
            found_connecting_log = False
            continue
    
    result.append(line)

# Now remove the duplicate buildWsUrl (second occurrence)
final_result = []
buildwsurl_seen = 0
skip_method = False
brace_depth = 0

for line in result:
    if skip_method:
        brace_depth += line.count('{') - line.count('}')
        if brace_depth <= 0 and line.strip() and not line.strip().startswith('//'):
            skip_method = False
            # Keep this line if it's a new method
            if re.match(r'^\s+\w+\(', line) or re.match(r'^\s+async\s+\w+\(', line):
                final_result.append(line)
        continue
    
    if 'buildWsUrl(room)' in line and '{' in line:
        buildwsurl_seen += 1
        if buildwsurl_seen == 2:
            skip_method = True
            brace_depth = 1
            continue
    
    final_result.append(line)

with open('/Users/godspeed/.openclaw/skills/openclawchat-autonomous-chat/index.js', 'w') as f:
    f.write('\n'.join(final_result))

print("Fixed!")
