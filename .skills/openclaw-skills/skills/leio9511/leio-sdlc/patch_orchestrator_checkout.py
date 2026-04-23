import re

with open('/root/.openclaw/workspace/leio-sdlc/scripts/orchestrator.py', 'r') as f:
    content = f.read()

# Add safe_git_checkout function at the top
safe_checkout_code = """
class GitCheckoutError(Exception):
    pass

def safe_git_checkout(branch_name, create=False):
    \"\"\"Safely checkout a branch, creating it if requested.\"\"\"
    cmd = ["git", "checkout"]
    if create:
        cmd.append("-b")
    cmd.append(branch_name)
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        error_msg = f"Failed to {'create and ' if create else ''}checkout branch {branch_name}. Aborting gracefully."
        print(f"Error: {error_msg}", file=sys.stderr)
        raise GitCheckoutError(error_msg)
"""

content = content.replace("def set_pr_status(pr_file, new_status):", safe_checkout_code + "\ndef set_pr_status(pr_file, new_status):")

# Replace checkout usages:

# 1. 
orig1 = '''            if branch_check.returncode == 0:
                try:
                    subprocess.run(["git", "checkout", branch_name], check=True)
                except subprocess.CalledProcessError as e:
                    print(f"Error: Failed to checkout branch {branch_name}. Aborting gracefully.", file=sys.stderr)
                    sys.exit(1)
            else:
                try:
                    subprocess.run(["git", "checkout", "-b", branch_name], check=True)
                except subprocess.CalledProcessError as e:
                    print(f"Error: Failed to create and checkout branch {branch_name}. Aborting gracefully.", file=sys.stderr)
                    sys.exit(1)'''

new1 = '''            try:
                if branch_check.returncode == 0:
                    safe_git_checkout(branch_name, create=False)
                else:
                    safe_git_checkout(branch_name, create=True)
            except GitCheckoutError:
                sys.exit(1)'''

content = content.replace(orig1, new1)

# 2.
orig2 = '''                    try:
                        subprocess.run(["git", "checkout", "master"], check=True)
                    except subprocess.CalledProcessError as e:
                        print(f"Error: Failed to checkout master. Aborting gracefully.", file=sys.stderr)
                        sys.exit(1)'''

new2 = '''                    try:
                        safe_git_checkout("master")
                    except GitCheckoutError:
                        sys.exit(1)'''

content = content.replace(orig2, new2)

with open('/root/.openclaw/workspace/leio-sdlc/scripts/orchestrator.py', 'w') as f:
    f.write(content)
