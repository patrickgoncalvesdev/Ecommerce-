from dataclasses import dataclass


@dataclass
class BetMessage:
    bet_id: int
    win: bool
    award_position: int
    results: str | None = None

@dataclass
class EndDrawMessage:
    draw_id: int
    results: str | None = None
    