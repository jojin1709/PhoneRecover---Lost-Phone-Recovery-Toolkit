#!/usr/bin/env python3
"""
Offline Location Recovery - Last-known location plan when phone is switched off.
"""


def recover(imei="", carrier="", email="", phone=""):
    imei = imei or input("IMEI: ").strip()
    carrier = carrier or input("Carrier: ").strip() or "jio"
    email = email or input("Email: ").strip()
    phone = phone or input("Phone: ").strip()
    
    print("OFFLINE LOCATION RECOVERY")
    print("=" * 60)
    print(f"IMEI    : {imei}")
    print(f"Carrier : {carrier}")
    print(f"Email   : {email}")
    print(f"Phone   : {phone}")
    print()
    print("This phone appears to be switched off.")
    print("Here is the recovery plan:")
    print()
    print("1. GOOGLE FIND MY DEVICE:")
    print("   - Open: https://www.google.com/android/find")
    print("   - Check for cached last-known location")
    print("   - Note the timestamp")
    print()
    print("2. APPLE FIND MY (if applicable):")
    print("   - Open: https://www.icloud.com/find")
    print("   - Check for offline device location cache")
    print()
    print("3. CARRIER REQUEST:")
    print("   - Last tower LAC + Cell ID")
    print("   - Last network activity timestamp")
    print("   - Any data session logs")
    print()
    print("4. CHECK GOOGLE PHOTOS/TIMELINE:")
    print("   - Auto-uploaded photos may show location")
    print("   - Google Maps Timeline may have cached locations")
    print()
    print("5. PHYSICAL SEARCH:")
    print("   - Go to last known location")
    print("   - Check CCTV in the area")
    print("   - Ask locals if they have seen the device")
    print()
    print('NOTE: When phone is switched on, Find My Device will show location immediately.')


if __name__ == "__main__":
    recover()
