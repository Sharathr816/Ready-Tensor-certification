from langchain.tools import tool
import os, shutil, json


#@tool("file_managing_tool", return_direct=False) # return direct used to decide to whom the o/p should be sent(user or llm)
@tool("file_system_access_tool", return_direct=False)
def file_system_access_tool(action: str, path: str = "", dest: str = "") -> dict:
    if action == "scan":
        try:
            return {"folders": os.listdir(path)}
        except Exception as e:
            return {"error": str(e)}

    elif action == "move":
        try:
            shutil.move(path, dest)
            return {"moved": path, "to": dest}
        except Exception as e:
            return {"error": str(e)}

    else:
        return {"error": "Unknown action"}