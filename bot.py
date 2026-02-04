import os
import time
import json
import random
import pytrends
from pytrends.request import TrendReq
from duckduckgo_search import DDGS
import google.generativeai as genai
from twikit import Client
from jinja2 import Environment, FileSystemLoader
from datetime import datetime
import subprocess

# --- CONFIGURATION ---
GEMINI_API_KEY = "AIzaSyB4mjb5rUQXbt702TMydxMQRRSuGdG3_Tc" # User provided key
GITHUB_REPO = os.environ.get("GITHUB_REPOSITORY", "sourajit-dey/news") # User provided repo
TWITTER_AUTH_TOKEN = os.environ.get("TWITTER_AUTH_TOKEN")
TWITTER_CT0 = os.environ.get("TWITTER_CT0")
TWITTER_GUEST_ID = os.environ.get("TWITTER_GUEST_ID")

# Setup Gemini
genai.configure(api_key=GEMINI_API_KEY)
generation_config = {
    "temperature": 0.7,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 1024,
    "response_mime_type": "application/json",
}
model = genai.GenerativeModel(
    model_name="gemini-pro",
    generation_config=generation_config,
    system_instruction="You are a strict fact-checker for Indian news. You will receive a trend and search results. Analyze if it is 'Fake News', 'Misleading', or 'Verified'. Return a JSON object with keys: 'verdict' (Fake News/Misleading/Verified), 'summary' (short debunking explanation), 'source' (main source name)."
)

# Setup Paths
DB_FILE = "db.json"
TEMPLATE_DIR = "templates"
OUTPUT_FILE = "index.html"

import requests
import xml.etree.ElementTree as ET

# ... (Imports remain the same, just adding requests/xml if needed, but requests is in variable scope usually or needs import)
# Actually I need to make sure 'requests' is imported at top level. 
# The replace tool works on chunks. I will do this logically.

def get_viral_trends():
    print("Fetching Google News RSS (India)...")
    try:
        url = "https://news.google.com/rss?hl=en-IN&gl=IN&ceid=IN:en"
        response = requests.get(url, timeout=15)
        root = ET.fromstring(response.content)
        trends = []
        # Get top 5 items
        for item in root.findall('./channel/item')[:5]:
            title = item.find('title').text
            # Remove source suffix for cleaner search (e.g. "News Title - NDTV")
            if ' - ' in title:
                title = title.rsplit(' - ', 1)[0]
            trends.append(title)
        return trends
    except Exception as e:
        print(f"Error fetching RSS: {e}")
        return []

def verify_trend(trend):
    print(f"Verifying trend: {trend}")
    
    # 1. Search Context
    try:
        results = DDGS().text(f"{trend} news india", max_results=5)
        context = "\n".join([f"- {r['title']}: {r['body']}" for r in results])
    except Exception as e:
        print(f"Search failed: {e}")
        return None

    # 2. Gemini Analysis with Retry Logic
    prompt = f"Trend: {trend}\n\nSearch Results:\n{context}"
    
    retries = 3
    for attempt in range(retries):
        try:
            response = model.generate_content(prompt)
            # Sleep to respect rate limits (SAFETY)
            time.sleep(10) 
            return json.loads(response.text)
        except Exception as e:
            if "429" in str(e):
                print("Rate limit hit (429). Sleeping for 60s...")
                time.sleep(60)
            else:
                print(f"Gemini error: {e}")
                return None
    return None

def update_database(trend, analysis):
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, 'w') as f:
            json.dump([], f)
    
    with open(DB_FILE, 'r') as f:
        data = json.load(f)
    
    # Check if already exists
    if any(d['trend'] == trend for d in data):
        return False # Already verified

    new_entry = {
        "trend": trend,
        "verdict": analysis['verdict'],
        "analysis": analysis['summary'],
        "source": analysis['source'],
        "timestamp": datetime.now().isoformat()
    }
    
    # Add to top
    data.insert(0, new_entry)
    
    # Keep only last 50
    data = data[:50]
    
    with open(DB_FILE, 'w') as f:
        json.dump(data, f, indent=4)
    
    return new_entry

def generate_website():
    print("Generating website...")
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    template = env.get_template("index.html")
    
    with open(DB_FILE, 'r') as f:
        news_list = json.load(f)
        
    html_output = template.render(
        news_list=news_list,
        last_updated=datetime.now().strftime("%Y-%m-%d %H:%M:%S IST"),
        github_repo=GITHUB_REPO
    )
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(html_output)

def setup_git():
    subprocess.run(["git", "config", "user.name", "TruthBot"], check=False)
    subprocess.run(["git", "config", "user.email", "bot@truthengine.ai"], check=False)

def publish_changes():
    print("Publishing to GitHub...")
    subprocess.run(["git", "add", DB_FILE, OUTPUT_FILE], check=False)
    subprocess.run(["git", "commit", "-m", "Auto-update: Truth Engine Verified"], check=False)
    subprocess.run(["git", "push"], check=False)

async def tweet_alert(entry):
    print("Sending Tweet Alert...")
    try:
        client = Client(language='en-US')
        # Authenticate using cookies
        client.set_cookies(
            auth_token=TWITTER_AUTH_TOKEN,
            ct0=TWITTER_CT0,
            guest_id=TWITTER_GUEST_ID
        )
        
        emoji = "🔴" if "Fake" in entry['verdict'] else "🟢"
        text = f"{emoji} FACT CHECK: {entry['trend']}\n\nVerdict: {entry['verdict']}\n{entry['analysis']}\n\nCheck details: https://{GITHUB_REPO.split('/')[0]}.github.io/{GITHUB_REPO.split('/')[1]}"
        
        await client.create_tweet(text=text)
        print("Tweet sent successfully!")
    except Exception as e:
        print(f"Twitter error: {e}")

async def main():
    setup_git()
    trends = get_viral_trends()
    
    if not trends:
        print("No trends found. Exiting.")
        return

    changes_made = False
    
    for trend in trends:
        print(f"Processing: {trend}")
        analysis = verify_trend(trend)
        
        if analysis:
            new_entry = update_database(trend, analysis)
            if new_entry:
                changes_made = True
                # Only tweet if it's Fake News or Misleading
                if new_entry['verdict'] in ['Fake News', 'Misleading']:
                     await tweet_alert(new_entry)
            else:
                print("Trend already in database.")
        
        print("Sleeping 10s between trends...")
        time.sleep(10)
    
    # ALWAYS generate website to update "Last Updated" timestamp (Heartbeat)
    generate_website()
    publish_changes()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
