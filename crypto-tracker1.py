import tkinter as tk
import requests
import threading
import yfinance as yf

# ---------------- CONFIG ----------------

BG_COLOR = "#0f172a"
CARD_COLOR = "#1e293b"
TEXT_COLOR = "#e2e8f0"
UP_COLOR = "#22c55e"
DOWN_COLOR = "#ef4444"

REFRESH_RATE = 60000  # 60 sec

# Crypto (CoinGecko IDs)
ASSETS = [
    ("bitcoin", "BTC"),
    ("ethereum", "ETH"),
    ("ripple", "XRP"),
    ("dogecoin", "DOGE"),
    ("litecoin", "LTC"),
    ("cardano", "ADA"),
    ("solana", "SOL"),
]

# Stocks
STOCKS = ["NVDA", "AAPL", "TSLA", "AMD", "ORCL"]

previous_prices = {}
price_widgets = {}

# ---------------- DATA FETCH ----------------

def get_crypto():
    try:
        ids = ",".join([a[0] for a in ASSETS])
        url = "https://api.coingecko.com/api/v3/simple/price"
        params = {
            "ids": ids,
            "vs_currencies": "usd",
            "include_24hr_change": "true",
        }
        return requests.get(url, params=params, timeout=10).json()
    except:
        return {}

def get_stocks():
    try:
        data = yf.download(
            tickers=" ".join(STOCKS),
            period="1d",
            interval="1m",
            progress=False,
            threads=False,
        )

        prices = {}

        for stock in STOCKS:
            close = data["Close"][stock].dropna()
            openp = data["Open"][stock].dropna()

            price = float(close.iloc[-1])
            change = ((price - openp.iloc[0]) / openp.iloc[0]) * 100

            prices[stock] = (price, change)

        return prices

    except Exception as e:
        print("Stock error:", e)
        return {}

# ---------------- UI UPDATE ----------------

def update_tile(symbol, price, change):

    old = previous_prices.get(symbol)

    color = TEXT_COLOR
    if change > 0:
        color = UP_COLOR
    elif change < 0:
        color = DOWN_COLOR

    price_widgets[symbol].config(
        text=f"{symbol}\n${price:,.2f}\n{change:+.2f}%",
        fg=color
    )

    previous_prices[symbol] = price


def refresh_data():

    crypto = get_crypto()
    stocks = get_stocks()

    def apply():
        for cid, sym in ASSETS:
            if cid in crypto:
                p = crypto[cid]["usd"]
                c = crypto[cid]["usd_24h_change"]
                update_tile(sym, p, c)

        for sym, (p, c) in stocks.items():
            update_tile(sym, p, c)

        root.after(REFRESH_RATE, refresh)

    root.after(0, apply)


def refresh():
    threading.Thread(target=refresh_data, daemon=True).start()

# ---------------- UI ----------------

root = tk.Tk()
root.attributes("-fullscreen", True)
root.configure(bg=BG_COLOR)
root.bind("<Escape>", lambda e: root.destroy())

root.update_idletasks()

SCREEN_W = root.winfo_screenwidth()
SCREEN_H = root.winfo_screenheight()

COLUMNS = 4
ROWS = 3

PAD_X = 20
PAD_Y = 20

CARD_W = (SCREEN_W // COLUMNS) - (PAD_X * 2)
CARD_H = (SCREEN_H // ROWS) - (PAD_Y * 2)

main = tk.Frame(root, bg=BG_COLOR)
main.place(relx=0.5, rely=0.5, anchor="center")

ORDER = [a[1] for a in ASSETS] + STOCKS

for i, symbol in enumerate(ORDER):

    r = i // COLUMNS
    c = i % COLUMNS

    card = tk.Frame(
        main,
        bg=CARD_COLOR,
        width=CARD_W,
        height=CARD_H
    )

    card.grid(row=r, column=c, padx=PAD_X, pady=PAD_Y)
    card.grid_propagate(False)

    label = tk.Label(
        card,
        text=f"{symbol}\nLoading...",
        font=("Segoe UI", int(CARD_H * 0.16), "bold"),
        bg=CARD_COLOR,
        fg=TEXT_COLOR,
        justify="center"
    )

    label.place(relx=0.5, rely=0.5, anchor="center")

    price_widgets[symbol] = label

# ---------------- START ----------------

refresh()
root.mainloop()
