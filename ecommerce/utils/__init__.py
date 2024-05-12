import ast
from typing import Union


def string_to_tuple(s):
    try:
        data = ast.literal_eval(s)
        if isinstance(data, tuple):
            return data
        else:
            raise ValueError
    except Exception as e:
        print("Invalid tuple string.")
        raise e
    
float_format = "{:,.2f}"
int_format = "{}"


format_options = {
    2: float_format,
    0: int_format,
}


def get_locale_formatted_value(value: Union[float, int], decimal_numbers: int = 2):
    format_number = format_options.get(decimal_numbers, float_format)
    number_str = format_number.format(value)
    if decimal_numbers:
        number_str = number_str.replace(",", "_")
        number_str = number_str.replace(".", ",")
        number_str = number_str.replace("_", ".")
    return number_str