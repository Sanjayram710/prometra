def calculate_tax(amount: float, rate: float = 0.15) -> float:
    """Calculate tax for a given amount and rate."""
    return round(amount * rate, 2)
