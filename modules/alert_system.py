#!/usr/bin/env python3
"""
Alert / notification system.
Supports Telegram, email, and SMS alerts.
"""

import os
import json
import smtplib
from datetime import datetime
from email.mime.text import MIMEText


def save_alert_config(config: dict, path="alert_config.json"):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)
    print(f"[+] Alert config saved: {path}")


def send_email_alert(subject: str, body: str, to_email: str, smtp_config: dict):
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = smtp_config.get("from_email", "")
    msg["To"] = to_email
    try:
        with smtplib.SMTP_SSL(smtp_config["host"], int(smtp_config.get("port", 465))) as server:
            server.login(smtp_config["username"], smtp_config["password"])
            server.sendmail(smtp_config["from_email"], [to_email], msg.as_string())
        print(f"[+] Email alert sent to {to_email}")
        return True
    except Exception as e:
        print(f"[-] Email alert failed: {e}")
        return False


def telegram_alert(message: str, bot_token: str, chat_id: str):
    try:
        import requests

        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {"chat_id": chat_id, "text": message}
        r = requests.post(url, json=payload, timeout=20)
        if r.status_code == 200:
            print("[+] Telegram alert sent")
            return True
        print(f"[-] Telegram failed: {r.text}")
    except Exception as e:
        print(f"[-] Telegram failed: {e}")
    return False


def build_alert(alert_type: str, message: str, imei="", link=""):
    data = {
        "type": alert_type,
        "message": message,
        "imei": imei,
        "link": link,
        "timestamp": datetime.now().isoformat(),
    }
    path = "last_alert.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"[+] Alert object saved: {path}")
    return data


if __name__ == "__main__":
    alert_type = input("Alert type (email/telegram): ").strip().lower()
    message = input("Alert message: ").strip()
    imei = input("IMEI (optional): ").strip()
    link = input("Link (optional): ").strip()
    build_alert(alert_type, message, imei, link)
    print("[OK] Alert prepared.")
