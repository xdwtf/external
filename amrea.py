import re
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from ub_core import BOT, bot, Message

# New tag and username to replace the old tag and username
new_tag = "isthisdeal-21"
new_username = "@ThisDeal"

# Regular expression to find the tag parameter in the URL
pattern_tag = r"(tag=)[^&]*"  # This will match 'tag=' and any characters following it
pattern_username = r"@SmartDealsOfindia"

# Target chat IDs
TARGET_CHAT_ID = [-1001267968308, -1001628270160, -1001678712638]
THIS_DEAL_ID = -1002108741045

@bot.on_message(filters.chat(TARGET_CHAT_ID), group=4)  # Listening to messages from the specified channels
async def url_replacement_handler(bot: BOT, message: Message):
    text_to_check = None
    is_modified = False  # Flag to track if any modification is made

    # If the message has a photo and a caption, check the caption
    if message.photo and message.caption:
        text_to_check = message.caption
    # If the message is a text message
    elif message.text:
        text_to_check = message.text

    # Check if the message contains URLs with the tag and proceed to replace
    if text_to_check:
        modified_caption = text_to_check

        # Replace the old tag with the new tag in the caption (if necessary)
        modified_caption = re.sub(pattern_tag, f"tag={new_tag}", modified_caption)
        if modified_caption != text_to_check:
            is_modified = True  # A modification has been made

        # Replace the old username with the new username in the caption (if necessary)
        modified_caption = re.sub(pattern_username, new_username, modified_caption)
        if modified_caption != text_to_check:
            is_modified = True  # A modification has been made

        # Modify the URLs inside text link entities, replacing only the tag in any URL
        if message.caption_entities:
            for entity in message.caption_entities:
                if entity.type == "text_link" and 'url' in entity:
                    original_url = entity.url
                    # Modify the URL to replace the old tag with the new tag
                    modified_url = re.sub(pattern_tag, f"tag={new_tag}", original_url)
                    if modified_url != original_url:
                        is_modified = True  # A modification has been made
                    # Update the caption with the new URL
                    modified_caption = modified_caption.replace(original_url, modified_url)

        # Modify the button URLs and text (if the message contains reply_markup)
        if message.reply_markup:
            for row in message.reply_markup.inline_keyboard:
                for button in row:
                    if button.url:
                        # Modify the URL to replace the old tag with the new tag
                        modified_url = re.sub(pattern_tag, f"tag={new_tag}", button.url)
                        if modified_url != button.url:
                            button.url = modified_url
                            is_modified = True  # A modification has been made
                    if button.text:
                        # Replace the old username with the new username in the button text
                        modified_text = button.text.replace("@SmartDealsOfindia", "@thisdeal")
                        if modified_text != button.text:
                            button.text = modified_text
                            is_modified = True  # A modification has been made

        # Send the modified message to the target chat only if it was modified
        if is_modified:
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
    else:
        # If the message doesn't contain any URLs, simply do nothing (ignore)
        pass
