from langchain_groq import ChatGroq
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel
from typing_extensions import TypedDict
from tools.file_system_tool import file_system_access_tool
from langgraph.graph import StateGraph, START, END

load_dotenv()

class state(BaseModel):
    output : str = ""


def fileManager(State: state):
    llm = ChatGroq(model="openai/gpt-oss-20b", temperature=0)
    llm_with_tool = llm.bind_tools([file_system_access_tool])
    #LangChain’s .invoke() doesn’t auto-execute tools. it returns message object(refer Agent_prac)
    response = llm_with_tool.invoke('''scan my X: drive folder and provide the name of folders present there, scan out of
     this project folder
     ''')

    # If it requested a tool call, run the tool manually
    if hasattr(response, "tool_calls") and response.tool_calls:
        tool_call = response.tool_calls[0]
        tool_name = tool_call["name"]
        args = tool_call["args"]

        print(f"🔧 Tool called: {tool_name} with {args}")
        tool_result = file_system_access_tool.func(**args)

        # Step 3: Send tool result back to LLM for reflection
        response = llm_with_tool.invoke(
            f"Tool result: {tool_result}\nNow explain what you did within 100 words."
        )

    return {"output":response.content}











