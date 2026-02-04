import asyncio
import os
import datetime
from twikit import Client

async def main():
    print("--- ADVANCED TWITTER DEBUG ---")
    client = Client(
        language='en-US',
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
    
    auth_token = os.environ.get("TWITTER_AUTH_TOKEN")
    ct0 = os.environ.get("TWITTER_CT0")
    guest_id = os.environ.get("TWITTER_GUEST_ID")

    if not auth_token:
        print("❌ Error: No secrets found in environment.")
        return

    try:
        print("1. Logging in...")
        cookies_dict = {
            "auth_token": auth_token,
            "ct0": ct0,
            "guest_id": guest_id
        }
        client.set_cookies(cookies_dict)
        print("   Login request sent.")

        print("2. Verifying User Identity...")
        # Try to get own user info. Note: Twikit might not have a direct 'me' without looking up user ID.
        # But commonly we check if we can get user state.
        user = await client.user()
        print(f"   ✅ Logged in as: @{user.screen_name} ({user.name})")
        print(f"   Favorites Count: {user.favourites_count}")
        
        print("3. Attempting to Tweet...")
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        text = f"Truth Engine Test Verify {timestamp} 🤖"
        
        tweet = await client.create_tweet(text=text)
        
        print(f"   ✅ Tweet Sent Object: {tweet}")
        # Twikit often returns the tweet object which has an ID
        if hasattr(tweet, 'id'):
            print(f"   🔗 Tweet ID: {tweet.id}")
            print(f"   🔗 Direct Link: https://x.com/{user.screen_name}/status/{tweet.id}")
        else:
            print("   ⚠️ Tweet sent but no ID returned (Check profile manually).")
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
