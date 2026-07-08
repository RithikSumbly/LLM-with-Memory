import config
from memory.stores import ActiveWindow, PinnedFactsStore, RunningSummary


def estimate_tokens(text: str) -> int:
    # rough but good enough — ~4 chars per token
    return len(text) // 4


def available_budget() -> int:
    return config.MAX_CONTEXT_TOKENS - config.RESERVE_FOR_REPLY


def estimate_context_tokens(
    pinned: PinnedFactsStore,
    summary: RunningSummary,
    window: ActiveWindow,
    current_message: str,
    system_instructions: str,
) -> int:
    chunks = [
        system_instructions,
        pinned.to_section(),
        summary.to_section(),
        window.to_text(),
        current_message,
    ]
    return estimate_tokens("\n\n".join(c for c in chunks if c))


def is_over_budget(total_tokens: int) -> bool:
    return total_tokens > available_budget()


def naive_token_estimate_at_turn(avg_tokens_per_turn: int, turn_number: int) -> int:
    return avg_tokens_per_turn * turn_number
