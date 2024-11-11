import re
from ub_core import BOT, bot, Message
from pyrogram import filters

# New tag to replace the old tag
new_tag = "isthisdeal-21"

# Regular expression to find the tag parameter in the URL
pattern = r"(tag=)[^&]*"

# Target chat IDs as a list
TARGET_CHAT_ID = [-1001267968308, -1001628270160]
THIS_DEAL_ID = -1002108741045

@bot.on_message(filters.chat(TARGET_CHAT_ID), group=4)  # Listen to messages in group with ID 4
async def url_replacement_handler(bot: BOT, message: Message):
    # Check if the message has a photo and a caption
    if message.photo and message.caption:
        text_to_check = message.caption
    # Check if the message is text
    elif message.text:
        text_to_check = message.text
    else:
        text_to_check = None

    if text_to_check:
        # Replace the old tag with the new tag in all URLs within the text
        modified_message = re.sub(pattern, f"tag={new_tag}", text_to_check)

        # Send the modified message as text or photo with new caption to the target chat
        if message.photo and message.caption:
            await bot.send_photo(
                chat_id=THIS_DEAL_ID,
                photo=message.photo.file_id,  # Use the existing photo file ID
                caption=modified_message,  # Send modified caption
                disable_web_page_preview=True
            )
        else:
            await bot.send_message(
                chat_id=THIS_DEAL_ID,
                text=modified_message,
                disable_web_page_preview=True
            )
