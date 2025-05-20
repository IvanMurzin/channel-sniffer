import os
import traceback
import re

from telethon import TelegramClient, events, functions
from telethon.tl.types import PeerChannel, PeerUser
from dotenv import load_dotenv

load_dotenv()

api_id = int(os.getenv('API_ID'))
api_hash = os.getenv('API_HASH')
phone_number = os.getenv('PHONE_NUMBER')
target_channel_id = os.getenv('TARGET_CHANNEL_ID')
peer_channel_id = int(os.getenv('PEER_CHANNEL_ID'))
max_message_length = int(os.getenv('MAX_MESSAGE_LENGTH'))

peer_channel = PeerChannel(peer_channel_id)

client = TelegramClient('my_session', api_id, api_hash)

@client.on(events.NewMessage())
async def handler(event):
    if event is None or event.message is None or event.message.chat is None or event.message.chat.id is None:
        return
    event_id = event.message.chat.id
    if event_id == peer_channel.channel_id:
        return
    if event_id == target_channel_id:
        message_text = event.message.text
        if not message_text:
            return
            
        # Check message length
        if len(message_text) > max_message_length:
            return
            
        # Check for currency patterns
        currency_patterns = [
            r'\d+\s*[$₽€£]',  # Matches numbers followed by currency symbols
            r'[$₽€£]\s*\d+'   # Matches currency symbols followed by numbers
        ]
        if any(re.search(pattern, message_text) for pattern in currency_patterns):
            return
            
        await client.forward_messages(peer_channel, event.message)
        await client(functions.messages.MarkDialogUnreadRequest(
            peer=peer_channel,
            unread=True
        ))


async def main():
    try: 
        await client.start(phone_number)
        try:
            chat_entity = await client.get_entity(PeerChannel(target_channel_id))
            print(f"Listen for channel: {chat_entity.title}")
        except Exception as e:
            error_message = f"Failed to get chat name for ID {target_channel_id}: {e}"
            print(error_message)
        await client.run_until_disconnected()
    except Exception as e:
        error_message = f"Main function error: {e}\n{traceback.format_exc()}"
        print(error_message)


client.loop.run_until_complete(main())
