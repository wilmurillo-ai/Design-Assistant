with open("scripts/merge_code.py", "r") as f:
    content = f.read()

old_block = """        except subprocess.CalledProcessError as e:
            print(f"Merge failed: {e.stderr}", file=sys.stderr)
            sys.exit(1)"""

new_block = """        except subprocess.CalledProcessError as e:
            print(f"Merge failed: {e.stderr}. Aborting merge.", file=sys.stderr)
            subprocess.run(["git", "merge", "--abort"], check=False)
            sys.exit(1)"""

content = content.replace(old_block, new_block)

with open("scripts/merge_code.py", "w") as f:
    f.write(content)
