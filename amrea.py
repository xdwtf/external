import re
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from ub_core import BOT, bot, Message

# New tag and username to replace the old tag and username
new_tag = "isthisdeal-21"
new_username = "@ThisDeal"

# Regular expression to find the tag parameter in the URL
pattern_tag = r"(tag=)[^&]*"
pattern_username = r"@SmartDealsOfindia"

# Target chat IDs
TARGET_CHAT_ID = [-1001267968308, -1001628270160]
THIS_DEAL_ID = -1002108741045

@bot.on_message(filters.chat(TARGET_CHAT_ID), group=4)  # Listening to messages from the specified channels
async def url_replacement_handler(bot: BOT, message: Message):
    text_to_check = None

    # If the message has a photo and a caption, check the caption
    if message.photo and message.caption:
        text_to_check = message.caption
    # If the message is a text message
    elif message.text:
        text_to_check = message.text
    
    if text_to_check:
        # Replace the old tag with the new tag in the caption
        modified_caption = re.sub(pattern_tag, f"tag={new_tag}", text_to_check)
        # Replace the old username with the new username in the caption
        modified_caption = re.sub(pattern_username, new_username, modified_caption)
        
        # Modify the button URLs and text (if the message contains reply_markup)
        if message.reply_markup:
            for row in message.reply_markup.inline_keyboard:
                for button in row:
                    if button.url:
                        # Replace the old tag in the button URL
                        button.url = re.sub(pattern_tag, f"tag={new_tag}", button.url)
                    if button.text:
                        # Replace the old username with the new username in the button text
                        button.text = button.text.replace("@SmartDealsOfindia", "@thisdeal")
        
        # Send the modified message to the target chat
        if message.photo:
            # Send photo with modified caption and reply markup if available
            if message.reply_markup:
                await bot.send_photo(
                    chat_id=THIS_DEAL_ID,
                    photo=message.photo.file_id,
                    caption=modified_caption,  # Send modified caption
                    reply_markup=message.reply_markup
                )
            else:
                await bot.send_photo(
                    chat_id=THIS_DEAL_ID,
                    photo=message.photo.file_id,
                    caption=modified_caption
                )
        else:
            # Send text message with modified caption and reply markup if available
            if message.reply_markup:
                await bot.send_message(
                    chat_id=THIS_DEAL_ID,
                    text=modified_caption,
                    reply_markup=message.reply_markup,  # Send modified inline keyboard
                    disable_web_page_preview=True
                )
            else:
                await bot.send_message(
                    chat_id=THIS_DEAL_ID,
                    text=modified_caption,
                    disable_web_page_preview=True
                )
