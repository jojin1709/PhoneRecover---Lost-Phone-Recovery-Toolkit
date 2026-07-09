#!/usr/bin/env python3
"""
Device history / timeline importer.
Imports Google Takeout Timeline JSON and summarizes last-known paths.
"""

import os
import json
from datetime import datetime
from urllib.parse import urlparse


def load_json(path: str):
    if not os.path.isfile(path):
        print(f"[-] File not found: {path}")
        return None
    with open(path, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except Exception as e:
            print(f"[-] JSON parse error: {e}")
            return None


def summarize_google_timeline_locations(data: dict):
    print("GOOGLE TIMELINE LOCATION SUMMARY")
    print("=" * 60)
    try:
        locations = (
            data.get("locations", [])
            if isinstance(data, dict)
            else (data if isinstance(data, list) else [])
        )
    except Exception:
        locations = []
    if not locations:
        print("[-] No locations found in loaded data.")
        return []
    summary = []
    for loc in locations[:20]:
        timestamp = loc.get("timestamp", loc.get("time", ""))
        lat = loc.get("latitude", loc.get("lat"))
        lon = loc.get("longitude", loc.get("lon"))
        if lat is None or lon is None:
            continue
        summary.append({"timestamp": timestamp, "lat": float(lat), "lon": float(lon)})
        print(f"  {timestamp} -> {lat}, {lon}")
    return summary


def export_timeline_summary(summary: list, path="timeline_summary.json"):
    data = {
        "exported_at": datetime.now().isoformat(),
        "count": len(summary),
        "locations": summary,
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"[+] Timeline summary saved: {path}")


if __name__ == "__main__":
    path = input("Path to Google Timeline JSON file: ").strip()
    data = load_json(path)
    if data is None:
        sys.exit(1)
    summary = summarize_google_timeline_locations(data)
    export_timeline_summary(summary)
