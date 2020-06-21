import discord
from discord.ext import commands
import random
import json
import asyncio
import time
import sqlite3
from sqlite3 import Error
from utils import *

class misc(commands.Cog):

    def __init__(self, client):
        self.client = client


    @commands.command()
    @commands.check(partnershipCheck)
    async def partner(self, ctx, member:discord.Member=None):
        
        if not member:
            await ctx.send('Enter a member to grant the partnership role to.')
        
        guild = self.client.get_guild(692906379203313695)
        role = guild.get_role(714891174984417342)

        await member.add_roles(role)
        await ctx.send(f'Granted partner role to {member.mention}.')

    @commands.command()
    @commands.check(partnershipCheck)
    async def unpartner(self, ctx, member:discord.Member=None):
        
        if not member:
            await ctx.send('Enter a member to remove the partnership role from.')
        
        guild = self.client.get_guild(692906379203313695)
        role = guild.get_role(714891174984417342)

        await member.remove_roles(role)
        await ctx.send(f'Removed partner role from {member.mention}.')



    @partner.error
    @unpartner.error
    async def member_not_found_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send("Member not found.")
        else:
            print(error)


def setup(client):
    client.add_cog(misc(client))