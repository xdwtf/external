import re, os
from pyrogram import filters, enums
from pyrogram.types import ReplyParameters
from ub_core import BOT, bot, Message
from datetime import datetime, timezone, timedelta
import pymongo

P_DATABASE_URL = os.getenv('P_DATABASE_URL')
P_DATABASE_NAME = os.getenv('P_DATABASE_NAME')

class Database:
    def __init__(self, uri, database_name):
        self.client = pymongo.MongoClient(uri)
        self.db = self.client[database_name]
        self.forum_topics = self.db["forum_topics"]

    async def update_forum_topics(self, chat_id, topics):
        """
        Update or insert the list of forum topics for a specific chat_id.
        Each time the command is run, this method will update the entire list of topics for the chat_id.
        """
        topic_data = {
            "chat_id": str(chat_id),
            "topics": topics,
            "updated_at": datetime.now(timezone.utc)  # Timestamp for last update
        }
        
        result = self.forum_topics.update_one(
            {"chat_id": str(chat_id)},  # Search by chat_id
            {"$set": topic_data},  # Update the topics
            upsert=True  # Insert if chat_id doesn't exist
        )

        if result.modified_count > 0:
            bot.log.info(f"Updated topics for chat_id: {chat_id}")
        elif result.upserted_id:
            bot.log.info(f"Inserted new topics for chat_id: {chat_id}")
        else:
            bot.log.info(f"No changes made for chat_id: {chat_id}")

    async def get_forum_topics(self, chat_id):
        """Retrieve the forum topics for a specific chat_id."""
        result = self.forum_topics.find_one({"chat_id": chat_id})
        return result["topics"] if result else None

db = Database(P_DATABASE_URL, P_DATABASE_NAME)


@bot.add_cmd("get_topics")
async def z(c, m):
    if not m.input:
        return await m.reply("Please provide a chat ID.")
    
    chat_id = int(m.input)
    # Send an initial message and store its reference
    status_message = await m.reply("Fetching topics started...")

    try:
        # Fetch forum topics asynchronously
        topic_list = []
        async for topic in bot.get_forum_topics(chat_id):
            topic_list.append({
                "topic_id": topic.message_thread_id,
                "name": topic.name,
            })
        
        # Log number of topics fetched
        bot.log.info(f"Fetched {len(topic_list)} topics for chat_id: {chat_id}")

        # Save topics to the database
        bot.log.info(f"Saving topics to the database for chat_id: {chat_id}")
        await db.update_forum_topics(chat_id, topic_list)
        bot.log.info(f"Successfully updated forum topics in the database for chat_id: {chat_id}")

        # Respond with the formatted list of topics
        if topic_list:
            total_count = len(topic_list)
            response = f"Forum Topics List (Total {total_count} Topics):\n\n" + "\n".join([f"Topic ID: {topic['topic_id']} - Name: {topic['name']}" for topic in topic_list])

            # Log the response content
            bot.log.info(f"Sending response to user with {total_count} topics.")

            file_path = "Forum.txt"
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(response)
            
            # Reply to the original message with the document using reply_parameters
            await bot.send_document(
                m.chat.id,
                file_path,
                reply_parameters=ReplyParameters(message_id=status_message.id)
                )
            bot.log.info(f"Sent document with forum topics to user {m.from_user.id}.")

            # Remove the temporary file after sending
            os.remove(file_path)
            bot.log.info(f"Temporary file {file_path} removed.")

            # Update the status message to indicate completion
            await status_message.edit_text(f"✅ Done fetching topics for {m.input}\n\ntotal_count: {total_count}")
        else:
            bot.log.info(f"No topics found for chat_id: {chat_id}.")
            await status_message.edit_text("No forum topics found in this chat.")

    except Exception as e:
        bot.log.error(f"Error while processing topics for chat_id {chat_id}: {e}")
        await status_message.edit_text(f"❌ Error: {e}")
