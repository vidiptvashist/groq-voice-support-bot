from langchain.tools import tool
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_tavily import TavilySearch
import weatherapi
from weatherapi.rest import ApiException
from dotenv import load_dotenv
import os
load_dotenv()

from typing import Annotated

from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain.chat_models import init_chat_model

from load_variables import llm

class State(TypedDict):
    # Messages have the type "list". The `add_messages` function
    # in the annotation defines how this state key should be updated
    # (in this case, it appends messages to the list, rather than overwriting them)
    messages: Annotated[list, add_messages]


web_search_tool = TavilySearch(max_results=4)



# Configure API key authorization: ApiKeyAuth
configuration = weatherapi.Configuration()
configuration.api_key['key'] = os.getenv("WEATHER_API_KEY")

@tool
def weather_tool(q: str)-> str:
    """
    Function to get the current weather for a given location.
    :param q: Location query (city name, zip code, etc.)
    :return: Weather data
    """
    # Create an instance of the API class
    api_instance = weatherapi.APIsApi(weatherapi.ApiClient(configuration))

    try:
        # Realtime API
        api_response = api_instance.realtime_weather(q)
        return str(api_response)
    except ApiException as e:
        return f"Exception when calling APIsApi->realtime_weather: {e}\n"
    
from langchain.tools import tool
import subprocess
import platform
import os
import shlex

ALLOWED_COMMANDS = ["ls", "dir", "mkdir", "rm", "del", "echo", "touch", "clear"]

@tool
def run_command_tool(command: str) -> str:
    """
    Safely executes a shell command for basic file operations like
    listing, creating, removing, or clearing files. The command is 
    executed inside BASE_DIR for safety.

    Supported operations: ls, dir, mkdir, rm, del, echo, clear

    Args:
        command (str): The shell command to run (e.g. "ls", "mkdir test").

    Environment:
        BASE_DIR: Optional environment variable to set base execution folder.

    Returns:
        str: Output or error message.
    """
    BASE_DIR = os.getenv("BASE_DIR", ".")
    BASE_DIR = os.path.abspath(BASE_DIR)

    # Normalize & tokenize command
    command_tokens = shlex.split(command)
    if not command_tokens:
        return "Error: Empty command."

    base_cmd = command_tokens[0].lower()
    if base_cmd not in ALLOWED_COMMANDS:
        return f"Error: Command '{base_cmd}' is not allowed."

    # For basic compatibility
    if platform.system() == "Windows":
        command = command.replace("ls", "dir").replace("clear", "cls")
        command = command.replace("rm", "del")

    try:
        # Execute inside BASE_DIR
        result = subprocess.run(
            command,
            shell=True,
            cwd=BASE_DIR,
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            return result.stdout.strip() or "(No output)"
        else:
            return f"Error: {result.stderr.strip()}"
    except Exception as e:
        return f"Exception: {str(e)}"


@tool
def create_file_tool(file_path: str, content: str) -> str:
    """
    Creates a new file at the given path with the specified content.
    
    Args:
        file_path (str): Full path where the file should be created.
        content (str): Text content to write into the file.

    Returns:
        str: Success message or error.
    """
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"File created successfully at {file_path}"
    except Exception as e:
        return f"Failed to create file: {str(e)}"
    

from langchain.tools import tool

@tool
def read_file_tool(file_path: str) -> str:
    """
    Reads the content of a file at the given path.

    Args:
        file_path (str): Path to the file.

    Returns:
        str: Content of the file or an error message.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return content
    except FileNotFoundError:
        return f"Error: File not found at {file_path}"
    except Exception as e:
        return f"Error reading file: {str(e)}"



tools = [web_search_tool , weather_tool , run_command_tool,create_file_tool, read_file_tool]

llm_with_tools = llm.bind_tools(tools)
tool_node = ToolNode(tools=tools)

def chatbot(state: State):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}


from langgraph.checkpoint.memory import MemorySaver

memory = MemorySaver()



graph_builder = StateGraph(State)
# graph_builder.add_node("rewrite_query_node" , rewrite_query_node)
graph_builder.add_node("chatbot", chatbot)
graph_builder.add_node("tools", tool_node)

# graph_builder.add_edge(START, "rewrite_query_node")
# graph_builder.add_edge("rewrite_query_node", "chatbot")

graph_builder.add_edge(START, "chatbot")
graph_builder.add_conditional_edges(
    "chatbot",
    tools_condition,
)
graph_builder.add_edge("tools", "chatbot")


graph = graph_builder.compile(checkpointer=memory)
# display(Image(graph.get_graph().draw_mermaid_png()))


def get_langgraph_response(user_number, user_input):
    config = {"configurable": {"thread_id": str(user_number)}}
    user_input = str(user_input).strip()

    if not user_input:
        return "Empty input not allowed."

    print("User:", user_input)
    final_response = None

    try:
        for events in graph.stream(
            {"messages": [{"role": "user", "content": user_input}]},
            config=config,
        ):
            print("[Events]:", events)
            for value in events.values():
                if value["messages"] and value["messages"][-1].content:
                    final_response = value["messages"][-1].content

        return final_response or "No response received."
    except Exception as e:
        print("❌ Error:", e)
        return "An error occurred."