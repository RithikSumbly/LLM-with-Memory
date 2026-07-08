from memory.types import Turn
from providers.gemini import GeminiProvider

SUMMARY_PROMPT = """Merge these turns into a short running summary. Keep names, dates, decisions.
No intro, just the summary."""

FACTS_PROMPT = """Pull out facts worth remembering long-term (names, dates, prefs, deadlines).
One per line. Write NONE if nothing useful."""


class Compressor:
    def __init__(self, provider: GeminiProvider):
        self.provider = provider

    def summarize_turns(self, existing_summary: str, turns: list[Turn]) -> str:
        turns_text = "\n\n".join(t.to_text() for t in turns)
        prompt = f"Existing summary:\n{existing_summary or '(empty)'}\n\nNew turns:\n{turns_text}"
        return self.provider.generate(prompt, system_instruction=SUMMARY_PROMPT)

    def extract_facts(self, turns: list[Turn]) -> list[str]:
        turns_text = "\n\n".join(t.to_text() for t in turns)
        raw = self.provider.generate(turns_text, system_instruction=FACTS_PROMPT)
        if raw.strip().upper() == "NONE":
            return []

        out = []
        for line in raw.splitlines():
            line = line.strip().lstrip("-•*").strip()
            if line and line.upper() != "NONE":
                out.append(line)
        return out

    def compress(self, existing_summary: str, turns: list[Turn]) -> tuple[str, list[str]]:
        return self.summarize_turns(existing_summary, turns), self.extract_facts(turns)
