#  Binance Futures Testnet Trading Bot

A simple, clean, and modular Python-based trading bot that places **MARKET** and **LIMIT** orders on Binance Futures Testnet (USDT-M) via a CLI interface.

# Features

*  Place **MARKET** and **LIMIT** orders
*  Supports both **BUY** and **SELL**
*  CLI-based input using argparse
*  Input validation (symbol, type, quantity, price)
*  Clean order request & response output
*  Logging of requests, responses, and errors
*  Retry mechanism for API/network failures
*  Trade preview before execution
*  Order history stored locally

---

##  Project Structure

trading_bot/
│
├── bot/
│   ├── client.py
│   ├── orders.py
│   ├── validators.py
│   ├── logging_config.py
│
├── cli.py
├── requirements.txt
├── README.md
├── .env.example
├── logs/
│   ├── bot.log
│   └── history.json


---

#  Setup Instructions

# 1. Clone the repository

```bash
git clone <your-repo-link>
cd trading_bot


---

# 2. Install dependencies

```bash
pip install -r requirements.txt
```

---

# 3. Setup environment variables

Create a `.env` file:

```env
API_KEY=your_api_key_here
API_SECRET=your_api_secret_here
```

---

# 4. Binance Testnet

Use Binance Futures Testnet:

https://testnet.binancefuture.com

* Create account
* Generate API keys
* Use test funds only

---

#  How to Run

# 🔹 MARKET Order

```bash
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001
```

---

# 🔹 LIMIT Order

```bash
python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.001 --price 60000
```

---

#  Example Output

```
--- ORDER REQUEST ---
Symbol   : BTCUSDT
Side     : BUY
Type     : MARKET
Quantity : 0.001

 Preview:
BUY 0.001 BTCUSDT at MARKET

Proceed? (y/n): y

--- ORDER RESPONSE ---
Order ID      : 123456
Status        : FILLED
Executed Qty  : 0.001
Avg Price     : 60234

 SUCCESS: Order placed successfully
```

---

# Logging

Logs are stored in:

```
logs/bot.log
```

Includes:

* API requests
* API responses
* Errors

---

# Order History

Recent orders are saved in:

```
logs/history.json
```

---

# Assumptions

* Only USDT pairs supported (e.g., BTCUSDT)
* Testnet environment only (no real trading)
* Price required only for LIMIT orders
* No leverage or margin configuration included

---

# Notes

* MARKET orders are usually executed immediately (FILLED)
* LIMIT orders may remain open (NEW) until price is reached

---

# Submission Checklist

*  MARKET order working
*  LIMIT order working
*  Logs generated
*  Clean code structure
*  README included

---

#  Author

Developed as part of a Python Developer application task.

---
