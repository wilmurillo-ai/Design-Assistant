#!/usr/bin/env python3
import os
import sys
import glob
import subprocess
from git_utils import safe_git_checkout, GitCheckoutError
import re
import argparse

MAX_RUNTIME = 1200 # 20 minutes

def set_pr_status(pr_file, new_status):
    with open(pr_file, 'r', encoding='utf-8') as f:
        content = f.read()
    updated = re.sub(r'^status:\s*\S+', f'status: {new_status}', content, count=1, flags=re.MULTILINE)
    with open(pr_file, 'w', encoding='utf-8') as f:
        f.write(updated)
    
    # Explicitly call git add . and git commit
    import os
    subprocess.run(["git", "add", "."], check=False)
    subprocess.run(["git", "commit", "-m", f"chore(state): update PR state to {new_status}"], check=False)

def get_pr_slice_depth(pr_file):
    with open(pr_file, 'r', encoding='utf-8') as f:
        content = f.read()
    match = re.search(r'slice_depth:\s*(\d+)', content)
    if match:
        return int(match.group(1))
    return 0

def append_to_pr(pr_file, text):
    with open(pr_file, 'a', encoding='utf-8') as f:
        f.write(f"\n{text}\n")
    import subprocess
    subprocess.run(["git", "add", "."], check=False)
    subprocess.run(["git", "commit", "-m", "chore(state): append context to PR state"], check=False)


def force_commit_untracked_changes(repo_path="."):
    import subprocess
    subprocess.run(["git", "add", "."], cwd=repo_path, check=False)
    subprocess.run(["git", "commit", "-m", "chore(auto): force commit uncommitted changes before review"], cwd=repo_path, check=False)

def teardown_coder_session(workdir):
    session_file = os.path.join(workdir, ".coder_session")
    if os.path.exists(session_file):
        with open(session_file, "r") as f:
            session_key = f.read().strip()
        if session_key:
            print(f"Tearing down coder session {session_key}")
            test_mode = os.environ.get("SDLC_TEST_MODE") == "true"
            if test_mode:
                log_entry = str({"tool": "teardown_coder", "args": {"sessionKey": session_key}})
                with open("tests/tool_calls.log", "a") as f:
                    f.write(log_entry + "\n")
            else:
                subprocess.run(["openclaw", "subagents", "kill", "target=" + session_key], check=False)
        try:
            os.remove(session_file)
        except OSError:
            pass

