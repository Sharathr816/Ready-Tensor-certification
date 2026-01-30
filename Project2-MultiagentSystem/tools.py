import os
import json
from pathlib import Path
from collections import Counter
from typing import List, Dict
from langchain.tools import tool


# =========================
# CONSTANTS (LOCKED)
# =========================

USER_FOLDERS = [
    "Desktop",
    "Documents",
    "Downloads",
    "Pictures",
    "Picture",
    "Music",
    "Musics",
    "Videos",
    "Video"
]

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

def should_prune_dir(dir_name: str, full_path: str) -> bool:
    if should_ignore_folder(dir_name):
        return True
    if has_project_marker(full_path):
        return True
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
    """Scan the system to search user folders in the whole system"""
    results = {}

    for drive_letter in "CDEFGHIJKLMNOPQRSTUVWXYZ":
        drive_path = Path(f"{drive_letter}:/")
        if not drive_path.exists():
            continue

        for root, dirs, _ in os.walk(drive_path, topdown=True):
            # 🔴 PRUNE FIRST
            pruned_dirs = [] # list containing dirs which needs trversal
            for d in dirs:
                full = os.path.join(root, d)
                if not should_prune_dir(d, full):
                    pruned_dirs.append(d)
            dirs[:] = pruned_dirs  # critical

            folder_name = Path(root).name

            if folder_name in USER_FOLDERS:
                key = root.replace("\\", "/")
                results[key] = search_user_folder(root)

                # stop diving into this user folder
                dirs.clear()

    with open("summaries.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4)

    return {
        "status": "Done",
        "file_name": "summaries.json"
    }

@tool
def read_summaries_by_folder(folder_name: str) -> dict:
    """
    Reads summaries.json and returns all entries whose path
    contains the given folder name (case-insensitive).
    """

    summaries_file = Path("summaries.json")
    if not summaries_file.exists():
        return {
            "folder": folder_name,
            "summary": []
        }

    with summaries_file.open("r", encoding="utf-8") as f:
        data = json.load(f)

    folder_name_lower = folder_name.lower()
    matched = {}

    for path_key, summary_list in data.items():
        if folder_name_lower in path_key.lower():
            matched[path_key] = summary_list

    return {
        "folder": f"{folder_name} done",
        "summaries": matched
    }

@tool
def write_for_analysis(data: dict) -> dict:
    """
    Expects data in the form:
    {
        "folder_paths": [list of folder paths],
        "summaries": [list of corresponding summaries]
    }
    Appends this entry to analysis.json
    """

    path = Path("analysis.json")

    if path.exists() and path.stat().st_size > 0:
        with path.open("r", encoding="utf-8") as f:
            existing = json.load(f)
    else:
        existing = []

    if not isinstance(existing, list):
        existing = [existing]

    # minimal validation
    entry = {
        "folder_paths": data.get("folder_paths", []),
        "summaries": data.get("summaries", [])
    }

    existing.append(entry)

    with path.open("w", encoding="utf-8") as f:
        json.dump(existing, f, indent=4)

    return {"status": "appended"}

