# context budget — kept low on purpose so compression shows up in a ~15 turn chat
MAX_CONTEXT_TOKENS = 3000
RESERVE_FOR_REPLY = 512
ACTIVE_WINDOW_TURNS = 6  # target size after compress, not a hard cutoff
COMPRESS_BATCH_SIZE = 4

MAX_PINNED_FACTS = 20

GEMINI_MODEL = "gemini-3.1-flash-lite"
GEMINI_FALLBACK_MODEL = "gemini-3.1-flash-lite-preview"

SYSTEM_INSTRUCTIONS = """You're a helpful assistant. Below you'll see pinned facts, a summary of older chat, and recent messages.
Use all of it to stay consistent. Don't talk about the memory system unless asked."""
