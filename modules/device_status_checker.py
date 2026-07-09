#!/usr/bin/env python3
"""
Live device status checker.
Provides manual/automated checks for device online status, battery,
network type, and Find My Device / Find My iPhone enabled status.
"""

import os
import json
import time
import webbrowser
from datetime import datetime


GOOGLE_FIND_MY = "https://www.google.com/android/find"
GOOGLE_DEVICE_ACTIVITY = "https://myaccount.google.com/device-activity"
APPLE_FIND_MY = "https://www.icloud.com/find"


def save_json(data, path="device_status_check.json"):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"[+] Saved device status JSON: {path}")


def google_device_status(email: str):
    print("GOOGLE DEVICE STATUS CHECK")
    print("=" * 60)
    print(f"Email: {email}")
    print()
    print("Manual checks to perform:")
    print(f"  1. Open: {GOOGLE_FIND_MY}")
    print("     -> Status shown: Online/Offline")
    print("     -> Last location timestamp")
    print("     -> Battery percentage (if available")
    print("     -> Network type (WiFi/Mobile)")
    print("  2. Open: https://android.com/find")
    print("  3. Open: https://myaccount.google.com/find-your-phone")
    print()
    webbrowser.open(GOOGLE_FIND_MY)


def apple_device_status(apple_id: str):
    print("APPLE DEVICE STATUS CHECK")
    print("=" * 60)
    print(f"Apple ID: {apple_id}")
    print()
    print("Manual checks to perform:")
    print(f"  1. Open: {APPLE_FIND_MY}")
    print("     -> Sign in with Apple ID")
    print("     -> Device list shows: location, battery, online/offline")
    print("  2. Status items to collect:")
    print("     - Is device online or offline?")
    print("     - Last location timestamp")
    print("     - Battery %")
    print("     - Is Lost Mode active?")
    print("     - Is Activation Lock on?")
    print()
    webbrowser.open(APPLE_FIND_MY)


def build_status_checklist(email="", apple_id="", imei=""):
    checklist = []
    checklist.append({
        "step": 1,
        "title": "Google Find My Device",
        "url": GOOGLE_FIND_MY,
        "items": [
            "Device online or offline",
            "Last location timestamp",
            "Battery percentage",
            "Network type",
            "Find My Device enabled/disabled",
        ],
    })
    checklist.append({
        "step": 2,
        "title": "Google Account Activity",
        "url": GOOGLE_DEVICE_ACTIVITY,
        "items": [
            "Recent login from unknown device/browser",
            "IP address and location of last login",
            "Apps with account access",
        ],
    })
    checklist.append({
        "step": 3,
        "title": "Apple Find My (if applicable)",
        "url": APPLE_FIND_MY,
        "items": [
            "Device online or offline",
            "Last location timestamp",
            "Battery percentage",
            "Lost mode status",
            "Play Sound available",
        ],
    })
    data = {
        "generated_at": datetime.now().isoformat(),
        "email": email,
        "apple_id": apple_id,
        "imei": imei,
        "checklist": checklist,
    }
    save_json(data)
    return data


if __name__ == "__main__":
    email = input("Google email (optional): ").strip()
    apple_id = input("Apple ID (optional): ").strip()
    imei = input("IMEI (optional): ").strip()
    build_status_checklist(email, apple_id, imei)
    print("[OK] Device status checklist generated.")
