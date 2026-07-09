#!/usr/bin/env python3
"""
Emergency contact / social alert system.
One-click alert templates for family, police, and social media.
"""

import os
import json
from datetime import datetime


def build_alerts(imei="", phone="", location_hint=""):
    alerts = {
        "generated_at": datetime.now().isoformat(),
        "imei": imei,
        "phone": phone,
        "location_hint": location_hint,
        "family_alert": {
            "subject": f"EMERGENCY: My phone was stolen (IMEI {imei})",
            "body": f"""Hi,

My phone has been stolen. I need your help.

IMEI: {imei}
Phone: {phone}
Last known location: {location_hint}

Please:
1. Share this message with family/friends
2. Monitor my social accounts for suspicious activity
3. If you see this device anywhere, note location and call police

Thank you.
""",
        },
        "police_alert": {
            "subject": f"Stolen Device Report - IMEI {imei}",
            "body": f"""To: Cyber Cell / Police

My phone has been stolen.

IMEI: {imei}
Phone: {phone}
Last known location: {location_hint}

I have:
- Filed FIR (copy attached)
- Blocked SIM via carrier
- Tracked on Google/Apple Find My Device

Request immediate action to trace and recover.

""",
        },
        "social_alert": {
            "platforms": ["Twitter/X", "Facebook", "Instagram", "WhatsApp"],
            "body": f"""URGENT: My phone was stolen!

IMEI: {imei}
Phone: {phone}
Last known location: {location_hint}

If found or spotted, please contact me immediately or inform police.
Reward offered for credible recovery info.

#StolenPhone #IMEI {imei}
""",
        },
    }
    path = "emergency_alerts.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(alerts, f, indent=2)
    print(f"[+] Emergency alerts saved: {path}")
    return alerts


if __name__ == "__main__":
    imei = input("IMEI: ").strip()
    phone = input("Phone number: ").strip()
    location_hint = input("Last known location: ").strip()
    build_alerts(imei, phone, location_hint)
