# Hackathon 2025 - Python OpenAI API

A simple Flask API that interfaces with a deployed Azure OpenAI service, plus a lightweight REPL CLI for direct experimentation.

## 🚀 Quick Start

### 1. Install dependencies
Open a terminal in the `api` folder and install required packages:

```powershell
cd api
pip install -r requirements.txt
```

### 2. Configure environment
Copy the template and populate the values (Azure endpoint, API key, deployment, etc.):

```powershell
cp .env.template .env
# then edit .env and set your values
```

Essential environment variables:
- `AZURE_OPENAI_ENDPOINT` — your Azure OpenAI endpoint URL
- `AZURE_OPENAI_API_KEY` — your Azure OpenAI API key
- `AZURE_OPENAI_DEPLOYMENT` — the model deployment name
- `AZURE_OPENAI_API_VERSION` — API version (e.g. `2024-02-15-preview`)

## 🧭 Running the services

### Run the Flask API
Start the API server:

```powershell
python app.py
```

The server listens on the port configured in `.env` (default: `5000`).

Endpoints:
- `GET /` — health check
- `POST /chat` — chat completion (JSON body)
  - Request JSON fields:
    - `message` (required)
    - `system_prompt` (optional) — overrides the default system prompt for that request
    - `max_tokens`, `temperature` (optional)

Example POST body:

```json
{
  "message": "Hello, how can you help me with onboarding?",
  "system_prompt": "You are an internal helpdesk assistant.",
  "max_tokens": 300,
  "temperature": 0.5
}
```

### Run the REPL CLI (`cli_direct.py`)
A small console-based client is provided for quick experimentation and interactive sessions.

- Send a single message and print the model reply:

```powershell
python cli_direct.py --message "Hello, how can you help me?"
```

- Start the interactive REPL (runs when no `--message` is provided and the process is attached to a TTY):

```powershell
python cli_direct.py
```

REPL commands:
- `/exit` or `/quit` — quit the REPL
- `/reset` — clear conversation history (retains the system prompt)
- `/history` — print conversation history

Override the system prompt on the CLI with `--system`:

```powershell
python cli_direct.py --message "Hi" --system "You are a supportive onboarding assistant for engineers."
```

## 🛠 Default system prompt — configuration & behavior

This project supports a readable, file-based system prompt to keep `.env` tidy and the prompt easy to edit. The loader lives in `prompt_utils.py` as the function `load_system_prompt()`.

Priority order used by `load_system_prompt()`:
1. If `DEFAULT_SYSTEM_PROMPT_FILE` is set in `.env` and the referenced file exists, the loader reads and returns that file's contents.
2. Otherwise, if `DEFAULT_SYSTEM_PROMPT` is set in `.env`, the loader returns that value after normalizing it (it converts literal `\n` escapes into real newlines and trims/collapses excessive blank lines).
3. If neither is set, the function returns a fallback string passed by the caller.

This allows you to store a multi-paragraph prompt in a separate text/Markdown file and reference it from `.env` for readability and easier editing.

### Example `.env` snippet

```ini
# point to a file that contains the full onboarding prompt (recommended)
DEFAULT_SYSTEM_PROMPT_FILE=alternative_system_prompt.md

# optional short inline fallback (kept short for readability)
# DEFAULT_SYSTEM_PROMPT="You are Onboarding Buddy, a helpful assistant."
```

### Example prompt file
Create a file such as `alternative_system_prompt.md` and paste your multi-line prompt there. Example content:

```text
You are Onboarding Buddy, a friendly and knowledgeable AI assistant designed to help new employees navigate their first days at the company. You specialize in answering onboarding-related questions using official documentation provided in Markdown format.

Your tone is warm, supportive, and professional. You never guess or invent information—only respond based on the retrieved content. If the answer isn’t available, say so clearly and suggest where the user might look or who to contact.

Always tailor your responses to the user's role and department when that information is available. Use plain language and avoid jargon unless it’s explained.

When referencing documents, summarize clearly and cite the document title if helpful. Do not quote large sections verbatim.

If multiple documents are relevant, synthesize the information into a coherent answer.

If the user asks a question outside the scope of onboarding, politely redirect them or suggest a relevant resource.

Your goal is to make the onboarding experience smooth, welcoming, and empowering.
```

> Note: If you prefer to keep the prompt inline in `.env` (for example in some deployment environments), the loader will convert `\n` escape sequences into real newlines for you.

## 🔁 How the prompt is applied
- `app.py` (`/chat`) will use the `system_prompt` provided in the request body if present. If not present, it calls `load_system_prompt(...)` to obtain the default prompt according to the rules above.
- `cli_direct.py` uses `load_system_prompt(...)` to decide the default `--system` prompt. Providing `--system` overrides the env/file value for that invocation.

Files of interest
- `app.py` — Flask API server
- `cli_direct.py` — REPL / CLI client
- `prompt_utils.py` — loader/normalizer for the default system prompt
- `.env` — configure `DEFAULT_SYSTEM_PROMPT_FILE` or `DEFAULT_SYSTEM_PROMPT`

## 🔒 Security & best practices
- Do not commit your `.env` file to version control — it may contain API keys.
- The prompt file (e.g. `alternative_system_prompt.md`) is safe to commit if it contains only non-sensitive instructions.
- Prefer a dedicated prompt file for multi-paragraph prompts for readability and editor support.

## ✅ Summary
- Use `DEFAULT_SYSTEM_PROMPT_FILE` in `.env` to point to a readable multi-line prompt file (recommended).
- `load_system_prompt()` will load and normalize that prompt for both the API and the CLI.
- Use `--system` (CLI) or `system_prompt` (API) to override the default on a per-call basis.

If you want, I can add a sample `alternative_system_prompt.md` file to the repo or update `.env.template` to include `DEFAULT_SYSTEM_PROMPT_FILE` and usage notes.