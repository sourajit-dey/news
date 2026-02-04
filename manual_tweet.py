import asyncio
import os
from twikit import Client

async def main():
    print("Authenticating with Twitter...")
    client = Client(language='en-US')
    
    # These will be passed via command line
    auth_token = os.environ.get("TWITTER_AUTH_TOKEN")
    ct0 = os.environ.get("TWITTER_CT0")
    guest_id = os.environ.get("TWITTER_GUEST_ID")

    if not auth_token:
        print("Error: No secrets found in environment.")
        return

    try:
        cookies_dict = {
            "auth_token": auth_token,
            "ct0": ct0,
            "guest_id": guest_id
        }
        client.set_cookies(cookies_dict)
        print("Login Success!")
        
        text = "🤖 Truth Engine System Check: Twitter module is fully operational. #TruthEngineIndia"
        print(f"Posting tweet: {text}")
        
        await client.create_tweet(text=text)
        print("✅ SUCCESS: Tweet posted successfully!")
        
    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    asyncio.run(main())
