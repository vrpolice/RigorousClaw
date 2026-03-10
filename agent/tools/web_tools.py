import os
import subprocess
from langchain_core.tools import tool
from tavily import TavilyClient
import requests

@tool
def tavily_search(query: str) -> str:
    """
    Search the web for current information, news, or general knowledge using Tavily.
    Use this strictly when the user asks for external information that is not in memory.
    """
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key or api_key == "your_tavily_api_key_here":
        return "Error: TAVILY_API_KEY is missing."
    
    client = TavilyClient(api_key=api_key)
    try:
        response = client.search(query=query, search_depth="advanced")
        return str(response)
    except Exception as e:
        return f"Error during search: {e}"

@tool
def jina_reader(url: str) -> str:
    """
    Read the contents of a specific web URL and convert it to clean Markdown text.
    Use this when the user explicitly asks to read a specific website link.
    """
    api_key = os.getenv("JINA_API_KEY")
    headers = {"Authorization": f"Bearer {api_key}"} if api_key and api_key != "your_jina_api_key_here" else {}
    
    try:
        # Jina Reader API takes the target URL appended to its base URL
        jina_url = f"https://r.jina.ai/{url}"
        response = requests.get(jina_url, headers=headers, timeout=30)
        response.raise_for_status()
        return response.text
    except Exception as e:
        return f"Error reading URL {url}: {e}"

@tool
def system_cli_command(command: str) -> str:
    """
    Execute a system command line operation (like checking system status, running a script, or using an AI CLI like 'gemini' or 'claude').
    WARNING: Use carefully. Only execute commands that are safe and relevant to the user's request.
    """
    try:
        # Run the command and capture output
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=60
        )
        output = result.stdout
        if result.stderr:
            output += f"\nErrors:\n{result.stderr}"
        return output if output else "Command executed successfully with no output."
    except subprocess.TimeoutExpired:
        return f"Error: Command '{command}' timed out."
    except Exception as e:
        return f"Error executing command: {e}"
