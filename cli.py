import argparse
from bot.orders import place_order, build_preview, format_order_result
from bot.validators import validate_side, validate_type, validate_quantity, validate_price
from bot.logging_config import setup_logger
from rich import print


def main():
    setup_logger()

    parser = argparse.ArgumentParser(description="Binance Futures Testnet Bot")

    parser.add_argument("--symbol", required=True, help="e.g., BTCUSDT")
    parser.add_argument("--side", required=True, help="BUY or SELL")
    parser.add_argument("--type", required=True, help="MARKET or LIMIT")
    parser.add_argument("--quantity", required=True, help="Order quantity")
    parser.add_argument("--price", required=False, help="Required for LIMIT")

    args = parser.parse_args()

    try:
        args.side = validate_side(args.side)
        args.type = validate_type(args.type)
        args.quantity = validate_quantity(args.quantity)
        args.price = validate_price(args.price, required=(args.type == "LIMIT"))

        print("\n[bold cyan]--- ORDER REQUEST ---[/bold cyan]")
        print(f"[white]Symbol:[/white] {args.symbol}")
        print(f"[white]Side:[/white] {args.side}")
        print(f"[white]Type:[/white] {args.type}")
        print(f"[white]Quantity:[/white] {args.quantity}")

        if args.type == "LIMIT":
            print(f"[white]Price:[/white] {args.price}")

        preview = build_preview(
            args.symbol,
            args.side,
            args.type,
            args.quantity,
            args.price
        )

        print("\n[yellow] Preview:[/yellow]")
        print(preview)

        confirm = input("Proceed? (y/n): ").lower()
        if confirm != "y":
            print("[red]Cancelled[/red]")
            return

        result = place_order(
            symbol=args.symbol,
            side=args.side,
            order_type=args.type,
            quantity=args.quantity,
            price=args.price
        )

        print(format_order_result(result))

    except Exception as e:
        print(f"\n[bold red] ERROR:[/bold red] {str(e)}")


if __name__ == "__main__":
    main()