# Finance Chatbot & Assistant

A Python-based command-line chatbot and advanced streaming assistant designed to answer questions strictly within the finance domain. This project is configured to use OpenRouter to access modern LLMs.

## Project Structure

- `main.py`: A standard command-line finance chatbot with retry logic, rate limit handling, and conversation history.
- `financebot.py`: An advanced command-line assistant featuring streaming responses, system commands, and conversation persistence (saving/loading chat history).
- `pyproject.toml`: Project configuration specifying python version requirements and dependencies.
- `.env.example`: Configuration template for API keys and options.
- `.gitignore`: Configured to keep virtual environments, secrets (`.env`), and cache files out of your Git repository.

## Setup Instructions

### 1. Prerequisites
Ensure you have Python 3.9 or higher installed.

### 2. Environment Configuration
Create a `.env` file in the root directory by copying the example template:
```bash
cp .env.example .env
```
Open the `.env` file and fill in your OpenRouter API key:
```env
OPENROUTER_API_KEY=your_actual_api_key_here
```

### 3. Dependency Installation

You can install dependencies in one of two ways:

#### Option A: Using `pip` (Standard)
1. Create a virtual environment:
   ```bash
   python -m venv .venv
   ```
2. Activate the virtual environment:
   - **macOS / Linux:**
     ```bash
     source .venv/bin/activate
     ```
   - **Windows:**
     ```cmd
     .venv\Scripts\activate
     ```
3. Install dependencies:
   ```bash
   pip install -r <(pip compile pyproject.toml)  # or directly from requirements:
   pip install httpx python-dotenv requests flask anthropic
   ```

#### Option B: Using `uv` (Fast)
If you have `uv` installed:
```bash
uv venv
source .venv/bin/activate
uv pip install -r pyproject.toml
# Or run scripts directly:
uv run main.py
```

---

## How to Run

### 1. Standard Chatbot (`main.py`)
Run the simple chat bot:
```bash
python main.py
```
This chatbot handles requests and keeps a memory of the current session. Type `exit` or `quit` to exit.

### 2. Advanced Streaming Assistant (`financebot.py`)
Run the streaming chatbot with command integrations:
```bash
python financebot.py
```
This bot streams the output token by token and supports special commands:
* `/save <name>` - Save the current conversation history (persisted to `~/.financebot_history/`).
* `/load <name>` - Load a previously saved conversation history.
* `/history` - List all saved conversation files.
* `/reset` - Start a fresh conversation session.
* `/exit` - Exit the chatbot.

---

## Finance Bot Scope
The assistant is strictly constrained to answer queries within the finance domain. This includes:
* Personal Finance & Budgeting
* Investing & Portfolio Allocation
* Banking & Credit
* Taxes
* Retirement & Estate Planning
* Insurance
* Corporate Finance & Accounting
* Economic Concepts
* Cryptocurrency Concepts (No price predictions)

For any off-topic queries, the bot will politely decline and redirect the user back to finance topics.
