# Obsidian workflow reference

## Setup workflow

1. Ensure the real Obsidian vault location is known.
2. Link the vault into the workspace with a symlink or create `obsidian/` as a normal folder.
3. Verify file visibility through the workspace path.
4. Start writing markdown files into category folders.

Example:

```bash
ln -s "/Users/yourname/Desktop/Obsidian/YourVault" ./obsidian
find -L ./obsidian -maxdepth 2 -type f | head
```

## Knowledge sync workflow

1. Read the source material.
2. Distill the stable facts and current judgment.
3. Decide whether the destination is person/org/methodology/journal/openclaw mirror.
4. Update an existing note or create a new note.
5. Keep wording readable for humans, not just machine-oriented.

## Daily journal workflow

A good daily note should contain:
- 今天做了什么
- 形成了哪些产出
- 阶段性结果是什么
- 接下来适合做什么

## Mirror workflow

When mirroring OpenClaw files into Obsidian:
- copy the current canonical text
- avoid partial snippets when the full file is short and operationally important
- keep filenames unchanged for easier cross-reference
