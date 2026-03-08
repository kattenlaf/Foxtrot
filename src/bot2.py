import discord
from discord.ext import commands
import constants
import json
import youtube_dl
import os
import asyncio

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.command()
async def join(context, *, channel: discord.VoiceChannel):
    if context.voice_client is not None:
        print("context voice client is not none")
        return await context.voice_client.move_to(channel)
    print("Joining")
    vc = await channel.connect()
    print(vc)
    print("Joined")

bot.run('<place token here>')