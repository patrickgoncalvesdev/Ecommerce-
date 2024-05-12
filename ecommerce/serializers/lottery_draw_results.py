from typing import List
from pydantic import BaseModel


class LotteryDrawResultSerializer(BaseModel):
    result: int
    animal: str
    group_number: str

