# Progree Python Internship — Programming Tasks

This repository contains my solutions to the Python programming tasks assigned during my internship with **Progree**. Each task lives in its own folder with its own README, source code, sample data, and real output.

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

## Task 3 at a glance

Sorts a messy folder into subdirectories by file extension, extracts emails, transaction IDs, and IP addresses from log files using regular expressions, and records everything in a master CSV with line-level traceability. Includes dry-run mode, activity logging, collision-safe moves, and a unit test suite.

```bash
cd Task3_File_Automator
python file_automator.py --source ./sample_data --dest ./organized --dry-run
```

Full documentation, CLI options, and real output: [`Task3_File_Automator/README.md`](Task3_File_Automator/README.md)

## Requirements

- Python 3.8+
- Standard library only (no installs needed)

## Skills demonstrated

File system automation (`os`, `shutil`, `pathlib`), regular expressions, CSV handling, CLI design with `argparse`, logging, and unit testing with `unittest`.

## License

MIT — see [LICENSE](LICENSE).
