import re, os
from pyrogram import filters, types, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from ub_core import BOT, bot, Message
from amazon_paapi import AmazonApi
from urllib.parse import urlparse

# Access environment variables
AMAZON_KEY = os.getenv('AMAZON_KEY')
AMAZON_SECRET = os.getenv('AMAZON_SECRET')
AMAZON_TAG = os.getenv('AMAZON_TAG')
AMAZON_COUNTRY = os.getenv('AMAZON_COUNTRY')

# New tag and username to replace the old tag and username
new_tag = "isthisdeal-21"
new_username = "@ThisDeal"

# Regular expression to find the tag parameter in the URL
pattern_tag = r"(tag=)[^&]*"
pattern_username = r"@SmartDealsOfindia"

# Target chat IDs
TARGET_CHAT_ID = [-1001267968308, -1001628270160, -1001678712638, 5071059420]
THIS_DEAL_ID = -1002108741045

# Define Amazon URL patterns
amazon_url_patterns = [
    r'https?://(?:www\.)?amazon\.(com|in)/[^\s]+',
]

amazon = AmazonApi(AMAZON_KEY, AMAZON_SECRET, AMAZON_TAG, AMAZON_COUNTRY)

def extract_amazon_url(text):
    """
    Extract the first Amazon URL from a message text.
    """
    for pattern in amazon_url_patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(0)  # Return the matched URL
    return None

def get_asin_from_url(url):
    """
    Extract ASIN from an Amazon product URL.
    """
    try:
        # Parse the URL and extract query parameters
        parsed_url = urlparse(url)
        path_segments = parsed_url.path.split('/')
        for segment in path_segments:
            if len(segment) == 10 and segment.isalnum():
                return segment  # Likely an ASIN
        return None
    except Exception as e:
        bot.log.error(e)
        return None

def get_product_details(asin):
    """
    Retrieve detailed information about a product.
    Only returns essential information: title, prices, and savings percentage.
    """
    try:
        # Fetch the product information
        item = amazon.get_items(asin)[0]
        
        # Extract product details, using .get() to avoid KeyError if any field is missing
        title = item.item_info.title.display_value if item.item_info.title else "No title available"
        image_url = item.images.primary.large.url if item.images.primary else None
        product_url = item.detail_page_url if item.detail_page_url else "N/A"
        current_price = item.offers.listings[0].price.amount if item.offers.listings else None
        current_price_display = item.offers.listings[0].price.display_amount if item.offers.listings else "N/A"
        
        # Handle savings and percentage
        savings_amount = item.offers.listings[0].price.savings.amount if hasattr(item.offers.listings[0].price, 'savings') else 0
        savings_percentage = item.offers.listings[0].price.savings.percentage if hasattr(item.offers.listings[0].price, 'savings') else 0
        
        # Calculate original price if savings amount exists
        original_price = current_price + savings_amount if savings_amount else None

        # Extract highest and lowest price details, default to "N/A" if unavailable
        highest_price = item.offers.summaries[0].highest_price.display_amount if item.offers.summaries else "N/A"
        lowest_price = item.offers.summaries[0].lowest_price.display_amount if item.offers.summaries else "N/A"

        # Return only the relevant product details
        return {
            'title': title,
            'current_price': current_price,
            'current_price_display': current_price_display,
            'highest_price': highest_price,
            'lowest_price': lowest_price,
            'savings_percentage': savings_percentage,
            'image_url': image_url,
            'product_url': product_url,
            'original_price': original_price,
        }
    
    except Exception as e:
        bot.log.error(e)
        return None

async def send_product_details(asin, chat_id):
    """
    Sends only the essential product details (title, prices, and savings) to Telegram.
    """
    # Fetch product details from Amazon API
    product_details = get_product_details(asin)
    
    # Check if product details were successfully fetched
    if not product_details or not product_details.get('title'):
        bot.log.error("Failed to fetch product details.")
        return False  # Indicate failure

    # Format the essential details (title, current price, high price, low price, and savings)
    title = product_details.get('title', 'N/A')
    current_price = product_details.get('current_price', 'N/A')
    original_price = product_details.get('original_price', 'N/A')
    savings_percentage = product_details.get('savings_percentage', 'N/A')

    # Format the message with the required details
    message_text = f"""
**{title}**
🔥 **Current Price: ₹{current_price}**
🛒 **Original Price: ~~₹{original_price}~~ **
🎉 **You Save: {savings_percentage}%**

**Link: {product_url}**
"""

    # Check if image URL is available
    if product_details.get('image_url'):
        # Send product details with image
        await bot.send_photo(
            chat_id=chat_id,
            photo=product_details.get('image_url', ''),
            caption=message_text,
            parse_mode=enums.ParseMode.MARKDOWN
        )
    else:
        # Send product details as a normal message if no image is available
        await bot.send_message(
            chat_id=chat_id,
            text=message_text,
            parse_mode=enums.ParseMode.MARKDOWN
        )
    
    return True  # Indicate success

@bot.on_message(filters.chat(TARGET_CHAT_ID), group=4)
async def url_replacement_handler(bot: BOT, message: Message):
    text_to_check = None

    # If the message has a photo and a caption, check the caption
    if message.photo and message.caption:
        text_to_check = message.caption
    # If the message is a text message
    elif message.text:
        text_to_check = message.text

    detected_url = extract_amazon_url(text_to_check)
    asin = get_asin_from_url(detected_url) if detected_url else None
    if asin:
        success = await send_product_details(asin=asin, chat_id=THIS_DEAL_ID)
        if not success:
            await handle_no_product_info(message)
    else:
        await handle_no_product_info(message)

async def handle_no_product_info(message: Message):
    """
    Handle the case where no product info is found.
    """
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
        
        # Modify the URLs inside text link entities
        if message.caption_entities:
            for entity in message.caption_entities:
                if entity.type == "text_link" and 'url' in entity:
                    # Modify the URL inside the text link
                    modified_url = re.sub(pattern_tag, f"tag={new_tag}", entity.url)
                    modified_caption = modified_caption.replace(entity.url, modified_url)
        
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
        
        # Check if the content has been modified
        if modified_caption != text_to_check:
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
