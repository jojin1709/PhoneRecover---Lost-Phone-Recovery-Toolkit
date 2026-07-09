#!/usr/bin/env python3
"""
EXIF / media GPS extractor.
Extracts GPS coordinates from images if available.
Requires: Pillow, exifread optional.
"""

import os
import json
import sys
from datetime import datetime


def extract_exif(image_path: str) -> dict:
    result = {"file": image_path, "exists": False, "gps": None}
    if not os.path.isfile(image_path):
        return result
    result["exists"] = True
    try:
        from PIL import Image
        from PIL.ExifTags import TAGS, GPSTAGS

        img = Image.open(image_path)
        raw = img._getexif() or {}
        result["exif_present"] = bool(raw)

        gps_info = {}
        for tag_id, value in raw.items():
            tag = TAGS.get(tag_id, tag_id)
            if tag == "GPSInfo":
                for gps_key in value:
                    try:
                        gps_tag = GPSTAGS.get(gps_key, gps_key)
                        gps_info[gps_tag] = value[gps_key]
                    except Exception:
                        pass

        def to_deg(val):
            try:
                d = float(val[0])
                m = float(val[1])
                s = float(val[2])
                return d + m / 60 + s / 3600
            except Exception:
                return None

        lat = lon = None
        if "GPSLatitude" in gps_info and "GPSLatitudeRef" in gps_info:
            lat = to_deg(gps_info["GPSLatitude"])
            if gps_info.get("GPSLatitudeRef") == "S" and lat is not None:
                lat = -lat
        if "GPSLongitude" in gps_info and "GPSLongitudeRef" in gps_info:
            lon = to_deg(gps_info["GPSLongitude"])
            if gps_info.get("GPSLongitudeRef") == "W" and lon is not None:
                lon = -lon

        if lat is not None and lon is not None:
            result["gps"] = {"lat": lat, "lon": lon}

        result["make"] = next(
            (raw[t] for t in raw if TAGS.get(t, t) == "Make"), None
        )
        result["model"] = next(
            (raw[t] for t in raw if TAGS.get(t, t) == "Model"), None
        )
        result["datetime_original"] = next(
            (raw[t] for t in raw if TAGS.get(t, t) == "DateTimeOriginal"), None
        )
    except Exception as e:
        result["error"] = str(e)
    return result


def scan_folder(folder: str) -> list:
    out = []
    if not folder or not os.path.isdir(folder):
        return out
    for root, _, files in os.walk(folder):
        for f in files:
            if f.lower().endswith((".jpg", ".jpeg", ".png", ".heic", ".heif", ".tiff")):
                data = extract_exif(os.path.join(root, f))
                out.append(data)
    return out


def save_results(results: list, path: str = "exif_gps_results.json"):
    data = {
        "scanned_at": datetime.now().isoformat(),
        "count": len(results),
        "with_gps": sum(1 for r in results if r.get("gps")),
        "results": results,
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"[+] Saved EXIF results: {path}")
    return path


if __name__ == "__main__":
    folder = sys.argv[1] if len(sys.argv) > 1 else "."
    print(f"[>] Scanning folder for EXIF GPS: {folder}")
    results = scan_folder(folder)
    for r in results:
        if r.get("gps"):
            print(f"[GPS] {r['file']} -> lat={r['gps']['lat']} lon={r['gps']['lon']}")
    save_results(results)
