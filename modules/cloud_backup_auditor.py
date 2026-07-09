#!/usr/bin/env python3
"""
Cloud backup auditor.
Checks Google/iCloud backup status and last backup times.
"""

import os
import json
from datetime import datetime


GOOGLE_BACKUP_URL = "https://one.google.com/settings/backup"
ICLOUD_BACKUP_URL = "https://www.icloud.com/settings"


def save_audit(audit: dict, path="cloud_backup_audit.json"):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(audit, f, indent=2)
    print(f"[+] Cloud backup audit saved: {path}")


def google_backup_audit(email: str):
    print("GOOGLE BACKUP AUDIT")
    print("=" * 60)
    print(f"Email: {email}")
    print()
    print("Manual checks:")
    print(f"  1. Open: {GOOGLE_BACKUP_URL}")
    print("  2. Check: Is backup enabled?")
    print("  3. Check: Last backup timestamp")
    print("  4. Check: What is backed up:")
    print("     - Device data")
    print("     - Photos")
    print("     - Messages")
    print("     - WhatsApp backups (Google Drive)")
    print("  5. Note: If thief uses the device, new backup may contain")
    print("     thief data / location / photos")
    print()
    audit = {
        "service": "google",
        "email": email,
        "url": GOOGLE_BACKUP_URL,
        "last_backup_timestamp": None,
        "backup_enabled": None,
        "backup_items": [],
        "secondary_accounts": [],
    }
    save_audit(audit, "google_backup_audit.json")
    return audit


def icloud_backup_audit(apple_id: str):
    print("ICLOUD BACKUP AUDIT")
    print("=" * 60)
    print(f"Apple ID: {apple_id}")
    print()
    print("Manual checks:")
    print(f"  1. Open: {ICLOUD_BACKUP_URL}")
    print("  2. Check: Is iCloud Backup enabled?")
    print("  3. Check: Last backup timestamp")
    print("  4. Check: What is backed up:")
    print("     - Photos")
    print("     - Messages")
    print("     - Health data")
    print("     - Device backup")
    print("  5. Note: If thief uses the device, new backup may contain")
    print("     thief data / location / photos")
    print()
    audit = {
        "service": "icloud",
        "apple_id": apple_id,
        "url": ICLOUD_BACKUP_URL,
        "last_backup_timestamp": None,
        "backup_enabled": None,
        "backup_items": [],
    }
    save_audit(audit, "icloud_backup_audit.json")
    return audit


def build_backup_audit(email="", apple_id=""):
    audits = []
    if email:
        audits.append(google_backup_audit(email))
    if apple_id:
        audits.append(icloud_backup_audit(apple_id))
    summary = {
        "generated_at": datetime.now().isoformat(),
        "email": email,
        "apple_id": apple_id,
        "audits": audits,
    }
    save_audit(summary, "cloud_backup_audit.json")
    return summary


if __name__ == "__main__":
    email = input("Google email (optional): ").strip()
    apple_id = input("Apple ID (optional): ").strip()
    build_backup_audit(email, apple_id)
