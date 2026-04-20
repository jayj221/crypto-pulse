import datetime
import os
import requests

TODAY = datetime.date.today()

COINS = [
    ("bitcoin", "BTC"),
    ("ethereum", "ETH"),
    ("solana", "SOL"),
    ("binancecoin", "BNB"),
    ("ripple", "XRP"),
    ("cardano", "ADA"),
    ("avalanche-2", "AVAX"),
    ("chainlink", "LINK"),
]


def fetch_market() -> list[dict]:
    ids = ",".join(c[0] for c in COINS)
    url = (
        "https://api.coingecko.com/api/v3/coins/markets"
        f"?vs_currency=usd&ids={ids}&order=market_cap_desc"
        "&price_change_percentage=1h,24h,7d"
    )
    try:
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"[CryptoPulse] API error: {e}")
        return []


def fetch_global() -> dict:
    try:
        r = requests.get("https://api.coingecko.com/api/v3/global", timeout=10)
        r.raise_for_status()
        return r.json().get("data", {})
    except Exception:
        return {}


def grade(chg_24h: float, chg_7d: float) -> str:
    score = 0
    if chg_24h > 5: score += 3
    elif chg_24h > 2: score += 2
    elif chg_24h > 0: score += 1
    elif chg_24h < -5: score -= 3
    elif chg_24h < -2: score -= 2
    else: score -= 1
    if chg_7d > 10: score += 2
    elif chg_7d > 3: score += 1
    elif chg_7d < -10: score -= 2
    elif chg_7d < -3: score -= 1
    if score >= 4: return "A"
    if score >= 2: return "B"
    if score >= 0: return "C"
    if score >= -2: return "D"
    return "F"


def sentiment_label(total_chg: float) -> str:
    if total_chg > 3: return "🟢 Bullish"
    if total_chg > 0: return "🟡 Cautiously Bullish"
    if total_chg > -3: return "🟠 Cautiously Bearish"
    return "🔴 Bearish"


def build_report(coins: list[dict], glbl: dict) -> str:
    if not coins:
        return f"# CryptoPulse — {TODAY}\n\nData unavailable.\n"

    btc = next((c for c in coins if c["symbol"] == "btc"), None)
    btc_dom = round(glbl.get("market_cap_percentage", {}).get("btc", 0), 1)
    total_mcap = glbl.get("total_market_cap", {}).get("usd", 0)
    total_vol = glbl.get("total_volume", {}).get("usd", 0)
    avg_chg = sum(c.get("price_change_percentage_24h", 0) or 0 for c in coins) / len(coins)

    lines = [
        f"# ₿ CryptoPulse — {TODAY}",
        "",
        "> Automated daily crypto market intelligence | Data: CoinGecko",
        "",
        "---",
        "",
        "## 1. Market Overview",
        "",
        "| Metric | Value |",
        "|--------|-------|",
        f"| Total Market Cap | ${total_mcap/1e12:.2f}T |" if total_mcap else "| Total Market Cap | N/A |",
        f"| 24h Volume | ${total_vol/1e9:.1f}B |" if total_vol else "| 24h Volume | N/A |",
        f"| BTC Dominance | {btc_dom}% |",
        f"| BTC Price | ${btc['current_price']:,.2f} |" if btc else "| BTC Price | N/A |",
        f"| Avg 24h Change | {avg_chg:+.2f}% |",
        f"| Market Sentiment | {sentiment_label(avg_chg)} |",
        "",
        "---",
        "",
        "## 2. Asset Breakdown",
        "",
        "| Coin | Price | 1h | 24h | 7d | Mkt Cap | Grade |",
        "|------|-------|----|----|-----|---------|-------|",
    ]

    grade_emoji = {"A": "🟢", "B": "🔵", "C": "🟡", "D": "🟠", "F": "🔴"}
    sorted_coins = sorted(coins, key=lambda x: x.get("market_cap", 0), reverse=True)

    for c in sorted_coins:
        chg1h = c.get("price_change_percentage_1h_in_currency") or 0
        chg24 = c.get("price_change_percentage_24h") or 0
        chg7d = c.get("price_change_percentage_7d_in_currency") or 0
        mcap = c.get("market_cap", 0)
        g = grade(chg24, chg7d)
        price = c.get("current_price", 0)
        price_str = f"${price:,.4f}" if price < 1 else f"${price:,.2f}"
        mcap_str = f"${mcap/1e9:.1f}B" if mcap >= 1e9 else f"${mcap/1e6:.0f}M"
        lines.append(
            f"| **{c['symbol'].upper()}** | {price_str} | {chg1h:+.2f}% | {chg24:+.2f}% "
            f"| {chg7d:+.2f}% | {mcap_str} | {grade_emoji[g]} {g} |"
        )

    lines += ["", "---", "", "## 3. Signals", ""]
    for c in sorted_coins:
        chg24 = c.get("price_change_percentage_24h") or 0
        chg7d = c.get("price_change_percentage_7d_in_currency") or 0
        high = c.get("high_24h", 0)
        low = c.get("low_24h", 0)
        price = c.get("current_price", 0)
        g = grade(chg24, chg7d)
        pct_range = round((price - low) / (high - low) * 100, 1) if high != low else 50
        action = "Strong momentum — watch for continuation" if g == "A" else \
                 "Positive bias — moderate interest" if g == "B" else \
                 "Neutral — wait for clearer signal" if g == "C" else \
                 "Weak — avoid new positions" if g == "D" else \
                 "Avoid — bearish structure"
        lines += [
            f"**{c['symbol'].upper()}** ({grade_emoji[g]} {g}) — {action}. "
            f"24h range position: {pct_range}% of day's range.",
            "",
        ]

    lines += [
        "---",
        "",
        f"*CryptoPulse | {TODAY} | Powered by CoinGecko API*",
    ]
    return "\n".join(lines)


def main():
    print(f"[CryptoPulse] Fetching data for {TODAY}...")
    coins = fetch_market()
    glbl = fetch_global()
    report = build_report(coins, glbl)
    os.makedirs("reports", exist_ok=True)
    path = f"reports/{TODAY}.md"
    with open(path, "w") as f:
        f.write(report)
    print(f"[CryptoPulse] Report saved → {path}")


if __name__ == "__main__":
    main()
