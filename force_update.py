import json
from datetime import datetime
import os
import subprocess

# Manual override data
manual_data = [
    {
        "trend": "Two terrorists killed in Kashmir",
        "verdict": "Verified",
        "analysis": "Security forces neutralized two terrorists in an encounter in Jammu and Kashmir. The operation is ongoing. Reports confirmed by official police sources.",
        "source": "India Today / NDTV",
        "timestamp": datetime.now().isoformat()
    },
    {
        "trend": "Supreme Court on NEET-PG",
        "verdict": "Verified",
        "analysis": "The Supreme Court has issued notice on a plea regarding the NEET-PG 2025 exam schedule. No stay order has been granted yet.",
        "source": "LiveLaw",
        "timestamp": datetime.now().isoformat()
    }
]

DB_FILE = "db.json"
OUTPUT_FILE = "index.html"
TEMPLATE_DIR = "templates"

# 1. Update DB
print("Updating DB...")
if os.path.exists(DB_FILE):
    with open(DB_FILE, 'r') as f:
        existing = json.load(f)
else:
    existing = []

# Prepend new data
existing = manual_data + existing
with open(DB_FILE, 'w') as f:
    json.dump(existing, f, indent=4)

# 2. Rebuild Site
print("Rebuilding Site...")
from jinja2 import Environment, FileSystemLoader
env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
template = env.get_template("index.html")
html_output = template.render(
    news_list=existing,
    last_updated=datetime.now().strftime("%Y-%m-%d %H:%M:%S IST"),
    github_repo="sourajit-dey/news"
)
with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    f.write(html_output)

# 3. Push
print("Pushing...")
subprocess.run(["git", "add", "."], check=False)
subprocess.run(["git", "commit", "-m", "Manual Content Injection"], check=False)
subprocess.run(["git", "push"], check=False)
print("Done.")
