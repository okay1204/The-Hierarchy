import discord
from discord.ext import commands
import json
from utils import *

class debug(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command()
    @commands.check(debugCheck)
    async def stats(self, ctx, member=None):
        hierarchy = open_json()
        guild = self.client.get_guild(692906379203313695)
        if not member:
            await ctx.send("Enter a user.")
        for person in hierarchy:
            if int(person["user"]) == int(member):
                await ctx.send(person)


    @commands.command()
    @commands.check(debugCheck)
    async def online(self, ctx):
        guild = self.client.get_guild(692906379203313695)
        channel = self.client.get_channel(698384786460246147)
        message = await channel.fetch_message(698775210173923429)
        embed = discord.Embed(color=0x42f57b)
        botuser = guild.get_member(698771271353237575)
        botuser = botuser.avatar_url_as(static_format='jpg',size=256)
        embed.set_author(name="Bot ready to use.",icon_url=botuser)
        await message.edit(embed=embed)
        await ctx.send("Status updated to online.")

    @commands.command()
    @commands.check(debugCheck)
    async def offline(self, ctx):
        guild = self.client.get_guild(692906379203313695)
        channel = self.client.get_channel(698384786460246147)
        message = await channel.fetch_message(698775210173923429)
        embed = discord.Embed(color=0xff5254)
        botuser = guild.get_member(698771271353237575)
        botuser = botuser.avatar_url_as(static_format='jpg',size=256)
        embed.set_author(name="Bot under development.",icon_url=botuser)
        await message.edit(embed=embed)
        await ctx.send("Status updated to offline.")
    




def setup(client):
    client.add_cog(debug(client))
