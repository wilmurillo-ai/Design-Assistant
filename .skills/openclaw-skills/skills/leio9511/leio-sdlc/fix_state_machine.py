with open("scripts/orchestrator.py", "r") as f:
    code = f.read()

# 1. Add pr_done = False before State 2 while True
code = code.replace("        reset_count = 0\n\n        while True:\n            print(f\"State 2:", 
                    "        reset_count = 0\n        pr_done = False\n\n        while True:\n            if pr_done:\n                break\n            print(f\"State 2:")

# 2. On merge success (Green Path), set pr_done = True instead of break or sys.exit
code = code.replace("""                        set_pr_status(current_pr, "closed")
                        print(f"Successfully closed {current_pr}")
                        break""",
                    """                        set_pr_status(current_pr, "closed")
                        print(f"Successfully closed {current_pr}")
                        pr_done = True
                        break""")
code = code.replace("""                        set_pr_status(current_pr, "closed")
                                print(f"Successfully closed {current_pr}")
                                sys.exit(0)""",
                    """                        set_pr_status(current_pr, "closed")
                                print(f"Successfully closed {current_pr}")
                                pr_done = True
                                break""")

# 3. On Planner Micro-Slicing success, set pr_done = True
code = code.replace("""                            print(f"Planner successfully generated {len(new_files)} new PRs. Marking original as superseded.")
                            set_pr_status(current_pr, "superseded")
                            break""",
                    """                            print(f"Planner successfully generated {len(new_files)} new PRs. Marking original as superseded.")
                            set_pr_status(current_pr, "superseded")
                            pr_done = True
                            break""")

with open("scripts/orchestrator.py", "w") as f:
    f.write(code)
