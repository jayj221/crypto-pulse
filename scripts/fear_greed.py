import requests
import json
import datetime
import os

TODAY = str(datetime.date.today())

def main():
    os.makedirs("data", exist_ok=True)
    try:
        r = requests.get("https://api.alternative.me/fng/?limit=30", timeout=15)
        r.raise_for_status()
        raw = r.json().get("data", [])
        history = [
            {"date": datetime.datetime.fromtimestamp(int(d["timestamp"])).strftime("%Y-%m-%d"),
             "value": int(d["value"]),
             "label": d["value_classification"]}
            for d in raw
        ]
        latest = history[0] if history else {}
        result = {"updated": TODAY, "latest": latest, "history": history[:14]}
    except Exception as e:
        print(f"[fear_greed] Error: {e}")
        result = {"updated": TODAY, "error": str(e)}

    with open("data/fear_greed.json", "w") as f:
        json.dump(result, f, indent=2)
    print(f"[fear_greed] Done — {result.get('latest', {}).get('label', 'N/A')}")

if __name__ == "__main__":
    main()
