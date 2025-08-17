import tkinter as tk
import requests
import time

# Coins to track (must match CoinGecko IDs)
COINS = ["bitcoin", "ethereum", "dogecoin", "litecoin"]
COIN_LABELS = ["BTC", "ETH", "DOGE", "LTC"]
CURRENCY = "usd"
REFRESH_RATE = 60_000  # 60 seconds (in ms)

def get_prices():
    try:
        url = "https://api.coingecko.com/api/v3/simple/price"
        params = {"ids": ",".join(COINS), "vs_currencies": CURRENCY}
        data = requests.get(url, params=params, timeout=10).json()
        return data
    except Exception as e:
        return {"error": str(e)}

def update_prices():
    data = get_prices()
    if "error" in data:
        label.config(fg="red")
        text = f"Error: {data['error']}"
    else:
        label.config(fg="grey")
        lines = [f"{label}: ${data[coin][CURRENCY]:,.2f}" for coin, label in zip(COINS, COIN_LABELS)]
        text = "\n".join(lines)
    label.config(text=text)
    root.after(REFRESH_RATE, update_prices)

# --- Tkinter GUI setup ---
root = tk.Tk()
root.attributes('-fullscreen', True)  # Fullscreen mode
root.bind("<Escape>", lambda e: root.destroy())  # ESC key to exit
root.configure(bg="black")

label = tk.Label(
    root,
    font=("Arial", 32, "bold"),
    fg="grey",   # Text color
    bg="black",
    justify="left",
    anchor="nw"  # Top-left corner alignment
)
label.pack(fill="both", expand=True, padx=20, pady=20)

update_prices()
root.mainloop()

