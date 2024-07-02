#bot.py
import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('Test')
CHANNEL_ID= int(os.getenv('DISCORD_GENERAL'))
VOICE_CHANNEL_ID = int(os.getenv('DISCORD_VOICE_GENERAL'))

intents = discord.Intents.all()
intents.members=True

bot = commands.Bot(command_prefix='!', intents=intents)
@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

    for guild in bot.guilds:
        if guild.name == GUILD:
            break

    print(
        f'{bot.user} is connected to the following guild:\n'
        f'{guild.name} (id: {guild.id})\n'
    )

    members = '\n - '.join([member.name for member in guild.members])
    print(f'Guild Members:\n - {members}')

@bot.command(name='join', help='Tells the bot to join the voice channel')
async def join(ctx):
    voice_channel = bot.get_channel(VOICE_CHANNEL_ID)
    if isinstance(voice_channel, discord.VoiceChannel):
        await voice_channel.connect()

@bot.command(name='leave', help='Tells the bot to leave the voice channel')
async def leave(ctx):
    voice_client = ctx.guild.voice_client
    if voice_client and voice_client.is_connected():
        await voice_client.disconnect()

@bot.command(name='message', help='Tells the bot to send a message to the specified channel')
async def message(ctx):
    channel = bot.get_channel(CHANNEL_ID)
    if channel:
        await channel.send('Hello, this is a message from the bot!')

bot.run(TOKEN)