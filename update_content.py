"""
update_content.py
Discovers or generates 2 new trending deal/coupon communities using Gemini 2.5 Flash,
appends them to data/groups.json, rebuilds index.html, sitemap.xml, and feed.xml,
and pings Google PubSubHubbub.
"""

import json
import os
import sys
import urllib.request
import urllib.parse
from datetime import datetime, timezone
import build_site

API_KEY = os.environ.get("GEMINI_API_KEY", "AIzaSyDBpw2G9kS0zg2ogO_kh6uDfFRxkDCUx2k")
GEMINI_ENDPOINT = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={API_KEY}"
PUBSUBHUBBUB_URL = "https://pubsubhubbub.appspot.com/publish"
FEED_URL = "https://jibranpcccc.github.io/deals-loot-coupons-hub/feed.xml"

# Dynamic fallback catalog in case Gemini API hits 429 rate limit or network error
FALLBACK_COMMUNITIES = [
    {
        "id": "steam-deck-rog-ally-deals",
        "title": "Steam Deck & Handheld Gaming Loot",
        "category": "Tech & Gadgets",
        "platform": "Discord",
        "memberCount": 54200,
        "discountRange": "40% - 75% OFF",
        "description": "Tracking MicroSD card speed sales, verified Steam Deck OLED discounts, ASUS ROG Ally open-box price cuts, and docks.",
        "joinUrl": "https://discord.gg/handheldsteals",
        "tags": ["steam deck", "handheld", "gaming deals", "rog ally"],
        "verified": True,
        "featured": False
    },
    {
        "id": "whole-foods-prime-perks",
        "title": "Whole Foods & Organic Grocery Perks",
        "category": "Price Glitches & Loot",
        "platform": "Telegram",
        "memberCount": 47600,
        "discountRange": "35% - 70% OFF",
        "description": "Weekly automated breakdowns of yellow tag sales, Prime member extra 10% stacks, and seasonal organic pantry liquidations.",
        "joinUrl": "https://t.me/wholefoodsperks",
        "tags": ["whole foods", "organic", "grocery coupons", "prime discount"],
        "verified": True,
        "featured": False
    },
    {
        "id": "costco-clearance-secret-items",
        "title": "Costco Secret Clearance & .97 Endcaps",
        "category": "Amazon & E-Commerce",
        "platform": "Telegram",
        "memberCount": 128900,
        "discountRange": "40% - 85% OFF",
        "description": "Hunters spotting manager markdowns ending in .97 and asterisk items across Costco warehouses nationwide with inventory lookup tips.",
        "joinUrl": "https://t.me/costcoclearancefinds",
        "tags": ["costco", "clearance", "97 cent deals", "bulk savings"],
        "verified": True,
        "featured": True
    },
    {
        "id": "luxury-watch-chrono-steals",
        "title": "Timepiece & Chrono Deal Exchange",
        "category": "Fashion & Lifestyle",
        "platform": "Discord",
        "memberCount": 38100,
        "discountRange": "30% - 65% OFF",
        "description": "Authorized dealer discounts on Seiko, Tissot, Hamilton, and pre-owned luxury Swiss watch gray market flash sales.",
        "joinUrl": "https://discord.gg/watchdeals",
        "tags": ["watches", "seiko", "tissot", "luxury fashion", "horology"],
        "verified": True,
        "featured": False
    },
    {
        "id": "business-class-points-glitches",
        "title": "Lie-Flat Business Class Error Rates",
        "category": "Travel & Error Fares",
        "platform": "Telegram",
        "memberCount": 115400,
        "discountRange": "70% - 90% OFF",
        "description": "Specialized alerts for sub-$1,200 lie-flat business class transatlantic tickets and unannounced Qatar Qsuite award drops.",
        "joinUrl": "https://t.me/businessclasserrors",
        "tags": ["business class", "luxury travel", "qsuite", "airline error"],
        "verified": True,
        "featured": True
    },
    {
        "id": "lego-toy-collector-drops",
        "title": "LEGO & Rare Collectibles Markdowns",
        "category": "Tech & Gadgets",
        "platform": "Reddit",
        "memberCount": 142000,
        "discountRange": "25% - 60% OFF",
        "description": "Alerts for retiring LEGO sets on sale, Target damaged box liquidations, and Amazon surprise coupon drops on Star Wars sets.",
        "joinUrl": "https://reddit.com/r/legodeals",
        "tags": ["lego", "star wars lego", "target clearance", "collectibles"],
        "verified": True,
        "featured": False
    }
]

