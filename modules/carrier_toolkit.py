#!/usr/bin/env python3
"""
Carrier Toolkit - Social engineering scripts to get tower data from carrier.
Generates request scripts for Airtel, Jio, VI, BSNL.
"""

import os
import json
from datetime import datetime


CARRIER_MAP = {
    "airtel": ("121", "405", "15"),
    "jio": ("199", "405", "20"),
    "vi": ("199", "405", "11"),
    "bsnl": ("1800-180-1503", "405", "74"),
}


def script(carrier: str, phone_number: str, imei: str):
    carrier = (carrier or "airtel").lower()
    helpline, mcc, mnc = CARRIER_MAP.get(carrier, CARRIER_MAP["airtel"])
    
    os.makedirs("output", exist_ok=True)
    script_path = os.path.join("output", f"carrier_script_{carrier}.txt")
    
    lines = [
        "CARRIER REQUEST SCRIPT",
        "=" * 60,
        f"Carrier  : {carrier.upper()}",
        f"Helpline : {helpline}",
        f"Phone    : {phone_number}",
        f"IMEI     : {imei}",
        "",
        "WHAT TO SAY:",
        f"  Hello, my phone (IMEI {imei}) was stolen. I need the last tower LAC + Cell ID for number {phone_number}. Also check if a duplicate SIM was requested and when. This is for police investigation. FIR copy available.",
        "",
        "QUESTIONS TO ASK:",
        "  1. Last network activity timestamp for this number",
        "  2. Current active SIM ICCID/IMSI",
        "  3. Last tower LAC + Cell ID",
        "  4. Duplicate SIM request record",
        "  5. Cell ID location / approximate GPS",
        "",
        f"NOTE: MCC={mcc}, MNC={mnc} for {carrier.upper()}",
        "=" * 60,
    ]
    
    with open(script_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    
    print(f"[+] Carrier script saved: {script_path}")
    return script_path


if __name__ == "__main__":
    carrier = input("Carrier (jio/airtel/vi/bsnl): ").strip() or "jio"
    phone = input("Phone number: ").strip()
    imei = input("IMEI: ").strip()
    script(carrier, phone, imei)
