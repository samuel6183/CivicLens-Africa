"""Explicit ingestion commands; no external requests on server startup."""
import argparse
import json
import math
from datetime import datetime, timezone
from urllib.request import urlopen, Request
from urllib.parse import urlparse
from pathlib import Path
from backend.store import upsert

INDICATORS = {
    "NY.GDP.MKTP.KD.ZG": ("GDP growth", "Percent, annual"),
    "FP.CPI.TOTL.ZG": ("Consumer price inflation", "Percent, annual"),
    "SP.POP.TOTL": ("Population", "People"),
}

def timestamp():
    return datetime.now(timezone.utc).isoformat()

def fetch_json(url):
    with urlopen(Request(url, headers={"User-Agent":"CivicLens-Africa/0.1"}), timeout=30) as response:
        return json.loads(response.read(10_000_001))

def world_bank(fetch=fetch_json):
    records = []
    now = timestamp()
    for code, (name, unit) in INDICATORS.items():
        url = f"https://api.worldbank.org/v2/country/KEN/indicator/{code}?format=json&date=2000:2026&per_page=100"
        payload = fetch(url)
        if not isinstance(payload, list) or len(payload) != 2 or not isinstance(payload[1], list):
            raise ValueError(f"Unexpected World Bank response for {code}")
        for row in payload[1]:
            value = row.get("value")
            if value is None:
                continue
            if not isinstance(value, (float,int)) or isinstance(value,bool) or not math.isfinite(value):
                raise ValueError("Invalid indicator value")
            year = str(row["date"])
            if not year.isdigit() or len(year)!=4 or row.get("countryiso3code")!="KEN":
                raise ValueError("Unexpected geography or period")
            records.append(dict(country="KE", category="Economy", title=f"{name} — Kenya ({year})",
                publisher="World Bank", url=f"https://data.worldbank.org/indicator/{code}?locations=KE",
                published_date="", summary=f"Annual observation for {year}; release date not supplied.",
                indicator=code, period=year, value=value, unit=unit, retrieved_at=now))
    upsert(records)
    return len(records)

def import_documents(path):
    rows = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(rows,list):
        raise ValueError("Expected a JSON array")
    records = []
    for row in rows:
        fields = ("country","category","title","publisher","url","published_date","summary")
        if not all(isinstance(row.get(k),str) for k in fields):
            raise ValueError("Missing or invalid document metadata")
        url = urlparse(row["url"])
        if url.scheme != "https" or not url.hostname or url.username or url.password:
            raise ValueError("Document source must use HTTPS")
        if row["country"]!="KE" or row["category"] not in ("Procurement","Public finance","Economy","Legislation"):
            raise ValueError("Unsupported country or category")
        if not all(row[k].strip() for k in ("title","publisher","summary")):
            raise ValueError("Empty document metadata")
        if row["published_date"]:
            datetime.strptime(row["published_date"], "%Y-%m-%d")
        records.append({**{k:row[k] for k in fields}, "indicator":"","period":"","value":None,"unit":"","retrieved_at":timestamp()})
    upsert(records)
    return len(records)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("source", choices=["world-bank","documents"])
    parser.add_argument("--file")
    args = parser.parse_args()
    if args.source=="documents" and not args.file:
        parser.error("--file required for documents")
    count = world_bank() if args.source=="world-bank" else import_documents(args.file)
    print(f"Processed {count} records (including updates).")
