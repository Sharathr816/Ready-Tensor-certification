from langchain.tools import tool
import os, shutil, json


@tool("file_managing_tool", return_direct=False) # return direct used to decide to whom the o/p should be sent(user or llm)
def file_system_access_tool(action: str, path: str = "", dest: str = ""):
    """
    A simple tool that lets the LLM query or act on the file system.
    """
    if action == "scan":
        return json.dumps({"folders": os.listdir(path)})

    elif action == "move":
        shutil.move(path, dest)
        return json.dumps({"moved": path, "to": dest})

    else:
        return json.dumps({"error": "unknown action"})