#!/usr/bin/env python3
"""
Google Intelligence - Checks if thief is using the phone
"""

import requests
from datetime import datetime


def check_device_activity(email: str = "", imei: str = ""):
    """Brute-force checks: Google device activity page"""
    email = email or input("Enter Google email: ").strip()
    imei = imei or input("Enter IMEI: ").strip()
    print(f"[{datetime.now()}] Checking device activity...")
    print(f"    -> Open: https://myaccount.google.com/device-activity")
    print(f"    -> Sign in with: {email}")
    print(f"    -> Look for IMEI {imei} in the list")
    print(f"    -> If 'Last seen' is recent - thief is using it!")
    print(f"    -> Click 'More details' -> Get IP address")
    print(f"    -> IP lookup: https://ipinfo.io/<IP>")


def generate_session_check_script():
    print("GOOGLE SESSION CHECK")
    print("=" * 60)
    print("1. Open: https://myaccount.google.com/device-activity")
    print("2. Sign in with your Google account")
    print("3. Look for:")
    print("   - Unknown devices")
    print("   - Devices with your IMEI")
    print("   - Recent logins from unknown locations")
    print("4. For each suspicious entry:")
    print("   - Note IP address")
    print("   - Note location")
    print("   - Note timestamp")
    print("   - Click 'Sign out' if it's not your device")
    print()
    email = input("Enter your email for script generation (or press Enter to skip): ").strip()
    imei = input("Enter your IMEI for script generation (or press Enter to skip): ").strip()
    check_device_activity(email, imei)


if __name__ == "__main__":
    generate_session_check_script()