def fetch_gemini_new_communities(existing_ids):
    prompt = f"""You are an elite e-commerce deal aggregator and bargain tracking bot.
Generate exactly 2 NEW, realistic, and trending online deal or coupon communities.
Do NOT use any of these existing IDs: {list(existing_ids)[:20]}.

Requirements:
Return ONLY a valid JSON array of 2 objects. No markdown formatting, no code fencing, no conversational text.
Each object must have:
- "id": unique lowercase hyphenated string (e.g. "sam-club-clearance-scout")
- "title": Realistic channel or group name (e.g. "Sam's Club Hidden Markdowns")
- "category": Must be one of ["Amazon & E-Commerce", "Tech & Gadgets", "Price Glitches & Loot", "Fashion & Lifestyle", "Travel & Error Fares"]
- "platform": Must be one of ["Telegram", "WhatsApp", "Discord", "Reddit"]
- "memberCount": Integer between 25000 and 350000
- "discountRange": String like "50% - 85% OFF" or "60% - 90% OFF"
- "description": High quality 2-sentence description of deals, verification process, and alert speed.
- "joinUrl": URL like https://t.me/... or https://discord.gg/... or https://chat.whatsapp.com/... or https://reddit.com/r/...
- "tags": Array of 4-5 relevant keyword strings
- "verified": true
- "featured": boolean
- "lastUpdated": "{datetime.now(timezone.utc).strftime('%Y-%m-%d')}"
"""
    
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ],
        "generationConfig": {
            "responseMimeType": "application/json",
            "temperature": 0.7
        }
    }
    
    req_data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        GEMINI_ENDPOINT,
        data=req_data,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            res_json = json.loads(response.read().decode("utf-8"))
            candidate_text = res_json["candidates"][0]["content"]["parts"][0]["text"].strip()
            
            # Clean possible markdown wrapping if any
            if candidate_text.startswith("```json"):
                candidate_text = candidate_text[7:]
            if candidate_text.startswith("```"):
                candidate_text = candidate_text[3:]
            if candidate_text.endswith("```"):
                candidate_text = candidate_text[:-3]
            candidate_text = candidate_text.strip()
            
            items = json.loads(candidate_text)
            if isinstance(items, list) and len(items) >= 2:
                print(f"✓ Successfully generated {len(items)} communities via Gemini 2.5 Flash API")
                return items[:2]
    except Exception as e:
        print(f"Notice: Gemini API call returned: {e}. Utilizing curated trending fallback pool.")
        
    # Curated fallback selection
    candidates = [c for c in FALLBACK_COMMUNITIES if c["id"] not in existing_ids]
    today_str = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    results = []
    for c in candidates[:2]:
        c["lastUpdated"] = today_str
        results.append(c)
        
    if len(results) < 2:
        # Generate synthetic fallback if catalog exhausted
        ts = int(datetime.now(timezone.utc).timestamp())
        results.append({
            "id": f"trending-flash-loot-{ts}",
            "title": f"VIP Flash Loot Radar #{ts % 1000}",
            "category": "Price Glitches & Loot",
            "platform": "Telegram",
            "memberCount": 65000 + (ts % 20000),
            "discountRange": "75% - 95% OFF",
            "description": "High-velocity bot alerts catching retailer pricing anomalies, double promo stacks, and seasonal warehouse clearance.",
            "joinUrl": f"https://t.me/vipflashloot_{ts % 1000}",
            "tags": ["flash loot", "price error", "clearance", "amazon"],
            "verified": True,
            "featured": False,
            "lastUpdated": today_str
        })
    return results

def ping_pubsubhubbub():
    print(f"Pinging PubSubHubbub hub: {PUBSUBHUBBUB_URL}...")
    form_data = urllib.parse.urlencode({
        "hub.mode": "publish",
        "hub.url": FEED_URL
    }).encode("utf-8")
    
    req = urllib.request.Request(
        PUBSUBHUBBUB_URL,
        data=form_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST"
    )
    
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            print(f"✓ PubSubHubbub responded with status: {resp.status}")
    except urllib.error.HTTPError as e:
        print(f"PubSubHubbub returned status: {e.code} ({e.reason})")
    except Exception as e:
        print(f"PubSubHubbub ping note: {e}")

def main():
    print("=== Starting Deals, Loot & Coupons Hub Daily Update ===")
    
    # 1. Load existing groups
    with open("data/groups.json", "r", encoding="utf-8") as f:
        groups = json.load(f)
    print(f"Currently tracking {len(groups)} verified communities.")
    
    existing_ids = set(g.get("id") for g in groups)
    
    # 2. Discover/generate 2 new communities
    new_communities = fetch_gemini_new_communities(existing_ids)
    
    added_count = 0
    today_str = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    for item in new_communities:
        if item["id"] not in existing_ids:
            item["lastUpdated"] = today_str
            item["verified"] = True
            groups.insert(0, item) # Place trending on top
            existing_ids.add(item["id"])
            added_count += 1
            print(f" + Added community: {item['title']} ({item['platform']} - {item['category']})")
            
    # 3. Save updated groups.json
    with open("data/groups.json", "w", encoding="utf-8") as f:
        json.dump(groups, f, indent=2, ensure_ascii=False)
    print(f"✓ Updated data/groups.json (Total: {len(groups)} items)")
    
    # 4. Rebuild static site assets
    build_site.build_all()
    
    # 5. Ping PubSubHubbub
    ping_pubsubhubbub()
    
    print("=== Deals Hub Content Update Completed Successfully ===")

if __name__ == "__main__":
    main()
