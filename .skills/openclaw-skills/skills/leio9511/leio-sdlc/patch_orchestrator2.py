import re
import os

filepath = "/root/.openclaw/workspace/leio-sdlc/scripts/orchestrator.py"
with open(filepath, "r") as f:
    code = f.read()

# Add import
if "from git_utils import safe_git_checkout, GitCheckoutError" not in code:
    code = code.replace("import subprocess\n", "import subprocess\nfrom git_utils import safe_git_checkout, GitCheckoutError\n")

# Replace set_pr_status manually
old_set_pr_status = """def set_pr_status(pr_file, new_status):
    with open(pr_file, 'r', encoding='utf-8') as f:
        content = f.read()
    updated = re.sub(r'^status:\s*\S+', f'status: {new_status}', content, count=1, flags=re.MULTILINE)
    with open(pr_file, 'w', encoding='utf-8') as f:
        f.write(updated)"""

new_set_pr_status = """def set_pr_status(pr_file, new_status):
    with open(pr_file, 'r', encoding='utf-8') as f:
        content = f.read()
    updated = re.sub(r'^status:\\s*\\S+', f'status: {new_status}', content, count=1, flags=re.MULTILINE)
    with open(pr_file, 'w', encoding='utf-8') as f:
        f.write(updated)
    
    # Explicitly call git add . and git commit
    import os
    subprocess.run(["git", "add", "."], check=False)
    subprocess.run(["git", "commit", "-m", f"chore(state): update PR state to {new_status}"], check=False)"""

code = code.replace(old_set_pr_status, new_set_pr_status)

old_append_to_pr = """def append_to_pr(pr_file, text):
    with open(pr_file, 'a', encoding='utf-8') as f:
        f.write(text + "\\n")"""

new_append_to_pr = """def append_to_pr(pr_file, text):
    with open(pr_file, 'a', encoding='utf-8') as f:
        f.write(text + "\\n")
    
    # Explicitly call git add . and git commit
    subprocess.run(["git", "add", "."], check=False)
    subprocess.run(["git", "commit", "-m", "chore(state): append to PR"], check=False)"""

code = code.replace(old_append_to_pr, new_append_to_pr)

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

with open(filepath, "w") as f:
    f.write(code)

print("Patched orchestrator.py successfully.")
