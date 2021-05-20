# pylint: disable=import-error

import asyncio
import json
import random
import time
import os
import datetime

import discord
from discord.ext import commands
from discord.ext.commands import BadArgument, CommandNotFound, MaxConcurrencyReached

# To import from different path
import sys
sys.path.insert(1 , os.getcwd())

from utils import bot_check, splittime, timestring, log_command

RIOT_DURATION = 120

def get_escape_chance(num_participants):

    if num_participants == 1:
        escape_chance = 0.25
    else:
        escape_chance = 0
        for x in range(num_participants - 1):
            escape_chance += 0.5 ** (x + 1)
            
    return escape_chance

class Jail(commands.Cog):

    def __init__(self, client):
        self.client = client

        self.riot = None
        self.riot_task = None

    @commands.command(aliases=['jailedm'])
    async def jailed(self, ctx, page=1):

        if isinstance(page, str):
            if page.isdigit():
                page = int(page)
            else:
                return await ctx.send("Enter a valid page number.")

        async with self.client.pool.acquire() as db:
            jailed = await db.fetch('SELECT id, name, jailtime FROM members WHERE jailtime > $1 ORDER BY jailtime DESC;', int(time.time()))

        if not jailed:
            embed = discord.Embed(color=0x941919, description="None")
            embed.set_author(name=f"Jailed Members")
            await ctx.send(embed=embed)
            return

        if ctx.message.content.startswith('.jailedm'):
            mobile = True
        else:
            mobile = False
        
        # dividing into lists of 5
        jailed = [jailed[x:x+10] for x in range(0, len(jailed), 5)]

        embed = discord.Embed(color=0x941919)
        embed.set_author(name=f"Jailed Members")

        if page > len(jailed):
            return await ctx.send("There are not that many pages.")
        
        for member in jailed[page-1]:

            if not mobile:
                embed.add_field(name=discord.utils.escape_markdown('___'), value=f"<@{member['id']}>: {splittime(member['jailtime'])}", inline=False)
            else:
                embed.add_field(name=discord.utils.escape_markdown('___'), value=f"{member['name']}: {splittime(member['jailtime'])}", inline=False)

        embed.set_footer(text=f"Page {page}/{len(jailed)}")

        
        await ctx.send(embed=embed)

    async def riot_escape(self):
        await asyncio.sleep(RIOT_DURATION)

        escape_chance = get_escape_chance(len(self.riot['participants']))
        
        # if successful
        if random.random() <= escape_chance:
            
            async with self.client.pool.acquire() as db:
                for userid in self.riot['participants']:
                    await db.set_member_val(userid, 'jailtime', 0)

                    money = await db.get_member_val(userid, 'money')
                    await db.set_member_val(userid, 'money', money + 200)

            await self.riot['location'].send('✊ The riot was successful and all participants managed to escape jail and got $200! ✊')
        
        else:
            async with self.client.pool.acquire() as db:
                for userid in self.riot['participants']:
                    jailtime = await db.get_member_val(userid, 'jailtime')
                    # extra 2 hours
                    await db.set_member_val(userid, 'jailtime', jailtime + 7200)

            await self.riot['location'].send('❌ The riot failed and all participants got an extra 2 hours of jailtime ❌.')

        with open('./storage/jsons/riot cooldown.json', 'w') as f:
            # 12 hours
            json.dump(int(time.time()) + 43200, f)

        self.riot = None
        self.riot_task = None

            

    @commands.group(name='riot', invoke_without_command=True)
    async def riot_group(self, ctx):
        await ctx.send(f'Incorrect command usage:\n`.riot start/join/list/time/chance`')

    @riot_group.command()
    async def start(self, ctx):

        async with self.client.pool.acquire() as db:
            jailtime = await db.get_member_val(ctx.author.id, 'jailtime')
            if jailtime <= time.time() + RIOT_DURATION:
                return await ctx.send(f'You must be in jail to start a riot.')

        with open('./storage/jsons/riot cooldown.json') as f:
            riotc = json.load(f)

        if riotc > time.time():
            return await ctx.send(f'Everyone must wait {splittime(riotc)} before another riot can happen.')

        elif self.riot:
            return await ctx.send(f"There is an ongoing riot right now.")
            
        self.riot = {
            'participants': [ctx.author.id],
            'location': ctx.channel,
            'start': int(time.time()) + RIOT_DURATION
        }

        await ctx.send(f'Riot started. You have two minutes to gather as many people as you can to break free from jail.')

        self.riot_task = asyncio.create_task(
            self.riot_escape()
        )

    @riot_group.command()
    async def join(self, ctx):

        async with self.client.pool.acquire() as db:
            jailtime = await db.get_member_val(ctx.author.id, 'jailtime')        

            if jailtime <= time.time() + RIOT_DURATION:
                return await ctx.send(f'You must be in jail to join a riot.')

        if not self.riot: return await ctx.send(f"There is no ongoing riot right now.")

        elif ctx.author.id in self.riot['participants']: return await ctx.send(f"You are already in this riot.")

        self.riot['participants'].append(ctx.author.id)

        await ctx.send(f'**{ctx.author.name}** has joined the riot.')


    @riot_group.command(name="list")
    async def riot_list(self, ctx):

        if not self.riot: return await ctx.send(f"There is no ongoing riot right now.")

        guild = self.client.mainGuild

        embed = discord.Embed(color=0xff1414, title=f'Jail Riot')

        for person in self.riot['participants']:
            name = discord.utils.escape_markdown(guild.get_member(person).name)
            embed.add_field(value=name, name=discord.utils.escape_markdown('___'), inline=True)

        await ctx.send(embed=embed)

    @riot_group.command(name="time")
    async def riot_time(self, ctx):

        if not self.riot:
            with open('./storage/jsons/riot cooldown.json') as f:
                riot_cooldown = json.load(f)
            
            if riot_cooldown > time.time():
                await ctx.send(f'A riot can be made in {splittime(riot_cooldown)}.') 
            else:
                await ctx.send('A riot can be made.')
        
        else:
            await ctx.send(f'The riot will start in {self.riot["start"]-int(time.time())} seconds.') 

    @riot_group.command()
    async def chance(self, ctx):

        if not self.riot: return await ctx.send(f"There is no ongoing riot right now.")
        
        num_participants = len(self.riot['participants'])
        await ctx.send(f'There is a {int(get_escape_chance(num_participants) * 100)}% chance the riot will be successful with {num_participants} participant{"s" if num_participants > 1 else ""}.')
    


def setup(client):
    client.add_cog(Jail(client))