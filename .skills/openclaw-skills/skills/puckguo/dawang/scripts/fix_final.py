with open('/Users/godspeed/.openclaw/skills/openclawchat-autonomous-chat/index.js', 'r') as f:
    lines = f.readlines()

# Find key line numbers
connecting_line = None
buildwsurl_line = None
promise_start = None
promise_end = None

for i, line in enumerate(lines):
    if 'console.log(`[AutonomousChat] Connecting to ${wsUrl}`);' in line:
        connecting_line = i
    if 'buildWsUrl(room)' in line and '{' in line and buildwsurl_line is None:
        buildwsurl_line = i
    if 'return new Promise((resolve, reject)' in line and promise_start is None:
        promise_start = i

# Find promise end - look for the closing of Promise and the method
brace_count = 0
for i in range(promise_start, len(lines)):
    brace_count += lines[i].count('{') - lines[i].count('}')
    if brace_count == 0 and '});' in lines[i]:
        promise_end = i
        break

print(f"connecting_line: {connecting_line}")
print(f"buildwsurl_line: {buildwsurl_line}")
print(f"promise_start: {promise_start}")
print(f"promise_end: {promise_end}")

# Reconstruct: keep lines up to connecting_line, then Promise, then buildWsUrl, then rest
result = []

# Part 1: up to and including connecting_line
result.extend(lines[:connecting_line+1])

# Add the Promise code (it already has proper indentation)
result.extend(lines[promise_start:promise_end+1])

# Close the connect method
result.append('  }\n')

# Add buildWsUrl (find where it ends)
buildwsurl_end = None
brace_count = 0
for i in range(buildwsurl_line, promise_start):
    brace_count += lines[i].count('{') - lines[i].count('}')
    if brace_count == 0 and lines[i].strip() == '}':
        buildwsurl_end = i
        break

result.extend(lines[buildwsurl_line:buildwsurl_end+1])

# Part 3: everything after promise_end, skipping the old buildWsUrl
# Skip until we find handleMessage or another method
for i in range(promise_end+1, len(lines)):
    if lines[i].strip() and not lines[i].strip().startswith('//'):
        # Check if this is the start of a new method
        if 'handleMessage' in lines[i] or 'async' in lines[i] or 'shouldReply' in lines[i]:
            result.extend(lines[i:])
            break

with open('/Users/godspeed/.openclaw/skills/openclawchat-autonomous-chat/index.js', 'w') as f:
    f.writelines(result)

print("Done!")
