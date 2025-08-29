import requests
import os

def send_txt_to_discord(webhook_url, filename):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            content = f.read()

        if len(content) > 2000:
            for i in range(0, len(content), 2000):
                chunk = content[i:i+2000]
                requests.post(webhook_url, json={"content": chunk})
        else:
            response = requests.post(webhook_url, json={"content": content})
            response.raise_for_status()
            print("Sent successfully!")

    except Exception as e:
        print("Error: ", e)


WEBHOOK_URL = webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
send_txt_to_discord(WEBHOOK_URL, "ko.txt")
send_txt_to_discord(WEBHOOK_URL, "tw.txt")
