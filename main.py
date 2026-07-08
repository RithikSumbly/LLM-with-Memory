#!/usr/bin/env python3

import sys
from datetime import datetime
from pathlib import Path

from memory.manager import ContextManager
from providers.gemini import GeminiProvider


def main():
    print("context-managed chat (gemini). /stats /quit\n")

    try:
        provider = GeminiProvider()
    except ValueError as e:
        print(e)
        sys.exit(1)

    mgr = ContextManager(provider=provider)
    log_dir = Path(__file__).parent / "logs"
    log_dir.mkdir(exist_ok=True)
    log_path = log_dir / f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    print(f"log -> {log_path}\n")

    with log_path.open("a") as f:
        while True:
            try:
                msg = input("you> ").strip()
            except (EOFError, KeyboardInterrupt):
                break

            if not msg:
                continue
            if msg == "/quit":
                break
            if msg == "/stats":
                s = mgr.stats()
                print(f"turns={s['turn_count']}  pinned={s['pinned_facts']}  window={s['window_turns']}")
                for p in s["pinned"]:
                    print(f"  * {p}")
                if s["summary_preview"]:
                    print(f"summary: {s['summary_preview']}")
                print()
                continue

            try:
                reply, log = mgr.chat(msg)
            except Exception as e:
                print(f"api error: {e}\n")
                f.write(f"turn {mgr.turn_count} error: {e}\n\n")
                continue

            out = log.render()
            print(out)
            print(f"assistant> {reply}\n")

            f.write(out + "\n\n")
            f.write(f"assistant> {reply}\n\n")

    print("bye")


if __name__ == "__main__":
    main()
