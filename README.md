Automated File Operating & Text-Parsing Script

A background automation utility that organizes a messy directory and mines flat log/text files for structured data (emails, transaction IDs, IP addresses), writing everything to a single clean CSV — with a full activity log, dry-run preview mode, and collision-safe file handling.

Built entirely on Python's standard library — no external dependencies.

## Task requirements and how they are met

| Requirement | Implementation |
|---|---|
| Use standard system libraries (`os`, `shutil`, `re`, `pathlib`) | `pathlib` for paths, `shutil` for moving files, `re` for extraction, plus `csv`, `argparse`, `logging` |
| Parse an unorganized folder and sort files into subdirectories by extension | `EXTENSION_MAP` + `process_directory()` sort files into `Images/`, `Documents/`, `Logs/`, `Spreadsheets/`, `Scripts/`, `Archives/`, `Videos/`, `Others/` |
| Use regular expressions to extract strings (emails, transaction IDs) from flat logs | `PATTERNS` dict: email, transaction ID (`TXN123456`), IP address |
| Log outputs to a clean master CSV | `master_extracted_data.csv` with source file, line number, match type, value, timestamp |

## Features

- Auto-sorts files by extension into category subfolders
- Extracts emails, transaction IDs, and IP addresses from `.log`/`.txt` files
- Master CSV with full traceability (source file + line number for every match)
- Persistent activity log for every run
- `--dry-run` mode to preview every action before anything is moved
- Collision-safe: never overwrites, auto-renames with a timestamp on conflict
- Configurable extension map and regex patterns
- Unit test suite (8 tests)

## Repository structure

```
PROGREE_Python_Tasks/
├── README.md
├── LICENSE
├── .gitignore
└── Task3_File_Automator/
    ├── file_automator.py
    ├── README.md
    ├── requirements.txt
    ├── sample_data/
    ├── tests/
    ├── docs/
    └── output/              # real output from running the script
```

## Project structure

```
Task3_File_Automator/
├── file_automator.py            # Main script
├── requirements.txt             # No dependencies (stdlib only)
├── README.md
├── sample_data/                 # Messy input files used for the demo
│   ├── server_access.log
│   ├── notes.txt
│   ├── photo.png
│   ├── report.pdf
│   ├── sales_data.csv
│   ├── backup.zip
│   ├── helper_script.py
│   └── mystery.xyz
├── tests/
│   └── test_file_automator.py   # Unit tests (unittest)
├── docs/
│   └── USAGE.md                 # Detailed usage and scheduling guide
└── output/                      # Real output from running the script
    ├── 01_dry_run_terminal_output.txt
    ├── 02_real_run_terminal_output.txt
    ├── 03_unit_tests_output.txt
    └── organized_result/
        ├── Archives/backup.zip
        ├── Documents/report.pdf
        ├── Images/photo.png
        ├── Logs/notes.txt
        ├── Logs/server_access.log
        ├── Others/mystery.xyz
        ├── Scripts/helper_script.py
        ├── Spreadsheets/sales_data.csv
        ├── file_automator_activity.log
        └── master_extracted_data.csv
```

## Requirements

- Python 3.8+
- Standard library only (no installs needed)
- No third-party packages

## How to run

```bash
# From inside the Task3_File_Automator folder
python --version                # use python3 on macOS/Linux

# 1. Preview first
python file_automator.py --source ./sample_data --dest ./organized --dry-run

# 2. Run for real
cp -r sample_data unsorted_demo           # Windows: xcopy sample_data unsorted_demo /E /I
python file_automator.py --source ./unsorted_demo --dest ./organized

# 3. Inspect results
ls -R organized                           # Windows: dir organized /s
cat organized/master_extracted_data.csv   # Windows: type organized\master_extracted_data.csv
```

## CLI options

