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

                feature = {
                    "type": "Feature",
                    "properties": {
                        "Date Time": cols[0],
                        "Latitude": lat,
                        "Longitude": lon,
                        "Depth (KM)": float(cols[3]),
                        "Magnitude": float(cols[4]),
                        "Location": cols[5]
                    },
                    "geometry": {
                        "type": "Point",
                        "coordinates": [lon, lat, float(cols[3])]
                    }
                }

                features.append(feature)

            except Exception:
                continue

    print(f"Parsed features: {len(features)}")

    return {
        "type": "FeatureCollection",
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "features": features
    }

def save_geojson(data):
    path = "data/earthquakes.geojson"

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"Saved {len(data['features'])} records")


if __name__ == "__main__":
    data = parse_table()
    save_geojson(data)
