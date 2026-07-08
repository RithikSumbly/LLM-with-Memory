from dataclasses import dataclass, field

import config
from memory.compressor import Compressor
from memory.stores import ActiveWindow, PinnedFactsStore, RunningSummary
from memory.token_budget import (
    available_budget,
    estimate_context_tokens,
    estimate_tokens,
    is_over_budget,
    naive_token_estimate_at_turn,
)
from memory.types import Turn
from providers.gemini import GeminiProvider


@dataclass
class ContextLog:
    turn_number: int = 0
    events: list[str] = field(default_factory=list)
    prompt_preview: str = ""

    def add(self, msg: str):
        self.events.append(msg)

    def render(self) -> str:
        lines = [f"--- turn {self.turn_number} ---"]
        lines.extend(self.events)
        if self.prompt_preview:
            lines.append("sent to api:")
            lines.append(self.prompt_preview)
        return "\n".join(lines)


class ContextManager:
    def __init__(self, provider: GeminiProvider | None = None):
        self.provider = provider or GeminiProvider()
        self.compressor = Compressor(self.provider)
        self.pinned = PinnedFactsStore(max_facts=config.MAX_PINNED_FACTS)
        self.summary = RunningSummary()
        self.window = ActiveWindow(max_turns=config.ACTIVE_WINDOW_TURNS)
        self._turn_count = 0
        self._cumulative_turn_tokens = 0

    @property
    def turn_count(self):
        return self._turn_count

    def _maybe_compress(self, current_message: str, log: ContextLog):
        while True:
            total = estimate_context_tokens(
                self.pinned,
                self.summary,
                self.window,
                current_message,
                config.SYSTEM_INSTRUCTIONS,
            )
            if not is_over_budget(total):
                break
            if self.window.count == 0:
                log.add("over budget but nothing left to compress")
                break

            n = min(config.COMPRESS_BATCH_SIZE, self.window.count)
            old_sum = self.summary.token_estimate()
            batch = self.window.pop_oldest(n)

            log.add(f"over budget ({total} > {available_budget()}), compressing {n} turns")

            new_summary, facts = self.compressor.compress(self.summary.text, batch)
            self.summary.update(new_summary)
            added = self.pinned.add_facts(facts)

            log.add(f"summary: {old_sum} -> {self.summary.token_estimate()} tokens (est)")
            if added:
                log.add(f"pinned {len(added)} new facts: {added}")
            log.add(f"dropped {n} raw turns, {self.window.count} left in window")

    def assemble_prompt(self, current_message: str) -> str:
        parts = [config.SYSTEM_INSTRUCTIONS]

        if self.pinned.to_section():
            parts.append(self.pinned.to_section())
        if self.summary.to_section():
            parts.append(self.summary.to_section())

        recent = self.window.to_text()
        if recent:
            parts.append(f"## Recent Conversation\n{recent}")

        parts.append(f"## Current Message\nUser: {current_message}")
        return "\n\n".join(parts)

    def prepare_context(self, current_message: str) -> tuple[str, ContextLog]:
        self._turn_count += 1
        log = ContextLog(turn_number=self._turn_count)

        self._maybe_compress(current_message, log)

        prompt = self.assemble_prompt(current_message)
        total = estimate_tokens(prompt)

        done = self._turn_count - 1
        avg = self._cumulative_turn_tokens // done if done else 150
        naive = naive_token_estimate_at_turn(avg, self._turn_count)

        log.prompt_preview = prompt
        log.add(
            f"context: {self.pinned.count} facts, summary~{self.summary.token_estimate()}, "
            f"window={self.window.count} turns, total~{total} tok "
            f"(naive full-history would be ~{naive})"
        )
        return prompt, log

    def record_turn(self, user_message: str, assistant_message: str):
        turn = Turn(user=user_message, assistant=assistant_message)
        self._cumulative_turn_tokens += turn.token_estimate()
        self.window.add(turn)

    def chat(self, user_message: str) -> tuple[str, ContextLog]:
        prompt, log = self.prepare_context(user_message)
        response = self.provider.generate(prompt)
        self.record_turn(user_message, response)
        return response, log

    def stats(self) -> dict:
        preview = self.summary.text
        if len(preview) > 200:
            preview = preview[:200] + "..."
        return {
            "turn_count": self._turn_count,
            "pinned_facts": self.pinned.count,
            "summary_tokens": self.summary.token_estimate(),
            "window_turns": self.window.count,
            "summary_preview": preview,
            "pinned": self.pinned.facts,
        }
