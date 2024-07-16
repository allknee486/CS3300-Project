import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import shutil
import whisper
from deep_translator import GoogleTranslator
from gtts import gTTS

# Language dictionary for translate audio function
language_dic = {'afrikaans': 'af', 'albanian': 'sq', 'amharic': 'am', 'arabic': 'ar', 'armenian': 'hy', 'assamese': 'as', 'aymara': 'ay', 'azerbaijani': 'az', 'bambara': 'bm', 'basque': 'eu', 'belarusian': 'be', 'bengali': 'bn', 'bhojpuri': 'bho', 'bosnian': 'bs', 'bulgarian': 'bg', 'catalan': 'ca', 'cebuano': 'ceb', 'chichewa': 'ny', 'chinese (simplified)': 'zh-CN', 'chinese (traditional)': 'zh-TW', 'corsican': 'co', 'croatian': 'hr', 'czech': 'cs', 'danish': 'da', 'dhivehi': 'dv', 'dogri': 'doi', 'dutch': 'nl', 'english': 'en', 'esperanto': 'eo', 'estonian': 'et', 'ewe': 'ee', 'filipino': 'tl', 'finnish': 'fi', 'french': 'fr', 'frisian': 'fy', 'galician': 'gl', 'georgian': 'ka', 'german': 'de', 'greek': 'el', 'guarani': 'gn', 'gujarati': 'gu', 'haitian creole': 'ht', 'hausa': 'ha', 'hawaiian': 'haw', 'hebrew': 'iw', 'hindi': 'hi', 'hmong': 'hmn', 'hungarian': 'hu', 'icelandic': 'is', 'igbo': 'ig', 'ilocano': 'ilo', 'indonesian': 'id', 'irish': 'ga', 'italian': 'it', 'japanese': 'ja', 'javanese': 'jw', 'kannada': 'kn', 'kazakh': 'kk', 'khmer': 'km', 'kinyarwanda': 'rw', 'konkani': 'gom', 'korean': 'ko', 'krio': 'kri', 'kurdish (kurmanji)': 'ku', 'kurdish (sorani)': 'ckb', 'kyrgyz': 'ky', 'lao': 'lo', 'latin': 'la', 'latvian': 'lv', 'lingala': 'ln', 'lithuanian': 'lt', 'luganda': 'lg', 'luxembourgish': 'lb', 'macedonian': 'mk', 'maithili': 'mai', 'malagasy': 'mg', 'malay': 'ms', 'malayalam': 'ml', 'maltese': 'mt', 'maori': 'mi', 'marathi': 'mr', 'meiteilon (manipuri)': 'mni-Mtei', 'mizo': 'lus', 'mongolian': 'mn', 'myanmar': 'my', 'nepali': 'ne', 'norwegian': 'no', 'odia (oriya)': 'or', 'oromo': 'om', 'pashto': 'ps', 'persian': 'fa', 'polish': 'pl', 'portuguese': 'pt', 'punjabi': 'pa', 'quechua': 'qu', 'romanian': 'ro', 'russian': 'ru', 'samoan': 'sm', 'sanskrit': 'sa', 'scots gaelic': 'gd', 'sepedi': 'nso', 'serbian': 'sr', 'sesotho': 'st', 'shona': 'sn', 'sindhi': 'sd', 'sinhala': 'si', 'slovak': 'sk', 'slovenian': 'sl', 'somali': 'so', 'spanish': 'es', 'sundanese': 'su', 'swahili': 'sw', 'swedish': 'sv', 'tajik': 'tg', 'tamil': 'ta', 'tatar': 'tt', 'telugu': 'te', 'thai': 'th', 'tigrinya': 'ti', 'tsonga': 'ts', 'turkish': 'tr', 'turkmen': 'tk', 'twi': 'ak', 'ukrainian': 'uk', 'urdu': 'ur', 'uyghur': 'ug', 'uzbek': 'uz', 'vietnamese': 'vi', 'welsh': 'cy', 'xhosa': 'xh', 'yiddish': 'yi', 'yoruba': 'yo', 'zulu': 'zu'}

# .env variables
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_ID = int(os.getenv('DISCORD_GENERAL'))
VOICE_CHANNEL_ID = int(os.getenv('DISCORD_VOICE_GENERAL'))

# Set up bot permissions, instance, command prefix, and temp audio file path
intents = discord.Intents.all()
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)
bot.temp_audio_files = []

# Whisper model (audio transcriptions)
model = whisper.load_model("base")

# Prints to console and discord when bot is ready and online
@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')
    channel = bot.get_channel(CHANNEL_ID)
    if channel:
        await channel.send("Dislingo is online! Use `!commands` to see how it works.")

