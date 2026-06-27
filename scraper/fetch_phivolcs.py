import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import urllib3

URL = "https://earthquake.phivolcs.dost.gov.ph/"

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def build_feature(date_time, lat, lon, depth, mag, location):
    """
    Converts the PHIVOLCS date/time string into separate date and time fields.

    Expected input format:
    "28 June 2026 - 03:15 PM"

    Output:
    date -> YYYYMMDD
    time -> HH:MM (24-hour)
    """

    dt = datetime.strptime(date_time, "%d %B %Y - %I:%M %p")

    date_part = dt.strftime("%Y%m%d")
    time_part = dt.strftime("%H:%M")

    return {
        "type": "Feature",
        "properties": {
            "date": date_part,
            "time": time_part,
            "latitude": float(lat),
            "longitude": float(lon),
            "depth_km": float(depth),
            "magnitude": float(mag),
            "location": location
        },
        "geometry": {
            "type": "Point",
            "coordinates": [float(lon), float(lat), float(depth)]
        }
    }


def parse_table():
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    r = requests.get(URL, headers=headers, timeout=30, verify=False)
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "html.parser")

    tables = soup.find_all("table")

    if not tables:
        raise Exception("No tables found on the page.")

    features = []

    for table in tables:
        rows = table.find_all("tr")

        for row in rows:
            cols = [c.get_text(strip=True) for c in row.find_all("td")]

            # Skip header or incomplete rows
            if len(cols) < 6:
                continue

            try:
                feature = build_feature(
                    cols[0],          # Date Time
                    cols[1],          # Latitude
                    cols[2],          # Longitude
                    cols[3],          # Depth
                    cols[4],          # Magnitude
                    cols[5]           # Location
                )

                features.append(feature)

            except Exception as e:
                print(f"Skipping row: {cols}")
                print(f"Reason: {e}")
                continue

    print(f"Parsed features: {len(features)}")

    return {
        "type": "FeatureCollection",
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "features": features
    }


def save_geojson(data, filename="earthquakes.geojson"):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    print(f"Saved {len(data['features'])} features to {filename}")


if __name__ == "__main__":
    data = parse_table()
    save_geojson(data)
