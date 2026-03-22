import discord
from discord.ext import commands
import constants
import json
# import youtube_dl - old module
import yt_dlp as youtube_dl
import os
import asyncio
from pathlib import Path

def GetResources():
    file_abs_path = os.path.abspath(os.path.dirname(__file__))
    resources_path = os.path.join(file_abs_path, '..', constants.DISCORD_RESOURCES)
    with open(resources_path, 'r') as f:
        file_data = f.read()
        resources_data = json.loads(file_data)
    return resources_data

def UpdateResources(file_data):
    file_abs_path = os.path.abspath(os.path.dirname(__file__))
    resources_path = os.path.join(file_abs_path, '..', constants.DISCORD_RESOURCES)
    with open(resources_path, 'w') as file:
        json.dump(file_data, file, indent=4)

def GetBotToken(resources):
    return resources[constants.TOKEN]

# Summary
# resources is the json file with the metadata needed for the bot, json_dict
# member_name is the name of the user's profile we want to check, string
# sound type denotes what type of sound we want to get for the user, int
def GetMemberSoundFromResources(resources, member_name, sound_type_val):
    profiles = resources[constants.MEMBER_PROFILES]
    if member_name in profiles:
        member_profile = profiles[member_name]
        sound_type = constants.SOUND_TYPES[sound_type_val]
        sound_to_play = constants.SOUNDS_AVAILABLE[member_profile[sound_type]]
        file_path = Path(sound_to_play)
        if not file_path.exists():
            sound_to_play = constants.SOUNDS_AVAILABLE[constants.DEFAULT]
        return sound_to_play
    else:
        # Todo create new user profile
        new_profile = {
            member_name: {
                constants.JSON_SOUND: constants.DEFAULT
            }
        }
        sound_to_play = constants.SOUNDS_AVAILABLE[constants.DEFAULT]
        profiles.update(new_profile) # Save to the file
        UpdateResources(resources)
        return sound_to_play



# Example taken from - https://github.com/Rapptz/discord.py/blob/master/examples/basic_voice.py
# Suppress noise about console usage from errors
# youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0',  # bind to ipv4 since ipv6 addresses cause issues sometimes
}


ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=constants.DEFAULT_VOLUME):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, options='-vn'), data=data)

class Events(commands.Cog):
    def __init__(self, disco_bot):
        self.bot = disco_bot
        print("bot is initialized with events")

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if before.channel is not None:
            if after.channel is None:
                print(f"{member.name} left {before.channel.name}")
                print(self.bot.voice_clients)
                voice_client = self.bot.voice_clients[0]
                if voice_client:
                    sound_to_play = GetMemberSoundFromResources(resources, member.name, constants.SOUND_TYPE_EXIT)
                    print(f"{member.name} entrance track is {sound_to_play}")
                    await self.play_sound(voice_client, sound_to_play)
                    return
            else:
                print(f"{member.name} left {before.channel.name} and went to {after.channel.name}")
        if after.channel is not None:
            # User has altered their voice state within the voice channel itself, i.e. streaming, deafen, mute
            if before.channel is not None and before.channel.id == after.channel.id:
                # User is streaming
                print('user altered their voice state a different way')
            else:
                voice_client = self.bot.voice_clients[0]
                if voice_client.channel.id == after.channel.id:
                    sound_to_play = GetMemberSoundFromResources(resources, member.name, constants.SOUND_TYPE_ENTER)
                    print(f"{member.name} exit track is {sound_to_play}")
                    await self.play_sound(voice_client, sound_to_play)

    async def play_sound(self, voice_client, sound_to_play):
        source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(sound_to_play))
        voice_client.play(source, after=lambda e: print(f'Player error: {e}') if e else None)

    @commands.Cog.listener()
    async def on_message(self, message):
        print(message.author)
        if len(message.content) < constants.CHECK_MESSAGE_LIMIT and message.content.find("remind him jarvis") != -1:
            await message.channel.send("you lame")


class Music(commands.Cog):
    def __init__(self, disco_bot):
        self.bot = disco_bot
        print("bot is initialized for music")

    @commands.command()
    async def join(self, context, *, channel: discord.VoiceChannel):
        if context.voice_client is not None:
            print("context voice client is not none")
            return await context.voice_client.move_to(channel)
        vc = await channel.connect()

    @commands.command()
    async def leave(self, context):
        if context.voice_client is None:
            await context.send("bot is currently not in a voice chat")
            return
        await context.voice_client.disconnect() # check documentation - https://discordpy.readthedocs.io/en/stable/api.html#discord.VoiceProtocol.disconnect
        print("bot disconnected")

    @commands.command()
    async def play(self, ctx, *, query):
        """Plays a file from the local filesystem"""
        true_query = f"{constants.LOCAL_SOUNDS}\\{query}.mp3"
        print(true_query)

        source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(true_query))
        ctx.voice_client.play(source, after=lambda e: print(f'Player error: {e}') if e else None)

        await ctx.send(f'Now playing: {query}')

    @commands.command()
    async def yt(self, ctx, *, url):
        """Plays from a url (almost anything youtube_dl supports)"""

        async with ctx.typing():
            player = await YTDLSource.from_url(url, loop=self.bot.loop)
            ctx.voice_client.play(player, after=lambda e: print(f'Player error: {e}') if e else None)

        await ctx.send(f'Now playing: {player.title}')

    @commands.command()
    async def stream(self, ctx, *, url):
        """Streams from a url (same as yt, but doesn't predownload)"""

        async with ctx.typing():
            player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
            ctx.voice_client.play(player, after=lambda e: print(f'Player error: {e}') if e else None)

        await ctx.send(f'Now playing: {player.title}')

    @commands.command()
    async def volume(self, ctx, volume: int):
        """Changes the player's volume"""

        if ctx.voice_client is None:
            return await ctx.send('Not connected to a voice channel.')

        ctx.voice_client.source.volume = volume / 100
        await ctx.send(f'Changed volume to {volume}%')

    @commands.command()
    async def stop(self, ctx):
        """Stops and disconnects the bot from voice"""

        await ctx.voice_client.disconnect()

    @play.before_invoke
    @yt.before_invoke
    @stream.before_invoke
    async def ensure_voice(self, ctx):
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send('You are not connected to a voice channel.')
                raise commands.CommandError('Author not connected to a voice channel.')
        elif ctx.voice_client.is_playing():
            ctx.voice_client.stop()



# --------------
# DRIVER
# --------------
resources = GetResources()
token = GetBotToken(resources)
intents = discord.Intents.default()
intents.message_content = True
disco_bot = commands.Bot(command_prefix=constants.JARVIS_CMD_PREFIX,
                         description='Simple music bot',
                         intents=intents)

@disco_bot.event
async def on_ready(self):
    print("test")
    assert disco_bot.user is not None
    print(f"Logged in as {disco_bot.user} {ID : {disco_bot.user.id}}")
    print('---------')

async def main():
    async with disco_bot:
        await disco_bot.add_cog(Music(disco_bot))
        await disco_bot.add_cog(Events(disco_bot))
        await disco_bot.start(token)

if __name__ == '__main__':
    asyncio.run(main())