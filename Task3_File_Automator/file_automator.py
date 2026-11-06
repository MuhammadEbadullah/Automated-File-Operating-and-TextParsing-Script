"""
File Automator — Automated File Operating & Text-Parsing Script
------------------------------------------------------------------
A background automation utility that:
  1. Sorts files in a source directory into category subfolders by extension.
  2. Uses regex to extract emails, transaction IDs, and IP addresses from
     .txt/.log files (with source file + line number for traceability).
  3. Logs every action (moves + extractions) to a master CSV file.
  4. Writes a persistent activity log for every run.
  5. Supports a --dry-run mode to preview actions without changing anything.
  6. Never overwrites files — auto-renames on filename collisions.

Built entirely on Python's standard library — no external dependencies.

Usage:
    python file_automator.py --source ./unsorted_data --dest ./organized
    python file_automator.py --source ./unsorted_data --dry-run
    python file_automator.py --source ./unsorted_data --no-sort
    python file_automator.py --source ./unsorted_data --quiet
"""

import argparse
import csv
import logging
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

# ---------------------------------------------------------
# CONFIG
# ---------------------------------------------------------

EXTENSION_MAP = {
    ".jpg": "Images", ".jpeg": "Images", ".png": "Images", ".gif": "Images", ".webp": "Images",
    ".pdf": "Documents", ".docx": "Documents", ".doc": "Documents", ".odt": "Documents",
    ".xlsx": "Spreadsheets", ".xls": "Spreadsheets", ".csv": "Spreadsheets",
    ".txt": "Logs", ".log": "Logs",
    ".zip": "Archives", ".rar": "Archives", ".7z": "Archives", ".tar": "Archives", ".gz": "Archives",
    ".py": "Scripts", ".js": "Scripts", ".sh": "Scripts", ".bat": "Scripts",
    ".mp4": "Videos", ".mov": "Videos", ".avi": "Videos", ".mkv": "Videos",
}
DEFAULT_CATEGORY = "Others"

PATTERNS = {
    "email": re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"),
    "transaction_id": re.compile(r"\bTXN[-_]?\d{4,10}\b", re.IGNORECASE),
    "ip_address": re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"),
}

MASTER_CSV_NAME = "master_extracted_data.csv"
ACTIVITY_LOG_NAME = "file_automator_activity.log"


# ---------------------------------------------------------
# LOGGING SETUP
# ---------------------------------------------------------

def setup_logging(dest_dir: Path, quiet: bool) -> logging.Logger:
    logger = logging.getLogger("file_automator")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s", "%Y-%m-%d %H:%M:%S")

    file_handler = logging.FileHandler(dest_dir / ACTIVITY_LOG_NAME, encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    if not quiet:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(logging.Formatter("%(levelname)s | %(message)s"))
        logger.addHandler(console_handler)

    return logger


# ---------------------------------------------------------
# HELPERS
# ---------------------------------------------------------

def get_category(file_path: Path) -> str:
    """Return the destination subfolder name for a file, based on its extension."""
    return EXTENSION_MAP.get(file_path.suffix.lower(), DEFAULT_CATEGORY)


def unique_destination(dest_path: Path) -> Path:
    """If dest_path already exists, append a timestamp to avoid overwriting."""
    if not dest_path.exists():
        return dest_path
    stamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return dest_path.with_name(f"{dest_path.stem}_{stamp}{dest_path.suffix}")


def extract_matches(file_path: Path, logger: logging.Logger) -> list:
    """Read a text file line-by-line and extract emails / transaction IDs / IPs."""
    rows = []
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            for line_number, line in enumerate(f, start=1):
                for match_type, pattern in PATTERNS.items():
                    for match in pattern.findall(line):
                        rows.append({
                            "source_file": file_path.name,
                            "line_number": line_number,
                            "match_type": match_type,
                            "match_value": match,
                            "extracted_at": datetime.now().isoformat(timespec="seconds"),
                        })
    except Exception as e:
        logger.warning(f"Could not parse {file_path.name}: {e}")
    return rows


# ---------------------------------------------------------
# CORE LOGIC
# ---------------------------------------------------------

def process_directory(source_dir: Path, dest_dir: Path, do_sort: bool,
                       dry_run: bool, logger: logging.Logger) -> list:
    """Walk source_dir, sort files into dest_dir by category, and extract data."""
    all_rows = []
    files = [f for f in source_dir.iterdir() if f.is_file()]
    logger.info(f"Found {len(files)} file(s) in source directory: {source_dir}")

    for file_path in files:
        if file_path.suffix.lower() in (".txt", ".log"):
            rows = extract_matches(file_path, logger)
            all_rows.extend(rows)
            if rows:
                logger.info(f"Parsed {file_path.name}: {len(rows)} match(es) found")

        if do_sort:
            category = get_category(file_path)
            category_dir = dest_dir / category
            target_path = unique_destination(category_dir / file_path.name)

            if dry_run:
                logger.info(f"[DRY RUN] Would move {file_path.name} -> {category}/{target_path.name}")
            else:
                category_dir.mkdir(parents=True, exist_ok=True)
                try:
                    shutil.move(str(file_path), str(target_path))
                    logger.info(f"Moved {file_path.name} -> {category}/{target_path.name}")
                except Exception as e:
                    logger.error(f"Failed to move {file_path.name}: {e}")

    return all_rows


def write_master_csv(dest_dir: Path, rows: list, dry_run: bool, logger: logging.Logger):
    if not rows:
        logger.info("No matches found — master CSV not updated.")
        return
    if dry_run:
        logger.info(f"[DRY RUN] Would write {len(rows)} row(s) to master CSV.")
        return

    csv_path = dest_dir / MASTER_CSV_NAME
    fieldnames = ["source_file", "line_number", "match_type", "match_value", "extracted_at"]
    file_exists = csv_path.exists()

    with open(csv_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerows(rows)

    logger.info(f"Wrote {len(rows)} row(s) to master CSV: {csv_path}")


# ---------------------------------------------------------
# CLI / MAIN
# ---------------------------------------------------------

def parse_args():
    parser = argparse.ArgumentParser(
        description="Automated File Operating & Text-Parsing Script"
    )
    parser.add_argument("--source", required=True, help="Path to the unorganized source directory")
    parser.add_argument("--dest", default="./organized", help="Destination root directory (default: ./organized)")
    parser.add_argument("--no-sort", action="store_true", help="Skip file sorting, only parse logs")
    parser.add_argument("--dry-run", action="store_true", help="Preview actions without moving/writing anything")
    parser.add_argument("--quiet", action="store_true", help="Suppress console output")
    return parser.parse_args()


def main():
    args = parse_args()

    source_dir = Path(args.source).expanduser().resolve()
    dest_dir = Path(args.dest).expanduser().resolve()

    if not source_dir.is_dir():
        print(f"Error: source directory '{source_dir}' does not exist.")
        sys.exit(1)

    dest_dir.mkdir(parents=True, exist_ok=True)
    logger = setup_logging(dest_dir, args.quiet)

    logger.info(f"Run started. Source: {source_dir} | Destination: {dest_dir} | "
                f"Sort: {not args.no_sort} | Dry run: {args.dry_run}")

    rows = process_directory(
        source_dir=source_dir,
        dest_dir=dest_dir,
        do_sort=not args.no_sort,
        dry_run=args.dry_run,
        logger=logger,
    )
    write_master_csv(dest_dir, rows, args.dry_run, logger)

    logger.info("Run complete.")


if __name__ == "__main__":
    main()
