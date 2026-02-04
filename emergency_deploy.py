from jinja2 import Environment, FileSystemLoader
from datetime import datetime
import json
import subprocess
import time

print("=== FORCE CLEAN DEPLOYMENT ===\n")

# 1. Rebuild with timestamp
print("1. Rebuilding website with cache-buster...")
env = Environment(loader=FileSystemLoader("templates"))
template = env.get_template("index.html")

with open("db.json", "r") as f:
    news_list = json.load(f)

# Add cache buster
cache_buster = int(time.time())
html_output = template.render(
    news_list=news_list,
    last_updated=datetime.now().strftime("%Y-%m-%d %H:%M:%S IST"),
    github_repo="sourajit-dey/news"
)

# Add cache control meta tag
html_output = html_output.replace(
    '<meta name="viewport"',
    f'<meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">\n    <meta http-equiv="Pragma" content="no-cache">\n    <meta http-equiv="Expires" content="0">\n    <meta name="viewport"'
)

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_output)
print("   ✅ Site rebuilt\n")

# 2. Force push
print("2. Force pushing to GitHub...")
subprocess.run(["git", "add", "-A"], check=False)
subprocess.run(["git", "commit", "-m", f"Force deployment - {cache_buster}"], check=False)
subprocess.run(["git", "push", "--force"], check=False)

print("\n✅ DONE! Wait 30 seconds, then hard refresh (Ctrl+Shift+R)")
