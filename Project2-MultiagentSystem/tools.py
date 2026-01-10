# implementation of system visibility and formatter tools
import os
from langchain.tools import tool


# need for returning structured data like dict
@tool
def file_management(paths: list) -> dict:
    """
    Recursively reads directories and files for multiple paths.
    Returns structured directory tree data.
    """

    def read_dir(path):
        node = {
            "files": [],
            "subdirs": {}
        }

        try:
            for entry in os.listdir(path):
                full_path = os.path.join(path, entry)

                if os.path.isdir(full_path):
                    node["subdirs"][entry] = read_dir(full_path) #if dir then recurse

                elif os.path.isfile(full_path):
                    node["files"].append(entry) # if file then add it to node

        except PermissionError:
            node["error"] = "permission_denied"

        except Exception as e:
            node["error"] = str(e)

        return node

    result = {}

    for path in paths:
        if not os.path.exists(path):
            result[path] = {"error": "path_not_found"}
            continue

        result[path] = read_dir(path)

    return result

