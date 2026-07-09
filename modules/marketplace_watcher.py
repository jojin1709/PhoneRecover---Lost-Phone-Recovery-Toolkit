#!/usr/bin/env python3
"""
Marketplace Watcher - Open OLX / Facebook / Quikr to manually inspect listings.
"""

import webbrowser


def monitor_marketplace(model: str = "", city: str = ""):
    print("MARKETPLACE WATCHER")
    print("=" * 60)
    model = model or input("Phone model to search: ").strip()
    city = city or input("City (optional): ").strip() or "India"
    
    query = model.replace(" ", "%20")
    
    urls = {
        "OLX": f"https://www.olx.in/items/q-{query}",
        "Facebook Marketplace": f"https://www.facebook.com/marketplace/search/?query={query}",
        "Quikr": f"https://www.quikr.com/mobiles/buy-sell?query={query}",
        "Cashify": f"https://www.cashify.in/search?q={query}",
    }
    
    print(f"\nSearching for: {model} in {city}")
    print("Links to check:")
    for site, url in urls.items():
        print(f"  [{site}]: {url}")
    
    choice = input("\nOpen all links? (y/n): ").strip().lower()
    if choice == "y":
        for url in urls.values():
            webbrowser.open(url)
    
    print("[OK] Marketplace watcher completed.")


if __name__ == "__main__":
    monitor_marketplace()
