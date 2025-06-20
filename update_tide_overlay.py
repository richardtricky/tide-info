import requests
from datetime import datetime, timezone

# ---- CONFIGURE THESE VALUES ----
API_KEY = "212ed417-7d00-412b-92f9-2d52852436b5"
LAT = 54.5809           # Replace with your latitude
LON = -3.5807           # Replace with your longitude
# ------------------------------

def fetch_tide_data(api_key, lat, lon):
    url = f"https://api.stormglass.io/v2/tide/extremes"
    headers = {"Authorization": api_key}
    params = {
        "lat": lat,
        "lng": lon,
        "start": datetime.now(timezone.utc).isoformat(),
        "end": (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
    }
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()

def format_tide_text(data):
    now = datetime.now(timezone.utc)
    upcoming = [
        e for e in data.get("extremes", [])
        if datetime.fromisoformat(e["date"]) > now
    ][:2]
    return " | ".join([
        f"{e['type'].capitalize()} Tide: {datetime.fromisoformat(e['date']).strftime('%H:%M')}"
        for e in upcoming
    ]).strip()

def main():
    try:
        data = fetch_tide_data(API_KEY, LAT, LON)
        text = format_tide_text(data).strip()
        print(f"Updating tide.txt with: {text}")

        # Write to file
        with open("tide.txt", "w", encoding="utf-8") as f:
            f.write(text)

    except Exception as e:
        print(f"Error fetching or writing tide data: {e}")

if __name__ == "__main__":
    main()
