# 📱 PhoneRecover - Lost Phone Recovery Toolkit

**If your phone was stolen or lost, this tool helps you track and recover it.**

Works on **Windows, macOS, Linux, and Kali Linux**.

---

## ⚡ Quick Start

```bash
# 1. Clone the repo
git clone https://github.com/jojin1709/PhoneRecover---Lost-Phone-Recovery-Toolkit.git
cd PhoneRecover---Lost-Phone-Recovery-Toolkit

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run setup and enter your details
python setup.py

# 4. Run the main tool
python phonerecover.py

# Or run the advanced toolkit
python PHOENIX.py
```

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| **IMEI Check** | Validates IMEI and checks blacklist status |
| **Google Find My Device** | Generates direct links to locate your phone |
| **Apple Find My** | iCloud Find My links and lost-mode guidance |
| **Carrier Scripts** | Ready-to-use scripts for Jio, Airtel, VI, BSNL |
| **Police Report** | Generates FIR-ready incident report |
| **Cell Tower GPS** | Converts LAC + Cell ID to GPS coordinates |
| **IP Tracker** | Traces IP addresses to city/ISP/lat-lon |
| **EXIF GPS** | Extracts GPS from photos if available |
| **SIM Swap Detector** | Detects duplicate SIM activations |
| **Marketplace Watcher** | Monitors OLX, Facebook, Quikr for resale |
| **Alert System** | Telegram/email/SMS alert templates |
| **Recovery Logger** | Logs all actions and outcomes |
| **Cloud Backup Audit** | Checks Google/iCloud backup status |
| **Timeline Importer** | Imports Google Takeout location history |
| **Remote Commands** | Android Lost / Cerberus / Prey command executor |
| **Device Status** | Online/offline/battery status checklist |
| **IMEI Blocking** | Official CEIR and carrier blocking portals |

---

## 📋 Requirements

- **Python 3.8+**
- **Go 1.19+** (optional, for IP tracker module)
- **Internet connection** (for lookup services)

### Kali Linux / Debian / Ubuntu

```bash
# Install Python and pip
sudo apt update
sudo apt install python3 python3-pip -y

# Install Go (for IP tracker)
sudo apt install golang-go -y

# Install Python dependencies
pip3 install -r requirements.txt

# Optional: install Pillow for EXIF GPS
sudo apt install python3-pil -y
```

---

## 🚀 Usage

### Step 1: Setup

Run setup and enter your details:

```bash
python setup.py
```

You will be asked for:
- IMEI number (15 digits)
- Phone number (+91...)
- Google email
- Phone model
- Carrier (Jio / Airtel / VI / BSNL)

This saves a `user_config.json` file (ignored by git).

### Step 2: Main Tool

```bash
python phonerecover.py
```

Options:
1. IMEI check + blacklist status
2. Google Find My Device links
3. Carrier request script
4. Police / FIR report
5. Marketplace watcher
6. **ALL actions at once**

### Step 3: Advanced Toolkit

```bash
python PHOENIX.py
```

Full menu with 25+ modules:
- Google intelligence
- Remote app pusher
- IMEI scanner
- Marketplace watcher
- Carrier toolkit
- SMS command center
- Monitor daemon
- Location tracker
- SIM duplicate check
- Google device status
- Offline location recovery
- Google Find My Device
- Device activity parser
- Cell tower lookup
- SIM forensic worksheet
- Carrier request letter
- Marketplace alert
- Forensic export
- Targeted recovery
- Apple Find My
- EXIF GPS extractor
- Live device status
- IMEI blocking portals
- IP tracker (Go)
- Alert system
- SIM change detector
- Remote command executor
- Cloud backup auditor
- Recovery logger

---

## 🔧 Configuration

Edit `user_config.json` to update your details:

```json
{
  "imei": "123456789012345",
  "phone_number": "+919999999999",
  "google_email": "your@gmail.com",
  "phone_model": "Your Phone Model",
  "carrier": "jio",
  "opencellid_token": ""
}
```

Or run `python setup.py` again.

---

## 📞 Supported Carriers (India)

| Carrier | Helpline | MCC | MNC |
|---------|----------|-----|-----|
| Jio | 199 | 405 | 20 |
| Airtel | 121 | 405 | 15 |
| VI | 199 | 405 | 11 |
| BSNL | 1800-180-1503 | 405 | 74 |

---

## 🗺️ How It Works

```
┌─────────────────────────────────────────────┐
│  1. User runs setup.py                      │
│     → Enters IMEI, phone, email, carrier    │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│  2. User runs phonerecover.py / PHOENIX.py  │
│     → Tool generates all reports/scripts    │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│  3. User takes action                       │
│     ├── Opens Google Find My Device         │
│     ├── Calls carrier for tower data        │
│     ├── Files FIR with generated report     │
│     ├── Checks resale sites                 │
│     └── Monitors for device activity        │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│  4. If tower data obtained (LAC+Cell ID)    │
│     → Run law_enforcement_tower_tracker.py  │
│     → Gets exact GPS coordinates            │
└─────────────────────────────────────────────┘
```

---

## 🚨 Emergency Actions

If your phone was stolen **RIGHT NOW**:

1. **Block IMEI**: https://ceir.gov.in/
2. **Call carrier**: Request blacklist and last tower data
3. **Google Find My**: https://www.google.com/android/find
4. **File FIR**: Go to nearest police station with IMEI and proof
5. **Check device activity**: https://myaccount.google.com/device-activity

---

## 📁 Project Structure

```
PhoneRecover/
├── phonerecover.py            # Main user-friendly tool
├── PHOENIX.py                 # Advanced toolkit with 25+ modules
├── setup.py                   # One-time setup for your details
├── imei_tracker.py            # Terminal-based tracker
├── requirements.txt           # Python dependencies
├── .gitignore                 # Git ignore file
├── README.md                  # This file
├── modules/                   # Helper modules
│   ├── apple_find_my.py
│   ├── exif_gps_extractor.py
│   ├── device_status_checker.py
│   ├── imei_blocking_portals.py
│   ├── alert_system.py
│   ├── timeline_importer.py
│   ├── sim_change_detector.py
│   ├── remote_command_executor.py
│   ├── cloud_backup_auditor.py
│   ├── emergency_alert_system.py
│   ├── recovery_logger.py
│   ├── carrier_toolkit.py
│   ├── google_intel.py
│   ├── remote_push.py
│   ├── sms_center.py
│   ├── phoenix_daemon.py
│   ├── offline_location_recovery.py
│   ├── marketplace_alert_watcher.py
│   ├── marketplace_watcher.py
│   ├── investigation_launcher.py
│   ├── law_enforcement_tower_tracker.py
│   └── hard_ip_tracker.py
├── output/                    # Generated reports (gitignored)
└── tracker-go/                # Go IP tracker (optional)
    ├── main.go
    └── go.mod
```

---

## ⚠️ Disclaimer

This tool is for **legitimate recovery of your own lost/stolen device** only.

- Do not use on devices you do not own
- Follow local laws and regulations
- This tool does not bypass carrier security or hack any system
- All carrier/legal requests must go through proper channels
- The tool cannot magically locate a phone without data from carrier/Google/Apple

---

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repo
2. Create a feature branch
3. Test your changes
4. Submit a pull request

---

## 📜 License

MIT License - Use responsibly and legally.

---

## 🙏 Support

If this tool helped you recover your device:
- Star the repo
- Share with others who lost devices
- File a proper FIR with all evidence

---

**Built for victims of phone theft. Stay safe.**
