# pylint: disable=import-error
import nextcord
from nextcord.ext import commands
import random
import json
import asyncio
import time
import os
from sqlite3 import Error

# To import from different path
import sys
sys.path.insert(1 , os.getcwd())

from utils import bot_check, splittime, timestring, log_command

class Misc(commands.Cog):

    def __init__(self, client):
        self.client = client

    async def cog_check(self, ctx):
        if ctx.channel.id == self.client.partnershipChannel:
            return True
        else:
            return False

    @commands.command()
    async def partner(self, ctx, member:nextcord.Member=None):
        
        if not member:
            await ctx.send('Incorrect command usage:\n`partner member`')
            return
        
        guild = self.client.mainGuild
        role = guild.get_role(714891174984417342)

        await member.add_roles(role)
        await ctx.send(f'Granted partner role to {member.mention}.')

    @commands.command()
    async def unpartner(self, ctx, member:nextcord.Member=None):
        
        if not member:
            await ctx.send('Incorrect command usage:\n`unpartner member`')
            return
        
        guild = self.client.mainGuild
        role = guild.get_role(714891174984417342)

        await member.remove_roles(role)
        await ctx.send(f'Removed partner role from {member.mention}.')


def setup(client):
    client.add_cog(Misc(client))