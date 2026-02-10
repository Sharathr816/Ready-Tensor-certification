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

MAX_EXTENSION_TYPES = 15


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
    """Ignore unnecessary folders (irrelevant to the user for organization)"""
    if should_ignore_folder(dir_name):
        return True
    if has_project_marker(full_path):
        return True
    return False

def matches_user_folder(folder_name: str, target: str) -> bool:
    """to search folders consisting even part of the target name in folder_name"""
    return target.lower() in folder_name.lower()



# =========================
# CORE TRAVERSAL
# =========================

def analyse_user_folder(root_path: str) -> List[Dict]:
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

        for root, dirs, _ in os.walk(drive_path, topdown=True): #
            """os.walk recurse deeper into folders, returns full path, dirs and files within.
            if root is c:// pics then dirs consists of all folders within pics"""
            # 🔴 PRUNE FIRST
            pruned_dirs = []
            for d in dirs: # deciding on relevant dirs for traversal
                full = os.path.join(root, d)
                if not should_prune_dir(d, full):
                    pruned_dirs.append(d)
            dirs[:] = pruned_dirs  # critical - keep only the dirs where we can find user folders

            folder_name = Path(root).name # Extracts last folder or file name from the path name

            for user_folder in USER_FOLDERS:
                if matches_user_folder(folder_name, user_folder):
                    key = root.replace("\\", "/")
                    results[key] = analyse_user_folder(root)

                    """Deeper analysis can be done here (use os.walk)"""
                    # stop diving into this user folder (stops os.walk at user folder)
                    dirs.clear()
                    break

    with open("summaries.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4)

    return {
        "status": "Scan Done",
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
        "folder": folder_name,
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

    Appends ONLY new paths to analysis.json
    (skips paths already present anywhere in the file)
    """

    path = Path("analysis.json")

    # Load existing data
    if path.exists() and path.stat().st_size > 0:
        with path.open("r", encoding="utf-8") as f:
            existing = json.load(f)
    else:
        existing = []

    if not isinstance(existing, list):
        existing = [existing]

    # Collect all existing folder paths (flattened)
    existing_paths = set()
    for entry in existing:
        for p in entry.get("folder_paths", []):
            existing_paths.add(p)

    # Incoming data
    incoming_paths = data.get("folder_paths", [])
    incoming_summaries = data.get("summaries", [])

    # Filter out already-existing paths
    new_paths = []
    new_summaries = []

    for p, s in zip(incoming_paths, incoming_summaries):
        if p not in existing_paths:
            new_paths.append(p)
            new_summaries.append(s)

    # If nothing new, do not write
    if not new_paths:
        return {
            "status": "skipped",
            "reason": "all paths already exist"
        }

    # Append only new data
    existing.append({
        "folder_paths": new_paths,
        "summaries": new_summaries
    })

    with path.open("w", encoding="utf-8") as f:
        json.dump(existing, f, indent=4)

    return {
        "status": "appended",
        "new_paths_count": len(new_paths)
    }


