
import os
import json
import requests
from pathlib import Path
from html import escape

BOT_TOKEN = os.environ["BOT_TOKEN"]
TALASANJ_KEY = os.environ["TALASANJ_KEY"]
CHANNEL_ID = "@FaravaharCoin"

API_URL = "https://talasanj.info/api/v1/prices"
TELEGRAM_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
STATE_FILE = Path("previous_prices.json")

SYMBOLS = {
    "gram18": "طلای ۱۸ عیار (هر گرم)",
    "coin_full": "سکه امامی",
    "coin_half": "نیم‌ سکه",
    "coin_quarter": "ربع‌ سکه",
    "usd": "دلار آزاد",
}

def get_prices():
    response = requests.get(
        API_URL,
        headers={"Authorization": f"Bearer {TALASANJ_KEY}"},
        timeout=20
    )
    response.raise_for_status()
    return response.json()["prices"]

def send_message(message):
    response = requests.post(
        TELEGRAM_URL,
        json={
            "chat_id": CHANNEL_ID,
            "text": message,
            "parse_mode": "HTML",
            "disable_web_page_preview": True
        },
        timeout=20
    )
    response.raise_for_status()
    if not response.json().get("ok"):
        raise RuntimeError("Telegram rejected the message")

def main():
    previous = {}
    if STATE_FILE.exists():
        previous = json.loads(STATE_FILE.read_text())

    prices = get_prices()
    current = {}
    lines = [
        "<b>📊 قیمت طلا، سکه و دلار</b>",
        ""
    ]

    for symbol, title in SYMBOLS.items():
        item = prices[symbol]
        value = int(float(str(item["price"]).replace(",", "")))
        current[symbol] = value

        old = previous.get(symbol)

        if old is None or value == old:
            arrow = "ـ"
            color = None
        elif value > old:
            arrow = "↑"
            color = "#16A34A"
        else:
            arrow = "↓"
            color = "#DC2626"

        if color:
            arrow = f'<span style="color:{color}">{arrow}</span>'

        lines.append(
            f"{arrow} {escape(title)}: {value:,} تومان"
        )

    lines += [
        "",
        "⚠️ قیمت‌ها تقریبی‌اند و ممکن است با بازار تفاوت داشته باشند.",
        "جهت استعلام دقیق قیمت و مشاوره با شماره 09129572767 تماس بگیرید."
    ]

    send_message("\n".join(lines))

    STATE_FILE.write_text(
        json.dumps(current, ensure_ascii=False, indent=2)
    )

    print("Published successfully")

if __name__ == "__main__":
    main()
