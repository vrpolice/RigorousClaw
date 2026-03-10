# RigorousClaw — 严格执行的智能体助手框架

<p align="center">
  <strong>🧠 Minimize AI improvisation. Maximize deterministic execution.</strong>
</p>

<p align="center">
  <a href="#english">English</a> · <a href="#中文">中文</a>
</p>

---

<a name="english"></a>

## 🌐 English

### Background & Motivation

When building AI-powered assistants with tool-calling capabilities, **a critical real-world problem emerges**: swapping from one LLM backend to another (e.g., GPT-4o → DeepSeek → Qwen → Llama) causes **dramatic, unpredictable differences** in agent behavior. The same prompt, the same tools, the same workflow — yet the agent may:

- Call the wrong tool, or no tool at all
- Hallucinate answers instead of using a search tool
- Creatively "reinterpret" instructions instead of following them literally
- Produce wildly inconsistent output formats

This happens because most agent frameworks let the AI model **freely decide** the entire workflow — which tools to use, when to use them, and how to interpret the results. The AI's "creativity" becomes a liability when you need **reliable, repeatable execution**.

### What RigorousClaw Does Differently

**RigorousClaw** is built around one core principle:

> **When AI judgment is NOT needed, follow deterministic logic strictly. When AI judgment IS needed, let the AI shine — but only then.**

| Aspect | Typical Agent | RigorousClaw |
|--------|--------------|--------------|
| File reading | AI decides whether to read the file | **Strict routing**: file is always parsed by `tika_parse` directly, AI only analyzes the result |
| Tool selection | AI freely picks tools | Workflows/skills define which tools to call and in what order |
| Memory recall | AI decides if memory is relevant | **Auto-recall**: relevant memories are always injected into context before AI responds |
| Output consistency | Varies wildly across LLMs | Deterministic steps produce consistent results regardless of LLM backend |

The goal is to build an agent that **works reliably no matter which LLM powers it** — from powerful cloud models to lightweight local ones.

### ⚠️ Project Status

> **This project is in an early proof-of-concept (PoC) stage.** The core architecture and key ideas are implemented, but many capabilities are still under active development. This is a research prototype, not production software. Contributions, ideas, and feedback are welcome!

#### Current Features (Working)
- ✅ LangGraph-based agent workflow with deterministic tool routing
- ✅ Web chat UI with persistent conversation history (survives refresh & restart)
- ✅ Strict file upload handling — documents are always parsed first, then analyzed
- ✅ Auto-recall: relevant long-term memories injected before every AI response
- ✅ Long-term memory via Qdrant vector database (`save_to_memory` / `recall_from_memory`)
- ✅ Built-in skills: Web search (Tavily), URL reading (Jina), web crawling (Crawl4AI), system CLI
- ✅ Configurable agent persona (name, role, style, system prompt)
- ✅ Hot-swappable LLM backend (OpenAI, DeepSeek, SiliconFlow, or any OpenAI-compatible API)
- ✅ Telegram bot integration
- ✅ CLI mode

#### Planned Features (TODO)
- 🔲 Declarative workflow/skill definitions (YAML/JSON-based, no code needed)
- 🔲 MCP (Model Context Protocol) integration
- 🔲 Strict routing engine — fully separate "deterministic steps" from "AI steps"
- 🔲 Streaming responses (SSE/WebSocket)
- 🔲 Multi-user / multi-session support
- 🔲 Better embedding model for memory (replacing hash-based vectors)
- 🔲 Skill/plugin marketplace
- 🔲 Voice input/output
- 🔲 Authentication & access control

### Project Structure

```
RigorousClaw/
├── main.py              # CLI entry point
├── web_app.py           # FastAPI web dashboard & chat API
├── telegram_bot.py      # Telegram bot integration
├── config.py            # Dual config system (config.json + .env)
├── shared_state.py      # Persistent chat history (JSON file-backed)
├── agent/
│   ├── graph.py         # LangGraph agent workflow & tool routing
│   ├── memory.py        # Qdrant-based long-term vector memory
│   └── tools/
│       ├── web_tools.py     # Tavily search, Jina reader, system CLI
│       └── crawler_tools.py # Crawl4AI web crawler
├── templates/
│   ├── index.html       # Chat interface
│   └── settings.html    # Configuration page
├── .env.example         # Environment variable template
└── .gitignore
```

### Quick Start

#### 1. Clone the Repository

```bash
git clone https://github.com/your-username/RigorousClaw.git
cd RigorousClaw
```

#### 2. Create a Virtual Environment

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

#### 3. Install Dependencies

```bash
pip install fastapi uvicorn langchain-openai langgraph langchain-core qdrant-client python-dotenv tavily-python requests crawl4ai nest_asyncio PyPDF2 python-docx openpyxl python-multipart jinja2 python-telegram-bot
```

#### 4. Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` and fill in your API keys:

```env
OPENAI_API_KEY=your_api_key_here
OPENAI_BASE_URL=https://api.deepseek.com/v1   # Optional: for DeepSeek/SiliconFlow
MODEL_NAME=deepseek-chat                        # Optional: default is gpt-4o
TAVILY_API_KEY=your_tavily_key                  # For web search
```

#### 5. Run the Web Dashboard

```bash
python web_app.py
```

Open your browser at **http://127.0.0.1:8000**

#### 6. (Optional) Run CLI Mode

```bash
python main.py
```

#### 7. (Optional) Run Telegram Bot

Set `TELEGRAM_BOT_TOKEN` in `.env`, then:

```bash
python telegram_bot.py
```

### Configuration

You can configure the agent in two ways:

