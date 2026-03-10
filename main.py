import os
import warnings
from dotenv import load_dotenv

# Load environment variables FIRST, before importing anything that needs them (like ChatOpenAI in agent.graph)
load_dotenv()

# Suppress harmless requests dependency warnings caused by system-level installed packages
from requests.packages.urllib3.exceptions import InsecureRequestWarning
warnings.filterwarnings("ignore", category=UserWarning, module='requests')
try:
    from requests.exceptions import RequestsDependencyWarning
    warnings.filterwarnings("ignore", category=RequestsDependencyWarning)
except ImportError:
    pass

from agent.graph import app as agent_app

def main():
    # We must have at least an OpenAI key to run the router
    if not os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY") == "your_openai_api_key_here":
        print("Error: OPENAI_API_KEY is not set in .env")
        print("Please configure your .env file before running.")
        return

    print("RigorousClaw Agentic Assistant (CLI Mode)")
    print("Type 'exit' or 'quit' to quit.")
    print("-" * 50)

    # Use a fixed thread ID for the terminal session to maintain memory
    config = {"configurable": {"thread_id": "cli_session_1"}}

    while True:
        try:
            user_input = input("\nYou: ")
            if user_input.lower() in ["exit", "quit"]:
                print("Goodbye!")
                break
            if not user_input.strip():
                continue
                
            print("Agent is thinking (and potentially using tools)...")
            
            # Invoke the LangGraph workflow
            result = agent_app.invoke({"messages": [("user", user_input)]}, config=config)
            
            # Print the final message
            final_message = result["messages"][-1]
            content = final_message.content if hasattr(final_message, "content") else str(final_message)
            print(f"\nAgent: {content}")
            
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"\nError: {e}")

if __name__ == "__main__":
    main()
