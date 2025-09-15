import os
import re
from dotenv import load_dotenv

# Ensure environment variables are loaded if this module is imported standalone
load_dotenv()

def _normalize_raw_prompt(raw: str) -> str:
    # Convert escaped \n sequences into actual newlines (harmless if file already contains real newlines)
    normalized = raw.replace("\\n", "\n")
    # Trim whitespace
    normalized = normalized.strip()
    # Collapse runs of 3+ newlines into 2
    normalized = re.sub(r"\n{3,}", "\n\n", normalized)
    return normalized

def load_system_prompt(fallback: str | None = None) -> str | None:
    """
    Load the system prompt, preferring a prompt file specified by DEFAULT_SYSTEM_PROMPT_FILE.
    Behavior:
      1. If DEFAULT_SYSTEM_PROMPT_FILE is set and the file exists, return its contents.
      2. Else, if DEFAULT_SYSTEM_PROMPT is set, return that (converting literal "\n" to newlines).
      3. Else, return the provided fallback.
    """
    # 1) Try file
    file_path = os.getenv("DEFAULT_SYSTEM_PROMPT_FILE")
    if file_path:
        expanded = os.path.expandvars(os.path.expanduser(file_path))
        try:
            with open(expanded, "r", encoding="utf-8") as fh:
                raw = fh.read()
                return _normalize_raw_prompt(raw)
        except FileNotFoundError:
            # File pointer set but missing; fall back to env var below
            pass
        except (PermissionError, IsADirectoryError, UnicodeDecodeError):
            # If any other expected I/O error occurs, fall back to env var below
            pass

    # 2) Try inline env var (may contain "\n" escapes)
    raw_env = os.getenv("DEFAULT_SYSTEM_PROMPT")
    if raw_env is not None:
        return _normalize_raw_prompt(raw_env)

    # 3) Fallback
    return fallback