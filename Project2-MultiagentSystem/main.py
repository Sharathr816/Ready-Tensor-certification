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
    current_summary: dict | None

tools = [scan_user_folders_across_drives, read_summaries_by_folder, write_for_analysis]


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
            "messages": [msg], # no context maintained here
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
            "phase": "decide"
        }

    # PHASE 3 → DECIDE + OPTIONAL WRITE
    msg = llm_tool.invoke([
            SystemMessage(
                content=f"""
                Folder under analysis: {folder}
                
                Summary:
                {json.dumps(state["current_summary"], indent=2)}
                
                You are analyzing file organization for a Windows 10+ user.

                You are given folder summaries for ONE logical user folder (e.g., Desktop, Downloads etc..,).
                
                Your task:
                - Inspect each path independently.
                - Decide whether it is structurally disorganized for a normal Windows user.
                
                Disorganization indicators include:
                - Many files at root level
                - Many extensions with Mixed unrelated extensions
                - Subfolder count > 0 
                
                Ignore:
                - Software installation paths
                - SDKs, build outputs, package directories
                - System-managed folders
                
                If at least one path is disorganized:
                - Call write_for_analysis ONCE.
                - Pass:
                  - folder_paths: list of disorganized paths only
                  - summary: corresponding summaries
                
                If no path is disorganized:
                - Do NOT call any tool.
                - Respond with a normal assistant message.
                
                You must NOT stop execution early.
                You must NOT decide control flow.
                """
                                    )
                                ])
    print("agent responded...")
    return {
            "messages": [msg],
            "phase": "read",
            "folder_index": idx + 1,
            "current_summary": None
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
            updates["current_summary"] = result

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