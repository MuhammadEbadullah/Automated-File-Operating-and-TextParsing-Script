# Usage Guide

## Command-line arguments

| Flag | Required | Default | Description |
|---|---|---|---|
| `--source` | Yes | — | Path to the unorganized source directory to process |
| `--dest` | No | `./organized` | Root directory where sorted folders + reports are written |
| `--no-sort` | No | off | Skip moving files — only parse `.txt`/`.log` files and extract data |
| `--dry-run` | No | off | Preview every action (what would move where, what would be extracted) without touching any file |
| `--quiet` | No | off | Suppress console output (the activity log file is still written) |

## Examples

### 1. Standard run

```bash
python file_automator.py --source ./sample_data --dest ./organized
```

Sorts every file in `sample_data/` into `organized/<Category>/`, and writes
`organized/master_extracted_data.csv` with any emails, transaction IDs, or IP
addresses found in `.txt`/`.log` files.

### 2. Preview only (dry run)

```bash
python file_automator.py --source ./sample_data --dry-run
```

Nothing is moved or written. The console/activity log shows exactly what
*would* happen — useful before running on a folder you care about.

### 3. Extract data only, don't move files

```bash
python file_automator.py --source ./sample_data --no-sort
```

Useful if you just want the CSV report and want files to stay where they are.

### 4. Silent run (e.g. for a scheduled task / cron job)

```bash
python file_automator.py --source ./sample_data --quiet
```

No console output — check `organized/file_automator_activity.log` afterwards
for a full record of what happened.

## Scheduling it to run automatically

**Windows (Task Scheduler):**
1. Open Task Scheduler → Create Basic Task
2. Set your trigger (e.g. daily at 9 PM)
3. Action → Start a program → `python.exe`
4. Arguments: `file_automator.py --source "C:\Downloads" --dest "C:\Organized" --quiet`

**macOS/Linux (cron):**
```bash
# Run daily at 9 PM
0 21 * * * cd /path/to/project && python3 file_automator.py --source ~/Downloads --dest ~/Organized --quiet
```

## Extending it

- Add a new extension category → edit `EXTENSION_MAP` at the top of `file_automator.py`
- Add a new regex pattern to extract (e.g. phone numbers) → add an entry to `PATTERNS`
- Both changes require no other code edits — the rest of the script picks them up automatically.
