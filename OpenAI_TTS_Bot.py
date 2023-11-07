import discord
from discord.ext import commands
import requests
import os
from io import BytesIO

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

# Initialize the Discord client
bot = commands.Bot(command_prefix='!', description="Bot", intents=intents)

#Discord Bot / Make sure your bot can attach files
DISCORD_TOKEN = "DISCORD_BOT_TOKEN"
#API KEy
OPENAI_KEY = "OPEN_API_KEY"

#Defaults Voice
current_voice = "echo" 

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord! ready to make mp3s!')
    
@bot.event
async def on_message(message):
    # Do not let the bot respond to itself
    if message.author == bot.user:
        return     
    # only work if is a DM
    if isinstance(message.channel, discord.DMChannel):
        
        #Show typing for good feedback
        async with message.channel.typing():
            if message.content.startswith("VOICE"):
                await message.author.send(change_voice(message.content))
                return
            # Call the function and get the speech synthesis
            audio_data  = synthesize_speech(message.content)

            if not isinstance(audio_data, str):  # Check if the result is not an error message
                
                # We use discord.File to send the BytesIO object as a file
                # The filename parameter is important as Discord needs to know what type of file it is
                fileName = trim_string(message.content)
                await message.author.send(file=discord.File(audio_data, filename=fileName +".mp3"))
            else:
                # Send the error message back in the DM
                await message.author.send("Sorry an error occured" + audio_data)

def synthesize_speech(what_to_say):
    #doing through the curl for now quick and easy!
    url = "https://api.openai.com/v1/audio/speech"
    headers = {
        "Authorization": f"Bearer {OPENAI_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "tts-1-hd",
        "input": what_to_say,
        "voice": current_voice
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        # Instead of saving the file, we return a BytesIO object so it can run anywhere
        return BytesIO(response.content)
    else:
        # Handle errors
        return f"Error: {response.status_code} - {response.text}"



#Change voice function acess by using VOICE in all caps     
def change_voice(message):
    #Purge word Voice
    message = message.replace("VOICE ",'');
    global current_voice
    print(message)
    valid_voices = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
    if message.lower() in valid_voices:
        current_voice = message.lower()
        return (f"Voice changed to {current_voice}. 🤖" )
    else:
        return (f"🤖 Please use alloy, echo, fable, onyx, nova, or shimmer. CURRENT VOICE: {current_voice}  MORE INFO:  <https://platform.openai.com/docs/guides/text-to-speech>"  )

def trim_string(string):

  words = string.split()
  if len(words) > 3:
    return " ".join(words[:3])
  else:
    return string
        
# Run the bot with the token from the environment variable
bot.run(DISCORD_TOKEN)
