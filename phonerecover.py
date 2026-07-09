#!/usr/bin/env python3
"""
PhoneRecover - Open Source Device Recovery Toolkit
--------------------------------------------------
Helps recover lost/stolen Android/iOS devices using:
  - IMEI / TAC blacklist checks
  - Real carrier request scripts for Airtel/Jio/VI/BSNL
  - Police-ready FIR evidence extraction
  - UnwiredLabs live cell-tower -> GPS lookup (if LAC/Cell ID available)
  - Google Find My Device / Apple Find My links
  - Resale-marketplace monitoring for stolen devices

Usage:
  python phonerecover.py

Notes:
  * This tool does not claim to "hack" or "intercept" anything.
  * Coordinates can only be obtained via legitimate APIs with valid data.
  * Carrier/police actions require human cooperation.

Author: PHOENIX Recovery Framework
License: MIT
"""

import os
import sys
import re
import json
import time
import webbrowser
import requests
from datetime import datetime
from urllib.parse import quote


# ─────────────────────────────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────────────────────────────

CONFIG = {
    "imei": "",
    "google_email": "",
    "apple_id": "",
    "phone_number": "",
    "phone_model": "",
    "carrier": "jio",
    "opencellid_token": "",
    "output_dir": "output",
}

_user_config_path = os.path.join(os.getcwd(), "user_config.json")
if os.path.isfile(_user_config_path):
    try:
        with open(_user_config_path, "r", encoding="utf-8") as _f:
            _user = json.load(_f)
        CONFIG.update({k: v for k, v in _user.items() if v})
    except Exception:
        pass

CARRIER_MAP = {
    "airtel": ("121", "405", "15"),
    "jio": ("199", "405", "20"),
    "vi": ("199", "405", "11"),
    "bsnl": ("1800-180-1503", "405", "74"),
}


# ─────────────────────────────────────────────────────────────────────
# ENGINE
# ─────────────────────────────────────────────────────────────────────

def log(msg: str):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{ts}] {msg}"
    print(entry)


