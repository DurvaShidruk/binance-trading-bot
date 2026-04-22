import json
import os
import time
from dataclasses import dataclass, asdict
from typing import Optional

from binance.exceptions import BinanceAPIException, BinanceRequestException

from .client import get_client
from .logging_config import setup_logger
from .validators import (
    validate_symbol,
    validate_side,
    validate_type,
    validate_quantity,
    validate_price,
    ValidationError,
)

logger = setup_logger()

HISTORY_FILE = os.path.join("logs", "history.json")
MAX_RETRIES = 2

@dataclass
class OrderResult:
    success: bool
    message: str
    orderId: Optional[int] = None
    status: Optional[str] = None
    executedQty: Optional[str] = None
    avgPrice: Optional[str] = None
    symbol: Optional[str] = None
    side: Optional[str] = None
    type: Optional[str] = None
    price: Optional[str] = None
    elapsed_ms: Optional[int] = None
    raw: Optional[dict] = None


def _save_history(entry: dict) -> None:
    os.makedirs("logs", exist_ok=True)

    history = []
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r") as f:
                history = json.load(f)
        except Exception:
            history = []

    history.insert(0, entry)
    history = history[:50]

    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2, default=str)


def get_history(limit: int = 5) -> list:
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)[:limit]
    except Exception:
        return []


def place_order(
    symbol: str,
    side: str,
    order_type: str,
    quantity,
    price=None,
) -> OrderResult:

    try:
        symbol = validate_symbol(symbol)
        side = validate_side(side)
        order_type = validate_type(order_type)
        quantity = validate_quantity(quantity)
        price = validate_price(price)
    except ValidationError as e:
        logger.warning("Validation failed: %s", e)
        return OrderResult(success=False, message=str(e))


    params = {
        "symbol": symbol,
        "side": side,
        "type": order_type,
        "quantity": quantity,
    }

    if order_type == "LIMIT":
        params["price"] = price
        params["timeInForce"] = "GTC"

    logger.info("REQUEST :%s", params)

    client = get_client()

    last_error = None
    start = time.perf_counter()

    for attempt in range(1, MAX_RETRIES + 2):
        try:
            response = client.futures_create_order(**params)

            elapsed_ms = int((time.perf_counter() - start) * 1000)

            logger.info("RESPONSE : %s", response)

            result = OrderResult(
                success=True,
                message="Order placed successfully",
                orderId=response.get("orderId"),
                status=response.get("status"),
                executedQty=response.get("executedQty"),
                avgPrice=response.get("avgPrice") or response.get("price"),
                symbol=response.get("symbol"),
                side=response.get("side"),
                type=response.get("type"),
                price=response.get("price"),
                elapsed_ms=elapsed_ms,
                raw=response,
            )

            _save_history(asdict(result))
            return result

        except BinanceAPIException as e:
            last_error = e
            logger.error("API Error (attempt %d): %s", attempt, e)

            if attempt <= MAX_RETRIES:
                time.sleep(0.5 * attempt)
                continue
            break

        except BinanceRequestException as e:
            last_error = e
            logger.error("Network Error (attempt %d): %s", attempt, e)

            if attempt <= MAX_RETRIES:
                time.sleep(0.5 * attempt)
                continue
            break

        except Exception as e:
            last_error = e
            logger.exception("Unexpected Error: %s", e)
            break

    elapsed_ms = int((time.perf_counter() - start) * 1000)

    fail_result = OrderResult(
        success=False,
        message=f"Order failed: {last_error}",
        symbol=symbol,
        side=side,
        type=order_type,
        price=str(price) if price else None,
        elapsed_ms=elapsed_ms,
    )

    _save_history(asdict(fail_result))
    return fail_result


def build_preview(symbol, side, order_type, quantity, price=None) -> str:
    base = f"{side} {quantity} {symbol} at {order_type}"

    if order_type == "LIMIT" and price:
        est = float(price) * float(quantity)
        return f"{base} @ {price}  •  Estimated value: {est:.2f} USDT"

    return base

def format_order_result(result: OrderResult) -> str:
    if result.success:
        return f"""
--- ORDER RESPONSE ---
Order ID      : {result.orderId}
Status        : {result.status}
Executed Qty  : {result.executedQty}
Avg Price     : {result.avgPrice}
Time Taken    : {result.elapsed_ms} ms

 SUCCESS: {result.message}
"""
    else:
        return f"""
 FAILED: {result.message}
Time Taken: {result.elapsed_ms} ms
"""
