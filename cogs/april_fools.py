# pylint: disable=import-error

import asyncio
import json
import random
import time
import datetime

import nextcord
from nextcord.ext import commands, tasks
from nextcord.ext.commands import BadArgument, CommandNotFound, MaxConcurrencyReached

from utils import bot_check, splittime, timestring, log_command

class AprilFools(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command()
    async def rickroll(self, ctx, *, member: nextcord.Member=None):

        if ctx.channel.category_id == 721444286591139963:
            return

        if not member:
            return await ctx.send("Incorrect command usage:\n`.rickroll member`")
        
        await ctx.send(f"**{ctx.author.name}** rickrolled **{member.name}**\n\nhaha dumb\nhttps://tenor.com/view/dance-moves-dancing-singer-groovy-gif-17029825")

    
                
def setup(client):
    client.add_cog(AprilFools(client))
