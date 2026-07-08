from memory.types import Turn


class ActiveWindow:
    def __init__(self, max_turns: int | None = None):
        self.max_turns = max_turns
        self._turns: list[Turn] = []

    @property
    def turns(self):
        return list(self._turns)

    @property
    def count(self):
        return len(self._turns)

    def add(self, turn: Turn):
        self._turns.append(turn)

    def pop_oldest(self, n: int) -> list[Turn]:
        n = min(n, len(self._turns))
        removed = self._turns[:n]
        self._turns = self._turns[n:]
        return removed

    def to_text(self) -> str:
        if not self._turns:
            return ""
        return "\n\n".join(t.to_text() for t in self._turns)

    def token_estimate(self) -> int:
        return len(self.to_text()) // 4


class RunningSummary:
    def __init__(self):
        self._text = ""

    @property
    def text(self):
        return self._text

    def update(self, new_summary: str):
        self._text = new_summary.strip()

    def token_estimate(self) -> int:
        return len(self._text) // 4

    def to_section(self) -> str:
        if not self._text:
            return ""
        return f"## Conversation Summary\n{self._text}"


class PinnedFactsStore:
    def __init__(self, max_facts: int = 20):
        self.max_facts = max_facts
        self._facts: list[str] = []

    @property
    def facts(self):
        return list(self._facts)

    @property
    def count(self):
        return len(self._facts)

    def add_facts(self, new_facts: list[str]) -> list[str]:
        added = []
        for fact in new_facts:
            fact = fact.strip().lstrip("-•").strip()
            if not fact:
                continue
            if any(fact.lower() == x.lower() for x in self._facts):
                continue
            if len(self._facts) >= self.max_facts:
                break
            self._facts.append(fact)
            added.append(fact)
        return added

    def token_estimate(self) -> int:
        return len(self.to_section()) // 4

    def to_section(self) -> str:
        if not self._facts:
            return ""
        return "## Pinned Facts\n" + "\n".join(f"- {f}" for f in self._facts)
