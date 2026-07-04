import os
import requests
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
API_URL = os.environ.get("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1") + "/chat/completions"
MODEL = os.environ.get("OPENROUTER_MODEL", "openrouter/free")

SYSTEM_PROMPT = "You are a professional financial assistant. Only answer questions about finance: budgeting, saving, investing, loans, taxes, banking, insurance, retirement, crypto, and accounting. If asked anything outside finance, politely decline. Never fabricate facts or predict prices."

import time

def chat(history):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://finance-chatbot.local",
        "X-Title": "Finance Chatbot",
    }
    for attempt in range(3):  # retry up to 3 times
        try:
            r = requests.post(API_URL, headers=headers, json={"model": MODEL, "messages": history}, timeout=60)
            if r.status_code == 429:
                wait = 30 * (attempt + 1)
                print(f"\n[Rate limited. Waiting {wait}s before retry...]\n")
                time.sleep(wait)
                continue
            r.raise_for_status()
            return r.json()["choices"][0]["message"]["content"]
        except Exception as e:
            return f"[Error] {e}"
    return "[Error] Too many requests. Please wait a minute and try again."

def main():
    if not OPENROUTER_API_KEY:
        print("No API key found. Make sure your .env file has OPENROUTER_API_KEY set.")
        return
    history = [{"role": "system", "content": SYSTEM_PROMPT}]
    print("\n==================================================")
    print("  Finance Assistant - Powered by OpenRouter")
    print(f"  Model: {MODEL}")
    print("  Type exit to quit.")
    print("==================================================\n")
    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break
        if not user_input:
            continue
        if user_input.lower() in ("exit", "quit"):
            print("Bot: Goodbye!")
            break
        history.append({"role": "user", "content": user_input})
        reply = chat(history)
        print(f"\nBot: {reply}\n")
        history.append({"role": "assistant", "content": reply})

if __name__ == "__main__":
    main()