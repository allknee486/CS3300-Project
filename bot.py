import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import shutil
import whisper

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_ID = int(os.getenv('DISCORD_GENERAL'))
VOICE_CHANNEL_ID = int(os.getenv('DISCORD_VOICE_GENERAL'))

intents = discord.Intents.all()
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)
bot.temp_audio_files = []

model = whisper.load_model("base")

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

@bot.command(name='join', help='Tells the bot to join the voice channel')
async def join(ctx):
    voice_channel = bot.get_channel(VOICE_CHANNEL_ID)

@bot.command(name='record', help='Tells the bot to record the voice channel')
async def record(ctx):
    if isinstance(voice_channel, discord.VoiceChannel):
        vc = await voice_channel.connect()
        vc.start_recording(discord.sinks.MP3Sink(), finished_callback, ctx)
        await ctx.send("Recording...")

async def finished_callback(sink, ctx):
    directory = os.path.join(os.getcwd(), "DiscordAudio")
    if not os.path.exists(directory):
        os.makedirs(directory)

    recorded_users = []
    files = []

    for user_id, audio in sink.audio_data.items():
        file_path = os.path.join(directory, f"{user_id}.{sink.encoding}")
        with open(file_path, "wb") as file_output:
            audio.file.seek(0)
            shutil.copyfileobj(audio.file, file_output)
        files.append(file_path)
        recorded_users.append(f"<@{user_id}>")

    bot.temp_audio_files = files
    if files:
        await ctx.send(f"Finished! Recorded audio for {', '.join(recorded_users)}.", files=[discord.File(fp) for fp in files])
    else:
        await ctx.send("No audio was recorded or no valid audio file found.")

@bot.command(name='translate_audio', help='Transcribes the audio in the specified language')
async def translate_audio(ctx, mention: str, language: str):
    user_id = int(mention.strip('<@!>'))
    audio_path = next((path for path in bot.temp_audio_files if str(user_id) in path), None)
    if audio_path:
        try:
            if os.path.getsize(audio_path) > 0:
                result = model.transcribe(audio_path, language=language)
                transcript = result.get('text', 'Transcription not available')
                await ctx.send(f"Transcription for <@{user_id}>: {transcript}")
            else:
                await ctx.send("Audio file is empty. No transcription made.")
        except Exception as e:
            await ctx.send(f"An error occurred: {str(e)}")
    else:
        await ctx.send("Audio file not found.")

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

bot.run(TOKEN)