# Allows for bot to join discord channel depending on "VOICE_CHANNEL_ID"
@bot.command(name='join', help='Tells the bot to join the voice channel')
async def join(ctx):
    voice_channel = bot.get_channel(VOICE_CHANNEL_ID)
    await voice_channel.connect()
    if voice_channel is None:
        await ctx.send("Unable to join the voice channel")

# Records audio in specified discord channel "VOICE_CHANNEL_ID"
@bot.command(name='record', help='Tells the bot to record the voice channel')
async def record(ctx):
    voice_channel = bot.get_channel(VOICE_CHANNEL_ID)
    if isinstance(voice_channel, discord.VoiceChannel):
        if ctx.voice_client is None:
            vc = await voice_channel.connect()
        elif ctx.voice_client.channel == voice_channel:
            vc = ctx.voice_client
        else:
            await ctx.voice_client.move_to(voice_channel)
            vc = ctx.voice_client
        vc.start_recording(discord.sinks.MP3Sink(), finished_callback, ctx)
        await ctx.send("Recording...")

# Callback function
async def finished_callback(sink, ctx):

    # Checks/Create directory
    directory = os.path.join(os.getcwd(), "DiscordAudio")
    if not os.path.exists(directory):
        os.makedirs(directory)

    recorded_users = []
    files = []

    # Records each users audio in different tracks
    for user_id, audio in sink.audio_data.items():
        file_path = os.path.join(directory, f"{user_id}.{sink.encoding}")
        with open(file_path, "wb") as file_output:
            audio.file.seek(0)
            shutil.copyfileobj(audio.file, file_output)
        files.append(file_path)
        recorded_users.append(f"<@{user_id}>")

    # Bots temp audio file
    bot.temp_audio_files = files

    # Message to see if recording was successful
    if files:
        await ctx.send(f"Finished! Recorded audio for {', '.join(recorded_users)}.", files=[discord.File(fp) for fp in files])
    else:
        await ctx.send("No audio was recorded or no valid audio file found.")

# Translates audio transcription into specified language
@bot.command(name='translate', help='Translates the audio transcription into the specified language')
async def translate(ctx, mention: str, language: str):
    # Get user id
    user_id = int(mention.strip('<@!>'))

    # Path to audio file based on user id
    audio_path = next((path for path in bot.temp_audio_files if str(user_id) in path), None)

    # Checks for audio file, its contents, transcription validity, and if bots is in channel.
    if audio_path:
        try:
            if os.path.getsize(audio_path) > 0:
                # Transcribe audio file
                result = model.transcribe(audio_path)
                transcription = result.get('text', 'Transcription not available')

                if transcription != 'Transcription not available':
                    # Translate text
                    translated_text = GoogleTranslator(source='auto', target=language).translate(transcription)
                    await ctx.send(f"Transcription for <@{user_id}>: {translated_text}")

                    # Convert TTS
                    tts = gTTS(text=translated_text, lang=language_dic.get(language))
                    tts_path = os.path.join(os.getcwd(), "tts_output.mp3")
                    tts.save(tts_path)

                    if ctx.voice_client and ctx.voice_client.is_connected():
                        # Play translate text into discord
                        ctx.voice_client.play(discord.FFmpegPCMAudio(tts_path))
                    else:
                        await ctx.send("Bot is not connected to a voice channel.")
                else:
                    await ctx.send("Transcription not available.")
            else:
                await ctx.send("Audio file is empty. No transcription made.")
        except Exception as e:
            await ctx.send(f"An error occurred: {str(e)}")
    else:
        await ctx.send("Audio file not found.")

# Bot stops recording audio
@bot.command(name='stop', help='Stops the recording')
async def stop(ctx):
    voice_client = ctx.guild.voice_client
    if ctx.voice_client:
        ctx.voice_client.stop_recording()
        await ctx.send("Stopped recording.")

# Bot leaves channel
@bot.command(name='leave', help='Tells the bot to leave the voice channel')
async def leave(ctx):
    voice_client = ctx.guild.voice_client
    if voice_client and voice_client.is_connected():
        await voice_client.disconnect()

# Prints all of our bot commands in discord chat
@bot.command(name='commands', help='Lists all available commands')
async def commands(ctx):
    help_text = """
    **List of Commands:**
    `!join` - Tells the bot to join the voice channel.
    `!record` - Tells the bot to record the voice channel.
    `!translate <mention> <language>` - Translates the audio transcription based on user into the specified language.
    `!stop` - Stops the recording.
    `!leave` - Tells the bot to leave the voice channel.
    """
    await ctx.send(help_text)

# Runs bot
bot.run(TOKEN)
