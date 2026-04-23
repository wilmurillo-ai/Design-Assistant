import re
import os

filepath = "/root/.openclaw/workspace/leio-sdlc/scripts/orchestrator.py"
with open(filepath, "r") as f:
    code = f.read()

# Add import
if "from git_utils import safe_git_checkout, GitCheckoutError" not in code:
    code = code.replace("import subprocess\n", "import subprocess\nfrom git_utils import safe_git_checkout, GitCheckoutError\n")

# Wrap set_pr_status with git commit
new_set_pr_status = """def set_pr_status(pr_file, new_status):
    with open(pr_file, 'r', encoding='utf-8') as f:
        content = f.read()
    updated = re.sub(r'^status:\s*\S+', f'status: {new_status}', content, count=1, flags=re.MULTILINE)
    with open(pr_file, 'w', encoding='utf-8') as f:
        f.write(updated)
    
    # Explicitly call git add . and git commit when modifying PR state trackers
    subprocess.run(["git", "add", pr_file], check=False)
    subprocess.run(["git", "commit", "-m", f"chore(state): update {os.path.basename(pr_file)} to {new_status}"], check=False)
"""

code = re.sub(r"def set_pr_status\(pr_file, new_status\):.*?(?=\ndef )", new_set_pr_status, code, flags=re.DOTALL)

# Wrap append_to_pr with git commit
new_append_to_pr = """def append_to_pr(pr_file, text):
    with open(pr_file, 'a', encoding='utf-8') as f:
        f.write(text + "\\n")
    
    # Explicitly call git add . and git commit
    subprocess.run(["git", "add", pr_file], check=False)
    subprocess.run(["git", "commit", "-m", f"chore(state): append to {os.path.basename(pr_file)}"], check=False)
"""

code = re.sub(r"def append_to_pr\(pr_file, text\):.*?(?=\ndef )", new_append_to_pr, code, flags=re.DOTALL)

# Replace git checkout commands
code = code.replace(
    'subprocess.run(["git", "checkout", branch_name], check=True)',
    'safe_git_checkout(branch_name)'
)

code = code.replace(
    'subprocess.run(["git", "checkout", "-b", branch_name], check=True)',
    'safe_git_checkout(branch_name, create=True)'
)

code = code.replace(
    'subprocess.run(["git", "checkout", "master"], check=True)',
    'safe_git_checkout("master")'
)

# And if there is any branch checkout error we need to handle it or let it fail gracefully.
# The orchestrator will now raise GitCheckoutError, which is an exception, preventing ungraceful rm -rf (actually it's uncaught so it crashes instead of deleting). Wait, the requirement says "catch the exception, log the error clearly, and raise a custom exception or return a defined failure state without executing any destructive commands."
# The orchestrator script has no `rm -rf` inside it right now, but raising `GitCheckoutError` satisfies "raise a custom exception" and stopping execution gracefully.

with open(filepath, "w") as f:
    f.write(code)

print("Patched orchestrator.py")
