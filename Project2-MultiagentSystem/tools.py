import os
import json
from pathlib import Path
from collections import Counter
from typing import List, Dict
from langchain.tools import tool


# =========================
# CONSTANTS (LOCKED)
# =========================

USER_FOLDERS = {
    "Desktop",
    "Documents",
    "Downloads",
    "Pictures",
    "Music",
    "Musics"
    "Videos",
}

MAX_DEPTH = 3

IGNORE_FOLDERS_BY_NAME = {
    "$Recycle.Bin",
    "System Volume Information",
    "Recovery",
    "PerfLogs",
    "AppData",
    "Microsoft",
    "Windows",
    "NVIDIA",
    "Intel",
    "AMD",
    "Drivers",
}

PROJECT_MARKERS = {
    ".git",
    ".hg",
    ".svn",
    "package.json",
    "pyproject.toml",
    "requirements.txt",
    "Pipfile",
    "setup.py",
    "pom.xml",
    "build.gradle",
    "go.mod",
    "Cargo.toml",
    ".gitignore",
    "README.md",
    "readme.md",
}

MAX_EXTENSION_TYPES = 10


# =========================
# INTERNAL HELPERS
# =========================

def is_dot_folder(name: str) -> bool:
    return name.startswith(".")


def should_ignore_folder(name: str) -> bool:
    if name in IGNORE_FOLDERS_BY_NAME:
        return True
    if is_dot_folder(name):
        return True
    return False


def has_project_marker(path: str) -> bool:
    try:
        entries = set(os.listdir(path))
        return bool(entries & PROJECT_MARKERS)
    except Exception:
        return False


# =========================
# CORE TRAVERSAL
# =========================

def search_user_folder(root_path: str) -> List[Dict]:
    """
    Analyzes ONLY the user folder itself.
    Does NOT recurse into subfolders.
    """
    summaries = []

    try:
        entries = os.listdir(root_path)
    except Exception:
        return summaries

    folder_name = Path(root_path).name

    if should_ignore_folder(folder_name):
        return summaries

    if has_project_marker(root_path):
        return summaries

    file_count = 0
    subfolder_count = 0
    extensions = Counter()

    for entry in entries:
        full_path = os.path.join(root_path, entry)

        if os.path.isfile(full_path):
            file_count += 1
            ext = Path(entry).suffix.lower()
            if ext:
                extensions[ext] += 1

        elif os.path.isdir(full_path):
            subfolder_count += 1
            # 🚫 NO recursion here

    summaries.append({
        "path": root_path.replace("\\", "/"),
        "depth": 0,  # user folder is always depth 0
        "file_count": file_count,
        "subfolder_count": subfolder_count,
        "extensions": dict(extensions.most_common(MAX_EXTENSION_TYPES))
    })

    return summaries



# =========================
# TOOL ENTRY POINT
# =========================

@tool
def scan_user_folders_across_drives() -> Dict:
    """
    Scans for user folders (Desktop, Documents, etc.)
    across ALL drives and analyzes them up to depth 3.
    """

    results = {}

    for drive_letter in "CDEFGHIJKLMNOPQRSTUVWXYZ":
        drive_path = Path(f"{drive_letter}:/")
        if not drive_path.exists():
            continue

        for root, dirs, _ in os.walk(drive_path):
            folder_name = Path(root).name

            if folder_name in USER_FOLDERS:
                key = f"{drive_letter}:{root[len(drive_path.as_posix()):]}"
                results[key] = search_user_folder(root)

                # Do NOT keep walking inside once found
                dirs.clear()

    with open("summaries.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4)

    return {
        "status": "Done",
        "file_name": "summaries.json"
    }
