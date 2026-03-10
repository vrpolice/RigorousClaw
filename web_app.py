import os
import json
import shutil
from fastapi import FastAPI, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from config import load_config, save_config
from agent.graph import app as agent_app
from agent.graph import tika_parse  # Import tika_parse directly for strict file reading
from shared_state import (
    web_chat_history,
    append_chat,
    append_conversation_message,
    get_langchain_messages,
    clear_history,
)

from langchain_core.messages import HumanMessage, AIMessage

app = FastAPI(title="RigorousClaw Agent Dashboard")

# Ensure directories exist
os.makedirs("static", exist_ok=True)
os.makedirs("templates", exist_ok=True)
os.makedirs("uploads", exist_ok=True)

UPLOAD_DIR = os.path.abspath("uploads")

# We will mount static files for CSS/JS
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

class ChatRequest(BaseModel):
    message: str

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Render the unified chat interface."""
    config = load_config()
    return templates.TemplateResponse("index.html", {
        "request": request,
        "chat_history": web_chat_history,
        "agent_name": config["agent"]["name"]
    })

@app.get("/history")
async def get_history():
    """API endpoint to retrieve existing chat history for the frontend."""
    return {"history": web_chat_history}

@app.post("/clear_history")
async def clear_chat_history():
    """API endpoint to clear all chat history."""
    clear_history()
    return {"status": "ok"}

@app.post("/chat")
async def chat_api(chat_req: ChatRequest):
    """API endpoint to handle chat messages from the web UI."""
    user_msg = chat_req.message
    if not user_msg:
        return {"response": "Please enter a message."}
        
    append_chat("user", user_msg)
    append_conversation_message("human", user_msg)
    
    # Rebuild LangChain message objects from persistent storage
    conversation_messages = get_langchain_messages()
    
    # Pass the FULL conversation history (not just the last message) to the agent
    agent_config = {"configurable": {"thread_id": "web_ui_session"}}
    
    try:
        result = agent_app.invoke({"messages": conversation_messages}, config=agent_config)
        final_message = result["messages"][-1]
        response_text = final_message.content if hasattr(final_message, "content") else str(final_message)
        
        # Persist the agent's response
        append_conversation_message("ai", response_text)
            
    except Exception as e:
        response_text = f"Error: {e}"
        
    append_chat("agent", response_text)
    
    return {"response": response_text}

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Handle file uploads. STRICTLY reads the file with tika_parse first, then sends the content to the agent."""
    if not file.filename:
        return JSONResponse({"error": "No file provided."}, status_code=400)
    
    # Save the uploaded file
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    try:
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
    except Exception as e:
        return JSONResponse({"error": f"Failed to save file: {e}"}, status_code=500)
    
    # STRICT ROUTING: Directly call tika_parse to read the file, don't let the AI decide
    try:
        file_content = tika_parse.invoke({"file_path": file_path})
    except Exception as e:
        file_content = f"(Failed to extract text from file: {e})"
    
    # Truncate very long files to avoid token overflow
    max_chars = 8000
    if len(file_content) > max_chars:
        file_content = file_content[:max_chars] + f"\n\n... [Content truncated, showing first {max_chars} characters of {len(file_content)} total]"
    
    # Send the EXTRACTED content (not just the path) to the agent
    user_msg = (
        f"The user uploaded a file named '{file.filename}'.\n"
        f"Here is the extracted text content of the file:\n"
        f"---FILE CONTENT START---\n{file_content}\n---FILE CONTENT END---\n\n"
        f"Please summarize or analyze this document."
    )
    
    append_chat("user", f"📎 Uploaded: {file.filename}")
    append_conversation_message("human", user_msg)
    
    # Rebuild LangChain message objects from persistent storage
    conversation_messages = get_langchain_messages()
    
    agent_config = {"configurable": {"thread_id": "web_ui_session"}}
    
    try:
        result = agent_app.invoke({"messages": conversation_messages}, config=agent_config)
        final_message = result["messages"][-1]
        response_text = final_message.content if hasattr(final_message, "content") else str(final_message)
        append_conversation_message("ai", response_text)
    except Exception as e:
        response_text = f"Error processing file: {e}"
    
    append_chat("agent", response_text)
    
    return {"filename": file.filename, "response": response_text}

@app.get("/settings", response_class=HTMLResponse)
async def settings_page(request: Request):
    """Render the configuration settings page."""
    config = load_config()
    return templates.TemplateResponse("settings.html", {
        "request": request,
        "config": config
    })

@app.post("/settings/save")
async def save_settings(request: Request):
    """Handle form submission from the settings page."""
    form_data = await request.form()
    
    config = load_config()
    
    # LLM Settings
    config["llm"]["openai_api_key"] = form_data.get("openai_api_key", "")
    config["llm"]["openai_base_url"] = form_data.get("openai_base_url", "")
    config["llm"]["model_name"] = form_data.get("model_name", "gpt-4o")
    
    # Agent Persona
    config["agent"]["name"] = form_data.get("agent_name", "Assistant")
    config["agent"]["role"] = form_data.get("agent_role", "")
    config["agent"]["style"] = form_data.get("agent_style", "")
    config["agent"]["system_prompt"] = form_data.get("system_prompt", "")
    
    # User Profile
    config["user"]["name"] = form_data.get("user_name", "")
    
    # Skills API Keys
    config["skills"]["tavily_api_key"] = form_data.get("tavily_api_key", "")
    config["skills"]["jina_api_key"] = form_data.get("jina_api_key", "")
    
    # Telegram
    config["telegram"]["bot_token"] = form_data.get("telegram_bot_token", "")
    
    save_config(config)
    
    # Redirect back to settings with a success flag (in a real app we'd use flash messages)
    return RedirectResponse(url="/settings?saved=true", status_code=303)

if __name__ == "__main__":
    import uvicorn
    # Start the FastAPI server
    print("Starting Web Dashboard on http://127.0.0.1:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)
