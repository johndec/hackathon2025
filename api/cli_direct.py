#!/usr/bin/env python3
import os
import argparse
import sys
from dotenv import load_dotenv
from openai import AzureOpenAI

load_dotenv()

AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")

def get_client():
    if not AZURE_OPENAI_API_KEY:
        raise RuntimeError("AZURE_OPENAI_API_KEY not set")
    return AzureOpenAI(
        api_key=AZURE_OPENAI_API_KEY,
        api_version=AZURE_OPENAI_API_VERSION,
        azure_endpoint=AZURE_OPENAI_ENDPOINT
    )

def single_request(client, user_message, system_prompt, max_tokens, temperature):
    resp = client.chat.completions.create(
        model=AZURE_OPENAI_DEPLOYMENT,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ],
        max_tokens=max_tokens,
        temperature=temperature
    )
    ai_text = resp.choices[0].message.content
    print(ai_text)
    try:
        usage = resp.usage
        print("\n--- usage ---")
        print(f"prompt: {usage.prompt_tokens}, completion: {usage.completion_tokens}, total: {usage.total_tokens}")
    except Exception:
        pass

def repl_loop(client, system_prompt, max_tokens, temperature):
    print("Entering interactive REPL. Type your message and press Enter.")
    print("Commands: /exit to quit, /reset to clear conversation, /history to show conversation")
    messages = [{"role": "system", "content": system_prompt}]

    while True:
        try:
            user_input = input("You> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting REPL.")
            break

        if not user_input:
            continue

        if user_input.lower() in ("/exit", "/quit"):
            print("Goodbye.")
            break
        if user_input.lower() == "/reset":
            messages = [{"role": "system", "content": system_prompt}]
            print("Conversation reset.")
            continue
        if user_input.lower() == "/history":
            print("--- Conversation history ---")
            for m in messages:
                role = m.get("role", "unknown")
                content = m.get("content", "")
                print(f"[{role}] {content}")
            print("---------------------------")
            continue

        # append user message and call API
        messages.append({"role": "user", "content": user_input})
        try:
            resp = client.chat.completions.create(
                model=AZURE_OPENAI_DEPLOYMENT,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
            ai_text = resp.choices[0].message.content
            print(f"AI> {ai_text}\n")
            # append assistant reply to conversation so context is preserved
            messages.append({"role": "assistant", "content": ai_text})
        except Exception as e:
            print(f"Error calling OpenAI: {e}", file=sys.stderr)

def main():
    p = argparse.ArgumentParser(description="Direct CLI to Azure OpenAI (uses AZ env vars)")
    p.add_argument("--message", "-m", help="Message to send (if omitted, REPL when running in a TTY)")
    p.add_argument("--system", default="You are a helpful AI agent.", help="System prompt")
    p.add_argument("--max-tokens", type=int, default=500)
    p.add_argument("--temperature", type=float, default=0.7)
    args = p.parse_args()

    # determine mode: single message (flag or piped input) or interactive REPL
    if args.message:
        user_message = args.message
        client = get_client()
        single_request(client, user_message, args.system, args.max_tokens, args.temperature)
        return

    if not sys.stdin.isatty():
        # piped input -> treat entire stdin as a single message
        user_message = sys.stdin.read().strip()
        if not user_message:
            print("No input provided", file=sys.stderr)
            return
        client = get_client()
        single_request(client, user_message, args.system, args.max_tokens, args.temperature)
        return

    # interactive REPL
    client = get_client()
    repl_loop(client, args.system, args.max_tokens, args.temperature)

if __name__ == "__main__":
    main()