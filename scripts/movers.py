import requests
import json
import datetime
import os

TODAY = str(datetime.date.today())
BASE = "https://api.coingecko.com/api/v3"

def main():
    os.makedirs("data", exist_ok=True)
    try:
        gainers_url = f"{BASE}/coins/markets?vs_currency=usd&order=price_change_percentage_24h_desc&per_page=250&page=1&price_change_percentage=24h"
        r = requests.get(gainers_url, timeout=20)
        r.raise_for_status()
        coins = r.json()
        gainers = [
            {"symbol": c["symbol"].upper(), "name": c["name"],
             "price": c["current_price"],
             "chg_24h": round(c.get("price_change_percentage_24h") or 0, 2),
             "mcap": c.get("market_cap", 0)}
            for c in coins if c.get("price_change_percentage_24h") is not None
        ]
        top_gainers = sorted(gainers, key=lambda x: x["chg_24h"], reverse=True)[:10]
        top_losers = sorted(gainers, key=lambda x: x["chg_24h"])[:10]
        result = {"date": TODAY, "top_gainers": top_gainers, "top_losers": top_losers}
    except Exception as e:
        print(f"[movers] Error: {e}")
        result = {"date": TODAY, "error": str(e)}

    with open("data/movers.json", "w") as f:
        json.dump(result, f, indent=2)
    print(f"[movers] Done — {len(result.get('top_gainers', []))} gainers logged")

if __name__ == "__main__":
    main()
