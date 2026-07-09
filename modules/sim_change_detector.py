#!/usr/bin/env python3
"""
SIM swap / change detector.
Generates scripts to check SIM ICCID/IMSI changes and detect duplicate SIMs.
"""

import os
import json
from datetime import datetime


CARRIER_HELPLINE = {
    "airtel": "121",
    "jio": "199",
    "vi": "199",
    "bsnl": "1800-180-1503",
}


def build_detection_plan(phone_number="", carrier="airtel"):
    carrier = (carrier or "airtel").lower()
    helpline = CARRIER_HELPLINE.get(carrier, "121")
    plan = {
        "generated_at": datetime.now().isoformat(),
        "phone_number": phone_number,
        "carrier": carrier,
        "helpline": helpline,
        "detection_items": [
            "Ask: Is the current SIM active still the original?",
            "Ask: What is the ICCID/IMSI of the active SIM?",
            "Ask: When was the active SIM last activated?",
            "Ask: Was a duplicate SIM requested after the theft date?",
            "Ask: What was the store/branch location of SIM issue?",
            "Ask: Is there CCTV of the person who collected SIM?",
        ],
        "immediate_actions": [
            "Call helpline and report SIM swap attempt",
            "Request SIM suspension until identity verified",
            "File police complaint with carrier acknowledgment",
        ],
    }
    path = "sim_change_detection_plan.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(plan, f, indent=2)
    print(f"[+] SIM change detection plan saved: {path}")
    print(f"Call helpline: {helpline}")
    return plan


if __name__ == "__main__":
    carrier = input("Carrier (airtel/jio/vi/bsnl): ").strip() or "airtel"
    phone = input("Phone number: ").strip()
    build_detection_plan(phone, carrier)
