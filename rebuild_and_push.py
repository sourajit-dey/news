from jinja2 import Environment, FileSystemLoader
from datetime import datetime
import json
import subprocess

# Rebuild website
print("Rebuilding website...")
env = Environment(loader=FileSystemLoader("templates"))
template = env.get_template("index.html")

with open("db.json", "r") as f:
    news_list = json.load(f)

html_output = template.render(
    news_list=news_list,
    last_updated=datetime.now().strftime("%Y-%m-%d %H:%M:%S IST"),
    github_repo="sourajit-dey/news"
)

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_output)
    
print("Pushing to GitHub...")
subprocess.run(["git", "add", "."], check=False)
subprocess.run(["git", "commit", "-m", "Fix: Update images with Wikimedia URLs"], check=False)
subprocess.run(["git", "push"], check=False)
print("Done!")