def save_json(filename: str, data: dict):
    os.makedirs(CONFIG["output_dir"], exist_ok=True)
    path = os.path.join(CONFIG["output_dir"], filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    log(f"[+] Saved: {path}")


def validate_imei(imei: str) -> bool:
    return bool(re.fullmatch(r"\d{15}", imei))


def validate_email(email: str) -> bool:
    return bool(re.fullmatch(r"[^@]+@[^@]+\.[^@]+", email))


def ensure_output_dir():
    os.makedirs(CONFIG["output_dir"], exist_ok=True)


# ─────────────────────────────────────────────────────────────────────
# MODULE 1: IMEI + DEVICE VALIDATION
# ─────────────────────────────────────────────────────────────────────

class IMEIChecker:
    @staticmethod
    def check(imei: str) -> dict:
        result = {"imei": imei, "format_valid": validate_imei(imei)}
        if not result["format_valid"]:
            log("[-] Invalid IMEI format. Expected 15 digits.")
            return result

        result["tac"] = imei[:8]
        result["digits"] = len(imei)
        log(f"[+] IMEI format OK. TAC: {imei[:8]}")

        # Check public GSMA-style status via iunlocker
        try:
            r = requests.post(
                "https://iunlocker.com/en/gsma_blacklist_check.php",
                data={"imei": imei},
                headers={"User-Agent": "Mozilla/5.0"},
                timeout=10,
            )
            txt = r.text.lower()
            result["gsma_blacklisted"] = "blacklist" in txt or "blocked" in txt
            if result["gsma_blacklisted"]:
                log("[!] IMEI may be BLACKLISTED globally.")
            else:
                log("[+] IMEI not reported as blacklisted in public check.")
        except Exception as e:
            result["gsma_error"] = str(e)
            log(f"[-] GSMA check failed: {e}")

        save_json("imei_check.json", result)
        return result


# ─────────────────────────────────────────────────────────────────────
# MODULE 2: UNWIREDLABS / OPENCELLID LIVE LOOKUP
# ─────────────────────────────────────────────────────────────────────

class CellTowerLookup:
    @staticmethod
    def lookup(
        mcc: str = "405",
        mnc: str = "15",
        lac: str = "",
        cell_id: str = "",
        token: str = "",
    ) -> dict:
        if not lac or not cell_id:
            log("[-] Missing LAC or Cell ID. Get them from your carrier first.")
            return {}

        token = token or CONFIG.get("opencellid_token", "")
        result = {
            "mcc": mcc,
            "mnc": mnc,
            "lac": lac,
            "cell_id": cell_id,
        }

        # Primary: UnwiredLabs (OpenCellID commercial path)
        try:
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
            r = requests.post(
                url,
                json=payload,
                headers={
                    "User-Agent": "Mozilla/5.0",
                    "Accept": "application/json",
                },
                timeout=20,
            )
            if r.status_code == 200 and r.text.strip():
                try:
                    data = r.json()
                    result["unwiredlabs"] = data
                    if data.get("status") == "ok" and data.get("lat") and data.get("lon"):
                        result["lat"] = float(data["lat"])
                        result["lon"] = float(data["lon"])
                        result["address"] = data.get("address", "")
                        log(f"[+] Live GPS: lat={data['lat']} lon={data['lon']}")
                        if data.get("address"):
                            log(f"    Address: {data['address']}")
                    else:
                        log(f"[-] UnwiredLabs: {data.get('message','no match')}")
                except Exception as e:
                    result["unwiredlabs_raw"] = r.text[:500]
                    log(f"[-] UnwiredLabs parse error: {e}")
            else:
                result["unwiredlabs_status"] = r.status_code
        except Exception as e:
            result["unwiredlabs_error"] = str(e)
            log(f"[-] UnwiredLabs request failed: {e}")

        # Fallback: OpenCellID direct
        if not result.get("lat"):
            try:
                url2 = (
                    "https://api.opencellid.org/cell/get"
                    f"?key={token}&mcc={mcc}&mnc={mnc}&lac={lac}&cellid={cell_id}&format=json"
                )
                r2 = requests.get(url2, headers={"User-Agent": "Mozilla/5.0"}, timeout=20)
                if r2.status_code == 200 and r2.text.strip():
                    try:
                        data2 = r2.json()
                        lat = data2.get("lat") or data2.get("latitude")
                        lon = data2.get("lon") or data2.get("longitude")
                        if lat and lon:
                            result["lat"] = float(lat)
                            result["lon"] = float(lon)
                            result["opencellid"] = data2
                            log(f"[+] OpenCellID returned lat={lat} lon={lon}")
                    except Exception:
                        pass
            except Exception:
                pass

        save_json("cell_tower_lookup.json", result)
        return result


# ─────────────────────────────────────────────────────────────────────
# MODULE 3: GOOGLE FIND MY DEVICE DEEP LINKS
# ─────────────────────────────────────────────────────────────────────

class GoogleFindMyDevice:
    @staticmethod
    def links(email: str, imei: str) -> dict:
        if not validate_email(email):
            log("[-] Invalid Google email.")
            return {}

        base = "https://www.google.com/android/find"
        links = {
            "find_my_device": f"{base}?u=0&hl=en",
            "account_device_activity": "https://myaccount.google.com/device-activity",
            "maps_timeline": "https://www.google.com/maps/timeline",
            "google_photos": "https://photos.google.com",
        }
        log(f"[+] Google recovery links ready for {email}")

        result = {
            "email": email,
            "imei": imei,
            "links": links,
        }
        save_json("google_links.json", result)
        return result

    @staticmethod
    def open():
        email = CONFIG.get("google_email", "")
        if validate_email(email):
            webbrowser.open("https://www.google.com/android/find?u=0&hl=en")
            log("[+] Opened Google Find My Device in browser.")


# ─────────────────────────────────────────────────────────────────────
# MODULE 4: CARRIER REQUEST SCRIPTS
# ─────────────────────────────────────────────────────────────────────

class CarrierToolkit:
    @staticmethod
    def script(carrier: str, phone_number: str, imei: str) -> str:
        carrier = (carrier or "airtel").lower()
        helpline, mcc, mnc = CARRIER_MAP.get(carrier, ("121", "405", "15"))

        ensure_output_dir()
        script_path = os.path.join(CONFIG["output_dir"], f"carrier_script_{carrier}.txt")
        lines = [
            "CARRIER REQUEST SCRIPT",
            "=" * 60,
            f"Carrier  : {carrier.upper()}",
            f"Helpline : {helpline}",
            f"Phone    : {phone_number}",
            f"IMEI     : {imei}",
            f"MCC      : {mcc}",
            f"MNC      : {mnc}",
            "",
            "Ask support for:",
            "  1. Last tower LAC + Cell ID for this IMEI/phone number",
            "  2. ICCID / IMSI of the currently active SIM",
            "  3. Last network activity timestamp",
            "  4. Whether a duplicate SIM was issued after theft",
            "  5. Approximate location / address for the last tower",
            "",
            "Sample script:",
            f"  'Hello, my phone (IMEI {imei}) was stolen.",
            f"   I need the last tower LAC + Cell ID for number {phone_number}.",
            "   This is for a police investigation. Please help.'",
            "",
            f"Note: MCC={mcc}, MNC={mnc} for {carrier.upper()} India.",
        ]

        with open(script_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        log(f"[+] Carrier script saved: {script_path}")
        return script_path


# ─────────────────────────────────────────────────────────────────────
# MODULE 5: POLICE / FIR REPORT
# ─────────────────────────────────────────────────────────────────────

class PoliceReport:
    @staticmethod
    def generate(
        imei: str,
        email: str,
        phone_number: str,
        model: str,
        carrier: str,
        location_hint: str = "",
    ) -> str:
        ensure_output_dir()
        report_path = os.path.join(CONFIG["output_dir"], "police_report.txt")
        now = datetime.now().isoformat()

        lines = [
            "PHONE RECOVERY - POLICE / FIR REPORT",
            "=" * 60,
            f"Generated : {now}",
            f"IMEI      : {imei}",
            f"Email     : {email}",
            f"Phone     : {phone_number}",
            f"Model     : {model}",
            f"Carrier   : {carrier}",
            "",
            "[INCIDENT SUMMARY]",
            "  The above device was lost / stolen. The owner has reason to",
            "  believe the device is still active or may have been moved",
            "  within the area shown below.",
            "",
        ]

        if location_hint:
            lines += [
                "[LAST KNOWN LOCATION / HINT]",
                f"  {location_hint}",
                "",
            ]

        lines += [
            "[REQUESTED ACTIONS]",
            "  1. File FIR under IMEI and phone number.",
            "  2. Request CCTV from last known location / relevant sites.",
            "  3. Request carrier to provide last tower LAC + Cell ID.",
            "  4. Request carrier to identify duplicate SIM activation details.",
            "  5. If device is found, verify IMEI before returning.",
            "",
            "[EVIDENCE TO ATTACH]",
            "  - Google Find My Device screenshots",
            "  - IMEI blacklist status output",
            "  - Any timeline / location evidence",
            "",
            "Report generated by PhoneRecover Toolkit",
        ]

        with open(report_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        log(f"[+] Police report saved: {report_path}")
        return report_path


# ─────────────────────────────────────────────────────────────────────
# MODULE 6: RESALE / MARKETPLACE WATCHER
# ─────────────────────────────────────────────────────────────────────

class MarketplaceWatcher:
    @staticmethod
    def links(model: str, city: str = "Thrissur") -> dict:
        model_q = quote(model)
        city_q = quote(city)
        sites = {
            "OLX": f"https://www.olx.in/items/q-{model_q.replace(' ', '-')}",
            "Facebook Marketplace": f"https://www.facebook.com/marketplace/search/?q={model_q.replace(' ', '%20')}",
            "Quikr": f"https://www.quikr.com/search?q={model_q.replace(' ', '+')}",
            "Cashify": "https://www.cashify.in/sell-old-phone",
        }
        log(f"[+] Marketplace watcher ready for {model} in {city}")
        return sites

    @staticmethod
    def open(model: str, city: str = "Thrissur"):
        sites = MarketplaceWatcher.links(model, city)
        for name, url in sites.items():
            log(f"[+] Opening {name}: {url}")
            webbrowser.open(url)
            time.sleep(0.5)


# ─────────────────────────────────────────────────────────────────────
# MODULE 7: MAIN MENU
# ─────────────────────────────────────────────────────────────────────

def banner():
    print(
        "\n"
        "==================================================\n"
        "              PHONE RECOVER TOOLKIT              \n"
        "           Legitimate Recovery Framework      \n"
        "==================================================\n"
    )


def menu():
    print(f"IMEI   : {CONFIG['imei']}")
    print(f"Email  : {CONFIG['google_email']}")
    print(f"Model  : {CONFIG['phone_model']}")
    print(f"Carrier: {CONFIG['carrier']}")
    print()
    print("1. IMEI check + blacklist status")
    print("2. UnwiredLabs / OpenCellID lookup (needs LAC + Cell ID)")
    print("3. Google Find My Device quick links")
    print("4. Carrier request script")
    print("5. Police / FIR report")
    print("6. Marketplace watcher (Thrissur)")
    print("7. Open ALL actions")
    print("0. Exit")
    print()


def action_imei_check():
    imei = CONFIG.get("imei", "")
    if not imei:
        imei = input("Enter IMEI: ").strip()
    IMEIChecker.check(imei)


def action_cell_lookup():
    imei = CONFIG.get("imei", "")
    carrier = CONFIG.get("carrier", "airtel")
    helpline, mcc, mnc = CARRIER_MAP.get(carrier, ("121", "405", "15"))
    log(f"[i] Carrier: {carrier.upper()} | Helpline: {helpline} | MCC={mcc} MNC={mnc}")
    log("    Ask your carrier for the last known LAC and Cell ID.")
    lac = input("Enter LAC from carrier (or press Enter to skip): ").strip()
    cell_id = input("Enter Cell ID from carrier (or press Enter to skip): ").strip()
    if lac and cell_id:
        token = CONFIG.get("opencellid_token", "")
        CellTowerLookup.lookup(mcc=mcc, mnc=mnc, lac=lac, cell_id=cell_id, token=token)
    else:
        log("[-] Skipped. No LAC/Cell ID provided.")


def action_google_links():
    GoogleFindMyDevice.links(CONFIG["google_email"], CONFIG["imei"])
    GoogleFindMyDevice.open()


def action_carrier_script():
    CarrierToolkit.script(
        CONFIG["carrier"],
        CONFIG.get("phone_number", ""),
        CONFIG["imei"],
    )


def action_police_report():
    location_hint = CONFIG.get("known_last_location", "")
    PoliceReport.generate(
        imei=CONFIG["imei"],
        email=CONFIG["google_email"],
        phone_number=CONFIG.get("phone_number", ""),
        model=CONFIG["phone_model"],
        carrier=CONFIG["carrier"],
        location_hint=location_hint,
    )


def action_marketplace():
    MarketplaceWatcher.open(CONFIG["phone_model"], "Thrissur")


def action_run_all():
    log("[+] Running ALL recovery actions...")
    action_imei_check()
    action_cell_lookup()
    action_google_links()
    action_carrier_script()
    action_police_report()
    action_marketplace()
    log("[+] All actions complete. Check the output/ folder.")


def main():
    os.makedirs(CONFIG["output_dir"], exist_ok=True)
    banner()

    while True:
        menu()
        choice = input("Enter choice: ").strip()

        if choice == "1":
            action_imei_check()
        elif choice == "2":
            action_cell_lookup()
        elif choice == "3":
            action_google_links()
        elif choice == "4":
            action_carrier_script()
        elif choice == "5":
            action_police_report()
        elif choice == "6":
            action_marketplace()
        elif choice == "7":
            action_run_all()
        elif choice == "0":
            log("Exiting.")
            sys.exit(0)
        else:
            log("[-] Invalid choice.")

        input("\nPress Enter to continue...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log("\n[!] Interrupted by user.")
        sys.exit(0)
    except Exception as e:
        log(f"[!] Unexpected error: {e}")
        sys.exit(1)
