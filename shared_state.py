# shared_state.py
# A module to hold global chat state with JSON file persistence.
# Chat history and conversation messages survive both page refresh AND server restart.

import os
import json

HISTORY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chat_history.json")

def _load_from_disk():
    """Load chat history from disk if it exists."""
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data.get("web_chat_history", []), data.get("conversation_messages", [])
        except (json.JSONDecodeError, IOError):
            return [], []
    return [], []

def _save_to_disk(web_history, conv_messages):
    """Persist chat history to disk as JSON."""
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump({
                "web_chat_history": web_history,
                "conversation_messages": conv_messages
            }, f, ensure_ascii=False, indent=2)
    except IOError:
        pass

# Load existing history on module import (server startup)
_saved_web, _saved_conv = _load_from_disk()
web_chat_history = _saved_web
# conversation_messages_raw stores dicts like {"role": "human", "content": "..."}
conversation_messages_raw = _saved_conv

def append_chat(role, content):
    """Append a message to web_chat_history and persist."""
    web_chat_history.append({"role": role, "content": content})
    _save_to_disk(web_chat_history, conversation_messages_raw)

def append_conversation_message(role, content):
    """Append a LangChain-compatible message record and persist."""
    conversation_messages_raw.append({"role": role, "content": content})
    # Trim to last 40 messages (20 turns)
    if len(conversation_messages_raw) > 40:
        conversation_messages_raw[:] = conversation_messages_raw[-40:]
    _save_to_disk(web_chat_history, conversation_messages_raw)

def get_langchain_messages():
    """Convert stored raw messages back to LangChain message objects."""
    from langchain_core.messages import HumanMessage, AIMessage
    msgs = []
    for m in conversation_messages_raw:
        if m["role"] == "human":
            msgs.append(HumanMessage(content=m["content"]))
        elif m["role"] == "ai":
            msgs.append(AIMessage(content=m["content"]))
    return msgs

def clear_history():
    """Clear all chat history (both in-memory and on disk)."""
    web_chat_history.clear()
    conversation_messages_raw.clear()
    _save_to_disk(web_chat_history, conversation_messages_raw)
