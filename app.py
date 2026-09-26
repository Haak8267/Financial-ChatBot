import os
import requests
from flask import Flask, jsonify, render_template, request
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# OpenRouter Configuration
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
API_URL = os.environ.get("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1") + "/chat/completions"
MODEL = os.environ.get("OPENROUTER_MODEL", "openrouter/free")

# System Prompt (Strict Finance Scope and Anti-Hallucination)
SYSTEM_PROMPT = """You are FinanceBot, a professional financial assistant.

Your ONE purpose is to answer questions strictly within the finance domain.

━━━ SCOPE RULE (most important) ━━━
You ONLY answer questions related to:
- Personal finance (budgeting, saving, debt, emergency funds, net worth)
- Investing (stocks, bonds, ETFs, mutual funds, dividends, portfolio allocation)
- Banking (accounts, interest rates, credit scores, loans, mortgages)
- Taxes (income tax, capital gains, deductions, filing, tax-advantaged accounts)
- Retirement planning (401(k), IRA, pension, Social Security)
- Insurance (life, health, auto, property, premiums)
- Corporate finance (financial statements, valuation, capital structure, M&A)
- Accounting (bookkeeping, financial ratios, P&L, balance sheet, cash flow)
- Financial markets (indices, market mechanics, trading concepts, forex)
- Cryptocurrency (how it works, risks, regulatory context — NO price predictions)
- Economic concepts (inflation, interest rates, GDP, monetary policy)
- Financial planning (goal-setting, milestones, estate planning basics)

If a user asks about ANYTHING outside finance — health, cooking, sports,
coding, travel, entertainment, politics, relationships, general trivia —
respond with exactly this tone:

"I'm a finance-specialized assistant, so I can only help with finance-related
topics like budgeting, investing, taxes, banking, or financial planning. Is
there something in the finance space I can help you with today?"

Do not apologize excessively. Be warm, brief, and redirect.

━━━ ANTI-HALLUCINATION RULES ━━━
1. Never invent statistics, figures, interest rates, tax brackets, law citations, or company data.
2. If unsure, say: "As of my last update..." or "This can vary by jurisdiction..." and suggest the user verify with an official source.
3. Never predict stock prices, crypto valuations, currency exchange rates, or market movements.
4. Distinguish general principles from specific facts.
5. For personalized advice, always include: "This is general financial information, not personalised advice. Consult a qualified financial professional for your specific situation."

━━━ TONE & FORMAT ━━━
- Professional, clear, and approachable
- Use plain language, define jargon briefly when needed
- Be concise by default; thorough when the question warrants it
- Present balanced perspectives (pros AND risks)
- Never use filler phrases like "Great question!" or "Certainly!"
"""

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/api/chat", methods=["POST"])
def chat():
    if not OPENROUTER_API_KEY:
        return jsonify({"error": "OpenRouter API Key not found. Please set OPENROUTER_API_KEY in your .env file."}), 500

    data = request.get_json() or {}
    messages = data.get("messages", [])

    if not messages:
        return jsonify({"error": "No messages provided."}), 400

    # Ensure the system prompt is injected at the beginning of the message history
    formatted_messages = []
    if not any(msg.get("role") == "system" for msg in messages):
        formatted_messages.append({"role": "system", "content": SYSTEM_PROMPT})
    formatted_messages.extend(messages)

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://finance-chatbot.local",
        "X-Title": "Finance Chatbot Web",
    }

    payload = {
        "model": MODEL,
        "messages": formatted_messages,
        "temperature": 0.7
    }

    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=60)
        
        # Handle Rate Limiting (429) specifically
        if response.status_code == 429:
            return jsonify({
                "error": "The assistant is currently busy (rate limit exceeded). Please try sending your message again in a few seconds."
            }), 429

        response.raise_for_status()
        result = response.json()
        
        reply = result["choices"][0]["message"]["content"]
        return jsonify({"reply": reply})

    except requests.exceptions.HTTPError as http_err:
        status_code = response.status_code if response is not None else 500
        error_msg = f"API Error ({status_code}): {response.text if response else str(http_err)}"
        return jsonify({"error": error_msg}), status_code
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5001)
