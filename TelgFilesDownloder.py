import os
import asyncio
import sys
from telethon import TelegramClient
from telethon.tl.types import MessageMediaDocument
# ---------------- CONFIG ----------------
api_id = 12345678          # <-- your api_id
api_hash = "b7fbc1****************c375bea1"      # <-- your api_hash

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