1. **Web Settings Page** — Visit `http://127.0.0.1:8000/settings` to change LLM model, API keys, agent persona, and more. Changes take effect immediately.
2. **`.env` file** — Set environment variables for initial/fallback configuration.

---

<a name="中文"></a>

## 🇨🇳 中文

### 项目背景与动机

在构建具有工具调用能力的 AI 助手时，一个**关键的现实问题**浮出水面：当你把底层 LLM 从一个模型换到另一个模型（例如 GPT-4o → DeepSeek → Qwen → Llama）时，智能体的行为会产生**巨大且不可预测的差异**。相同的提示词、相同的工具、相同的工作流 — 但智能体可能会：

- 调用错误的工具，或根本不调用工具
- 编造答案，而不是使用搜索工具
- 创造性地"重新解读"指令，而非按字面意思执行
- 输出格式在不同模型间差异巨大

这是因为大多数 Agent 框架让 AI 模型**自由决定**整个工作流 — 使用哪些工具、何时使用、如何解读结果。当你需要**可靠、可重复的执行**时，AI 的"创造力"反而成了隐患。

### RigorousClaw 的核心理念

**RigorousClaw** 围绕一个核心原则构建：

> **不需要 AI 判断的环节，严格按照确定性逻辑执行。需要 AI 判断的环节，再让 AI 发挥优势 — 仅此而已。**

| 方面 | 传统 Agent | RigorousClaw |
|------|-----------|--------------|
| 文件读取 | AI 决定是否读取文件 | **严格路由**：文件始终由 `tika_parse` 直接解析，AI 只负责分析结果 |
| 工具选择 | AI 自由挑选工具 | 工作流/技能定义调用哪些工具以及调用顺序 |
| 记忆回调 | AI 决定是否需要记忆 | **自动回调**：相关记忆在 AI 响应前始终注入上下文 |
| 输出一致性 | 不同 LLM 差异巨大 | 确定性步骤保证一致的结果，无论底层 LLM 是什么 |

目标是构建一个**无论由哪个 LLM 驱动都能可靠工作的智能体** — 从强大的云模型到轻量的本地模型。

### ⚠️ 项目状态

> **本项目目前处于早期概念验证（PoC）阶段。** 核心架构和关键思路已经实现，但许多能力仍在积极开发中。这是一个研究原型，而非生产级软件。欢迎提出建议、反馈和贡献！

#### 已实现功能
- ✅ 基于 LangGraph 的 Agent 工作流与确定性工具路由
- ✅ Web 聊天界面，对话历史持久化（刷新页面和重启服务后自动恢复）
- ✅ 严格的文件上传处理 — 文档始终先解析，再分析
- ✅ 自动记忆回调：每次 AI 响应前自动注入相关长期记忆
- ✅ 基于 Qdrant 向量数据库的长期记忆（`save_to_memory` / `recall_from_memory`）
- ✅ 内置技能：网页搜索（Tavily）、URL 读取（Jina）、网页爬取（Crawl4AI）、系统命令
- ✅ 可配置的 Agent 人设（名称、角色、风格、系统提示词）
- ✅ 热切换 LLM 后端（OpenAI、DeepSeek、SiliconFlow 或任何兼容 OpenAI 接口的模型）
- ✅ Telegram Bot 集成
- ✅ 命令行 CLI 模式

#### 待开发功能
- 🔲 声明式工作流/技能定义（基于 YAML/JSON，无需编码）
- 🔲 MCP（Model Context Protocol）集成
- 🔲 严格路由引擎 — 完全分离"确定性步骤"和"AI 步骤"
- 🔲 流式响应（SSE/WebSocket）
- 🔲 多用户 / 多会话支持
- 🔲 更好的嵌入模型（替换当前基于哈希的向量方案）
- 🔲 技能/插件市场
- 🔲 语音输入/输出
- 🔲 身份认证与权限控制

### 快速开始

#### 1. 克隆仓库

```bash
git clone https://github.com/your-username/RigorousClaw.git
cd RigorousClaw
```

#### 2. 创建虚拟环境

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

#### 3. 安装依赖

```bash
pip install fastapi uvicorn langchain-openai langgraph langchain-core qdrant-client python-dotenv tavily-python requests crawl4ai nest_asyncio PyPDF2 python-docx openpyxl python-multipart jinja2 python-telegram-bot
```

#### 4. 配置环境变量

```bash
cp .env.example .env
```

编辑 `.env` 文件，填入你的 API 密钥：

```env
OPENAI_API_KEY=你的API密钥
OPENAI_BASE_URL=https://api.deepseek.com/v1   # 可选：使用 DeepSeek/SiliconFlow
MODEL_NAME=deepseek-chat                        # 可选：默认为 gpt-4o
TAVILY_API_KEY=你的Tavily密钥                    # 用于网页搜索
```

#### 5. 启动 Web 界面

```bash
python web_app.py
```

打开浏览器访问 **http://127.0.0.1:8000**

#### 6.（可选）命令行模式

```bash
python main.py
```

#### 7.（可选）运行 Telegram Bot

在 `.env` 中设置 `TELEGRAM_BOT_TOKEN`，然后：

```bash
python telegram_bot.py
```

### 配置方式

支持两种配置方式：

1. **Web 设置页面** — 访问 `http://127.0.0.1:8000/settings`，可更改 LLM 模型、API 密钥、Agent 人设等，**即时生效**。
2. **`.env` 文件** — 设置环境变量，用于初始化和备选配置。

---

## License

MIT — See [LICENSE](LICENSE) for details.

## Contributing

This project is in its early stages. Issues, suggestions, and pull requests are all welcome!

本项目处于早期阶段，欢迎提交 Issue、建议和 Pull Request！
