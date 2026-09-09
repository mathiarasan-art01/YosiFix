"""Optional LLM upgrade layer.

Every module in this app works fully with NO API key configured. If
GROQ_API_KEY or ANTHROPIC_API_KEY is set in the environment, this
client can be used by modules (like classifier.py) to sharpen their
output. Any failure (missing key, network error, bad response) is
swallowed and callers should treat a None/False result as "use the
rule-based path" -- never let this raise up into a request handler.
"""
import json
import requests


class LLMClient:
    def __init__(self, groq_api_key="", anthropic_api_key="", timeout=15):
        self.groq_api_key = groq_api_key
        self.anthropic_api_key = anthropic_api_key
        self.timeout = timeout

    def is_available(self):
        return bool(self.groq_api_key or self.anthropic_api_key)

    def ask_json(self, prompt):
        """Returns a parsed dict, or None on any failure."""
        text = self._ask_text(prompt)
        if not text:
            return None
        try:
            cleaned = text.strip()
            if cleaned.startswith("```"):
                cleaned = cleaned.strip("`")
                cleaned = cleaned.replace("json\n", "", 1) if cleaned.startswith("json\n") else cleaned
            return json.loads(cleaned)
        except (json.JSONDecodeError, ValueError):
            return None

    def _ask_text(self, prompt):
        if self.groq_api_key:
            result = self._ask_groq(prompt)
            if result:
                return result
        if self.anthropic_api_key:
            result = self._ask_anthropic(prompt)
            if result:
                return result
        return None

    def _ask_groq(self, prompt):
        try:
            resp = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {self.groq_api_key}", "Content-Type": "application/json"},
                json={
                    "model": "llama-3.1-8b-instant",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.3,
                    "max_tokens": 500,
                },
                timeout=self.timeout,
            )
            if resp.status_code == 200:
                return resp.json()["choices"][0]["message"]["content"]
        except (requests.RequestException, KeyError, IndexError):
            pass
        return None

    def _ask_anthropic(self, prompt):
        try:
            resp = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": self.anthropic_api_key,
                    "anthropic-version": "2023-06-01",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "claude-sonnet-4-6",
                    "max_tokens": 500,
                    "messages": [{"role": "user", "content": prompt}],
                },
                timeout=self.timeout,
            )
            if resp.status_code == 200:
                content = resp.json().get("content", [])
                texts = [c["text"] for c in content if c.get("type") == "text"]
                return "\n".join(texts) if texts else None
        except (requests.RequestException, KeyError, IndexError):
            pass
        return None
