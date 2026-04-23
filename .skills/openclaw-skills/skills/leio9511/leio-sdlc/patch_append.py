with open("scripts/orchestrator.py", "r") as f:
    content = f.read()

pattern = """def append_to_pr(pr_file, text):
    with open(pr_file, 'a', encoding='utf-8') as f:
        f.write(f"\\n{text}\\n")"""

replace = """def append_to_pr(pr_file, text):
    with open(pr_file, 'a', encoding='utf-8') as f:
        f.write(f"\\n{text}\\n")
    import subprocess
    subprocess.run(["git", "add", "."], check=False)
    subprocess.run(["git", "commit", "-m", "chore(state): append context to PR state"], check=False)"""

content = content.replace(pattern, replace)

with open("scripts/orchestrator.py", "w") as f:
    f.write(content)
