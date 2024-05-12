from pydantic import BaseModel
from decimal import Decimal
from ecommerce.utils.consts import PuleType
from datetime import datetime


class ModalityCart(BaseModel):
    id: int
    name: str
    is_active: bool
    max_len_input_guess: int
    min_len_input_guess: int
    max_quantity_guess: int
    number_separator: bool
    max_guess_value: int
    big_guess: bool
    
class LotteryCart(BaseModel):
    id: int
    name: str
    
    
class PlacingCart(BaseModel):
    id: int
    name: str
    award_range: str
    is_active: bool
    
class LotteryDrawCart(BaseModel):
    id: int
    name: str
    date: datetime
    is_active: bool
    lottery: LotteryCart

class BetCart(BaseModel):
    guess: str
    bet_value: Decimal
    modality_name: str

class PuleCart(BaseModel):
    id: int
    value_total: Decimal
    guesses: list[str]
    type: PuleType
    modality: ModalityCart
    placing: PlacingCart | None = None
    lottery_draw: LotteryDrawCart
    bets: list[BetCart]
    
    def finalize_purchase_payload(self):
        return {
            "modality": self.modality.id,
            "placing": self.placing.id if self.placing else None,
            "lottery_draw": self.lottery_draw.id,
            "value_total": self.value_total,
            "guesses": self.guesses,
            "type": self.type,
            "bets": [bet.model_dump() for bet in self.bets],
        }

class Cart(BaseModel):
    value_total: Decimal = Decimal("0.0")
    pules: list[PuleCart] = []    
    
    def add_item(self, item: PuleCart):
        self.value_total += item.value_total
        self.pules.append(item)
        
    def remove_item(self, id: int):
        item_to_remove = None
        for item in self.pules:
            if item.id == id:
                item_to_remove = item
                break
        self.value_total -= item_to_remove.value_total
        self.pules.remove(item_to_remove)
        
    def remove_all(self):
        self.value_total = Decimal("0.0")
        self.pules = []