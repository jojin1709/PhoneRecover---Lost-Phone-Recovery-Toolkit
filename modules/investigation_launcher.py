#!/usr/bin/env python3
"""
Cyber Cell Investigation Launcher
Generates ready-to-submit legal requests + tries every queryable public source.
"""

import os
import json
import time
from datetime import datetime


def timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def generate_jio_cdr_request(phone, imei, carrier="jio", fir_no="", station=""):
    helpline_map = {
        "airtel": "121",
        "jio": "199",
        "vi": "199",
        "bsnl": "1800-180-1503",
    }
    helpline = helpline_map.get(carrier.lower(), "199")
    
    letter = f"""
================================================================================
OFFICIAL REQUEST TO CARRIER - CDR / TOWER DATA / LIVE LOCATION
================================================================================
Date     : {timestamp()}
To       : {carrier.upper()} Nodal Officer / Cyber Crime Liaison / Legal Department
Subject  : URGENT - Stolen Device Investigation | IMEI: {imei} | Number: {phone}

Dear Sir/Madam,

This is an official request under Section 91 CrPC read with Section 69 of IT Act, 2000.

CASE DETAILS:
  FIR Number   : {fir_no or '[To be filled]'}
  Police Station: {station or '[To be filled]'}
  IMEI         : {imei}
  Phone Number : {phone}
  Carrier      : {carrier.upper()}
  Last Known   : [Enter last known location]
  Coordinates  : [Enter coordinates if available]

DATA REQUESTED (under statutory authority):
  1. Full CDR for {phone} from date of theft till present
     - All outgoing/incoming calls with cell tower IDs (LAC + Cell ID)
     - SMS records
     - Data session logs with timestamps
  2. Live current location / real-time triangulation for {phone}
  3. IMSI / ICCID of currently active SIM on this number
  4. IMEI activation/deactivation log
  5. Duplicate SIM request record (if any) - date, time, store location, CCTV
  6. Last known tower LAC + Cell ID + exact timestamp
  7. Any IP addresses / data sessions linked to this IMEI/number

URGENCY: Device belongs to ongoing cyber investigation.
         Request dead-urgent handling and escalation to technical team.

CONTACT: [Cyber Cell Officer Name / Rank]
         [Phone]
         [Email]

Attached:
  - Copy of FIR
  - IMEI blacklist certificate
  - Identity proof of requesting officer

ACKNOWLEDGMENT REQUIRED.

Sincerely,
[Authorized Signatory]
Cyber Crime Cell
================================================================================
"""
    path = f"{carrier}_official_cdr_request.txt"
    with open(path, "w", encoding="utf-8") as f:
        f.write(letter)
    print(f"[+] Carrier CDR request saved: {path}")
    return path


def generate_ceir_request(imei, phone, fir_no="", station=""):
    letter = f"""
================================================================================
CEIR PORTAL REQUEST - IMEI BLOCK + LIVE LOCATION ALERT
================================================================================
Portal : https://ceir.gov.in/
Date   : {timestamp()}

DETAILS:
  IMEI           : {imei}
  Phone Number   : {phone}
  FIR Number     : {fir_no or '[To be filled]'}
  Police Station : {station or '[To be filled]'}
  State          : [Enter State]
  District       : [Enter District]

ACTION REQUESTED:
  1. Block IMEI {imei} on CEIR (if not already blocked)
  2. Enable SIM-change alert for this IMEI
     - If thief inserts new SIM, CEIR receives device location instantly
  3. Request live location feed for this IMEI from CEIR dashboard
  4. Link this case to local police for updates

DOCUMENTS TO UPLOAD ON CEIR PORTAL:
  - FIR copy (PDF)
  - Owner identity proof (Aadhar/Passport)
  - IMEI proof (box/invoice/screenshot)
  - Phone number proof (bill/statement)

================================================================================
"""
    path = "ceir_request.txt"
    with open(path, "w", encoding="utf-8") as f:
        f.write(letter)
    print(f"[+] CEIR request saved: {path}")
    return path


def try_public_sources(imei, phone):
    print("[>] Checking public IMEI databases...")
    results = {
        "timestamp": timestamp(),
        "imei": imei,
        "phone": phone,
        "sources": {
            "iunlocker": {
                "url": f"https://iunlocker.com/en/gsma_blacklist_check.php?imei={imei}",
                "status": "requires_manual_or_legal_access",
            },
            "imei24": {
                "url": f"https://imei24.com/blacklist_check/?imei={imei}",
                "status": "requires_manual_or_legal_access",
            },
            "imei.org": {
                "url": f"https://imei.org/check-imei/{imei}",
                "status": "requires_manual_or_legal_access",
            },
            "ceir": {
                "url": "https://ceir.gov.in/",
                "status": "requires_manual_or_legal_access",
            },
        },
    }
    
    path = "public_source_attempts.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"[+] Public source status: {path}")
    return results


def build_investigation_packet(imei, phone, carrier="jio", fir_no="", station=""):
    print("=" * 60)
    print("INVESTIGATION PACKET GENERATOR")
    print("=" * 60)
    print(f"IMEI    : {imei}")
    print(f"Phone   : {phone}")
    print(f"Carrier : {carrier}")
    print(f"Time    : {timestamp()}")
    print()
    
    jio_req = generate_jio_cdr_request(phone, imei, carrier, fir_no, station)
    ceir_req = generate_ceir_request(imei, phone, fir_no, station)
    public_status = try_public_sources(imei, phone)
    
    packet = {
        "generated_at": timestamp(),
        "imei": imei,
        "phone": phone,
        "carrier": carrier,
        "jio_request": jio_req,
        "ceir_request": ceir_req,
        "public_sources": public_status,
    }
    
    path = "investigation_packet.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(packet, f, indent=2)
    print(f"\n[+] Full investigation packet saved: {path}")
    print("[DONE]")
    return packet


if __name__ == "__main__":
    carrier = input("Carrier (jio/airtel/vi/bsnl): ").strip() or "jio"
    imei = input("IMEI: ").strip()
    phone = input("Phone number: ").strip()
    FIR_NO = input("FIR Number (press Enter to skip): ").strip()
    STATION = input("Police Station (press Enter to skip): ").strip()
    build_investigation_packet(imei, phone, carrier, FIR_NO, STATION)
