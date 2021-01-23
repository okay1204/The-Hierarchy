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

from utils import bot_check, splittime, timestring, log_command

class ItemUses:

    def __init__(self, client, db):
        self.client = client
        self.db = db

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

        await self.db.add_use(ctx.author.id, 'padlock', timer)
        await self.db.remove_item(ctx.author.id, 'padlock')

        await ctx.send(f"**{ctx.author.name}** used a 🔒 **padlock**.")

    async def gun(self, ctx):
        timer = int(time.time()) + 46800

        await self.db.add_use(ctx.author.id, 'gun', timer)
        await self.db.remove_item(ctx.author.id, 'gun')

        await ctx.send(f"**{ctx.author.name}** used a 🔫 **gun**.")

    async def backpack(self, ctx):


        storage = await self.db.fetchval('UPDATE members SET storage = storage + 1 WHERE id = $1 RETURNING storage;', ctx.author.id)

        await self.db.remove_item('backpack', ctx.author.id)

        await ctx.send(f"**{ctx.author.name}** used a 🎒 **backpack**.\nYou can now carry up to {storage} items.")
    
    async def pass_item(self, ctx):

        jailtime = await self.db.get_member_val(ctx.author.id, 'jailtime')
        
        if jailtime < time.time():
            return await ctx.send('You are not in jail.')
    
        else:
            bailprice = self.client.bailprice(jailtime)
            
            money = await self.db.get_member_val(ctx.author.id, 'money')

            if bailprice > money:
                await ctx.send(f'You must have at least ${bailprice} to bail yourself.')

            else:
                money -= bailprice

                await self.db.set_member_val(ctx.author.id, 'money', money)
                await self.db.set_member_val(ctx.author.id, 'jailtime', 0)

                await self.db.remove_item(ctx.author.id, 'pass')
                await ctx.send(f"**{ctx.author.name}** used a 🏳️ **pass**.\n💸 You bailed yourself for ${bailprice}. 💸")
                
    
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
        
        elif ctx.author.id == member.id:
            await ctx.send("You can't handcuff yourself.")
            return
        
        elif await self.db.get_member_val(member.id, 'jailtime') > time.time():
            await ctx.send("This user is already in jail.")
            return
        
        cuffc = await self.db.get_member_val(member.id, 'cuffc')
        if cuffc > time.time():
            await ctx.send(f"You must wait {splittime(cuffc)} before you can handcuff this user again.")
            return

        await self.db.remove_item(ctx.author.id, 'handcuffs')

        if random.randint(1, 10) > 3:
            random_time = int(time.time()) + random.randint(5400, 7200) # 1h 30m to 2h

            await self.db.set_member_val(member.id, 'jailtime', random_time)
            await self.db.set_member_val(member.id, 'cuffc', int(time.time()) + 10800) # three hours

            await ctx.send(f"<:handcuffs:722687293638574140> You successfully jailed **{member.name}** for {splittime(random_time)}. <:handcuffs:722687293638574140>")
        
        else:
            random_time = int(time.time()) + random.randint(600, 1800) # 10m to 30m
            await self.db.set_member_val(ctx.author.id, 'jailtime', random_time)
            await ctx.send(f"<:handcuffs:722687293638574140> Your plan backfired and you got jailed for {splittime(random_time)}! <:handcuffs:722687293638574140>")


    async def thingy(self, ctx):
        
        await ctx.send("💠 You uhh... used? the useless thingy? 💠")
        await self.db.remove_item(ctx.author.id, 'thingy')
    
