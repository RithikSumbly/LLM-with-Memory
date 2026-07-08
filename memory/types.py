from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class Turn:
    user: str
    assistant: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_text(self) -> str:
        return f"User: {self.user}\nAssistant: {self.assistant}"

    def token_estimate(self) -> int:
        return len(self.to_text()) // 4
