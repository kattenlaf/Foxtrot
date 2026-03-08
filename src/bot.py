import discord
from discord.ext import commands
import constants
import json
import youtube_dl
import os
import asyncio

def GetResources():
    file_abs_path = os.path.abspath(os.path.dirname(__file__))
    resources_path = os.path.join(file_abs_path, '..', constants.DISCORD_RESOURCES)
    with open(resources_path, 'r') as f:
        file_data = f.read()
        resources_data = json.loads(file_data)
    return resources_data

def GetBotToken(resources):
    return resources[constants.TOKEN]

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
    def __init__(self, source, *, data, volume=0.5):
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

class Music(commands.Cog):
    def __init__(self, disco_bot):
        self.bot = disco_bot
        print("bot is initialized for music")

    # Todo still need to fix the joining here, getting an error - discord.errors.ConnectionClosed: Shard ID None WebSocket closed with 4017
    @commands.command()
    async def join(self, context, *, channel: discord.VoiceChannel):
        if context.voice_client is not None:
            print("context voice client is not none")
            return await context.voice_client.move_to(channel)
        print("Joining")
        vc = await channel.connect()
        print(vc)
        print("Joined")

    @commands.command()
    async def play(self, ctx, *, query):
        """Plays a file from the local filesystem"""

        source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(query))
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
        await disco_bot.start(token)

if __name__ == '__main__':
    asyncio.run(main())