| Flag | Description |
|---|---|
| `--source` | **(required)** Path to the unorganized source directory |
| `--dest` | Destination root directory (default: `./organized`) |
| `--no-sort` | Skip file sorting, only parse logs |
| `--dry-run` | Preview actions without moving/writing anything |
| `--quiet` | Suppress console output (activity log is still written) |

More examples and scheduling instructions: [`docs/USAGE.md`](docs/USAGE.md)

## Output (real results from this repo's sample data)

The full output is saved in the [`output/`](output/) folder.

### Dry run

```
INFO | Found 8 file(s) in source directory: ./sample_data
INFO | [DRY RUN] Would move photo.png -> Images/photo.png
INFO | [DRY RUN] Would move helper_script.py -> Scripts/helper_script.py
INFO | [DRY RUN] Would move report.pdf -> Documents/report.pdf
INFO | [DRY RUN] Would move mystery.xyz -> Others/mystery.xyz
INFO | [DRY RUN] Would move sales_data.csv -> Spreadsheets/sales_data.csv
INFO | Parsed notes.txt: 2 match(es) found
INFO | [DRY RUN] Would move notes.txt -> Logs/notes.txt
INFO | Parsed server_access.log: 7 match(es) found
INFO | [DRY RUN] Would move server_access.log -> Logs/server_access.log
INFO | [DRY RUN] Would move backup.zip -> Archives/backup.zip
INFO | [DRY RUN] Would write 9 row(s) to master CSV.
```

### Real run

```
INFO | Found 8 file(s) in source directory: ./unsorted_demo
INFO | Moved photo.png -> Images/photo.png
INFO | Moved helper_script.py -> Scripts/helper_script.py
INFO | Moved report.pdf -> Documents/report.pdf
INFO | Moved mystery.xyz -> Others/mystery.xyz
INFO | Moved sales_data.csv -> Spreadsheets/sales_data.csv
INFO | Parsed notes.txt: 2 match(es) found
INFO | Moved notes.txt -> Logs/notes.txt
INFO | Parsed server_access.log: 7 match(es) found
INFO | Moved server_access.log -> Logs/server_access.log
INFO | Moved backup.zip -> Archives/backup.zip
INFO | Wrote 9 row(s) to master CSV
INFO | Run complete.
```

### Generated `master_extracted_data.csv`

| source_file | line_number | match_type | match_value |
|---|---|---|---|
| notes.txt | 2 | email | client.lead@business.org |
| notes.txt | 3 | transaction_id | TXN-445566 |
| server_access.log | 1 | email | ebad@gmail.com |
| server_access.log | 1 | ip_address | 192.168.1.45 |
| server_access.log | 2 | transaction_id | TXN123456 |
| server_access.log | 3 | email | ali@microsoft.com |
| server_access.log | 4 | transaction_id | TXN-778890 |
| server_access.log | 5 | ip_address | 10.0.0.23 |
| server_access.log | 6 | email | contact.us@google.co |

### Unit tests

```
Ran 8 tests in 0.004s
OK
```

## Configuration

`EXTENSION_MAP` (file categories) and `PATTERNS` (regex) sit at the top of `file_automator.py`. Adding a new category or a new pattern (e.g. phone numbers) takes one line.

## Note for Windows / PowerShell users

`echo "text" > file.log` writes UTF-16 in Windows PowerShell, but this script reads UTF-8, which can make regex matches silently fail. Create test files with:

```powershell
Set-Content -Path file.log -Value "your text" -Encoding utf8
```
## Skills demonstrated

File system automation (`os`, `shutil`, `pathlib`), regular expressions, CSV handling, CLI design with `argparse`, logging, and unit testing with `unittest`.

## Real-world use cases

- Scheduled cleanup of shared drives or download folders
- Reconciling transaction IDs and customer emails from payment logs
- First-pass security triage of IPs and emails in auth logs
- Pre-migration cleanup of a messy legacy file share

## License

MIT — see [LICENSE](LICENSE).
