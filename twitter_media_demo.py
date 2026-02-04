import asyncio
import os
from twikit import Client
import requests

async def main():
    print("=== TRUTH ENGINE TWITTER MEDIA DEMO ===\n")
    
    # Setup
    client = Client(
        language='en-US',
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
    
    auth_token = os.environ.get("TWITTER_AUTH_TOKEN")
    ct0 = os.environ.get("TWITTER_CT0")
    guest_id = os.environ.get("TWITTER_GUEST_ID")

    if not auth_token:
        print("❌ Error: Twitter credentials not found in environment.")
        return

    # Login
    print("1. Authenticating...")
    cookies_dict = {
        "auth_token": auth_token,
        "ct0": ct0,
        "guest_id": guest_id
    }
    client.set_cookies(cookies_dict)
    print("   ✅ Logged in!\n")

    # Download demo image
    print("2. Downloading demo image...")
    image_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c5/Supreme_Court_of_India_-_01.jpg/800px-Supreme_Court_of_India_-_01.jpg"
    img_data = requests.get(image_url).content
    with open("demo_img.jpg", "wb") as f:
        f.write(img_data)
    print("   ✅ Image saved!\n")

    # Upload media
    print("3. Uploading image to Twitter...")
    with open("demo_img.jpg", "rb") as f:
        media_data = f.read()
    media_id = await client.upload_media(media_data, media_type="image/jpeg", media_category="tweet_image")
    print(f"   ✅ Media uploaded! ID: {media_id}\n")

    # Compose tweet
    text = """🚨 FAKE NEWS ALERT

❌ CLAIM: Supreme Court has cancelled NEET-PG 2025

👉 TRUTH: FALSE. Only a notice was issued on a plea. No stay order or cancellation. Exam proceeding as planned.

🔗 Full Story: https://sourajit-dey.github.io/news

#TruthEngine #FactCheck"""

    print("4. Posting tweet with image...")
    tweet = await client.create_tweet(text=text, media_ids=[media_id])
    print(f"   ✅ Tweet posted!\n")
    
    # Cleanup
    os.remove("demo_img.jpg")
    
    print("🎉 SUCCESS! Check your Twitter profile.")

if __name__ == "__main__":
    asyncio.run(main())
