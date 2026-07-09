#!/usr/bin/env python3
"""
IMEI blocking / blacklist portal workflow.
Provides official blocking links for carriers and government portals.
"""

import os
import json
from datetime import datetime


def portals(carrier="airtel", country="IN"):
    carrier = (carrier or "airtel").lower()
    data = {
        "generated_at": datetime.now().isoformat(),
        "carrier": carrier,
        "country": country,
        "carrier_portals": {
            "airtel": {
                "name": "Airtel Thanks App / Web",
                "block_imei_url": "https://www.airtel.in/support",
                "alternative": "Call 121 and request IMEI block",
                "note": "Block via customer care or support ticket.",
            },
            "jio": {
                "name": "Jio Support",
                "block_imei_url": "https://www.jio.com/selfcare",
                "alternative": "Call 199 or visit nearest Jio store",
                "note": "Provide IMEI + FIR copy for faster action.",
            },
            "vi": {
                "name": "Vodafone Idea Support",
                "block_imei_url": "https://www.vodafoneidea.com/web/my-account",
                "alternative": "Call 199",
                "note": "Provide IMEI + FIR copy.",
            },
            "bsnl": {
                "name": "BSNL Support",
                "block_imei_url": "https://portal1.bsnl.in/myportal/",
                "alternative": "Call 1800-180-1503",
                "note": "Provide IMEI + FIR copy.",
            },
        },
        "government_portals": {
            "IN": {
                "name": "CEIR India (Central Equipment Identity Register)",
                "url": "https://ceir.gov.in",
                "action": "Request IMEI blocking through CEIR portal using FIR copy",
                "note": "Official govt portal. Upload FIR and IMEI details.",
            }
        },
        "global_checks": [
            {
                "name": "GSMA Blacklist Check",
                "url": "https://iunlocker.com/en/gsma_blacklist_check.php",
            },
            {
                "name": "IMEI.info",
                "url": "https://imei.info",
            },
        ],
    }
    path = "imei_blocking_portals.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"[+] Saved IMEI blocking portals: {path}")
    return data


if __name__ == "__main__":
    carrier = input("Carrier (airtel/jio/vi/bsnl): ").strip() or "airtel"
    portals(carrier)
