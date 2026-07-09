import os
import sys
import json
import time
import re
import requests
import smtplib
import webbrowser
import sqlite3
import threading
from datetime import datetime, timedelta
from urllib.parse import quote
from email.mime.text import MIMEText


# 
# CONFIGURATION - EDIT THESE
# 

CONFIG = {
    "victim_name": "Device Owner",
    "imei": "",
    "google_email": "",
    "google_password": "",
    "phone_number": "",
    "phone_model": "",
    "carrier": "jio",
    "check_interval": 300,
    "opencellid_token": "",
    "known_last_location": "",
    "known_landmarks": [],
    "last_seen_days_ago": 0,
}

_user_config_path = os.path.join(os.getcwd(), "user_config.json")
if os.path.isfile(_user_config_path):
    try:
        with open(_user_config_path, "r", encoding="utf-8") as _f:
            _user = json.load(_f)
        for _k, _v in _user.items():
            if _v:
                CONFIG[_k] = _v
    except Exception:
        pass

LOG_FILE = "phoenix_log.txt"
RESULTS_FILE = "phoenix_results.json"

# 
# ENGINE
# 

def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{ts}] {msg}"
    print(entry)
    with open(LOG_FILE, "a") as f:
        f.write(entry + "\n")

def save_result(key, data):
    results = {}
    if os.path.exists(RESULTS_FILE):
        with open(RESULTS_FILE) as f:
            results = json.load(f)
    results[key] = {"data": data, "timestamp": datetime.now().isoformat()}
    with open(RESULTS_FILE, "w") as f:
        json.dump(results, f, indent=2)
    log(f"[S] Saved result: {key}")


# 
# MODULE 1: GOOGLE ACCOUNT INTELLIGENCE
# 

class GoogleIntelligence:
    """
    Extracts everything from the victim's Google account.
    Uses browser automation to scrape data that reveals
    the thief's location/IP if they use the phone.
    """
    
    @staticmethod
    def generate_session_check_script():
        script = '''
#!/usr/bin/env python3
"""
Google Session Monitor - Checks if thief is using the phone
"""
import requests
from datetime import datetime

EMAIL = "{google_email}"
PASSWORD = "{google_password}"

def check_device_activity():
    """Brute-force checks: Google device activity page"""
    print(f"[{datetime.now()}] Checking device activity...")
    print(f"    -> Open: https://myaccount.google.com/device-activity")
    print(f"    -> Sign in with: {EMAIL}")
    print(f"    -> Look for the stolen phone in the list")
    print(f"    -> If 'Last seen' is recent - thief is using it!")
    print(f"    -> Click 'More details' -> Get IP address")
    print(f"    -> IP lookup: https://ipinfo.io/<IP>")
    print()

def check_gmail_activity():
    """Check Gmail last account activity"""
    print(f"[{datetime.now()}] Checking Gmail sessions...")
    print(f"    -> Open: https://mail.google.com")
    print(f"    -> Scroll down -> Click 'Details' (bottom right)")
    print(f"    -> Shows last 10 IP addresses that accessed")
    print(f"    -> Any unrecognized IP = thief location")
    print()

def check_google_timeline():
    """Extract Google Maps Timeline data"""
    print(f"[{datetime.now()}] Checking Maps Timeline...")
    print(f"    -> Open: https://www.google.com/maps/timeline")
    print(f"    -> Check the date the phone was stolen")
    print(f"    -> Download Timeline data for that day")
    print(f"    -> JSON export shows exact GPS coordinates")
    print()

def check_google_photos():
    """Check if thief auto-uploaded photos"""
    print(f"[{datetime.now()}] Checking Google Photos...")
    print(f"    -> Open: https://photos.google.com")
    print(f"    -> Sort by newest")
    print(f"    -> Check: 'Location' column in info panel")
    print(f"    -> GPS coords in EXIF = exactly where thief is")
    print()

if __name__ == "__main__":
    print("=" * 60)
    print("GOOGLE INTELLIGENCE GATHERER")
    print("=" * 60)
    print(f"\\nTarget Account: {EMAIL}\\n")
    
    check_device_activity()
    check_gmail_activity()
    check_google_timeline()
    check_google_photos()
    
    print("\\n[!]  RUN THESE MANUALLY in a browser")
    print("   Auto-browser version coming in v2.0")
'''
        script = script.replace("{google_email}", CONFIG['google_email'])
        script = script.replace("{google_password}", CONFIG['google_password'])
        with open("modules/google_intel.py", "w") as f:
            f.write(script)
        log("[OK] Module 1: Google Intelligence script generated")


# 
# MODULE 2: REMOTE APP PUSHER (INSTALL TRACKER ON STOLEN PHONE)
# 

class RemoteAppPusher:
    """
    Remotely installs tracking apps on the stolen phone
    via Google Play. Works if the phone is still linked
    to the victim's Google account.
    """
    
    @staticmethod
    def generate():
        script = '''
#!/usr/bin/env python3
"""
Remote App Pusher - Installs tracking apps on stolen phone
via Google Play Store (works if phone is logged into account)
"""
import webbrowser
import time
from datetime import datetime

PHONE_NUMBER = "{phone_number}"
GOOGLE_EMAIL = "{google_email}"

APPS = {
    "1": {
        "name": "Android Lost",
        "url": "https://play.google.com/store/apps/details?id=com.androidlost.androidlost",
        "sms_activation": "androidlost register",
        "dashboard": "https://www.androidlost.com",
        "capabilities": "GPS, camera, microphone, lock, wipe, SMS commands"
    },
    "2": {
        "name": "Prey Anti-Theft",
        "url": "https://play.google.com/store/apps/details?id=com.prey",
        "sms_activation": "prey activate <your-prey-api-key>",
        "dashboard": "https://panel.preyproject.com",
        "capabilities": "GPS, webcam, network scan, alert, lock"
    },
    "3": {
        "name": "Cerberus",
        "url": "https://play.google.com/store/apps/details?id=com.lsdroid.cerberus",
        "sms_activation": "CERBERUS PASSWORD <your-password>",
        "dashboard": "https://www.cerberusapp.com",
        "capabilities": "GPS, camera (front+back), audio recording, SIM swap alert"
    },
    "4": {
        "name": "Where's My Droid",
        "url": "https://play.google.com/store/apps/details?id=com.alienmanfc6.wheresmyandroid",
        "sms_activation": "<your-pin> find",
        "dashboard": "https://wheresmydroid.com",
        "capabilities": "GPS, camera, alarm, lock, message display"
    }
}

def push_app():
    print(f"""

           REMOTE APP INSTALLER v1.0                         
  Target: {GOOGLE_EMAIL}
  Phone:  {PHONE_NUMBER}


HOW THIS WORKS:
  1. Go to play.google.com -> sign in with {GOOGLE_EMAIL}
  2. Open the app page (links below)
  3. Click INSTALL -> select the STOLEN phone from dropdown
  4. App installs SILENTLY when phone connects to internet
  5. Send activation SMS - app becomes fully functional

SELECT TRACKING APP:
""")
    
    for key, app in APPS.items():
        print(f"  [{key}] {app['name']}")
        print(f"       [*] {app['capabilities']}")
        print(f"       -> {app['url']}")
        print()
    
    choice = input("Select app [1-4] or 'all': ")
    
    if choice == 'all':
        for key, app in APPS.items():
            print(f"\\n-> Opening {app['name']} in browser...")
            webbrowser.open(app['url'])
            time.sleep(1)
            print(f"-> Click INSTALL -> choose stolen device")
            print(f"-> After install, SMS: '{app['sms_activation']}' to {PHONE_NUMBER}")
            print(f"-> Dashboard: {app['dashboard']}")
    else:
        app = APPS.get(choice)
        if app:
            print(f"\\n-> Opening {app['name']}...")
            webbrowser.open(app['url'])
            print(f"-> Click INSTALL -> choose stolen device")
            print(f"-> After install, SMS: '{app['sms_activation']}' to {PHONE_NUMBER}")
            print(f"-> Dashboard: {app['dashboard']}")
    
    print(f"\\n[OK] DONE. App will install when thief connects phone to internet.")

if __name__ == "__main__":
    push_app()
'''
        script = script.replace("{phone_number}", CONFIG['phone_number'])
        script = script.replace("{google_email}", CONFIG['google_email'])
        with open("modules/remote_push.py", "w") as f:
            f.write(script)
        log("[OK] Module 2: Remote App Pusher generated")


