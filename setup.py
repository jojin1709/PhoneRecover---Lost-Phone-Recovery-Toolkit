#!/usr/bin/env python3
"""
PhoneRecover - Setup and Configuration
Run this first to set up your details.
"""

import os
import json
import sys

CONFIG_FILE = "user_config.json"


def setup():
    print("=" * 60)
    print("       PHONE RECOVER - SETUP")
    print("=" * 60)
    print()
    print("Enter your details. You can change these later by running")
    print("this setup again.")
    print()
    
    config = {}
    
    config["imei"] = input("Enter your IMEI number (15 digits): ").strip()
    if not config["imei"]:
        print("[!] IMEI is required.")
        sys.exit(1)
    
    config["phone_number"] = input("Enter your phone number (with +91): ").strip()
    config["google_email"] = input("Enter your Google email: ").strip()
    config["phone_model"] = input("Enter your phone model (optional): ").strip() or "Unknown"
    
    print()
    print("Select your carrier:")
    print("  1. Jio")
    print("  2. Airtel")
    print("  3. Vi")
    print("  4. BSNL")
    carrier_choice = input("Enter choice [1-4, default=1]: ").strip() or "1"
    carrier_map = {
        "1": "jio",
        "2": "airtel",
        "3": "vi",
        "4": "bsnl",
    }
    config["carrier"] = carrier_map.get(carrier_choice, "jio")
    
    config["opencellid_token"] = input("Enter OpenCellID token (optional, press Enter to skip): ").strip()
    
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)
    
    print()
    print(f"[+] Configuration saved to {CONFIG_FILE}")
    print()
    print("Next steps:")
    print("  1. Run: python phonerecover.py")
    print("  2. Or run: python PHOENIX.py")


if __name__ == "__main__":
    setup()
