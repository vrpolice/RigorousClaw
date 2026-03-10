import json
import os
from typing import Dict, Any

CONFIG_FILE = "config.json"

DEFAULT_CONFIG = {
    "llm": {
        "openai_api_key": "",
        "openai_base_url": "",
        "model_name": "gpt-4o"
    },
    "skills": {
        "tavily_api_key": "",
        "jina_api_key": "",
        "crawl4ai_api_token": ""
    },
    "agent": {
        "name": "ClawOnline Assistant",
        "role": "Rigorous Agentic Assistant",
        "style": "Professional, concise, and disciplined",
        "system_prompt": "You are a rigorous, highly-disciplined Agentic Assistant. You DO NOT guess or hallucinate code or facts. ALWAYS prefer using a tool if appropriate rather than free-text answering. When a user asks you to read a link, ALWAYS use jina_reader or robust_web_crawler. When asked to search, ALWAYS use tavily_search."
    },
    "user": {
        "name": "Charles",
        "preferences": ""
    },
    "telegram": {
        "bot_token": ""
    }
}

def load_config() -> Dict[str, Any]:
    """Load configuration from config.json and fallback to .env variables if empty."""
    from dotenv import load_dotenv
    load_dotenv()
    
    config_data = DEFAULT_CONFIG.copy()
    
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                config_data = _merge_configs(DEFAULT_CONFIG, data)
        except Exception as e:
            print(f"Error loading config.json: {e}")
            
    # Sync from environment variables (.env) if the JSON values are empty
    llm = config_data.get("llm", {})
    if not llm.get("openai_api_key"):
        env_key = os.getenv("OPENAI_API_KEY")
        if env_key and env_key != "your_openai_api_key_here":
            llm["openai_api_key"] = env_key
            
    if not llm.get("openai_base_url"):
        llm["openai_base_url"] = os.getenv("OPENAI_BASE_URL", "")
        
    if llm.get("model_name") == "gpt-4o": # default
        env_model = os.getenv("MODEL_NAME")
        if env_model:
            llm["model_name"] = env_model

    skills = config_data.get("skills", {})
    if not skills.get("tavily_api_key"):
        env_key = os.getenv("TAVILY_API_KEY")
        if env_key and env_key != "your_tavily_api_key_here":
            skills["tavily_api_key"] = env_key
            
    if not skills.get("jina_api_key"):
        env_key = os.getenv("JINA_API_KEY")
        if env_key and env_key != "your_jina_api_key_here":
            skills["jina_api_key"] = env_key
            
    telegram = config_data.get("telegram", {})
    if not telegram.get("bot_token"):
        env_token = os.getenv("TELEGRAM_BOT_TOKEN")
        if env_token and env_token != "your_telegram_bot_token_here":
            telegram["bot_token"] = env_token
            
    return config_data

def set_env_variable(key: str, value: str):
    """Utility to update or add a variable to the .env file."""
    env_file = ".env"
    lines = []
    found = False
    
    if value is None:
        value = ""
        
    if os.path.exists(env_file):
        with open(env_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
            
    # Update existing line
    for i, line in enumerate(lines):
        if line.strip().startswith(f"{key}="):
            lines[i] = f"{key}={value}\n"
            found = True
            break
            
    # Add new line if not found
    if not found:
        # Add a newline if the file doesn't end with one
        if lines and not lines[-1].endswith("\n"):
            lines[-1] += "\n"
        lines.append(f"{key}={value}\n")
        
    with open(env_file, "w", encoding="utf-8") as f:
        f.writelines(lines)
        
    # Also update the current process memory immediately
    os.environ[key] = value

def save_config(config: Dict[str, Any]) -> bool:
    """Save configuration to config.json and sync key fields to .env."""
    try:
        # Save to JSON
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
            
        # Sync to .env
        llm = config.get("llm", {})
        if llm.get("openai_api_key"): set_env_variable("OPENAI_API_KEY", llm["openai_api_key"])
        if llm.get("openai_base_url"): set_env_variable("OPENAI_BASE_URL", llm["openai_base_url"])
        if llm.get("model_name"): set_env_variable("MODEL_NAME", llm["model_name"])
        
        skills = config.get("skills", {})
        if skills.get("tavily_api_key"): set_env_variable("TAVILY_API_KEY", skills["tavily_api_key"])
        if skills.get("jina_api_key"): set_env_variable("JINA_API_KEY", skills["jina_api_key"])
        
        telegram = config.get("telegram", {})
        if telegram.get("bot_token"): set_env_variable("TELEGRAM_BOT_TOKEN", telegram["bot_token"])
        
        return True
    except Exception as e:
        print(f"Error saving config: {e}")
        return False

def _merge_configs(default: dict, user: dict) -> dict:
    result = default.copy()
    for key, value in user.items():
        if isinstance(value, dict) and key in result:
            result[key] = _merge_configs(result[key], value)
        else:
            result[key] = value
    return result
