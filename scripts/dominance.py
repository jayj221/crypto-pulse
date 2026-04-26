import requests
import json
import datetime
import os

TODAY = str(datetime.date.today())

def main():
    os.makedirs("data", exist_ok=True)
    try:
        r = requests.get("https://api.coingecko.com/api/v3/global", timeout=15)
        r.raise_for_status()
        data = r.json().get("data", {})
        dom = data.get("market_cap_percentage", {})
        result = {
            "date": TODAY,
            "btc_dominance": round(dom.get("btc", 0), 2),
            "eth_dominance": round(dom.get("eth", 0), 2),
            "total_mcap_usd": data.get("total_market_cap", {}).get("usd", 0),
            "total_volume_usd": data.get("total_volume", {}).get("usd", 0),
            "active_coins": data.get("active_cryptocurrencies", 0),
        }
    except Exception as e:
        print(f"[dominance] Error: {e}")
        result = {"date": TODAY, "error": str(e)}

    with open("data/market_dominance.json", "w") as f:
        json.dump(result, f, indent=2)
    print(f"[dominance] Done — BTC: {result.get('btc_dominance')}%")

if __name__ == "__main__":
    main()
