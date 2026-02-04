import json
from datetime import datetime
import os
import subprocess

# Manual Data with IMAGES and NARRATIVE
viral_data = [
    {
        "trend": "Supreme Court on NEET-PG",
        "verdict": "Verified",
        "rumor": "Supreme Court has cancelled NEET-PG 2025.",
        "reality": "FALSE. The Supreme Court has only issued a notice on a plea regarding the schedule. No stay order or cancellation has been granted. The exam is proceeding as planned.",
        "analysis": "The Supreme Court has issued notice on a plea regarding the NEET-PG 2025 exam schedule. No stay order has been granted yet.",
        "source": "LiveLaw",
        "image_url": "https://images.indianexpress.com/2024/07/SC-NEET-UG-2024-LIVE-UPDATES.jpg?w=640", 
        "timestamp": datetime.now().isoformat()
    },
    {
        "trend": "Digital Rupee Replacement",
        "verdict": "Fake News",
        "rumor": "Government will replace physical cash with Digital Rupee by March 31.",
        "reality": "This is completely baseless. The Digital Rupee (e₹) is a complementary digital currency, not a replacement for physical cash. Verify official RBI notifications.",
        "analysis": " viral message claiming that RBI will ban PhonePe, GPay, and Paytm from February 28 is FALSE.",
        "source": "RBI / PIB Fact Check",
        "image_url": "https://akm-img-a-in.tosshub.com/businesstoday/images/story/202212/digital-rupee-sixteen_nine.jpg",
        "timestamp": datetime.now().isoformat()
    },
    {
        "trend": "Two terrorists killed in Kashmir",
        "verdict": "Verified",
        "rumor": "Terror attack ongoing in Srinagar.",
        "reality": "Security forces successfully neutralized two terrorists in Sopore. The operation is concluded. Search operations are underway.",
        "analysis": "Security forces neutralized two terrorists in an encounter.",
        "source": "India Today",
        "image_url": "https://images.hindustantimes.com/img/2022/01/04/1600x900/JK_encounter_1641263229671_1641263230154.jpg",
        "timestamp": datetime.now().isoformat()
    }
]

DB_FILE = "db.json"
OUTPUT_FILE = "index.html"
TEMPLATE_DIR = "templates"

def main():
    # 1. Update DB
    print("Updating DB with Viral Content...")
    with open(DB_FILE, 'w') as f:
        json.dump(viral_data, f, indent=4)

    # 2. Rebuild Site
    print("Rebuilding Site with Hero Layout...")
    from jinja2 import Environment, FileSystemLoader
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    template = env.get_template("index.html")
    html_output = template.render(
        news_list=viral_data,
        last_updated=datetime.now().strftime("%Y-%m-%d %H:%M:%S IST"),
        github_repo="sourajit-dey/news"
    )
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(html_output)

    # 3. Push
    print("Pushing...")
    subprocess.run(["git", "add", "."], check=False)
    subprocess.run(["git", "commit", "-m", "Viral Upgrade: Images & Hero UI"], check=False)
    subprocess.run(["git", "push"], check=False)
    print("Done.")

if __name__ == "__main__":
    main()
