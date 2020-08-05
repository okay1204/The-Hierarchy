# pylint: disable=import-error

import discord
from discord.ext import commands
import json
import sqlite3
import os
from sqlite3 import Error

# To import from different path
import sys
sys.path.insert(1 , os.getcwd())

from utils import (read_value, write_value, update_total, leaderboard,
rolecheck, splittime, open_heist, bot_check, in_use, jail_heist_check, around,
remove_item, remove_use, add_item, write_heist, add_use)

class debug(commands.Cog):

    def __init__(self, client):
        self.client = client

    async def cog_check(self, ctx):
        if ctx.channel.category.id == self.client.adminChannel:
            return True
        else:
            return False

    @commands.command()
    async def online(self, ctx):
        guild = self.client.get_guild(self.client.mainGuild)
        channel = self.client.get_channel(698384786460246147)
        message = await channel.fetch_message(698775210173923429)
        embed = discord.Embed(color=0x42f57b)
        botuser = guild.get_member(698771271353237575)
        botuser = botuser.avatar_url_as(static_format='jpg',size=256)
        embed.set_author(name="Bot ready to use.",icon_url=botuser)
        await message.edit(embed=embed)
        await ctx.send("Status updated to online.")
        await self.client.change_presence(status=discord.Status.online,activity=discord.Game(name='with money'))

    @commands.command()
    async def offline(self, ctx):
        guild = self.client.get_guild(self.client.mainGuild)
        channel = self.client.get_channel(698384786460246147)
        message = await channel.fetch_message(698775210173923429)
        embed = discord.Embed(color=0xff5254)
        botuser = guild.get_member(698771271353237575)
        botuser = botuser.avatar_url_as(static_format='jpg',size=256)
        embed.set_author(name="Bot under development.",icon_url=botuser)
        await message.edit(embed=embed)
        await ctx.send("Status updated to offline.")
        await self.client.change_presence(status=discord.Status.dnd, activity=discord.Game(name='UNDER DEVELOPMENT'))
    
def setup(client):
    client.add_cog(debug(client))
