import re, os

with open("scripts/orchestrator.py", "r") as f:
    content = f.read()

def set_pr_status_replace():
    pass

# Manually replace set_pr_status
start = content.find("def set_pr_status(pr_file, new_status):")
end = content.find("def get_pr_slice_depth(pr_file):")
if start != -1 and end != -1:
    new_set_pr = """def set_pr_status(pr_file, new_status):
    with open(pr_file, 'r', encoding='utf-8') as f:
        file_content = f.read()
    updated = re.sub(r'^status:\\s*\\S+', f'status: {new_status}', file_content, count=1, flags=re.MULTILINE)
    with open(pr_file, 'w', encoding='utf-8') as f:
        f.write(updated)
    subprocess.run(["git", "add", pr_file], check=False)
    subprocess.run(["git", "commit", "-m", f"chore(orchestrator): update {os.path.basename(pr_file)} to {new_status}"], check=False)

"""
    content = content[:start] + new_set_pr + content[end:]

start2 = content.find("def append_to_pr(pr_file, text):")
end2 = content.find("def main():")
if start2 != -1 and end2 != -1:
    new_append = """def append_to_pr(pr_file, text):
    with open(pr_file, 'a', encoding='utf-8') as f:
        f.write(f"\\n{text}\\n")
    subprocess.run(["git", "add", pr_file], check=False)
    subprocess.run(["git", "commit", "-m", f"chore(orchestrator): append context to {os.path.basename(pr_file)}"], check=False)

"""
    content = content[:start2] + new_append + content[end2:]


checkout_branch_pattern = """            branch_check = subprocess.run(["git", "show-ref", "--verify", "--quiet", f"refs/heads/{branch_name}"])
            if branch_check.returncode == 0:
                subprocess.run(["git", "checkout", branch_name], check=True)
            else:
                subprocess.run(["git", "checkout", "-b", branch_name], check=True)"""
checkout_branch_replace = """            try:
                branch_check = subprocess.run(["git", "show-ref", "--verify", "--quiet", f"refs/heads/{branch_name}"])
                if branch_check.returncode == 0:
                    subprocess.run(["git", "checkout", branch_name], check=True)
                else:
                    subprocess.run(["git", "checkout", "-b", branch_name], check=True)
            except subprocess.CalledProcessError as e:
                print(f"Failed to checkout branch {branch_name}: {e}. Aborting gracefully.", file=sys.stderr)
                sys.exit(1)"""
content = content.replace(checkout_branch_pattern, checkout_branch_replace)

checkout_master_pattern1 = """                    print("State 6: Green Path - Merging code")
                    subprocess.run(["git", "checkout", "master"], check=True)"""
checkout_master_replace1 = """                    print("State 6: Green Path - Merging code")
                    try:
                        subprocess.run(["git", "checkout", "master"], check=True)
                    except subprocess.CalledProcessError as e:
                        print(f"Failed to checkout master: {e}. Aborting gracefully.", file=sys.stderr)
                        sys.exit(1)"""
content = content.replace(checkout_master_pattern1, checkout_master_replace1)

checkout_master_pattern2 = """                            print("Arbitrator overrode rejection. State 6: Green Path - Merging code")
                            subprocess.run(["git", "checkout", "master"], check=True)"""
checkout_master_replace2 = """                            print("Arbitrator overrode rejection. State 6: Green Path - Merging code")
                            try:
                                subprocess.run(["git", "checkout", "master"], check=True)
                            except subprocess.CalledProcessError as e:
                                print(f"Failed to checkout master: {e}. Aborting gracefully.", file=sys.stderr)
                                sys.exit(1)"""
content = content.replace(checkout_master_pattern2, checkout_master_replace2)

checkout_master_pattern3 = """                    print("Tier 1 (Reset): Deleting branch and retrying.")
                    subprocess.run(["git", "checkout", "master"], check=True)"""
checkout_master_replace3 = """                    print("Tier 1 (Reset): Deleting branch and retrying.")
                    try:
                        subprocess.run(["git", "checkout", "master"], check=True)
                    except subprocess.CalledProcessError as e:
                        print(f"Failed to checkout master: {e}. Aborting gracefully.", file=sys.stderr)
                        sys.exit(1)"""
content = content.replace(checkout_master_pattern3, checkout_master_replace3)

with open("scripts/orchestrator.py", "w") as f:
    f.write(content)
