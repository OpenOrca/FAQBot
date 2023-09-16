import os
from utils import cleaned_message, get_message_id
from event_handlers import handle_reaction, handle_on_message
import discord
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.reactions = True
intents.messages = True
intents.members = True
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

@client.event
async def on_message(message):
    if message.author.bot:
        return
    await handle_on_message(message, client)

@client.event
async def on_reaction_add(reaction, user):
    await handle_reaction('add', reaction, user, client)

@client.event
async def on_reaction_remove(reaction, user):
    await handle_reaction('remove', reaction, user, client)

client.run(TOKEN)