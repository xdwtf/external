import re
from app import BOT, bot, Message
from pyrogram import filters

# New tag to replace the old tag
new_tag = "isthisdeal-21"

# Regular expression to find the tag parameter in the URL
pattern = r"(tag=)[^&]*"

# Target chat ID where the modified message will be sent
TARGET_CHAT_ID = "-1001258664792"  # Replace with your target chat ID
THIS_DEAL_ID = "-1002108741045"

@bot.on_message(filters.chat(TARGET_CHAT_ID)  & filters.chat(4))  # Listen to messages in group with ID 4
async def url_replacement_handler(bot: BOT, message: Message):
    if message.text:
        # Regular expression to match URLs in the message
        url_pattern = r'(https?://[^\s]+)'
        modified_message = message.text

        # Search for URLs in the message text
        urls = re.findall(url_pattern, message.text)
        if urls:
            for url in urls:
                # Replace the old tag with the new tag in the URL
                modified_url = re.sub(pattern, f"tag={new_tag}", url)
                # Replace the original URL in the message with the modified URL
                modified_message = modified_message.replace(url, modified_url)

            # Send the modified message to the target chat
            await bot.send_message(chat_id=THIS_DEAL_ID, text=modified_message)
