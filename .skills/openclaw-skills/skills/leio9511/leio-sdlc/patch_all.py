import re

with open("scripts/orchestrator.py", "r") as f:
    lines = f.readlines()

new_lines = []
in_loop = False

for line in lines:
    if line.startswith("    md_files = glob.glob(os.path.join(job_dir, \"*.md\"))"):
        new_lines.append("    while True:\n")
        in_loop = True

    if line.startswith("if __name__ == \"__main__\":"):
        in_loop = False
        
    if in_loop:
        if line.strip() == "":
            new_lines.append(line)
        else:
            new_lines.append("    " + line)
    else:
        new_lines.append(line)

code = "".join(new_lines)

old_tier2 = """                        print(f"Slice depth is {slice_depth} (< 2). Micro-slicing PR.")
                        set_pr_status(current_pr, "superseded")
                        subprocess.run([
                            sys.executable, "scripts/spawn_planner.py",
                            "--slice-failed-pr", current_pr,
                            "--repo-dir", workdir
                        ])
                        sys.exit(0)
                    else:
                        print(f"Tier 3 (Dead Letter Queue): Slice depth is {slice_depth} (>= 2).")"""

new_tier2 = """                        print(f"Slice depth is {slice_depth} (< 2). Micro-slicing PR.")
                        pr_files_before = set(glob.glob(os.path.join(job_dir, "PR_*.md")))
                        subprocess.run([
                            sys.executable, "scripts/spawn_planner.py",
                            "--slice-failed-pr", current_pr,
                            "--repo-dir", workdir
                        ])
                        pr_files_after = set(glob.glob(os.path.join(job_dir, "PR_*.md")))
                        new_files = pr_files_after - pr_files_before
                        if len(new_files) >= 2:
                            print(f"Planner successfully generated {len(new_files)} new PRs. Marking original as superseded.")
                            set_pr_status(current_pr, "superseded")
                            pr_done = True
                            break
                        else:
                            print(f"Planner failed to generate >= 2 new PRs (generated {len(new_files)}). Escalating to Tier 3.")
                            print(f"Tier 3 (Dead Letter Queue): Slice failed on {current_pr}.")
                            set_pr_status(current_pr, "blocked_fatal")
                            print(f"PR {current_pr} is fatally blocked.")
                            while True:
                                choice = input("Process suspended. [A]bort or [C]ontinue? ").strip().upper()
                                if choice == 'A':
                                    sys.exit(1)
                                elif choice == 'C':
                                    print("Continuing...")
                                    sys.exit(1)
                                else:
                                    print("Invalid choice.")
                    else:
                        print(f"Tier 3 (Dead Letter Queue): Slice depth is {slice_depth} (>= 2).")"""

code = code.replace(old_tier2, new_tier2)

# 1. Add pr_done = False before State 2 while True
code = code.replace("        reset_count = 0\n\n        while True:\n            print(f\"State 2:", 
                    "        reset_count = 0\n        pr_done = False\n\n        while True:\n            if pr_done:\n                break\n            print(f\"State 2:")

# 2. On merge success (Green Path), set pr_done = True
code = code.replace("""                        set_pr_status(current_pr, "closed")
                        print(f"Successfully closed {current_pr}")
                        sys.exit(0)""",
                    """                        set_pr_status(current_pr, "closed")
                        print(f"Successfully closed {current_pr}")
                        pr_done = True
                        break""")
code = code.replace("""                                set_pr_status(current_pr, "closed")
                                print(f"Successfully closed {current_pr}")
                                sys.exit(0)""",
                    """                                set_pr_status(current_pr, "closed")
                                print(f"Successfully closed {current_pr}")
                                pr_done = True
                                break""")

with open("scripts/orchestrator.py", "w") as f:
    f.write(code)
print("All patches applied.")
