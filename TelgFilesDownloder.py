# pip install telethon cryptg
'''
# =========================================================
# Developer Reference
# =========================================================
# This script uses the Telegram official API via Telethon.
#
# Required Credentials:
# ---------------------
# api_id and api_hash are required to authenticate a user
# session with Telegram.
#
# How to get api_id & api_hash:
# -----------------------------
# 1. Open https://my.telegram.org
# 2. Login using your Telegram phone number
# 3. Go to "API development tools"
# 4. Create a new application (one-time):
#    - App title  : any name
#    - Short name : lowercase + numbers only
#    - Platform   : Desktop
# 5. Copy the generated:
#    - api_id
#    - api_hash
#
# Features Used in This Script:
# -----------------------------
# - Telethon user session (not a bot)
# - Public channel access
# - Message ID–based file fetching
# - Document media download (PDF, EPUB, ZIP, etc.)
# - Progress callback for download status
# - Fault-tolerant looping (skips missing IDs)
#
# Notes for Other Developers:
# ---------------------------
# - Works only for PUBLIC Telegram channels
# - First run requires OTP login (saved as session file)
# - Do not hardcode credentials in shared repositories
# - Respect Telegram ToS and rate limits
# =========================================================
'''

import os
import asyncio
import sys
from telethon import TelegramClient
from telethon.tl.types import MessageMediaDocument
# ---------------- CONFIG ----------------
api_id = 12345678          # <-- your api_id
api_hash = "b7fbc**********************bea1"      # <-- your api_hash

channel_username = input("Enter the channel username (without @): ")
start_id = int(input("Enter the starting message ID: "))
end_id = int(input("Enter the ending message ID: "))
download_folder = "downloads"
# ---------------------------------------
os.makedirs(download_folder, exist_ok=True)

# -------- Progress callback --------
def progress_callback(current, total):
    if total:
        percent = current * 100 / total
        bar_len = 20
        filled = int(bar_len * percent / 100)
        bar = "█" * filled + "-" * (bar_len - filled)

        sys.stdout.write(
            f"\r⬇️ [{bar}] {percent:5.1f}% "
            f"({current/1024/1024:.2f} MB / {total/1024/1024:.2f} MB)"
        )
        sys.stdout.flush()


async def main():
    async with TelegramClient("session", api_id, api_hash) as client:
        for msg_id in range(start_id, end_id + 1):

            try:
                message = await client.get_messages(channel_username, ids=msg_id)

                if not message:
                    print(f"\n⚠️ Message {msg_id} not found — skipping")
                    continue

                if not message.media:
                    print(f"\n⚠️ Message {msg_id} has no file — skipping")
                    continue

                if isinstance(message.media, MessageMediaDocument):
                    file_name = message.file.name or "unknown_file"
                    print(f"\n📥 Message {msg_id}: {file_name}")

                    await client.download_media(
                        message.media,
                        file=download_folder,
                        progress_callback=progress_callback
                    )

                    print("\n✅ Download completed")

                else:
                    print(f"\n⚠️ Message {msg_id} media is not a document — skipping")

            except Exception as e:
                print(f"\n❌ Error on message {msg_id}: {e}")
                continue

    print("\n🎉 Finished all downloads")

if __name__ == "__main__":
    asyncio.run(main())
