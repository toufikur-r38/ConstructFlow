from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

MONEY_QUANT = Decimal("0.01")
PERCENT_QUANT = Decimal("0.1")
ZERO = Decimal("0.00")


def to_decimal(value, default=ZERO):
    if value in (None, ""):
        return default
    if isinstance(value, Decimal):
        parsed = value
    else:
        try:
            parsed = Decimal(str(value).strip())
        except (InvalidOperation, ValueError, AttributeError):
            raise InvalidOperation
    if not parsed.is_finite():
        raise InvalidOperation
    return parsed


def to_money(value, default=ZERO):
    return to_decimal(value, default).quantize(MONEY_QUANT, rounding=ROUND_HALF_UP)


def calculate_total(quantity, unit_rate):
    return (to_money(quantity) * to_money(unit_rate)).quantize(
        MONEY_QUANT,
        rounding=ROUND_HALF_UP,
    )


def percent_used(spent, budget):
    spent_value = to_money(spent)
    budget_value = to_money(budget)
    if budget_value <= 0:
        return Decimal("0.0")
    return (spent_value / budget_value * Decimal("100")).quantize(
        PERCENT_QUANT,
        rounding=ROUND_HALF_UP,
    )


def format_money(value, prefix="TK"):
    amount = to_money(value)
    return f"{prefix} {amount:,.2f}" if prefix else f"{amount:,.2f}"
