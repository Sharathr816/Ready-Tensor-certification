from os import write

from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage
from langchain_groq import ChatGroq
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict
from typing import Annotated
from tools import scan_user_folders_across_drives

from pathlib import Path
import json
load_dotenv()


# Define your agent's state - this is your agent's memory
class State(TypedDict):# used to define dictionary-like objects with fixed keys and types.
    user_query: Annotated[list, add_messages]
    processed_q_data: Annotated[list, add_messages]
    file_sys_msg: str
    process_sys_msg: str
    agent_choice: str

tools = [scan_user_folders_across_drives]

# Router
def router(state:State):
    if state["agent_choice"] == "file":
        return "file"
    return "process"

# The nodes

# orchestor
def orchestor(state: State):
    orc_llm = ChatGroq(model="openai/gpt-oss-20b", temperature=0)
    response = orc_llm.invoke(state["user_query"]) # response in json inside string
    # remove ```json and ```
    clean = response.content.strip().removeprefix("```json").removesuffix("```").strip()
    data = json.loads(clean)
    print(data["processed_query"])
    return {"agent_choice": data["agent"], "processed_q_data": [HumanMessage(content=data["processed_query"])]}


# File managing nodes
def file_manager(state: State):
    file_llm = ChatGroq(model="openai/gpt-oss-20b", temperature=0)
    llm_tool = file_llm.bind_tools(tools)
    response = llm_tool.invoke([
        SystemMessage(
            content="""You are a file organization assistant for Windows 10 or later systems.

            Your responsibility is to help the user by recommending best file organizational practices in order to reduce clutter in their file system
            by analyzing file structure and identifying organizational issues.
            
            IMPORTANT CONSTRAINTS:
            - You do NOT modify, move, delete, or rename any files or folders.
            - You ONLY analyze file structure and report issues.
            - You do NOT reason about issues during scanning.
            - You use tools exactly as instructed.
            
            AVAILABLE ACTIONS:
            1. When the user provides a query, first you will use the scan tool to search for all user folders in the system.
            
            2. You will 
            
            3. 
            
            GOAL:
            Your goal is to produce accurate, deterministic analysis of file organization
            and resolve the clutter and file organizational problems present in user system.
            """),
        *state["processed_q_data"] # * means expanding the list
    ])
    print("agent responded...")
    return {"processed_q_data":response}

def file_tools_node(state: State):
    """Your agent's hands - executes the chosen tools."""
    tool_registry = {tool.name: tool for tool in tools}# {"Duck_search": duckduckgoToolObject}

    last_message = state["processed_q_data"][-1]# consists of the ai message
    tool_messages = []

    # Execute each tool the agent requested
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
        # print(tool_messages)
    print("agent successfully called tools...\n")

    return {"processed_q_data": tool_messages}





def process_manager(state: State):
    pass


# Build the complete workflow
def create_agent():
    graph = StateGraph(State)
    # Add the nodes
    graph.add_node("file_node", file_manager)
    graph.add_node("tool_node", file_tools_node)
    graph.add_node("orchestor", orchestor)
    # Set the starting point
    graph.set_entry_point("orchestor")
    # Add the flow logic
    graph.add_conditional_edges("orchestor", router, {"file": "file_node", "process": END})
    graph.add_edge("file_node", "tool_node")
    graph.add_edge("tool_node", END)# After using tools, go back to thinking
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
        HumanMessage(content="I want the scanning of my C:\\Users drive")
    ]
}
# final output
result = agent.invoke(initial_state)
print(result["processed_q_data"][-1].content)