import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import shutil

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('Test')
CHANNEL_ID = int(os.getenv('DISCORD_GENERAL'))
VOICE_CHANNEL_ID = int(os.getenv('DISCORD_VOICE_GENERAL'))

intents = discord.Intents.all()
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    for guild in bot.guilds:
        if guild.name == GUILD:
            break
    print(f'{bot.user} is connected to the following guild:\n{guild.name} (id: {guild.id})')
    members = '\n - '.join([member.name for member in guild.members])
    print(f'Guild Members:\n - {members}')

@bot.command(name='join', help='Tells the bot to join the voice channel')
async def join(ctx):
    voice_channel = bot.get_channel(VOICE_CHANNEL_ID)
    if isinstance(voice_channel, discord.VoiceChannel):
        vc = await voice_channel.connect()
        vc.start_recording(discord.sinks.MP3Sink(), finished_callback, ctx)
        await ctx.send("Recording...")

async def finished_callback(sink, ctx):
    directory = r"C:\Users\aman7\Desktop\DiscordAudio"  # Change path for where u want audio file to go
    if not os.path.exists(directory):
        os.makedirs(directory)

    recorded_users = []
    files = []

    for user_id, audio in sink.audio_data.items():
        file_path = os.path.join(directory, f"{user_id}.{sink.encoding}")
        with open(file_path, "wb") as file_output:
            audio.file.seek(0)
            shutil.copyfileobj(audio.file, file_output)
        files.append(discord.File(file_path, filename=f"{user_id}.{sink.encoding}"))
        recorded_users.append(f"<@{user_id}>")

    if files:
        await ctx.channel.send(f"Finished! Recorded audio for {', '.join(recorded_users)}.", files=files)
    else:
        await ctx.channel.send("No audio was recorded or no valid audio file found.")

@bot.command(name='stop_recording', help='Stops the recording')
async def stop_recording(ctx):
    if ctx.voice_client:
        ctx.voice_client.stop_recording()
        await ctx.send("Stopped recording.")

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
