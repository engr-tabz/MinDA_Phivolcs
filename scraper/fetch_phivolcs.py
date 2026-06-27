import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

URL = "https://earthquake.phivolcs.dost.gov.ph/"

def parse_table():
    import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

headers = {
    "User-Agent": "Mozilla/5.0"
}

r = requests.get(
    URL,
    headers=headers,
    timeout=30,
    verify=False
)
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "html.parser")

    # Try to find first table (PHIVOLCS uses HTML tables for listings)
    table = soup.find("table")
    if not table:
        raise Exception("No table found on page. HTML structure may have changed.")

    rows = table.find_all("tr")[1:]  # skip header

    features = []

    for row in rows:
        cols = [c.get_text(strip=True) for c in row.find_all("td")]
        
        if len(cols) < 6:
            continue

        # ⚠️ Adjust indexes if PHIVOLCS layout differs
        date_time = cols[0]
        latitude = float(cols[1])
        longitude = float(cols[2])
        depth = float(cols[3])
        magnitude = float(cols[4])
        location = cols[5]

        feature = {
            "type": "Feature",
            "properties": {
                "Date Time": date_time,
                "Latitude": latitude,
                "Longitude": longitude,
                "Depth (KM)": depth,
                "Magnitude": magnitude,
                "Location": location
            },
            "geometry": {
                "type": "Point",
                "coordinates": [longitude, latitude, depth]
            }
        }

        features.append(feature)

    geojson = {
        "type": "FeatureCollection",
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "features": features
    }

    return geojson


def save_geojson(data):
    path = "data/earthquakes.geojson"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Saved {len(data['features'])} records")


if __name__ == "__main__":
    data = parse_table()
    save_geojson(data)
