#!/usr/bin/env python3
"""
Hard IP Tracker - Go-backed IP tracker wrapper.
Runs the compiled Go tracker as a subprocess and parses JSON output.
"""

import os
import sys
import json
import subprocess
import shutil
from datetime import datetime


HERE = os.path.dirname(os.path.abspath(__file__))
TRACKER_DIR = os.path.join(os.path.dirname(HERE), "tracker-go")
TRACKER_BIN = os.path.join(TRACKER_DIR, "tracker-go.exe" if os.name == "nt" else "tracker-go")


def find_tracker_bin():
    candidates = [
        TRACKER_BIN,
        os.path.join(os.getcwd(), "tracker-go", "tracker-go.exe" if os.name == "nt" else "tracker-go"),
        "tracker-go.exe" if os.name == "nt" else "tracker-go",
    ]
    for c in candidates:
        if os.path.isfile(c) or shutil.which(c):
            return c
    return None


def track_ip(target: str) -> dict:
    bin_path = find_tracker_bin()
    if not bin_path:
        return {"error": "tracker-go binary not found. Build it first with: cd tracker-go && go build -o tracker-go ."}
    try:
        out = subprocess.check_output(
            [bin_path, "track", target],
            stderr=subprocess.STDOUT,
            text=True,
            timeout=30,
        )
    except subprocess.CalledProcessError as e:
        return {"error": e.output}
    except Exception as e:
        return {"error": str(e)}
    try:
        with open(os.path.join(os.getcwd(), "ip_track_results.json"), "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"raw": out}


def scan_lan(subnet: str = "") -> dict:
    bin_path = find_tracker_bin()
    if not bin_path:
        return {"error": "tracker-go binary not found. Build it first."}
    args = [bin_path, "scan"]
    if subnet:
        args.append(subnet)
    try:
        out = subprocess.check_output(
            args,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=120,
        )
    except subprocess.CalledProcessError as e:
        return {"error": e.output}
    except Exception as e:
        return {"error": str(e)}
    try:
        with open(os.path.join(os.getcwd(), "network_scan_results.json"), "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"raw": out}


if __name__ == "__main__":
    print("HARD IP TRACKER - GO BACKEND")
    print("=" * 60)
    print(f"Binary: {find_tracker_bin()}")
    print()
    print("1. Track IP / domain")
    print("2. Scan LAN for devices")
    print("3. Trace target")
    choice = input("Choice [1-3]: ").strip()
    if choice == "1":
        target = input("IP or domain: ").strip()
        print(json.dumps(track_ip(target), indent=2))
    elif choice == "2":
        subnet = input("Subnet (eg 192.168.1.0/24) [Enter=auto]: ").strip()
        print(json.dumps(scan_lan(subnet), indent=2))
    else:
        print("Invalid choice")