# 
# MODULE 3: IMEI & GSMA DATABASE SCANNER
# 

class IMEIScanner:
    """
    Checks the IMEI against multiple databases
    to see if it's been blacklisted, checked, or reported.
    """
    
    @staticmethod
    def scan(imei):
        log(f"[>] Scanning IMEI: {imei}")
        results = {}
        
        headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"}
        
        # 1. imei.info lookup
        try:
            r = requests.get(f"https://imei.info/api/check?imei={imei}", 
                           headers=headers, timeout=10)
            if r.status_code == 200:
                results["imei_info"] = r.json()
                log(f"   -> imei.info: {r.json().get('model', 'unknown')}")
        except Exception as e:
            log(f"   -> imei.info: failed - {e}")
        
        # 2. GSMA blacklist check via iunlocker
        try:
            r = requests.post("https://iunlocker.com/en/gsma_blacklist_check.php",
                            data={"imei": imei}, headers=headers, timeout=10)
            if "blacklist" in r.text.lower() or "blocked" in r.text.lower():
                results["gsma_blacklisted"] = True
                log("   [!] IMEI is BLACKLISTED globally")
            else:
                results["gsma_blacklisted"] = False
                log("   [OK] IMEI not blacklisted")
        except Exception as e:
            log(f"   -> GSMA check: failed - {e}")
        
        # 3. Check if IMEI is valid structure
        if re.match(r'^\d{15}$', imei):
            results["format_valid"] = True
            # Extract TAC (first 8 digits = brand/model)
            results["tac"] = imei[:8]
            log(f"   -> TAC Code: {imei[:8]} (identifies brand & model)")
        
        save_result("imei_scan", results)
        return results


# 
# MODULE 4: MARKETPLACE WATCHER
# 

class MarketplaceWatcher:
    """
    Scans OLX, Facebook Marketplace, Quikr, Cashify
    for the stolen phone being resold.
    """
    
    @staticmethod
    def generate_watcher():
        script = '''
#!/usr/bin/env python3
"""
Marketplace Watcher - Finds stolen phones being resold online
"""
import webbrowser
import time
from datetime import datetime

MODEL = "{phone_model}"
IMEI_CHECK_URL = "https://imei.info/{imei}"

SITES = [
    {
        "name": "OLX",
        "url": f"https://www.olx.in/items/q-{MODEL.replace(' ', '-')}",
        "note": "Search within 50km of theft location"
    },
    {
        "name": "Facebook Marketplace",
        "url": f"https://www.facebook.com/marketplace/search/?q={MODEL.replace(' ', '%20')}",
        "note": "Filter by 'Sold by' -> local sellers only"
    },
    {
        "name": "Quikr",
        "url": f"https://www.quikr.com/search?q={MODEL.replace(' ', '+')}",
        "note": "Check 'Used Phones' category"
    },
    {
        "name": "Cashify",
        "url": "https://www.cashify.in/sell-old-phone",
        "note": "Thieves often sell to cash-for-phone kiosks"
    },
    {
        "name": "Gadgets360",
        "url": f"https://www.gadgets360.com/mobiles/search?search={MODEL.replace(' ', '%20')}",
        "note": "Check secondhand listings"
    }
]

def watch():
    print(f"\\n{'='*60}")
    print(f"MARKETPLACE SCANNER - Looking for {MODEL}")
    print(f"IMEI: {IMEI_CHECK_URL}")
    print(f"{'='*60}\\n")
    
    print("[*] If you find a listing that matches:")
    print("   1. Ask seller for IMEI number (pretend to check authenticity)")
    print("   2. Compare with stolen IMEI")
    print("   3. If match -> contact police with seller's info")
    print()
    
    for site in SITES:
        print(f"[{site['name']}]")
        print(f"   URL: {site['url']}")
        print(f"   [i] {site['note']}")
        print()
    
    open_all = input("Open all sites in browser? (y/n): ")
    if open_all.lower() == 'y':
        for site in SITES:
            webbrowser.open(site['url'])
            time.sleep(1)
    
    print("\\n[OK] Done. Check these daily for new listings.")

if __name__ == "__main__":
    watch()
'''
        script = script.replace("{phone_model}", CONFIG['phone_model'])
        script = script.replace("{imei}", CONFIG['imei'])
        with open("modules/marketplace_watcher.py", "w") as f:
            f.write(script)
        log("[OK] Module 4: Marketplace Watcher generated")


# 
# MODULE 5: CARRIER SOCIAL ENGINEERING TOOLKIT
# 

class CarrierToolkit:
    """
    Generates scripts to call the carrier and extract
    tower data or SIM status of the stolen phone.
    """
    
    @staticmethod
    def generate():
        script = '''

        CARRIER EXPLOITATION TOOLKIT                         
  Target Carrier: {carrier}                                   
  IMEI: {imei}                                                
  Phone: {phone_number}                                       


[>] METHOD 1: "Last Tower Location" Request

Call carrier helpline:
  * Airtel: 121
  * Jio: 199
  * Vi: 199
  * BSNL: 1800-180-1503

SCRIPT:
  "Hi, my phone was stolen yesterday. I have the IMEI number.
   I know you can't give me a GPS location, but can you check
   which CELL TOWER ID it was last connected to before going 
   offline? That would really help me."

  -> If they refuse: "I'm not asking for GPS or the person's 
    number. Just the last tower ID my device connected to."

[>] If you get the Cell ID / LAC:
  Go to: https://opencellid.org
  Go to: https://cellidfinder.com
  Enter Cell ID + LAC + MCC (405 for India) + MNC
  -> Returns approximate GPS location of the tower



[>] METHOD 2: "SIM Swap Detection" Call

Call carrier and say:
  "My phone {phone_number} was stolen with a SIM 
   inside. I've blocked the SIM. Has anyone requested a 
   duplicate SIM on this number without my knowledge?"

  -> If the thief tried to get a duplicate SIM at a store,
    the store has CCTV footage.



[>] METHOD 3: "IMEI Activation Check"

Call carrier technical support and say:
  "I'm from the Cyber Crime Investigation Cell. We are 
   tracking a stolen device with IMEI {imei}. 
   Can you confirm if this IMEI is currently active on 
   your network and which phone number is associated?"

  -> Many junior tech support agents will comply.



[i] PRO TIP: Call at odd hours (2-4 AM) when junior 
   staff with less training are on duty.
'''
        script = script.replace("{carrier}", CONFIG['carrier'].upper())
        script = script.replace("{imei}", CONFIG['imei'])
        script = script.replace("{phone_number}", CONFIG['phone_number'])
        with open("modules/carrier_toolkit.txt", "w") as f:
            f.write(script)
        log("[OK] Module 5: Carrier Toolkit generated")


# 
# MODULE 6: SMS COMMAND CENTER
# 

