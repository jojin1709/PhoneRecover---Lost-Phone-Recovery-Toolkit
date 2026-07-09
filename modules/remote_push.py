#!/usr/bin/env python3
"""
Remote App Pusher - Install Android Lost / Prey / Cerberus on stolen phone
"""

import webbrowser
from datetime import datetime


def generate():
    print("REMOTE APP PUSHER")
    print("=" * 60)
    print("This helps install anti-theft apps remotely.")
    print()
    print("ANDROID:")
    print("  1. Ask carrier to enable data on the SIM")
    print("  2. Open Play Store on a friend's device")
    print("  3. Install: Android Lost / Cerberus / Prey")
    print("  4. Use the app's web dashboard to send commands")
    print()
    print("WEB LINKS:")
    print("  - Android Lost: https://androidlost.com")
    print("  - Cerberus: https://cerberusapp.com")
    print("  - Prey: https://panel.preyproject.com")
    print()
    
    choice = input("Open a link? (androidlost/cerberus/prey/n): ").strip().lower()
    if choice == "androidlost":
        webbrowser.open("https://androidlost.com")
    elif choice == "cerberus":
        webbrowser.open("https://cerberusapp.com")
    elif choice == "prey":
        webbrowser.open("https://panel.preyproject.com")
    
    print("[DONE] Remote app pusher completed.")


if __name__ == "__main__":
    generate()
