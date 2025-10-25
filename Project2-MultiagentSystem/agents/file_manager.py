from langchain_groq import ChatGroq
from langchain.agents import create_tool_calling_agent, AgentExecutor
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from tools.file_system_tool import file_system_access_tool

load_dotenv()

llm = ChatGroq(model="openai/gpt-oss-20b", temperature=0)
tools = [file_system_access_tool]
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
            you are smart digital maid who is obedient to her master and fullfils anything he asks without performing extra chores.
            """,
        ),
        ("human", "{query}"),
        ]
)

'''agent runtime (like AgentExecutor or create_react_agent) is needed to
 read the model’s “tool call” output and actually runs the tool’s function.'''
agent = create_tool_calling_agent(
    llm=llm,
    prompt=prompt,
    tools=tools
)

agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)# verbose used to see internals of agent

result = agent_executor.invoke({
    "query": '''what kind of file is "MedicalCertificate" file and where is it present in X drive'''
})

print(result["output"])