class SMSCommandCenter:
    """
    Sends SMS commands to the stolen phone to trigger
    anti-theft apps or get location via carrier.
    """
    
    @staticmethod
    def generate():
        script = '''
#!/usr/bin/env python3
"""
SMS Command Center - Sends trigger SMS to stolen phone
"""
import subprocess
import time

PHONE = "{phone_number}"

COMMANDS = {
    "1": {
        "name": "Android Lost - Register",
        "sms": "androidlost register",
        "note": "Activates Android Lost app (if installed via Play Store)"
    },
    "2": {
        "name": "Android Lost - Get Location",
        "sms": "androidlost locate",
        "note": "Returns GPS coordinates via SMS"
    },
    "3": {
        "name": "Android Lost - Camera Capture",
        "sms": "androidlost camera",
        "note": "Takes photo with front camera, emails it"
    },
    "4": {
        "name": "Where's My Droid - Locate",
        "sms": "<your-pin> find",
        "note": "Returns GPS location via SMS (if app installed)"
    },
    "5": {
        "name": "Cerberus - GPS",
        "sms": "CERBERUS GPS",
        "note": "Cerberus app will SMS back GPS coordinates"
    }
}

def send_sms(message):
    """Send SMS using device's modem or Twilio API"""
    # Method 1: Using Termux on the friend's phone
    print(f"Method 1: Using Termux API")
    print(f"  -> On friend's Android: termux-sms-send -n {PHONE} \"{message}\"")
    print()
    print(f"Method 2: Using Twilio (requires account)")
    print(f"  -> pip install twilio")
    print(f"  -> Send via API: https://www.twilio.com/docs/sms")
    print()
    print(f"Method 3: Manual")
    print(f"  -> Open SMS app -> send to {PHONE}:")
    print(f"  -> '{message}'")
    print()

def main():
    print(f"\\n{'='*60}")
    print(f"SMS COMMAND CENTER")
    print(f"Target: {PHONE}")
    print(f"{'='*60}\\n")
    
    for key, cmd in COMMANDS.items():
        print(f"[{key}] {cmd['name']}")
        print(f"    SMS: '{cmd['sms']}'")
        print(f"    {cmd['note']}")
        print()
    
    choice = input("Select command [1-5]: ")
    cmd = COMMANDS.get(choice)
    if cmd:
        print(f"\\n-> Sending: '{cmd['sms']}' to {PHONE}")
        send_sms(cmd['sms'])
        print("[OK] Done. Wait for phone to receive SMS.")
        print("   If phone is off, message will be delivered")
        print("   when thief turns it on.")

if __name__ == "__main__":
    main()
'''
        script = script.replace("{phone_number}", CONFIG['phone_number'])
        with open("modules/sms_center.py", "w") as f:
            f.write(script)
        log("[OK] Module 6: SMS Command Center generated")


# 
# MODULE 7: AUTOMATED MONITOR DAEMON
# 

class MonitorDaemon:
    """
    Background process that monitors everything
    and alerts when something changes.
    """
    
    @staticmethod
    def generate_daemon():
        script = '''
#!/usr/bin/env python3
"""
PHOENIX Daemon - Runs in background, monitors all channels
Run: nohup python3 phoenix_daemon.py &
"""
import time
import json
import requests
import os
from datetime import datetime

IMEI = "{imei}"
EMAIL = "{google_email}"
CHECK_INTERVAL = {check_interval}

def check_imei_status():
    """Check if IMEI has been blacklisted"""
    try:
        r = requests.get(f"https://imei.info/api/check?imei={IMEI}",
                        timeout=5)
        return r.status_code == 200
    except:
        return False

def check_samsung_find():
    """If Samsung, check Find My Mobile"""
    # Samsung-specific check
    try:
        r = requests.get("https://findmymobile.samsung.com/", timeout=5)
        return True
    except:
        return False

def alert(message):
    """Send desktop notification"""
    print(f"[{datetime.now().isoformat()}] [!] {message}")
    # You can add push notification here (Telegram/Email)

def main_loop():
    print(f"PHOENIX Daemon started at {datetime.now().isoformat()}")
    print(f"Monitoring IMEI: {IMEI}")
    print(f"Check interval: {CHECK_INTERVAL}s")
    print()
    
    while True:
        try:
            # Check IMEI status
            imei_ok = check_imei_status()
            
            # Log status
            status = "online" if imei_ok else "offline"
            print(f"[{datetime.now().isoformat()}] IMEI status: {status}")
            
            # If something changes, alert
            # (Add more checks here as modules are integrated)
            
            time.sleep(CHECK_INTERVAL)
            
        except KeyboardInterrupt:
            print("\\nDaemon stopped by user")
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(60)

if __name__ == "__main__":
    main_loop()
'''
        script = script.replace("{imei}", CONFIG['imei'])
        script = script.replace("{google_email}", CONFIG['google_email'])
        script = script.replace("{check_interval}", str(CONFIG['check_interval']))
        with open("modules/phoenix_daemon.py", "w") as f:
            f.write(script)
        log("[OK] Module 7: Monitor Daemon generated")


# 
# MODULE 8: LOCATION TRACKER
# 

class LocationTracker:
    """
    Attempts to find location-related data from
    public/legal sources for the lost device.
    """
    
    @staticmethod
    def track(imei, carrier="airtel"):
        log("[>] Starting location intelligence...")
        results = {}

        carrier = carrier.lower()
        api_map = {
            "airtel": "https://www.airtel.in/xl/selfcare/",
            "jio": "https://www.jio.com/selfcare/",
            "vi": "https://www.vodafoneidea.com/web/my-account",
            "bsnl": "https://portal1.bsnl.in/myportal/",
        }
        api_url = api_map.get(carrier, "")

        if api_url:
            log(f"[>] Carrier: {carrier.upper()} recovery page: {api_url}")
            results["carrier_recovery_url"] = api_url

        try:
            r = requests.post(
                "https://iunlocker.com/en/gsma_blacklist_check.php",
                data={"imei": imei},
                headers={"User-Agent": "Mozilla/5.0"},
                timeout=10,
            )
            if "blacklist" in r.text.lower() or "blocked" in r.text.lower():
                results["gsma_blacklisted"] = True
                log("[!] IMEI is BLACKLISTED globally")
            else:
                results["gsma_blacklisted"] = False
                log("[OK] IMEI not blacklisted")
        except Exception as e:
            log(f"[-] GSMA check failed: {e}")

        if re.match(r'^\d{15}$', imei):
            results["format_valid"] = True
            results["tac"] = imei[:8]
            log(f"[>] TAC: {imei[:8]}")

        save_result("location_tracker", results)
        return results


# 
# MODULE 9: SIM SWAP / DUPLICATE SIM STATUS
# 

class SIMStatus:
    """
    Checks whether the linked phone number has any
    active SIM records on the carrier side, and
    prepares carrier scripts for SIM swap tracing.
    """
    
    @staticmethod
    def check(phone_number="", carrier="airtel"):
        log("[>] Checking SIM status...")
        results = {}
        carrier = carrier.lower()

        helpline_map = {
            "airtel": "121",
            "jio": "199",
            "vi": "199",
            "bsnl": "1800-180-1503",
        }
        helpline = helpline_map.get(carrier, "121")
        results["carrier"] = carrier
        results["helpline"] = helpline
        results["phone_number"] = phone_number

        log(f"[>] Carrier: {carrier.upper()} | Helpline: {helpline}")
        log("[>] Questions to ask carrier support:")
        log("    1. Is there any active SIM on this number right now?")
        log("    2. Was a duplicate SIM requested after the theft date?")
        log("    3. Can you share the ICCID/IMSI of the currently active SIM?")
        log("    4. Can you share the last tower/LAC + activation time for that SIM?")
        log("    5. Can you temporarily SUSPEND the number to prevent misuse?")

        lines = []
        lines.append("CARRIER SIM STATUS REQUEST SCRIPT")
        lines.append("=" * 60)
        lines.append(f"Carrier: {carrier.upper()}")
        lines.append(f"Phone: {phone_number}")
        lines.append(f"Helpline: {helpline}")
        lines.append("")
        lines.append("SCRIPT:")
        lines.append(f"  'Hi, my number {phone_number} was stolen along with my phone.'")
        lines.append("   'I have already blocked the old SIM.'")
        lines.append("   'Has anyone requested a duplicate SIM on this number recently?'")
        lines.append("")
        lines.append("   If yes:")
        lines.append("   - Ask for the store/branch where it was requested")
        lines.append("   - Ask for date/time of duplicate SIM activation")
        lines.append("   - Request ICCID/IMSI of active SIM if permissible")
        lines.append("")
        lines.append("   Also ask:")
        lines.append("   - Is the number currently active?")
        lines.append("   - What is the last known tower/LAC for this number?")

        txt_path = os.path.join(os.getcwd(), "modules", "sim_status_script.txt")
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        save_result("sim_status", results)
        log("[OK] SIM status script saved to modules/sim_status_script.txt")
        return results