def main():
    # Enforce absolute base path to prevent workspace code hijacking (ISSUE-065)
    RUNTIME_DIR = os.path.dirname(os.path.abspath(__file__))
    parser = argparse.ArgumentParser()
    parser.add_argument("--workdir", default=".")
    parser.add_argument("--prd-file", required=True)
    parser.add_argument("--job-dir", default=None)
    parser.add_argument("--max-runs", type=int, default=0, help="Max loops")
    parser.add_argument("--force-replan", action="store_true")
    args = parser.parse_args()

    workdir = os.path.abspath(args.workdir)
    
    prd_filename = os.path.basename(args.prd_file)
    base_name, _ = os.path.splitext(prd_filename)
    # Dynamically compute job directory from PRD (PR_002)
    args.job_dir = os.path.join("docs", "PRs", base_name)
    
    args.job_dir = os.path.join(workdir, args.job_dir)
    job_dir = os.path.abspath(args.job_dir)
    
    os.chdir(workdir)

    import shutil
    has_md = False
    if os.path.exists(job_dir):
        md_files = glob.glob(os.path.join(job_dir, "*.md"))
        has_md = len(md_files) > 0

    if has_md and not args.force_replan:
        print("State 0: Existing PRs detected. Resuming queue...")
    else:
        if args.force_replan and os.path.exists(job_dir):
            shutil.rmtree(job_dir)
        
        print("State 0: Auto-slicing PRD...")
        try:
            subprocess.run([sys.executable, os.path.join(RUNTIME_DIR, "spawn_planner.py"), "--prd-file", args.prd_file, "--workdir", workdir], check=True)
        except subprocess.CalledProcessError:
            pass

        if not os.path.exists(job_dir):
            print("[FATAL] Planner failed to generate any PRs.")
            sys.exit(1)
        
        md_files = glob.glob(os.path.join(job_dir, "*.md"))
        if len(md_files) == 0:
            print("[FATAL] Planner failed to generate any PRs.")
            sys.exit(1)

    loops = 0
    while True:
        if args.max_runs > 0 and loops >= args.max_runs:
            print(f"Max runs ({args.max_runs}) reached. Exiting orchestrator.")
            break
        loops += 1
        md_files = glob.glob(os.path.join(job_dir, "*.md"))
        md_files.sort()
    
        current_pr = None
        for md_file in md_files:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
                if re.search(r'^status:\s*in_progress\b', content, re.MULTILINE):
                    current_pr = md_file
                    break

        if not current_pr:
            result = subprocess.run([
                sys.executable, os.path.join(RUNTIME_DIR, "get_next_pr.py"),
                "--workdir", workdir,
                "--job-dir", job_dir
            ], capture_output=True, text=True)
        
            output = result.stdout.strip()
            if "[QUEUE_EMPTY]" in output or not output:
                print("No open PRs found. Exiting.")
                sys.exit(0)
            
            current_pr = output.split('\n')[-1].strip()
            if not os.path.exists(current_pr):
                print(f"Error: PR file {current_pr} not found.")
                sys.exit(1)
            
            set_pr_status(current_pr, "in_progress")
            print(f"Transitioned {current_pr} to in_progress")

        base_filename = os.path.splitext(os.path.basename(current_pr))[0]
        parent_dir_name = os.path.basename(os.path.dirname(os.path.abspath(current_pr)))
        branch_name = f"{parent_dir_name}/{base_filename}".replace(":", "_").replace(" ", "_").replace("?", "_")

        reset_count = 0
        pr_done = False

        while True:
            if pr_done:
                break
                
            # State 0 Solidification (Pre-Checkout Commit)
            status_result = subprocess.run(["git", "diff", "--cached", "--quiet"])
            if status_result.returncode != 0:
                print("State 0: Found uncommitted staged changes. Solidifying state...")
                subprocess.run(["git", "commit", "-m", "docs(planner): auto-generated PR contracts"], check=True)

            print(f"State 2: Checking out branch {branch_name}")
        
            try:
                branch_check = subprocess.run(["git", "show-ref", "--verify", "--quiet", f"refs/heads/{branch_name}"])
                if branch_check.returncode == 0:
                    safe_git_checkout(branch_name)
                else:
                    safe_git_checkout(branch_name, create=True)
            except GitCheckoutError as e:
                print(f"Failed to checkout branch {branch_name}: {e}. Aborting gracefully.", file=sys.stderr)
                sys.exit(1)

            rejection_count = 0
            state_5_trigger = False

            while True:
                print(f"State 3: Spawning Coder for {current_pr}")
                try:
                    coder_result = subprocess.run([
                        sys.executable, os.path.join(RUNTIME_DIR, "spawn_coder.py"),
                        "--pr-file", current_pr,
                        "--workdir", workdir,
                        "--prd-file", args.prd_file
                    ], timeout=MAX_RUNTIME)
                
                    if coder_result.returncode != 0:
                        print("Coder failed. Triggering State 5.")
                        state_5_trigger = True
                        break
                except subprocess.TimeoutExpired:
                    print("Coder timeout. Triggering State 5.")
                    state_5_trigger = True
                    break

                review_artifact = "Review_Report.md"
                review_report_path = os.path.join(workdir, review_artifact)
                if os.path.exists(review_report_path):
                    try:
                        os.remove(review_report_path)
                    except FileNotFoundError:
                        pass

                print(f"State 4: Spawning Reviewer for {current_pr}")
                force_commit_untracked_changes(workdir)
                subprocess.run([
                    sys.executable, os.path.join(RUNTIME_DIR, "spawn_reviewer.py"),
                    "--pr-file", current_pr,
                    "--diff-target", "master",
                    "--workdir", workdir,
                    "--out-file", review_artifact
                ])
            
                if os.path.exists(review_report_path):
                    with open(review_report_path, 'r', encoding='utf-8') as f:
                        review_content = f.read()
                else:
                    review_content = ""

                if "[LGTM]" in review_content:
                    print("State 6: Green Path - Merging code")
                    try:
                        safe_git_checkout("master")
                    except GitCheckoutError as e:
                        print(f"Failed to checkout master: {e}. Aborting gracefully.", file=sys.stderr)
                        sys.exit(1)
                    merge_result = subprocess.run([
                        sys.executable, os.path.join(RUNTIME_DIR, "merge_code.py"),
                        "--branch", branch_name,
                        "--review-file", review_report_path
                    ])
                
                    if merge_result.returncode == 0:
                        subprocess.run(["git", "branch", "-D", branch_name], check=True)
                        set_pr_status(current_pr, "closed")
                        print(f"Successfully closed {current_pr}")
                        teardown_coder_session(workdir)
                        pr_done = True
                        break
                    else:
                        print("Merge failed. Triggering State 5.")
                        state_5_trigger = True
                        break
                elif "[ACTION_REQUIRED]" in review_content:
                    rejection_count += 1
                    if rejection_count < 5:
                        print(f"Review rejected. Count: {rejection_count}. Looping back to State 3.")
                        continue
                    else:
                        print(f"Review rejected 5 times. Invoking Arbitrator.")
                        arbitrator_result = subprocess.run([
                            sys.executable, os.path.join(RUNTIME_DIR, "spawn_arbitrator.py"),
                            "--pr-file", current_pr,
                            "--diff-target", "master",
                            "--workdir", workdir
                        ], capture_output=True, text=True)
                    
                        arb_output = arbitrator_result.stdout
                        if "[OVERRIDE_LGTM]" in arb_output:
                            print("Arbitrator overrode rejection. State 6: Green Path - Merging code")
                            try:
                                safe_git_checkout("master")
                            except GitCheckoutError as e:
                                print(f"Failed to checkout master: {e}. Aborting gracefully.", file=sys.stderr)
                                sys.exit(1)
                            merge_result = subprocess.run([
                                sys.executable, os.path.join(RUNTIME_DIR, "merge_code.py"),
                                "--branch", branch_name,
                                "--review-file", review_report_path
                            ])
                            if merge_result.returncode == 0:
                                subprocess.run(["git", "branch", "-D", branch_name], check=True)
                                set_pr_status(current_pr, "closed")
                                print(f"Successfully closed {current_pr}")
                                teardown_coder_session(workdir)
                                pr_done = True
                                break
                            else:
                                print("Merge failed. Triggering State 5.")
                                state_5_trigger = True
                                break
                        else:
                            print("Arbitrator confirmed rejection. Triggering State 5.")
                            state_5_trigger = True
                            break
                else:
                    print("Invalid Reviewer output. Triggering State 5.")
                    state_5_trigger = True
                    break
        
            if state_5_trigger:
                print("State 5: Triggering 3-Tier Escalation Protocol")
                if reset_count == 0:
                    print("Tier 1 (Reset): Deleting branch and retrying.")
                    try:
                        safe_git_checkout("master")
                    except GitCheckoutError as e:
                        print(f"Failed to checkout master: {e}. Aborting gracefully.", file=sys.stderr)
                        sys.exit(1)
                    # Ignore failure if branch is current or doesn't exist
                    subprocess.run(["git", "branch", "-D", branch_name], check=False)
                    append_to_pr(current_pr, "\n> [Escalation] Tier 1 Reset triggered due to Coder failure or Arbitrator rejection.")
                    reset_count += 1
                    continue
                else:
                    print("Tier 2 (Micro-Slicing): Checking slice depth.")
                    slice_depth = get_pr_slice_depth(current_pr)
                    if slice_depth < 2:
                        print(f"Slice depth is {slice_depth} (< 2). Micro-slicing PR.")
                        pr_files_before = set(glob.glob(os.path.join(job_dir, "PR_*.md")))
                        subprocess.run([
                            sys.executable, os.path.join(RUNTIME_DIR, "spawn_planner.py"),
                            "--slice-failed-pr", current_pr,
                            "--workdir", workdir,
                            "--prd-file", args.prd_file
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
                            print("Process suspended at Tier 3. Human intervention required.")
                            sys.exit(1)
                    else:
                        print(f"Tier 3 (Dead Letter Queue): Slice depth is {slice_depth} (>= 2).")
                        set_pr_status(current_pr, "blocked_fatal")
                        print(f"PR {current_pr} is fatally blocked.")
                        print("Process suspended at Tier 3. Human intervention required.");
                        sys.exit(1)


if __name__ == "__main__":
    main()
