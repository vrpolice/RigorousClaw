import os
import asyncio
import logging
import warnings
from dotenv import load_dotenv

from config import load_config
from shared_state import append_chat

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

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

load_dotenv()
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /start is issued."""
    await update.message.reply_text('Hello! I am your rigorous Agentic Assistant. How can I help you today?')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text messages by passing them to the LangGraph agent."""
    user_text = update.message.text
    chat_id = update.message.chat_id
    
    # Placeholder for agent invocation
    # In the future, we will invoke the graph here and stream or send the final response
    await update.message.reply_text("Working on it...")
    
    try:
        # Save to shared history before sending to agent
        append_chat("user", f"[Telegram] {user_text}")
        
        # Invoke the LangGraph agent
        config_params = {"configurable": {"thread_id": str(chat_id)}}
        result = agent_app.invoke({"messages": [("user", user_text)]}, config=config_params)
        
        # Extract response
        final_message = result["messages"][-1]
        final_response = final_message.content if hasattr(final_message, "content") else str(final_message)
        
        # Save Agent response to shared history
        append_chat("agent", f"[Telegram] {final_response}")
        
        await update.message.reply_text(final_response)
    except Exception as e:
        logging.error(f"Error processing message: {e}")
        append_chat("agent", f"[Telegram Error] {str(e)}")
        await update.message.reply_text(f"Sorry, I encountered an error while processing your request: {str(e)}")

def main():
    """Start the bot."""
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token or token == "your_telegram_bot_token_here":
        print("Error: TELEGRAM_BOT_TOKEN is not set in .env")
        return

    application = ApplicationBuilder().token(token).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Run the bot until the user presses Ctrl-C
    print("Starting Telegram Bot...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
