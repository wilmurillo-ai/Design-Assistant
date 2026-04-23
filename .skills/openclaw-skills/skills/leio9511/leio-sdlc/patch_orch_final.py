import re
import sys

with open("scripts/orchestrator.py", "r") as f:
    content = f.read()

# Replace checkout of branch_name
pattern1 = """            branch_check = subprocess.run(["git", "show-ref", "--verify", "--quiet", f"refs/heads/{branch_name}"])
            if branch_check.returncode == 0:
                safe_git_checkout(branch_name)
            else:
                safe_git_checkout(branch_name, create=True)"""
replace1 = """            try:
                branch_check = subprocess.run(["git", "show-ref", "--verify", "--quiet", f"refs/heads/{branch_name}"])
                if branch_check.returncode == 0:
                    safe_git_checkout(branch_name)
                else:
                    safe_git_checkout(branch_name, create=True)
            except GitCheckoutError as e:
                print(f"Failed to checkout branch {branch_name}: {e}. Aborting gracefully.", file=sys.stderr)
                sys.exit(1)"""
content = content.replace(pattern1, replace1)

# Replace checkout of master 1
pattern2 = """                    print("State 6: Green Path - Merging code")
                    safe_git_checkout("master")"""
replace2 = """                    print("State 6: Green Path - Merging code")
                    try:
                        safe_git_checkout("master")
                    except GitCheckoutError as e:
                        print(f"Failed to checkout master: {e}. Aborting gracefully.", file=sys.stderr)
                        sys.exit(1)"""
content = content.replace(pattern2, replace2)

# Replace checkout of master 2
pattern3 = """                            print("Arbitrator overrode rejection. State 6: Green Path - Merging code")
                            safe_git_checkout("master")"""
replace3 = """                            print("Arbitrator overrode rejection. State 6: Green Path - Merging code")
                            try:
                                safe_git_checkout("master")
                            except GitCheckoutError as e:
                                print(f"Failed to checkout master: {e}. Aborting gracefully.", file=sys.stderr)
                                sys.exit(1)"""
content = content.replace(pattern3, replace3)

# Replace checkout of master 3
pattern4 = """                    print("Tier 1 (Reset): Deleting branch and retrying.")
                    safe_git_checkout("master")"""
replace4 = """                    print("Tier 1 (Reset): Deleting branch and retrying.")
                    try:
                        safe_git_checkout("master")
                    except GitCheckoutError as e:
                        print(f"Failed to checkout master: {e}. Aborting gracefully.", file=sys.stderr)
                        sys.exit(1)"""
content = content.replace(pattern4, replace4)


with open("scripts/orchestrator.py", "w") as f:
    f.write(content)
