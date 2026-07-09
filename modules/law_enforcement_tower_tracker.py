#!/usr/bin/env python3
"""
Law Enforcement Tower Tracker - converts cell data to GPS
for active investigations using IMEI/phone number.
"""

import os
import json
import time
import requests
from datetime import datetime


def save_json(data, path="tower_track_results.json"):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"[+] Saved tower results: {path}")


def unwired_geo(token, mcc, mnc, lac, cell_id):
    url = "https://us1.unwiredlabs.com/v2/process.php"
    payload = {
        "token": token,
        "radio": "LTE",
        "mcc": int(mcc),
        "mnc": int(mnc),
        "lac": int(lac),
        "cells": [
            {
                "lac": int(lac),
                "cid": int(cell_id),
                "mnc": int(mnc),
                "mcc": int(mcc),
                "radio": "LTE",
                "signal": -70,
            }
        ],
        "address": 1,
    }
    try:
        r = requests.post(url, json=payload, timeout=20)
        if r.status_code == 200 and r.text.strip():
            data = r.json()
            if data.get("status") == "ok" and data.get("lat") and data.get("lon"):
                return {
                    "source": "unwiredlabs",
                    "lat": float(data["lat"]),
                    "lon": float(data["lon"]),
                    "address": data.get("address", ""),
                    "raw": data,
                }
    except Exception as e:
        print(f"[-] UnwiredLabs failed: {e}")
    return None


def opencellid_geo(token, mcc, mnc, lac, cell_id):
    urls = [
        f"https://api.opencellid.org/cell/get?key={token}&mcc={mcc}&mnc={mnc}&lac={lac}&cell_id={cell_id}&format=json",
        f"https://api.opencellid.org/cell/get?key={token}&mcc={mcc}&mnc={mnc}&lac={lac}&cellid={cell_id}&format=json",
    ]
    for url in urls:
        try:
            r = requests.get(url, timeout=20)
            if r.status_code == 200 and r.text.strip():
                data = r.json()
                lat = data.get("lat") or data.get("latitude")
                lon = data.get("lon") or data.get("longitude")
                if lat and lon:
                    return {
                        "source": "opencellid",
                        "lat": float(lat),
                        "lon": float(lon),
                        "address": data.get("address", data.get("location", "")),
                        "raw": data,
                    }
        except Exception:
            continue
    return None


def cell_tower_to_gps(lac, cell_id, mcc="405", mnc="20", token=""):
    print(f"[>] Converting tower to GPS: LAC={lac}, CellID={cell_id}, MCC={mcc}, MNC={mnc}")
    token = token or os.environ.get("OPENCELLID_TOKEN", "pk.c6319034a85d5790a56b6ebccc122d81")
    
    result = {
        "lac": lac,
        "cell_id": cell_id,
        "mcc": mcc,
        "mnc": mnc,
        "checked_at": datetime.now().isoformat(),
        "gps": None,
    }
    
    r1 = unwired_geo(token, mcc, mnc, lac, cell_id)
    if r1:
        result["gps"] = r1
        print(f"[+] GPS: {r1['lat']}, {r1['lon']} ({r1.get('address','')})")
        return result
    
    r2 = opencellid_geo(token, mcc, mnc, lac, cell_id)
    if r2:
        result["gps"] = r2
        print(f"[+] GPS: {r2['lat']}, {r2['lon']} ({r2.get('address','')})")
        return result
    
    print("[-] No GPS result from any source")
    return result


def build_jio_request(phone, imei, carrier="jio"):
    helpline_map = {
        "airtel": "121",
        "jio": "199",
        "vi": "199",
        "bsnl": "1800-180-1503",
    }
    carrier = (carrier or "jio").lower()
    helpline = helpline_map.get(carrier, "199")
    req = {
        "carrier": carrier.upper(),
        "helpline": helpline,
        "phone": phone,
        "imei": imei,
        "official_email": "[Check carrier website for nodal officer email]",
        "required_data": [
            "Last tower LAC + Cell ID",
            "Last network activity timestamp",
            "ICCID/IMSI of currently active SIM",
            "Duplicate SIM request record",
            "Full CDR from date of theft",
            "IMEI activation/deactivation log",
        ],
        "legal_basis": "Section 91 CrPC / IT Act",
        "note": "Use this when submitting official request to carrier for tower data.",
    }
    path = f"{carrier}_tower_request.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(req, f, indent=2)
    print(f"[+] {carrier.upper()} tower request template saved: {path}")
    return req


def bssid_geo_lookup(bssids):
    print(f"[>] Looking up {len(bssids)} BSSIDs...")
    results = []
    for bssid in bssids:
        results.append({
            "bssid": bssid,
            "note": "Requires Google Geolocation API key or official Google data request",
            "action": "Request Google geolocation data with warrant for BSSID locations",
        })
    path = "bssid_geo_results.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"[+] BSSID lookup template saved: {path}")
    return results


if __name__ == "__main__":
    print("LAW ENFORCEMENT TOWER TRACKER")
    print("=" * 60)
    print("1. Convert LAC+Cell ID to GPS")
    print("2. Generate official carrier data request")
    print("3. BSSID geolocation template")
    choice = input("Choice [1-3]: ").strip()
    
    if choice == "1":
        lac = input("LAC (from carrier): ").strip()
        cell = input("Cell ID (from carrier): ").strip()
        if lac and cell:
            res = cell_tower_to_gps(lac, cell)
            save_json(res)
        else:
            print("[-] LAC and Cell ID required")
    elif choice == "2":
        phone = input("Phone number: ").strip()
        imei = input("IMEI: ").strip()
        carrier = input("Carrier (jio/airtel/vi/bsnl): ").strip() or "jio"
        build_jio_request(phone, imei, carrier)
    elif choice == "3":
        print("[i] For BSSID, use the LAN scanner or provide BSSID list")
        bssids = input("BSSIDs (comma separated, or Enter to skip): ").strip()
        bssid_geo_lookup([b.strip() for b in bssids.split(",") if b.strip()])
    else:
        print("[-] Invalid choice")
