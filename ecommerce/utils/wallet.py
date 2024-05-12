import math
from decimal import Decimal


def truncate(number: Decimal | float, precision: int = 10) -> Decimal:
    try:
        if isinstance(number, Decimal):
            number = float(number)
        if not isinstance(number, float):
            raise TypeError("Invalid type for number")
        nbDecimals = len(str(number).split(".")[1])
        if nbDecimals <= precision:
            return Decimal(f"{number}")
        stepper = 10.0**precision
        return Decimal(f"{math.trunc(stepper * number) / stepper}")
    except TypeError as te:
        raise te
    except Exception:
        return Decimal(f"{number}")
    