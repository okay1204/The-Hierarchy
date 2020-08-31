# pylint: disable=import-error

import asyncio
import json
import random
import sqlite3
import time
import os
from sqlite3 import Error

import discord
from discord.ext import commands

# To import from different path
import sys
sys.path.insert(1 , os.getcwd())

from utils import (read_value, write_value, update_total, leaderboard,
rolecheck, splittime, open_heist, bot_check, in_use, jail_heist_check, around,
remove_item, remove_use, add_item, write_heist, add_use)
class premium(commands.Cog):

    def __init__(self, client):
        self.client = client

    async def cog_check(self, ctx):
        if ctx.channel.category.id != self.client.rightCategory:
            return False
        else:
            return True

    @commands.command()
    async def boost(self, ctx):
        author = ctx.author
        
        if not ctx.author.premium_since:
            await ctx.send("You don't have __premium__. Get __premium__ by boosting the server!")
            return

        with open('./storage/jsons/mode.json') as f:
            mode = json.load(f)
            
        if mode == "event":
            await ctx.send("Premium perks are disabled during events.")
            return

        boosts = read_value(author.id, 'boosts')
        if boosts <= 0:
            await ctx.send("You're don't have any boosts.")
            return
        
        timers = ["workc", "jailtime", "stealc", "rpsc", "bankc", "dailytime", "studyc"]
        for timer in timers:
            current = read_value(author.id, timer)
            current -= 3600
            write_value(author.id, timer, current)

        boosts -= 1
        write_value(author.id, "boosts", boosts)
        await ctx.send('⏱️ You boosted 1 hour! ⏱️')

    @commands.command()
    async def boostcount(self, ctx, *, member:discord.Member=None):
        if not member:

            author = ctx.author

            if not ctx.author.premium_since:
                await ctx.send("You don't have __premium__. Get __premium__ by boosting the server!")
                return

            boosts = read_value(author.id, 'boosts')
            await ctx.send(f"⏱️ **{author.name}**'s boosts: {boosts}")

        elif not await bot_check(self.client, ctx, member):
            return

        else:

            if not member.premium_since:      
                await ctx.send(f"**{member.name}** does not have __premium__.")
                return

                
            boosts = read_value(member.id, 'boosts')
            await ctx.send(f"⏱️ **{member.name}**'s boosts: {boosts}")



def setup(client):
    client.add_cog(premium(client))