import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import urllib3

URL = "https://earthquake.phivolcs.dost.gov.ph/"

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def parse_table():
    headers = {"User-Agent": "Mozilla/5.0"}

    r = requests.get(URL, headers=headers, timeout=30, verify=False)
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "html.parser")

    tables = soup.find_all("table")

    if not tables:
        raise Exception("No tables found at all on page")

    features = []

    for table in tables:
        rows = table.find_all("tr")

        for row in rows:
            cols = [c.get_text(strip=True) for c in row.find_all("td")]

            # skip non-data rows
            if len(cols) < 6:
                continue

            try:
                lat = float(cols[1])
                lon = float(cols[2])

            feature = build_feature(
                cols[0],
                lat,
                lon,
                float(cols[3]),
                float(cols[4]),
                cols[5]
            )
            
            features.append(feature)

            except Exception:
                continue

    print(f"Parsed features: {len(features)}")

    return {
        "type": "FeatureCollection",
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "features": features
    }

def build_feature(date_time, lat, lon, depth, mag, location):
    # Example PHIVOLCS format:
    # "28 June 2026 - 03:15 PM"
    dt = datetime.strptime(date_time, "%d %B %Y - %I:%M %p")

    date_part = dt.strftime("%Y%m%d")   # YYYYMMDD
    time_part = dt.strftime("%H:%M")    # HH:MM (24-hour)

    return {
        "type": "Feature",
        "properties": {
            "date": date_part,
            "time": time_part,
            "latitude": lat,
            "longitude": lon,
            "depth_km": depth,
            "magnitude": mag,
            "location": location
        },
        "geometry": {
            "type": "Point",
            "coordinates": [float(lon), float(lat), float(depth)]
        }
    }
    save_geojson(data)
