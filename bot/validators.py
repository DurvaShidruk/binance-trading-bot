class ValidationError(Exception):
    pass


def validate_symbol(symbol):
    if not symbol or not isinstance(symbol, str):
        raise ValidationError("Invalid symbol")

    symbol = symbol.upper()

    if not symbol.endswith("USDT"):
        raise ValidationError("Only USDT pairs allowed (e.g., BTCUSDT)")

    return symbol


def validate_side(side):
    side = side.upper()
    if side not in ["BUY", "SELL"]:
        raise ValidationError("Side must be BUY or SELL")
    return side


def validate_type(order_type):
    order_type = order_type.upper()
    if order_type not in ["MARKET", "LIMIT"]:
        raise ValidationError("Type must be MARKET or LIMIT")
    return order_type


def validate_quantity(qty):
    try:
        qty = float(qty)
        if qty <= 0:
            raise ValidationError
        return qty
    except:
        raise ValidationError("Quantity must be a positive number")


def validate_price(price, required=False):
    if required and price is None:
        raise ValidationError("Price required for LIMIT order")

    if price is None:
        return None

    try:
        price = float(price)
        if price <= 0:
            raise ValidationError
        return price
    except:
        raise ValidationError("Price must be a positive number")