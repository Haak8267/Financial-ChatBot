import json
import os
import sys
from datetime import datetime
from pathlib import Path

import httpx
from dotenv import load_dotenv

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
1. Never invent statistics, figures, interest rates, tax brackets, law
   citations, or company data.
2. If unsure, say: "As of my last update..." or "This can vary by jurisdiction..."
   and suggest the user verify with an official source.
3. Never predict stock prices, crypto valuations, currency exchange rates,
   or market movements.
4. Distinguish general principles from specific facts.
5. For personalized advice, always include: "This is general financial
   information, not personalised advice. Consult a qualified financial
   professional for your specific situation."

━━━ TONE & FORMAT ━━━
- Professional, clear, and approachable — like a well-informed colleague
- Use plain language, define jargon briefly when needed
- Be concise by default; thorough when the question warrants it
- Present balanced perspectives (pros AND risks)
- Never use filler phrases like "Great question!" or "Certainly!"
"""

load_dotenv()

HISTORY_DIR = Path.home() / ".financebot_history"
HISTORY_DIR.mkdir(exist_ok=True)

API_URL = "https://openrouter.ai/api/v1/chat/completions"
API_KEY = os.environ.get("OPENROUTER_API_KEY")
MODEL = os.environ.get("OPENROUTER_MODEL", "openai/gpt-4o-mini")


def load_history(name: str) -> list[dict]:
    path = HISTORY_DIR / f"{name}.json"
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return []


def save_history(name: str, messages: list[dict]):
    path = HISTORY_DIR / f"{name}.json"
    with open(path, "w") as f:
        json.dump(messages, f, indent=2)
    print(f"  Saved to {path}")


def list_histories():
    files = sorted(HISTORY_DIR.glob("*.json"))
    if not files:
        print("  No saved conversations found.")
        return
    print("  Saved conversations:")
    for f in files:
        ts = datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
        print(f"    {f.stem}  ({ts})")


def stream_response(messages: list[dict]) -> str:
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": MODEL,
        "messages": messages,
        "stream": True,
        "temperature": 0.7,
    }

    full_content = ""
    with httpx.Client(timeout=120) as client:
        with client.stream("POST", API_URL, json=payload, headers=headers) as resp:
            if resp.status_code != 200:
                print(f"\n  Error {resp.status_code}: {resp.text}")
                return ""

            for line in resp.iter_lines():
                if not line.startswith("data: "):
                    continue
                data_str = line[6:]
                if data_str.strip() == "[DONE]":
                    break
                try:
                    chunk = json.loads(data_str)
                    delta = chunk.get("choices", [{}])[0].get("delta", {})
                    content = delta.get("content", "")
                    if content:
                        print(content, end="", flush=True)
                        full_content += content
                except json.JSONDecodeError:
                    continue

    return full_content


def main():
    if not API_KEY:
        print("Error: OPENROUTER_API_KEY environment variable is not set.")
        print("Set it with: export OPENROUTER_API_KEY='your-key'")
        sys.exit(1)

    print("FinanceBot")
    print("=" * 40)
    print("Commands: /save <name>  /load <name>  /history  /reset  /exit")
    print()

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    current_save = None

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not user_input:
            continue

        if user_input.startswith("/"):
            parts = user_input.split(maxsplit=1)
            cmd = parts[0].lower()
            arg = parts[1] if len(parts) > 1 else None

            if cmd == "/exit":
                print("Goodbye!")
                break

            elif cmd == "/reset":
                messages = [{"role": "system", "content": SYSTEM_PROMPT}]
                current_save = None
                print("  Conversation reset.")
                continue

            elif cmd == "/save":
                name = arg or current_save or "conversation"
                save_history(name, messages)
                current_save = name
                continue

            elif cmd == "/load":
                if not arg:
                    print("  Usage: /load <name>")
                    continue
                loaded = load_history(arg)
                if loaded:
                    messages = loaded
                    current_save = arg
                    print(f"  Loaded {len(loaded)} messages from '{arg}'.")
                else:
                    print(f"  No saved conversation named '{arg}'.")
                continue

            elif cmd == "/history":
                list_histories()
                continue

            else:
                print(f"  Unknown command: {cmd}")
                continue

        messages.append({"role": "user", "content": user_input})
        print("Bot: ", end="", flush=True)
        reply = stream_response(messages)
        if reply:
            messages.append({"role": "assistant", "content": reply})
        print()


if __name__ == "__main__":
    main()
