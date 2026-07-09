#!/usr/bin/env python3
"""
Recovery success logger.
Tracks actions, timestamps, and outcomes for recovery attempts.
"""

import os
import json
from datetime import datetime


LOG_PATH = "recovery_success_log.json"


def log_entry(action: str, status: str, details: str = "", imei="", phone=""):
    entry = {
        "timestamp": datetime.now().isoformat(),
        "imei": imei,
        "phone": phone,
        "action": action,
        "status": status,
        "details": details,
    }
    data = []
    if os.path.isfile(LOG_PATH):
        try:
            with open(LOG_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            data = []
    data.append(entry)
    with open(LOG_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"[+] Recovery log updated: {LOG_PATH}")
    return entry


def summary():
    if not os.path.isfile(LOG_PATH):
        print("[-] No recovery log found yet.")
        return
    with open(LOG_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    success = sum(1 for e in data if e.get("status") == "success")
    failed = sum(1 for e in data if e.get("status") == "failed")
    print("RECOVERY LOG SUMMARY")
    print("=" * 60)
    print(f"Total entries : {len(data)}")
    print(f"Success       : {success}")
    print(f"Failed        : {failed}")
    print()
    for e in data[-10:]:
        print(f"  {e['timestamp']} | {e['action']} | {e['status']}")
        if e.get("details"):
            print(f"    -> {e['details']}")


if __name__ == "__main__":
    print("Recovery Success Logger")
    print("1. Log action")
    print("2. Show summary")
    choice = input("Choice [1/2]: ").strip()
    if choice == "1":
        action = input("Action: ").strip()
        status = input("Status (success/failed/pending): ").strip().lower()
        details = input("Details: ").strip()
        imei = input("IMEI (optional): ").strip()
        phone = input("Phone (optional): ").strip()
        log_entry(action, status, details, imei, phone)
    elif choice == "2":
        summary()
