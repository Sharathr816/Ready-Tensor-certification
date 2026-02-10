from os import write

from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage, AIMessage
from langchain_groq import ChatGroq
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict
from typing import Annotated
from tools import scan_user_folders_across_drives, USER_FOLDERS, read_summaries_by_folder, write_for_analysis

from pathlib import Path
import json
load_dotenv()


# Define your agent's state - this is your agent's memory
class State(TypedDict):
    # routing / orchestration
    user_query: Annotated[list, add_messages]
    agent_choice: str
    file_sys_msg: str
    process_sys_msg: str

    # file-analysis specific
    folder_index: int
    messages: Annotated[list, add_messages]
    phase: str
    # summary handling - (chunk the user folder related summaries)
    current_summary: dict | None
    summary_chunks: list | None
    chunk_index: int

tools = [scan_user_folders_across_drives, read_summaries_by_folder, write_for_analysis]


#helper
def chunk_dict(d: dict, size: int = 5):
    items = list(d.items())
    for i in range(0, len(items), size):
        yield dict(items[i:i + size])


# Routers
#orchestor
def router(state:State):
    if state["agent_choice"] == "file":
        return "file"
    return "process"

# file_manager
def proceed(state: State):
    if state["folder_index"] >= len(USER_FOLDERS):
        return "end"

    last_msg = state["messages"][-1]
    if isinstance(last_msg, AIMessage) and last_msg.tool_calls:
        return "tool"

    return "file"   # continue to next folder



# The nodes
# orchestor
def orchestor(state: State):
    orc_llm = ChatGroq(model="openai/gpt-oss-20b", temperature=0)
    response = orc_llm.invoke(state["user_query"]) # response in json inside string
    # remove ```json and ```
    clean = response.content.strip().removeprefix("```json").removesuffix("```").strip()
    data = json.loads(clean)
    print(data["processed_query"])
    return {"agent_choice": data["agent"], "messages": [HumanMessage(content=data["processed_query"])]}


# File managing nodes
def file_manager(state: State):
    file_llm = ChatGroq(model="openai/gpt-oss-20b", temperature=0)
    llm_tool = file_llm.bind_tools(tools)
    idx = state["folder_index"]
    phase = state["phase"]

    folder = USER_FOLDERS[idx]

    # phase 1 -> Scan
    if phase == "scan":
        msg = llm_tool.invoke([
            SystemMessage(
                content=f"""
                Call the scan tool to search for user folder in the system drives.
                """
            )
        ])
        return {
            "messages": [msg],
            "phase": "read"
        }

    # PHASE 2 → READ
    if phase == "read":
        msg = llm_tool.invoke([
            SystemMessage(
                content=f"""
                Call the tool read_summaries_by_folder for folder: {folder}.
                Do not make any decision yet.
                """
            )
        ])
        return {
            "messages": [msg],
            "phase": "decide",
            "chunk_index": 0,
        }

    #phase -> decide (Batched calling)
    if phase == "decide":
        chunks = state["summary_chunks"]
        i = state["chunk_index"]

        # finished all chunks for this folder
        if i >= len(chunks):
            return {
                "phase": "read",
                "folder_index": idx + 1,
                "current_summary": None,
                "summary_chunks": None,
                "chunk_index": 0
            }

        current_chunk = chunks[i]
        msg = llm_tool.invoke([
                SystemMessage(
                    content=f"""
                    Folder under analysis: {folder}
                    
                    Batch summary:
                    {json.dumps(current_chunk, indent=2)}
                    
                    You are analyzing file organization for a Windows 10+ user.
                    You are given folder summaries for MULTIPLE paths
                    
                    Your task:
                    - Inspect each path independently.
                    - Decide whether it should be ignored for a normal Windows user.
                       
                    Ignore Rules (To be followed strictly):
                        Operating system core directories
                        Application installation directories
                        Runtime, framework, or language environments bundled with applications
                        Software update, patching, or auto-generated support folders
                        Dependency, package, or library directories managed by tools
                        Build outputs, compiled artifacts, or internal resource folders
                        Application cache, logs, metadata, configuration, or documentation folders
                        Security, antivirus, backup, or system protection data
                        Default or template user profiles
                        Cloud-sync service internal folders and placeholders
                        Framework, platform, or tool-specific internal directories
                        Hidden or system-marked folders unless explicitly user-created
                    
                    Not to be ignored rules:
                        Personal or public user folders
                        (Desktop, Downloads, Documents, Pictures, Music, Videos)
                        User-created folders on internal or external drives
                        (including personal project folders, media collections, archives)
                        Any folder primarily containing user-authored content
                        (files the user downloads, creates, edits, or organizes manually)
                    
                    If at least one path is not to be ignored:
                    - Call write_for_analysis ONCE.
                    - Pass:
                      - folder_paths: list of paths not to be ignored
                      - summary: corresponding summaries
                    
                    If all paths are to be ignored then:
                    - Do NOT call any tool.
                    - Respond with a normal assistant message.
                    """
                                        )
                                    ])
        print("agent responded...")
        return {
            "messages": [msg],
            "chunk_index": i + 1
        }





def file_tools_node(state: State):
    """Your agent's hands - executes the chosen tools."""
    tool_registry = {tool.name: tool for tool in tools}# {"Duck_search": duckduckgoToolObject}

    last_message = state["messages"][-1]# consists of the ai message
    tool_messages = []
    updates = {}

    # Execute each tool the agent requested
    # print(last_message.tool_calls)
    for tool_call in last_message.tool_calls:
        tool = tool_registry[tool_call["name"]]
        print(tool_call["name"])
        print(tool_call["args"])
        result = tool.invoke(tool_call["args"])

        # Send the result back to the agent - appending the ToolMessage object
        tool_messages.append(ToolMessage(
            content=result,
            tool_call_id=tool_call["id"]
        ))

        # Capture read result
        if tool_call["name"] == "read_summaries_by_folder":
            summary = result
            updates["current_summary"] = summary
            updates["summary_chunks"] = list(chunk_dict(summary, size=3))

    # print(tool_messages)
    print("agent successfully called tools...\n")

    return {
        "messages": state["messages"] + tool_messages,
        **updates
}






def process_manager(state: State):
    pass


# Build the complete workflow
def create_agent():
    graph = StateGraph(State)
    # Add the nodes
    graph.add_node("file_node", file_manager)
    graph.add_node("file_tool", file_tools_node)
    graph.add_node("orchestor", orchestor)
    # Set the starting point
    graph.set_entry_point("orchestor")
    # Add the flow logic
    graph.add_conditional_edges("orchestor", router, {"file": "file_node", "process": END})
    graph.add_conditional_edges("file_node", proceed, {"file": "file_node", "tool": "file_tool", "end": END})
    graph.add_edge("file_tool", "file_node")
    return graph.compile()

# Create and use your enhanced agent
agent = create_agent()



# Test it out by invoking the graph
initial_state = {
"user_query": [
        SystemMessage(content="""You are an orchestor who manages the routing process in a PC manager system made for windows. Your task is to take the user text query and 
        parse it into a dictionary with the following key-value pairs...
        1. agent -  which can have value either "process" if query is related to process management work or "file" if query is related to file/dir management in system
        2. processed_query - processed user query which is clear and unambigous such that other llm can work without confusion"""),
        HumanMessage(content="I want the scanning of my systems file structure to organize everything")
    ],
"folder_index": 0,
"phase": "scan"

}
# final output
result = agent.invoke(initial_state, config={"recursion_limit": 100})
print(result["messages"][-1].content)


"""
"""