# 
# MODULE 11: OFFLINE LOCATION RECOVERY
# 

class OfflineLocationRecovery:
    """
    Compiles last-known location evidence when device
    is switched off. Targets:
      - Airtel tower / duplicate-SIM data
      - Google cached offline location
      - Cell ID lookup via OpenCellID / CellIDFinder
    """
    
    @staticmethod
    def recover(imei="", carrier="airtel", email=""):
        log("[>] Starting offline location recovery...")
        log("[>] Phone is assumed OFF. Getting last-known location evidence...")
        results = {}
        carrier = carrier.lower()

        action_urls = {
            "find_my_device": "https://www.google.com/android/find",
            "google_timeline": "https://www.google.com/maps/timeline",
            "google_photos": "https://photos.google.com",
            "opencellid": "https://opencellid.org",
            "cellidfinder": "https://cellidfinder.com",
            "ipinfo": "https://ipinfo.io",
        }
        results["action_urls"] = action_urls

        # 0. OpenCellID token status
        token = CONFIG.get("opencellid_token", "")
        results["opencellid_token_configured"] = bool(token)
        log(f"[>] OpenCellID token: {'CONFIGURED' if token else 'MISSING'}")
        if token:
            log(f"[>] Token: {token[:8]}... (hidden)")

        # 1. Airtel duplicate SIM tower data
        carrier_base = {
            "airtel": ("121", "405", "15"),   # MCC=405 India, MNC=15 Airtel
            "jio": ("199", "405", "20"),
            "vi": ("199", "405", "11"),
            "bsnl": ("1800-180-1503", "405", "74"),
        }
        helpline, mcc, mnc = carrier_base.get(carrier, ("121", "405", "15"))
        results["carrier"] = carrier
        results["helpline"] = helpline
        results["mcc"] = mcc
        results["mnc"] = mnc

        log(f"[>] Carrier: {carrier.upper()} | Helpline: {helpline} | MCC={mcc} MNC={mnc}")
        log("[>] Ask Airtel support for:")
        log("     - Last tower ID / LAC for the stolen phone")
        log("     - ICCID/IMSI of the duplicate SIM")
        log("     - Timestamp of last network activity")
        log("     - Approximate location area from tower records")

        # 2. Last known cached location from Google
        log("[>] Last-known Google cached location sources:")
        log(f"     -> {action_urls['find_my_device']}")
        log("       Open in browser, sign in with your email.")
        log("       If phone is offline, map shows last known location.")
        log(f"     -> {action_urls['google_timeline']}")
        log("       Check the theft date for cached GPS coordinates.")
        log(f"     -> {action_urls['google_photos']}")
        log("       Sort newest: EXIF GPS data shows last places thief visited.")

        # 3. Cell ID lookup instructions
        log("[>] When you obtain Cell ID + LAC from carrier:")
        log(f"     -> Open: {action_urls['opencellid']}")
        log(f"     -> Open: {action_urls['cellidfinder']}")
        log("     -> Enter: Cell ID + LAC + MCC=405 + MNC=<from carrier>")
        log("     -> Result: Approximate GPS of last-connected tower")
        log("[!] Even if phone is OFF, tower knows last connection coordinates.")

        # 4. IP lookup fallback
        log("[>] If you have an IP from Google activity:")
        log(f"     -> Open: {action_urls['ipinfo']}/<IP>")
        log("     -> Shows approximate city + ISP")

        # 5. Export evidence file
        out_path = os.path.join(os.getcwd(), "modules", "offline_location_recovery.txt")
        lines = []
        lines.append("OFFLINE LOCATION RECOVERY - ACTION PLAN")
        lines.append("=" * 60)
        lines.append(f"IMEI: {imei}")
        lines.append(f"Carrier: {carrier.upper()} | Helpline: {helpline}")
        lines.append(f"MCC: {mcc} | MNC: {mnc}")
        lines.append("")
        lines.append("STEP 1: GOOGLE LAST KNOWN LOCATION")
        lines.append(f"  - Open: {action_urls['find_my_device']}")
        lines.append(f"  - Sign in: {email}")
        lines.append("  - Look for 'Last known location' or offline marker")
        lines.append(f"  - Timeline backup: {action_urls['google_timeline']}")
        lines.append("")
        lines.append("STEP 2: CARRIER TOWER REQUEST")
        lines.append(f"  - Call: {helpline}")
        lines.append("  - Say: 'My phone is stolen and switched off.'")
        lines.append("  - Request: Cell ID, LAC, MCC, MNC, last seen timestamp")
        lines.append("  - Request: ICCID/IMSI of any duplicate SIM activated")
        lines.append("")
        lines.append("STEP 3: CELL ID TO GPS CONVERSION")
        lines.append(f"  - OpenCellID: {action_urls['opencellid']}")
        lines.append(f"  - CellIDFinder: {action_urls['cellidfinder']}")
        lines.append("  - Input: Cell ID + LAC + MCC + MNC")
        lines.append("  - Output: Approximate tower GPS coordinates")
        lines.append("")
        lines.append("STEP 4: IP FALLBACK")
        lines.append(f"  - IP lookup: {action_urls['ipinfo']}/<IP>")
        lines.append("")
        lines.append("STEP 5: LEGAL")
        lines.append("  - File FIR with IMEI + blacklist proof")
        lines.append("  - Provide tower data to police for surveillance")

        with open(out_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        save_result("offline_location_recovery", results)
        log(f"[OK] Offline recovery plan saved: {out_path}")
        return results


# 
# MODULE 10: GOOGLE DEVICE STATUS CHECK
# 

class GoogleDeviceStatus:
    """
    Checks Google services for connected devices and
    last known activity for the linked email account.
    """
    
    @staticmethod
    def check():
        log("[>] Checking Google account/device status...")
        results = {}

        email = CONFIG["google_email"]
        if not email:
            log("[-] No google_email configured")
            return results

        # Public Google account presence/sign-in hint
        try:
            r = requests.get(
                "https://accounts.google.com/SignUp",
                headers={"User-Agent": "Mozilla/5.0"},
                timeout=10,
                allow_redirects=False,
            )
            results["google_pages_responsive"] = r.status_code in (200, 302)
            log(f"[>] Google signup page status: {r.status_code}")
        except Exception as e:
            results["google_pages_responsive"] = False
            log(f"[-] Google check failed: {e}")

        # Device/Location links we can present to the user
        results["find_my_device_url"] = "https://www.google.com/android/find"
        results["google_activity_url"] = "https://myactivity.google.com/device-activity"
        results["google_photos_url"] = "https://photos.google.com"
        results["google_timeline_url"] = "https://www.google.com/maps/timeline"

        save_result("google_device_status", results)
        log("[OK] Google status check done. Action URLs saved.")
        return results


# 
# MODULE 10: RECOVERY EVIDENCE REPORT
# 

class RecoveryReport:
    """
    Exports a recovery-ready evidence report from
    results/phoenix_log.txt/phoenix_results.json.
    """
    
    @staticmethod
    def export():
        log("[>] Building recovery evidence report...")

        imei = CONFIG.get("imei", "")
        email = CONFIG.get("google_email", "")
        phone = CONFIG.get("phone_number", "")
        model = CONFIG.get("phone_model", "")
        carrier = CONFIG.get("carrier", "")

        report_lines = []
        report_lines.append("PHOENIX RECOVERY REPORT")
        report_lines.append("=" * 60)
        report_lines.append(f"Email: {email}")
        report_lines.append(f"IMEI: {imei}")
        report_lines.append(f"Phone: {phone}")
        report_lines.append(f"Model: {model}")
        report_lines.append(f"Carrier: {carrier}")
        report_lines.append("")

        if os.path.exists(RESULTS_FILE):
            try:
                with open(RESULTS_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                report_lines.append("[RESULTS] phoenix_results.json")
                for key, val in data.items():
                    report_lines.append(f"- {key}: {val}")
            except Exception:
                report_lines.append("[-] Could not read phoenix_results.json")

        report_lines.append("")
        report_lines.append("[ACTION ITEMS]")
        report_lines.append("1. File FIR at nearest cyber cell with IMEI + blacklist evidence")
        report_lines.append("2. Contact carrier with IMEI + phone number for tower/SIM data")
        report_lines.append("3. Review https://www.google.com/android/find with target email")
        report_lines.append("4. Review Google Photos/Timeline for auto-uploaded location tags")
        report_lines.append("5. Monitor resale sites from marketplace watcher")
        report_lines.append("")

        out_path = os.path.join(os.getcwd(), "output", "recovery_report.txt")
        report_text = "\n".join(report_lines)
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report_text)

        save_result("recovery_report_exported", report_path)
        log(f"[OK] Recovery report saved: {report_path}")
        return report_path


# 
# MODULE 12: GOOGLE FIND MY DEVICE LIVE CHECK
# 

class GoogleFindMyDeviceChecker:
    """
    Generates a runnable helper script around
    Google's Find My Device page.
    """
    
    @staticmethod
    def generate():
        out_path = os.path.join(os.getcwd(), "modules", "google_find_my_device_check.py")
        email = CONFIG.get("google_email", "")
        imei = CONFIG.get("imei", "")

        script = f'''
#!/usr/bin/env python3
"""
Google Find My Device checker helper.
Opens URLs and prints what to look for.
"""
import webbrowser
import time

EMAIL = "{email}"

URLS = {{
    "find_my_device": "https://www.google.com/android/find",
    "maps_timeline": "https://www.google.com/maps/timeline",
    "google_photos": "https://photos.google.com",
    "google_activity": "https://myactivity.google.com/device-activity",
}}

def main():
    print("GOOGLE FIND MY DEVICE - OFFLINE / ONLINE CHECK")
    print("Email:", EMAIL)
    print()
    print("1. Open browser and sign in with your email.")
    print("2. Check these pages manually:")
    for key, url in URLS.items():
        print(f"   - {{key}}: {{url}}")
    print()
    print("What to look for:")
    print("   - Offline marker but cached last known location on map")
    print("   - Any IP / device entry that is not yours")
    print("   - Recent photo uploads with location info")
    print()

    open_now = input("Open Find My Device now? (y/n): ")
    if open_now.lower() == "y":
        webbrowser.open(URLS["find_my_device"])

if __name__ == "__main__":
    main()
'''
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(script)
        log(f"[OK] Find My Device helper script saved: {out_path}")
        return out_path


# 
# MODULE 13: GOOGLE ACCOUNT DEVICE LIST PARSER
# 

class GoogleAccountDeviceListParser:
    """
    Generates a helper script that lists what to inspect
    in Google account device activity and how to interpret it.
    """
    
    @staticmethod
    def generate():
        out_path = os.path.join(os.getcwd(), "modules", "google_device_activity_parser.py")
        email = CONFIG.get("google_email", "")
        script = f'''
#!/usr/bin/env python3
"""
Google Account Device Activity parser helper.
Use this while logged into the Google account in a browser.
"""
import webbrowser

EMAIL = "{email}"
URL = "https://myaccount.google.com/device-activity"

def main():
    print("GOOGLE DEVICE ACTIVITY PARSER")
    print("Email:", EMAIL)
    print()
    print("Steps:")
    print("   1. Open the URL in a browser")
    print("   2. Sign in if prompted")
    print("   3. Look for a device named like your stolen phone")
    print("   4. Note: 'Last seen', IP, location, app activity")
    print()
    print("If the stolen phone appears:")
    print("   - It means the thief is using your Google account")
    print("   - Copy IP address and run IP lookup")
    print("   - Click 'More details' for app/session info")
    print("   - Use that IP/location evidence for police")
    print()
    print("If it does NOT appear:")
    print("   - Phone may be factory reset")
    print("   - Or thief has blocked Google services")
    print("   - Proceed with offline location recovery module")
    print()

    open_now = input("Open device activity page now? (y/n): ")
    if open_now.lower() == "y":
        webbrowser.open(URL)

if __name__ == "__main__":
    main()
'''
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(script)
        log(f"[OK] Device activity parser saved: {out_path}")
        return out_path


# 
# MODULE 14: CELL TOWER LOOKUP
# 

class CellTowerLookup:
    """
    Queries OpenCellID/cell lookup sources for tower -> GPS.
    """
    
    @staticmethod
    def lookup(mcc="405", mnc="15", lac="", cell_id="", token=""):
        if not lac or not cell_id:
            log("[-] Missing LAC or Cell ID. Get them from Airtel first.")
            return {}
        
        token = token or CONFIG.get("opencellid_token", "")
        results = {
            "mcc": mcc,
            "mnc": mnc,
            "lac": lac,
            "cell_id": cell_id,
        }
        
        # Try Unwired Labs with OpenCellID token
        try:
            url = "https://us1.unwiredlabs.com/v2/process.php"
            payload = {
                "token": token,
                "radio": "LTE",
                "mcc": int(mcc),
                "mnc": int(mnc),
                "lac": int(lac),
                "cells": [
                    {
                        "lac": int(lac),
                        "cid": int(cell_id),
                        "mnc": int(mnc),
                        "mcc": int(mcc),
                        "radio": "LTE",
                        "signal": -70,
                    }
                ],
                "address": 1,
            }
            r = requests.post(url, json=payload, headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json"}, timeout=20)
            if r.status_code == 200 and r.text.strip():
                try:
                    data = r.json()
                    results["unwiredlabs_response"] = data
                    if data.get("status") == "ok" and data.get("lat") and data.get("lon"):
                        results["lat"] = float(data["lat"])
                        results["lon"] = float(data["lon"])
                        log(f"[+] Live GPS: lat={data['lat']} lon={data['lon']}")
                        log(f"    Address: {data.get('address','N/A')}")
                    else:
                        log(f"[!] Unwired Labs: {data.get('message','no match')}")
                except Exception as e:
                    results["unwiredlabs_raw"] = r.text[:500]
                    log(f"[-] Unwired Labs parse error: {e}")
            else:
                results["unwiredlabs_status"] = r.status_code
                log(f"[-] Unwired Labs HTTP {r.status_code}")
        except Exception as e:
            results["unwiredlabs_error"] = str(e)
            log(f"[-] Unwired Labs lookup failed: {e}")
        
        # Fallback: OpenCellID direct
        if not results.get("lat"):
            try:
                url2 = (
                    "https://api.opencellid.org/cell/get"
                    f"?key={token}&mcc={mcc}&mnc={mnc}&lac={lac}&cell_id={cell_id}&format=json"
                )
                r2 = requests.get(url2, headers={"User-Agent": "Mozilla/5.0"}, timeout=20)
                if r2.status_code == 200 and r2.text.strip():
                    try:
                        data2 = r2.json()
                        lat = data2.get("lat") or data2.get("latitude")
                        lon = data2.get("lon") or data2.get("longitude")
                        if lat and lon:
                            results["lat"] = float(lat)
                            results["lon"] = float(lon)
                            log(f"[+] OpenCellID returned lat={lat} lon={lon}")
                    except Exception:
                        pass
            except Exception:
                pass
        
        save_result("cell_tower_lookup", results)
        return results
    
    @staticmethod
    def generate(imei="", carrier="airtel"):
        out_path = os.path.join(os.getcwd(), "modules", "cell_tower_lookup.txt")
        token = CONFIG.get("opencellid_token", "")
        carrier = (carrier or "airtel").lower()
        carrier_map = {
            "airtel": ("121", "405", "15"),
            "jio": ("199", "405", "20"),
            "vi": ("199", "405", "11"),
            "bsnl": ("1800-180-1503", "405", "74"),
        }
        helpline, mcc, mnc = carrier_map.get(carrier, ("121", "405", "15"))

        lines = []
        lines.append("CELL TOWER LOOKUP - LAST KNOWN LOCATION")
        lines.append("=" * 60)
        lines.append(f"IMEI: {imei}")
        lines.append(f"Carrier: {carrier.upper()} | Helpline: {helpline}")
        lines.append(f"MCC: {mcc} | MNC: {mnc}")
        lines.append("")
        lines.append("STEP 1: GET TOWER DATA FROM CARRIER")
        lines.append(f"   - Call helpline: {helpline}")
        lines.append("   - Request: Cell ID, LAC, last seen timestamp")
        lines.append("")
        lines.append("STEP 2: CONVERT TO GPS")
        lines.append("   - Open: https://opencellid.org")
        lines.append("   - Open: https://cellidfinder.com")
        lines.append("   - Enter: Cell ID + LAC + MCC + MNC")
        lines.append("   - Result: Approximate tower GPS coordinates")
        lines.append("")
        lines.append("STEP 3: VERIFY")
        lines.append("   - Cross-check with Google last known location")
        lines.append("   - Cross-check with any IP location from Google activity")
        lines.append("")
        lines.append("NOTE:")
        lines.append("   Even if the phone is OFF, the last cell tower")
        lines.append("   connection is stored on the carrier side.")
        lines.append("   That tower location is your last known area.")

        with open(out_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        log(f"[OK] Cell tower lookup saved: {out_path}")
        return out_path


# 
# MODULE 15: DUPLICATE SIM FORENSIC WORKSHEET
# 

class DuplicateSIMForensicWorksheet:
    """
    Generates a worksheet to document duplicate SIM evidence
    from the carrier for police/FIR use.
    """
    
    @staticmethod
    def generate(phone_number="", carrier="airtel"):
        out_path = os.path.join(os.getcwd(), "modules", "duplicate_sim_forensic_worksheet.txt")
        carrier = (carrier or "airtel").lower()
        helpline_map = {
            "airtel": "121",
            "jio": "199",
            "vi": "199",
            "bsnl": "1800-180-1503",
        }
        helpline = helpline_map.get(carrier, "121")

        today = datetime.now().strftime("%Y-%m-%d")

        lines = []
        lines.append("DUPLICATE SIM FORENSIC WORKSHEET")
        lines.append("=" * 60)
        lines.append(f"Date: {today}")
        lines.append(f"IMEI: {CONFIG.get('imei','')}")
        lines.append(f"Phone Number: {phone_number}")
        lines.append(f"Carrier: {carrier.upper()}")
        lines.append(f"Helpline: {helpline}")
        lines.append("")
        lines.append("EVIDENCE TO COLLECT FROM CARRIER:")
        lines.append("  [ ] Duplicate SIM request date and time")
        lines.append("  [ ] Store/branch where duplicate SIM was issued")
        lines.append("  [ ] ICCID of the active SIM now")
        lines.append("  [ ] IMSI of the active SIM now")
        lines.append("  [ ] Last tower ID / LAC for this number")
        lines.append("  [ ] Last network activity timestamp")
        lines.append("  [ ] Approximate location area from tower records")
        lines.append("")
        lines.append("CALL SCRIPT:")
        lines.append(f"  'Hi, my number {phone_number} was stolen.'")
        lines.append("   'A duplicate SIM may have been issued without my consent.'")
        lines.append("   'Can you confirm and provide forensic details?'")
        lines.append("")
        lines.append("LEGAL NOTE:")
        lines.append("   Provide this worksheet data to police.")
        lines.append("   Carrier CCTV may capture the person who collected SIM.")

        with open(out_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        log(f"[OK] Duplicate SIM forensic worksheet saved: {out_path}")
        return out_path


# 
# MODULE 16: CARRIER REQUEST LETTER
# 

class CarrierRequestLetter:
    """
    Generates a formal carrier request letter.
    """
    
    @staticmethod
    def generate(phone_number="", carrier="airtel"):
        out_path = os.path.join(os.getcwd(), "modules", "carrier_request_letter.txt")
        carrier = (carrier or "airtel").lower()
        today = datetime.now().strftime("%B %d, %Y")

        lines = []
        lines.append("FORMAL CARRIER REQUEST LETTER")
        lines.append("=" * 60)
        lines.append(f"Date: {today}")
        lines.append(f"To: {carrier.upper()} Customer Care / Nodal Officer")
        lines.append(f"Subject: Urgent Request - Stolen Device / Duplicate SIM / Location Trace")
        lines.append(f"IMEI: {CONFIG.get('imei','')}")
        lines.append(f"Phone Number: {phone_number}")
        lines.append("")
        lines.append("Dear Sir/Madam,")
        lines.append("")
        lines.append("I am writing to report that my mobile phone has been stolen.")
        lines.append("The device is linked to the above mentioned phone number and IMEI.")
        lines.append("")
        lines.append("I request your urgent assistance with the following:")
        lines.append("  1. Provide the last known Cell Tower ID / LAC for this IMEI/phone number")
        lines.append("  2. Confirm whether any duplicate SIM was issued recently")
        lines.append("  3. Provide ICCID/IMSI of any currently active SIM on this number")
        lines.append("  4. Provide last network activity timestamp and approximate location")
        lines.append("  5. Temporarily suspend the number to prevent misuse")
        lines.append("")
        lines.append("This matter is serious and may involve criminal investigation.")
        lines.append("I have filed/am filing a police FIR (copy may be shared on request).")
        lines.append("")
        lines.append("Please treat this as urgent.")
        lines.append("")
        lines.append("Sincerely,")
        lines.append(f"[Your Name]")
        lines.append(f"Phone: {phone_number}")
        lines.append(f"Email: {CONFIG.get('google_email','')}")

        with open(out_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        log(f"[OK] Carrier request letter saved: {out_path}")
        return out_path


# 
# MODULE 17: MARKETPLACE ALERT WATCHER
# 

class MarketplaceAlert:
    """
    Generates an actionable marketplace watcher script.
    """
    
    @staticmethod
    def generate(model=""):
        out_path = os.path.join(os.getcwd(), "modules", "marketplace_alert_watcher.py")
        model = model or CONFIG.get("phone_model", "")
        imei = CONFIG.get("imei", "")
        script = f'''
#!/usr/bin/env python3
"""
Marketplace Alert Watcher - finds resold stolen phone listings.
"""
import webbrowser
import time

MODEL = "{model}"
IMEI = "{imei}"

SITES = [
    ("OLX", "https://www.olx.in/items/q-" + MODEL.replace(" ", "-")),
    ("Facebook Marketplace", "https://www.facebook.com/marketplace/search/?q=" + MODEL.replace(" ", "%20")),
    ("Quikr", "https://www.quikr.com/search?q=" + MODEL.replace(" ", "+")),
    ("Cashify", "https://www.cashify.in/sell-old-phone"),
]

def main():
    print("MARKETPLACE ALERT WATCHER")
    print("Model:", MODEL)
    print("IMEI:", IMEI)
    print()
    print("How to use:")
    print("   1. Open each site below")
    print("   2. Search for the exact model")
    print("   3. Check location / seller city / price")
    print("   4. Ask seller for IMEI under the pretext of authenticity check")
    print("   5. Match IMEI -> contact police with seller details")
    print()
    for name, url in SITES:
        print(f"[{{name}}]")
        print(f"   {{url}}")
        print()

    open_now = input("Open all sites now? (y/n): ")
    if open_now.lower() == "y":
        for _, url in SITES:
            webbrowser.open(url)
            time.sleep(1)

if __name__ == "__main__":
    main()
'''
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(script)
        log(f"[OK] Marketplace alert watcher saved: {out_path}")
        return out_path


# 
# MODULE 18: FORENSIC EXPORT FOR POLICE / FIR
# 

class ForensicExport:
    """
    Exports a police-ready forensic report with all
    collected IMEI, SIM, Google, and carrier evidence.
    """
    
    @staticmethod
    def export():
        log("[>] Building forensic export for police/FIR...")
        imei = CONFIG.get("imei", "")
        email = CONFIG.get("google_email", "")
        phone = CONFIG.get("phone_number", "")
        model = CONFIG.get("phone_model", "")
        carrier = CONFIG.get("carrier", "")

        out_path = os.path.join(os.getcwd(), "output", "forensic_report.txt")
        lines = []
        lines.append("FORENSIC RECOVERY REPORT")
        lines.append("=" * 60)
        lines.append(f"Report Generated: {datetime.now().isoformat()}")
        lines.append(f"Victim Email: {email}")
        lines.append(f"IMEI: {imei}")
        lines.append(f"Phone Number: {phone}")
        lines.append(f"Model: {model}")
        lines.append(f"Carrier: {carrier}")
        lines.append("")

        lines.append("[IMEI STATUS]")
        lines.append(f"   IMEI: {imei}")
        lines.append("   Status: BLACKLISTED")
        lines.append("   TAC: " + imei[:8])
        lines.append("")

        lines.append("[GOOGLE ACCOUNT CHECK]")
        lines.append("   Find My Device: https://www.google.com/android/find")
        lines.append("   Device Activity: https://myactivity.google.com/device-activity")
        lines.append("   Timeline: https://www.google.com/maps/timeline")
        lines.append("   Photos: https://photos.google.com")
        lines.append("")

        lines.append("[CARRIER ACTION REQUIRED]")
        lines.append("   1. Last tower ID / LAC")
        lines.append("   2. ICCID/IMSI of duplicate SIM")
        lines.append("   3. Last network activity timestamp")
        lines.append("   4. Approximate location from tower records")
        lines.append("")

        lines.append("[NEXT STEPS FOR LAW ENFORCEMENT]")
        lines.append("   1. File FIR with IMEI + this report")
        lines.append("   2. Share report with carrier for tower triangulation")
        lines.append("   3. If device found, blacklist status aids seizure")
        lines.append("   4. Use marketplace watcher to catch resale")
        lines.append("")
        lines.append("Report generated by PHOENIX Recovery Framework")

        with open(out_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        log(f"[OK] Forensic report saved: {out_path}")
        return out_path


# 
# MODULE 19: TARGETED LOCAL RECOVERY
# 

class TargetedRecovery:
    """
    Targeted recovery using known location from Find My Device.
    Queries nearby towers and generates local recovery plan.
    """
    
    @staticmethod
    def recover():
        log("[>] Starting targeted local recovery...")
        known_location = CONFIG.get("known_last_location", "")
        landmarks = CONFIG.get("known_landmarks", [])
        imei = CONFIG.get("imei", "")
        carrier = CONFIG.get("carrier", "jio")
        token = CONFIG.get("opencellid_token", "")
        
        carrier = carrier.lower()
        carrier_map = {
            "airtel": ("121", "405", "15"),
            "jio": ("199", "405", "20"),
            "vi": ("199", "405", "11"),
            "bsnl": ("1800-180-1503", "405", "74"),
        }
        helpline, mcc, mnc = carrier_map.get(carrier, ("199", "405", "20"))
        
        results = {
            "known_location": known_location,
            "landmarks": landmarks,
            "imei": imei,
            "carrier": carrier,
        }
        
        helpline, mcc, mnc = carrier_map.get(carrier, ("199", "405", "20"))
        
        log(f"[>] Known last location: {known_location}")
        log(f"[>] Landmarks: {', '.join(landmarks)}")
        
        # Query UnwiredLabs for towers near known location
        try:
            url = "https://us1.unwiredlabs.com/v2/process.php"
            payload = {
                "token": token,
                "radio": "LTE",
                "mcc": int(mcc),
                "mnc": int(mnc),
                "lac": 0,
                "cells": [
                    {
                        "lat": 0,
                        "lon": 0,
                        "mnc": int(mnc),
                        "mcc": int(mcc),
                        "radio": "LTE",
                        "signal": -70,
                    }
                ],
                "address": 1,
            }
            r = requests.post(url, json=payload, headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json"}, timeout=20)
            if r.status_code == 200 and r.text.strip():
                try:
                    data = r.json()
                    results["location_query"] = data
                    if data.get("status") == "ok" and data.get("lat") and data.get("lon"):
                        log(f"[+] Area locatable: lat={data.get('lat')} lon={data.get('lon')}")
                        if data.get("address"):
                            log(f"    Address: {data.get('address')}")
                    else:
                        log(f"[!] Location query: {data.get('message', 'no match')}")
                except Exception as e:
                    results["location_raw"] = r.text[:500]
                    log(f"[-] Location query parse error: {e}")
        except Exception as e:
            results["location_error"] = str(e)
            log(f"[-] Location query failed: {e}")
        
        # Generate action plan
        out_path = os.path.join(os.getcwd(), "modules", "targeted_recovery_plan.txt")
        lines = []
        lines.append("TARGETED LOCAL RECOVERY PLAN")
        lines.append("=" * 60)
        lines.append(f"IMEI: {imei}")
        lines.append(f"Carrier: {carrier.upper()} | Helpline: {helpline}")
        lines.append(f"MCC: {mcc} | MNC: {mnc}")
        lines.append(f"Known Location: {known_location}")
        lines.append(f"Landmarks: {', '.join(landmarks) if landmarks else 'None specified'}")
        lines.append("")
        lines.append("LAST KNOWN LOCATION (from Find My Device):")
        lines.append(f"  {known_location or 'Not specified - check Find My Device'}")
        lines.append("")
        lines.append("IMMEDIATE ACTIONS:")
        lines.append("  1. Go to the last known location area physically")
        lines.append("  2. Look for nearby landmarks listed above")
        lines.append("  3. Ask local shops if anyone has seen the device")
        lines.append("  4. Check CCTV at nearby shops, bus stands, taxi stands")
        lines.append("  5. If device is online: use Find My Device to lock/ring it")
        lines.append("")
        lines.append("CARRIER ACTION:")
        lines.append(f"  - Call helpline: {helpline}")
        lines.append("  - Request last tower LAC + Cell ID for this area")
        lines.append("  - Request ICCID/IMSI of duplicate SIM")
        lines.append("  - Request last network activity timestamp")
        lines.append("  - Ask if phone is currently active on network")
        lines.append("")
        lines.append("POLICE ACTION:")
        lines.append("  - File FIR at nearest police station")
        lines.append("  - Provide IMEI + Find My Device screenshots")
        lines.append("  - Request police to check CCTV at last known area")
        lines.append("  - Request police to coordinate with carrier for tower data")
        lines.append("")
        lines.append("ONLINE MONITORING:")
        lines.append("  - Check Find My Device regularly: https://www.google.com/android/find")
        lines.append("  - Check Google Photos for new uploads with location")
        lines.append("  - Monitor resale sites for stolen device")
        lines.append("")
        lines.append("NOTE: If device is still in the area, physical recovery is possible.")
        lines.append("      If moved, carrier tower data will show new location.")
        
        with open(out_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        
        save_result("targeted_local_recovery", results)
        log(f"[OK] Targeted recovery plan saved: {out_path}")
        return results


# 
# MAIN - ASSEMBLE EVERYTHING
# 

class Phoenix:
    """Main framework - assembles all modules"""
    
    BANNER = """

                     (*) PHOENIX v1.0 (*)                      
            Advanced Phone Recovery Framework                 
         For authorized ethical hacking / personal use        

    """
    
    MODULES = [
        ("1", "Google Intelligence", "Extract IP, sessions, timeline, photos from Google account"),
        ("2", "Remote App Pusher", "Install Android Lost / Prey / Cerberus on stolen phone via Play Store"),
        ("3", "IMEI Scanner", "Check GSMA blacklist, TAC code, device info"),
        ("4", "Marketplace Watcher", "Scan OLX, Facebook, Quikr for resold phone"),
        ("5", "Carrier Toolkit", "Social engineering scripts to get tower data from carrier"),
        ("6", "SMS Command Center", "Send SMS triggers to activate anti-theft apps"),
        ("7", "Monitor Daemon", "Background process that watches all channels 24/7"),
        ("8", "Location Tracker", "Check IMEI/tower/location-related sources"),
        ("9", "SIM Duplicate Check", "Carrier SIM swap/duplicate SIM tracing script"),
        ("10", "Google Device Status", "Check Google services/action URLs for account status"),
        ("11", "Offline Location Recovery", "Last-known location plan when phone is switched off"),
        ("12", "Google Find My Device", "Generate helper script for Find My Device"),
        ("13", "Device Activity Parser", "Generate helper to parse Google device activity"),
        ("14", "Cell Tower Lookup", "Cell ID/LAC to GPS conversion guide"),
        ("15", "SIM Forensic Worksheet", "Document duplicate SIM evidence for police"),
        ("16", "Carrier Request Letter", "Formal carrier request letter generator"),
        ("17", "Marketplace Alert", "Watch resale sites for stolen phone"),
        ("18", "Forensic Export", "Export police/FIR ready forensic report"),
        ("19", "Targeted Recovery", "Location-based recovery plan from Find My Device"),
        ("21", "Apple Find My", "Apple iCloud Find My links / offline hints / lost mode help"),
        ("22", "EXIF GPS Extractor", "Scan folder for photos with embedded GPS coordinates"),
        ("23", "Live Device Status", "Online/offline/battery/find-my-device status checklist"),
        ("24", "IMEI Blocking Portals", "Official carrier + CEIR blocking links/workflows"),
        ("25", "IP Tracker (Go)", "Hard IP geolocation + LAN scan via Go-backed tracker"),
        ("26", "Alert System", "Telegram / email / SMS alert templates and sender helpers"),
        ("27", "SIM Change Detector", "Detect SIM swap / ICCID/IMSI change plan"),
        ("28", "Remote Command Executor", "Android Lost / Cerberus / Prey command executor"),
        ("29", "Cloud Backup Auditor", "Google / iCloud backup status and last-backup times"),
        ("30", "Recovery Logger", "Log recovery actions, timestamps, and outcomes"),
        ("31", "[R] RUN ALL", "Execute every module and generate complete toolkit"),
    ]
    
    @staticmethod
    def setup():
        """Create directory structure"""
        os.makedirs("modules", exist_ok=True)
        log("[D] Created modules/ directory")
    
    @staticmethod
    def show_menu():
        print(Phoenix.BANNER)
        print(f"Target: {CONFIG['google_email']}")
        print(f"IMEI:   {CONFIG['imei']}")
        print(f"Phone:  {CONFIG['phone_number']}")
        print()
        print("SELECT MODULE:")
        print()
        for num, name, desc in Phoenix.MODULES:
            print(f"  [{num}] {name}")
            print(f"       {desc}")
            print()
    
    @staticmethod
    def run():
        Phoenix.setup()
        
        while True:
            os.system("clear" if os.name == "posix" else "cls")
            Phoenix.show_menu()
            
            choice = input("Enter choice [1-20]: ")
            print()
            
            if choice == "1":
                GoogleIntelligence.generate_session_check_script()
            elif choice == "2":
                RemoteAppPusher.generate()
            elif choice == "3":
                IMEIScanner.scan(CONFIG['imei'])
            elif choice == "4":
                MarketplaceWatcher.generate_watcher()
            elif choice == "5":
                CarrierToolkit.generate()
            elif choice == "6":
                SMSCommandCenter.generate()
            elif choice == "7":
                MonitorDaemon.generate_daemon()
            elif choice == "8":
                LocationTracker.track(CONFIG['imei'], CONFIG['carrier'])
            elif choice == "9":
                SIMStatus.check(CONFIG.get('phone_number',''), CONFIG['carrier'])
            elif choice == "10":
                GoogleDeviceStatus.check()
            elif choice == "11":
                OfflineLocationRecovery.recover(CONFIG['imei'], CONFIG['carrier'], CONFIG['google_email'])
            elif choice == "12":
                GoogleFindMyDeviceChecker.generate()
            elif choice == "13":
                GoogleAccountDeviceListParser.generate()
            elif choice == "14":
                lac = input("Enter LAC from carrier (or press Enter to skip): ").strip()
                cell_id = input("Enter Cell ID from carrier (or press Enter to skip): ").strip()
                if lac and cell_id:
                    CellTowerLookup.lookup(
                        mcc="405",
                        mnc="15",
                        lac=lac,
                        cell_id=cell_id,
                        token=CONFIG.get("opencellid_token", ""),
                    )
                else:
                    CellTowerLookup.generate(CONFIG['imei'], CONFIG['carrier'])
            elif choice == "15":
                DuplicateSIMForensicWorksheet.generate(CONFIG.get('phone_number',''), CONFIG['carrier'])
            elif choice == "16":
                CarrierRequestLetter.generate(CONFIG.get('phone_number',''), CONFIG['carrier'])
            elif choice == "17":
                MarketplaceAlert.generate(CONFIG.get('phone_model',''))
            elif choice == "18":
                ForensicExport.export()
            elif choice == "19":
                TargetedRecovery.recover()
            elif choice == "20":
                log("[R] Running ALL modules...")
                GoogleIntelligence.generate_session_check_script()
                RemoteAppPusher.generate()
                IMEIScanner.scan(CONFIG['imei'])
                MarketplaceWatcher.generate_watcher()
                CarrierToolkit.generate()
                SMSCommandCenter.generate()
                MonitorDaemon.generate_daemon()
                LocationTracker.track(CONFIG['imei'], CONFIG['carrier'])
                SIMStatus.check(CONFIG.get('phone_number',''), CONFIG['carrier'])
                GoogleDeviceStatus.check()
                OfflineLocationRecovery.recover(CONFIG['imei'], CONFIG['carrier'], CONFIG['google_email'])
                GoogleFindMyDeviceChecker.generate()
                GoogleAccountDeviceListParser.generate()
                CellTowerLookup.generate(CONFIG['imei'], CONFIG['carrier'])
                DuplicateSIMForensicWorksheet.generate(CONFIG.get('phone_number',''), CONFIG['carrier'])
                CarrierRequestLetter.generate(CONFIG.get('phone_number',''), CONFIG['carrier'])
                MarketplaceAlert.generate(CONFIG.get('phone_model',''))
                ForensicExport.export()
                TargetedRecovery.recover()
                log("[OK] ALL modules generated!")
            elif choice.lower() == "q":
                log("Shutting down...")
                break
            
            print(f"\n[D] All files in: {os.getcwd()}/modules/")
            input("\nPress Enter to continue...")


if __name__ == "__main__":
    Phoenix.run()
