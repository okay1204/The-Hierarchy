# pylint: disable=import-error

import os
import time
import asyncio
import random
import discord
from discord.ext import commands

# To import from different path
import sys
sys.path.insert(1 , os.getcwd())

from utils import read_value, write_value, add_item, remove_item, add_use, splittime

class ItemUses:

    def __init__(self, client):
        self.client = client

        self.dispatcher = {
            'padlock': self.padlock, 
            'gun': self.gun, 
            'backpack': self.backpack, 
            'pass': self.pass_item,
            'handcuffs': self.handcuffs,
            'thingy': self.thingy
            }

    async def dispatch(self, ctx, item):
        
        await self.dispatcher[item](ctx)

    async def padlock(self, ctx):
        timer = int(time.time()) + 172800
        add_use('padlock', timer, ctx.author.id)
        remove_item('padlock', ctx.author.id)
        await ctx.send(f"**{ctx.author.name}** used a **padlock**.")

    async def gun(self, ctx):
        timer = int(time.time()) + 46800
        add_use('gun', timer, ctx.author.id)
        remove_item('gun', ctx.author.id)
        await ctx.send(f"**{ctx.author.name}** used a **gun**.")

    async def backpack(self, ctx):
        storage = read_value(ctx.author.id, 'storage')
        storage += 1
        write_value(ctx.author.id, 'storage', storage)
        remove_item('backpack', ctx.author.id)
        await ctx.send(f"**{ctx.author.name}** used a **backpack**.\nYou can now carry up to {storage} items.")
    
    async def pass_item(self, ctx):

        jailtime = read_value(ctx.author.id, 'jailtime')
        if jailtime < time.time():
            await ctx.send('You are not in jail.')
            return
        else:
            bailprice = int(int(jailtime-time.time())/3600*40)
            money = read_value(ctx.author.id, 'money')
            if bailprice > money:
                await ctx.send(f'You must have at least ${bailprice} to bail yourself.')
            else:
                money -= bailprice
                write_value(ctx.author.id, 'money', money)
                write_value(ctx.author.id, 'jailtime', int(time.time()))

                remove_item('pass', ctx.author.id)
                await ctx.send(f"**{ctx.author.name}** used a **pass**.")
                await ctx.send(f'💸 You bailed yourself for ${bailprice}. 💸')
    
    async def handcuffs(self, ctx):

        await ctx.send("Who do you want to handcuff?")
        try:
            member = await self.client.wait_for('message', check=lambda x: x.channel == ctx.channel and x.author == ctx.author, timeout=20)
        except asyncio.TimeoutError:
            await ctx.send("Handcuff timed out.")
            return

        member = member.content.lower()

        member = await commands.MemberConverter().convert(ctx, member)

        if not member:
            await ctx.send("Member not found.")
            return
        
        elif ctx.author == member:
            await ctx.send("You can't handcuff yourself.")
            return
        
        elif read_value(member.id, 'jailtime') > time.time():
            await ctx.send("This user is already in jail.")
            return
        
        cuffc = read_value(member.id, 'cuffc')
        if cuffc > time.time():
            await ctx.send(f"You must wait {splittime(cuffc)} before you can handcuff this user again.")
            return

        remove_item('handcuffs', ctx.author.id)

        if random.randint(1, 10) > 3:
            random_time = int(time.time()) + random.randint(5400, 7200) # 1h 30m to 2h
            write_value(member.id, 'jailtime', random_time)
            write_value(member.id, 'cuffc', int(time.time()) + 10800) # three hours
            await ctx.send(f"You successfully jailed **{member.name}** for {splittime(random_time)}.")
        
        else:
            random_time = int(time.time()) + random.randint(600, 1800) # 10m to 30m
            write_value(ctx.author.id, 'jailtime', random_time)
            await ctx.send(f"Your plan backfired and you got jailed for {splittime(random_time)}!")

    async def thingy(self, ctx):
        
        await ctx.send("You uhh... used? the useless thingy?")
        remove_item('thingy', ctx.author.id)
    
