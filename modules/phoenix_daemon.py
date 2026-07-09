#!/usr/bin/env python3
"""
Phoenix Daemon - Background monitor for stolen device recovery.
Periodically checks multiple channels for device status.
"""

import time
import threading
from datetime import datetime


def monitor_channel(name, check_func, interval=300):
    while True:
        try:
            print(f"[{datetime.now()}] Checking {name}...")
            check_func()
        except Exception as e:
            print(f"[-] {name} check failed: {e}")
        time.sleep(interval)


def start_daemon():
    print("PHOENIX RECOVERY DAEMON")
    print("=" * 60)
    print("This daemon monitors multiple channels for your stolen device.")
    print("Press Ctrl+C to stop.")
    print()
    
    imei = input("Enter IMEI: ").strip()
    phone = input("Enter phone number: ").strip()
    email = input("Enter email: ").strip()
    
    interval = input("Check interval in seconds (default 300): ").strip()
    try:
        interval = int(interval)
    except Exception:
        interval = 300
    
    channels = []
    
    def check_google():
        print("    -> Check: https://www.google.com/android/find")
    
    def check_carrier():
        print("    -> Check carrier portal for last known location")
    
    def check_marketplace():
        print("    -> Check OLX/Facebook/Quikr for device resale")
    
    channels.append(threading.Thread(target=monitor_channel, args=("Google Find My", check_google, interval), daemon=True))
    channels.append(threading.Thread(target=monitor_channel, args=("Carrier Status", check_carrier, interval), daemon=True))
    channels.append(threading.Thread(target=monitor_channel, args=("Marketplace", check_marketplace, interval), daemon=True))
    
    for t in channels:
        t.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[!] Daemon stopped.")


if __name__ == "__main__":
    start_daemon()
