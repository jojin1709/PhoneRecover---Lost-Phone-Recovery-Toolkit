#!/usr/bin/env python3
"""
Apple Find My Device - iCloud/FMF integration helper.
Provides links and status checks for Find My iPhone / Find My Friends.
"""

import webbrowser
from datetime import datetime

EMAIL = ""
ICLOUD_BASE = "https://www.icloud.com/find"


def ensure_email(email: str) -> str:
    return email or ""


def links(email: str, imei: str, apple_id: str = ""):
    email = ensure_email(email)
    account = apple_id or email
    data = {
        "email": email,
        "apple_id": account,
        "imei": imei,
        "find_my_device": f"{ICLOUD_BASE}",
        "fmip_website": "https://www.icloud.com/find",
        "apple_support": "https://support.apple.com/en-us/HT201572",
    }
    path = "apple_find_my_links.json"
    with open(path, "w", encoding="utf-8") as f:
        import json
        json.dump(data, f, indent=2)
    print(f"[+] Saved Apple Find My links: {path}")
    return data


def show_status_checks():
    print("APPLE FIND MY DEVICE - STATUS CHECKS")
    print("=" * 60)
    print("1. Open https://www.icloud.com/find")
    print("2. Sign in with the victim/owner Apple ID")
    print("3. Look for the stolen device in the device list")
    print("4. Device status to note:")
    print("   - Online / Offline")
    print("   - Last location timestamp")
    print("   - Battery percentage (if available)")
    print("   - Lost mode status")
    print("   - Sound / Play Sound capability")
    print("5. Actions available if device is online:")
    print("   - Play Sound (to locate nearby)")
    print("   - Lost Mode (lock + message)")
    print("   - Erase This Device (last resort)")
    print()
    webbrowser.open(ICLOUD_BASE)


def lost_mode_instructions():
    print("LOST MODE INSTRUCTIONS")
    print("=" * 60)
    print("If the device is online:")
    print("  1. Select it in Find My")
    print("  2. Click 'Mark as Lost'")
    print("  3. Enter a phone number and message")
    print("  4. Device locks immediately")
    print("  5. You get an email when location updates")
    print()
    print("If the device is offline:")
    print("  - Lost Mode activates when it comes online")
    print("  - You will receive notification email then")


def offline_location_hints():
    print("OFFLINE LOCATION HINTS")
    print("=" * 60)
    print("Apple keeps last-known location for offline devices.")
    print("Check:")
    print("  - Find My device list -> Last known location")
    print("  - Family Sharing -> location of shared devices")
    print("  - Email notifications from iCloud for location updates")
    print("  - Check if thief uses the device to sign into any")
    print("    Apple service (iMessage, FaceTime, App Store)")


if __name__ == "__main__":
    show_status_checks()
    lost_mode_instructions()
    offline_location_hints()
