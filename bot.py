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
import requests
import xml.etree.ElementTree as ET

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
    model_name="models/gemini-1.5-flash",
    generation_config=generation_config,
    system_instruction="""You are a strict fact-checker for Indian news. Analyze if a trend is 'Fake News', 'Misleading', or 'Verified'. 
    Return a JSON object with keys: 
    - 'verdict' (Fake News/Misleading/Verified)
    - 'rumor' (What is the viral claim? Keep it short & punchy. If Verified, state the news header.)
    - 'reality' (What is the actual truth? Explain clearly. Debunk if fake.)
    - 'analysis' (A detailed 3-sentence context for the website.)
    - 'source' (Main source name)"""
)

# Setup Paths
DB_FILE = "db.json"
TEMPLATE_DIR = "templates"
OUTPUT_FILE = "index.html"

def get_viral_trends():
    print("Fetching Google News RSS (India)...")
    try:
        url = "https://news.google.com/rss?hl=en-IN&gl=IN&ceid=IN:en"
        response = requests.get(url, timeout=15)
        root = ET.fromstring(response.content)
        trends = []
        for item in root.findall('./channel/item')[:5]:
            title = item.find('title').text
            if ' - ' in title:
                title = title.rsplit(' - ', 1)[0]
            trends.append(title)
        return trends
    except Exception as e:
        print(f"Error fetching RSS: {e}")
        return []

def get_image_url(query):
    print(f"Fetching image for: {query}")
    try:
        results = DDGS().images(f"{query} news india", max_results=1)
        if results:
            return results[0]['image']
    except Exception as e:
        print(f"Image search failed: {e}")
    return "https://via.placeholder.com/800x400?text=Truth+Engine+India" # Fallback

def verify_trend(trend):
    print(f"Verifying trend: {trend}")
    
    # 1. Search Context
    context = ""
    try:
        results = DDGS().text(f"{trend} news india", max_results=5)
        if results:
            context = "\n".join([f"- {r['title']}: {r['body']}" for r in results])
        else:
            context = "Search returned no results. Verify based on internal knowledge if possible."
    except Exception as e:
        print(f"Search failed: {e}")
        context = "Search unavailable. Verify based on internal knowledge."

    # 2. Gemini Analysis
    prompt = f"Trend: {trend}\n\nSearch Results:\n{context}"
    
    retries = 3
    for attempt in range(retries):
        try:
            response = model.generate_content(prompt)
            text = response.text
            # Clean markdown
            if text.startswith("```json"): text = text[7:]
            if text.startswith("```"): text = text[3:]
            if text.endswith("```"): text = text[:-3]
            
            data = json.loads(text.strip())
            
            # Fetch Image ONLY if we have a verdict
            data['image_url'] = get_image_url(trend)
            return data
            
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
        with open(DB_FILE, 'w') as f: json.dump([], f)
    
    with open(DB_FILE, 'r') as f: data = json.load(f)
    
    if any(d['trend'] == trend for d in data): return False 

    new_entry = {
        "trend": trend,
        "verdict": analysis['verdict'],
        "rumor": analysis['rumor'],
        "reality": analysis['reality'],
        "analysis": analysis['analysis'],
        "source": analysis['source'],
        "image_url": analysis.get('image_url', ''),
        "timestamp": datetime.now().isoformat()
    }
    
    data.insert(0, new_entry)
    data = data[:50]
    
    with open(DB_FILE, 'w') as f: json.dump(data, f, indent=4)
    return new_entry

def generate_website():
    print("Generating website...")
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    template = env.get_template("index.html")
    
    with open(DB_FILE, 'r') as f: news_list = json.load(f)
        
    html_output = template.render(
        news_list=news_list,
        last_updated=datetime.now().strftime("%Y-%m-%d %H:%M:%S IST"),
        github_repo=GITHUB_REPO
    )
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f: f.write(html_output)

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
        client = Client(
            language='en-US',
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        
        cookies_dict = {
            "auth_token": TWITTER_AUTH_TOKEN,
            "ct0": TWITTER_CT0,
            "guest_id": TWITTER_GUEST_ID
        }
        client.set_cookies(cookies_dict)
        
        # Determine Emoji & Text
        if "Fake" in entry['verdict']:
            header = "� FAKE NEWS ALERT"
            emoji = "❌"
        elif "Misleading" in entry['verdict']:
            header = "⚠️ MISLEADING CLAIM"
            emoji = "⚠️"
        else:
            # We usually don't verify 'Verified' news unless viral, or user wants all.
            # Assuming we tweet all.
            header = "✅ VERIFIED NEWS"
            emoji = "🟢"

        text = f"{header}\n\n{emoji} CLAIM: {entry['rumor']}\n\n👉 TRUTH: {entry['reality']}\n\n🔗 Full Story & Proof: https://{GITHUB_REPO.split('/')[0]}.github.io/{GITHUB_REPO.split('/')[1]}"

        # Handle Image
        media_ids = []
        if entry.get('image_url') and "placeholder" not in entry['image_url']:
            try:
                # Download image to temp
                img_data = requests.get(entry['image_url']).content
                with open("temp_img.jpg", "wb") as f:
                    f.write(img_data)
                
                # Upload to Twitter
                media_id = await client.upload_media("temp_img.jpg")
                media_ids.append(media_id)
                os.remove("temp_img.jpg")
            except Exception as e:
                print(f"Image upload failed: {e}")

        await client.create_tweet(text=text, media_ids=media_ids if media_ids else None)
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
                # Tweet everything (or filter if desired, currently tweeting all new items)
                await tweet_alert(new_entry)
            else:
                print("Trend already in database.")
        
        print("Sleeping 10s between trends...")
        time.sleep(10)
    
    generate_website()
    publish_changes()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
