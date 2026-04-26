import re


def parse_price(raw: str) -> float | None:
    numbers = re.findall(r"\$[\d,]+\.?\d*", raw)
    if not numbers:
        return None
    return float(numbers[0].replace("$", "").replace(",", ""))
