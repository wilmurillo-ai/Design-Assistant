# Homework Command Reference

```bash
tronclass homework <subcommand> [options]
tronclass hw <subcommand>
```

---

## `list <course_id>`

```bash
tronclass homework list <course_id> [--fields f1,f2,...]
tronclass hw l <course_id>
```

Lists all homework activities for a course.

**Default fields:** `id, title, deadline, status, score`

| Field | Description |
|---|---|
| `id` | Activity ID |
| `title` | Homework title |
| `deadline` / `due_at` | Submission deadline |
| `status` | Computed: 已繳交 / 待繳交 / 未繳 |
| `score` | Score received (if graded) |
| `max_score` | Maximum possible score |

---

## `submit <activity_id> <file...>`

```bash
tronclass homework submit <activity_id> <file1> [file2 ...] [--draft]
tronclass hw s <activity_id> ./essay.pdf ./appendix.pdf
```

Uploads one or more files and submits them for the specified homework activity.

A confirmation prompt is shown before submitting, displaying the homework title and the file(s) to be submitted.

| Option | Description |
|---|---|
| `--draft` | Save as draft instead of final submission |

### Notes

- Multiple files can be submitted in one command.
- Folders are not supported — only individual files.
- Supported file types: any (MIME type detected automatically).
- The activity ID is the `id` from `homework list`.

### Example

```bash
# Find the homework ID
tronclass homework list <course_id>

# Submit a single file
tronclass homework submit 2901222 ./report.pdf

# Submit multiple files
tronclass homework submit 2901222 ./report.pdf ./data.xlsx

# Save as draft first
tronclass homework submit 2901222 ./draft_report.pdf --draft
```
