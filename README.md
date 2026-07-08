# LLM with Memory

Context management for long Gemini chats. Instead of sending the full history every turn, this keeps pinned facts + a running summary + recent messages.

## setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Add your key to `.env`:
```
GEMINI_API_KEY=your_key
```

## run

```bash
python main.py
```

`/stats` to see memory state, `/quit` to exit. Logs saved to `logs/`.

## how it works

Three stores:
- **pinned facts** — names, dates, prefs extracted from old turns
- **summary** — compressed older chat
- **window** — recent turns kept verbatim

Prompt order: system → pinned → summary → recent → current message.

When token estimate crosses 2488 (3000 max minus 512 reserved for reply), oldest 4 turns get summarized and dropped. Facts worth keeping get pinned.

| approach | tokens at turn 20 | growth |
|---|---|---|
| send full history | ~3000 | linear |
| this | ~1500-1700 | flat after compress |

## log excerpt

turn 6 from `logs/run_20260708_093533.log`:

```
--- turn 6 ---
over budget (2974 > 2488), compressing 4 turns
summary: 0 -> 294 tokens (est)
pinned 4 new facts: ['Trip dates: October 12–22 (Tokyo to Osaka).', 'Budget: $2,500 (excluding flights).', ...]
dropped 4 raw turns, 1 left in window
context: 4 facts, summary~294, window=1 turns, total~1052 tok (naive full-history would be ~3492)
```

Also compressed on turns 10, 14, 17. Full run log in `logs/`.
