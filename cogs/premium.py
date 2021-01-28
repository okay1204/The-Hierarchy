# pylint: disable=import-error

import asyncio
import json
import random
import time
import os
from sqlite3 import Error
import re

import discord
from discord.ext import commands

# To import from different path
import sys
sys.path.insert(1 , os.getcwd())

from utils import bot_check, splittime, timestring, log_command
class Premium(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.control_sessions = []

    async def cog_check(self, ctx):
        if ctx.command.name == "control" and ctx.channel.category.id in (
            692949458551439370, # chat
            716729977223119018, # staff
            757374291028213852, # voice chats
            self.client.rightCategory
        ):
            return True

        if ctx.channel.category.id != self.client.rightCategory:
            return False
        else:
            return True

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):

        error = getattr(error, 'original', error)

        if isinstance(error, commands.MaxConcurrencyReached):
            if ctx.command.name == 'control':
                await ctx.message.delete()

    @commands.command()
    async def boost(self, ctx):
        author = ctx.author
        
        if not ctx.author.premium_since:
            await ctx.send("You don't have __premium__. Get __premium__ by boosting the server!")
            return

        with open('./storage/jsons/mode.json') as f:
            mode = json.load(f)
        
        async with self.client.pool.acquire() as db:

            if mode == "event" and await db.get_member_val(ctx.author.id, 'in_event'):
                return await ctx.send("Premium perks are disabled during events.")

            boosts = await db.get_member_val(author.id, 'boosts')
            if boosts <= 0:
                await ctx.send("You don't have any boosts left.")
                return
            
            timers = ["workc", "jailtime", "stealc", "rpsc", "bankc", "dailytime", "studyc", "applyc"]
            for timer in timers:
                current = await db.get_member_val(author.id, timer)
                current -= 3600
                await db.set_member_val(author.id, timer, current)

            boosts -= 1
            await db.set_member_val(author.id, "boosts", boosts)

        await ctx.send('⏱️ You boosted 1 hour! ⏱️')

    @commands.command()
    async def boostcount(self, ctx, *, member:discord.Member=None):

        async with self.client.pool.acquire() as db:

            if not member:

                if not ctx.author.premium_since:
                    await ctx.send("You don't have __premium__. Get __premium__ by boosting the server!")
                    return

                boosts = await db.get_member_val(ctx.author.id, 'boosts')
                await ctx.send(f"⏱️ **{ctx.author.name}**'s boosts: {boosts}")

            elif not await bot_check(self.client, ctx, member):
                return

            else:

                if not member.premium_since:      
                    await ctx.send(f"**{member.name}** does not have __premium__.")
                    return

                    
                boosts = await db.get_member_val(member.id, 'boosts')

        await ctx.send(f"⏱️ **{member.name}**'s boosts: {boosts}")

    @commands.command()
    @commands.max_concurrency(1, per=commands.BucketType.member)
    async def control(self, ctx):

        if (not ctx.author.premium_since) and ctx.author.id != self.client.myself.id:
            return await ctx.send("You don't have __premium__. Get __premium__ by boosting the server!")

        elif ctx.channel.id in map(lambda session: session["channel"].id, self.control_sessions): 
            await ctx.message.delete()
            try:
                await ctx.author.send("Someone else is controlling in this channel.")
            except:
                pass
            return

        allowed_categories = (692949972764590160, 692949458551439370, 716729977223119018, 761669069094387732, 757374291028213852)

        if ctx.channel.category.id not in allowed_categories:
            try:
                await ctx.author.send("You may not control in this channel.")
            except:
                pass
            return

        try:
            await ctx.author.send(f"You are now talking in {ctx.channel.mention}. Type `.stop` in this DM to stop.")
        except:
            return await ctx.send("Give me permissions to DM you!")

        await ctx.message.delete()

        self.control_sessions.append( {"channel": ctx.channel, "author": ctx.author, "messages": []} )
        index = len(self.control_sessions) - 1
        author_timeout = asyncio.create_task( self.author_timeout(ctx) )
        control_input = asyncio.create_task( self.control_input(ctx) )
        control_editing = asyncio.create_task( self.control_editing(ctx) )
        control_deleting = asyncio.create_task( self.control_deleting(ctx) )

        await asyncio.wait([
            author_timeout, control_input
        ], return_when=asyncio.FIRST_COMPLETED)

        if not author_timeout.done():
            author_timeout.cancel()
        
        else:
            control_input.cancel()

        control_deleting.cancel()
        control_editing.cancel()
        self.control_sessions.pop(index)


    async def author_timeout(self, ctx):

        while True:
            try:
                await self.client.wait_for('message', check=lambda m: m.author == ctx.author and not m.guild, timeout=120)
            except asyncio.TimeoutError:
                return await ctx.author.send("Control timed out.")


    async def control_editing(self, ctx):
        while True:
            message = await self.client.wait_for('message_edit', check=lambda before, after: not before.author.bot)
            message = message[1]

            if message.channel == ctx.channel:
                
                breakOut = False
                for session in self.control_sessions:
                    if session["channel"] == ctx.channel:

                        for index, both_messages in enumerate(session["messages"]):
                            channel_message, author_message = both_messages

                            # to convert finished task to message
                            if not isinstance(channel_message, discord.Message):
                                session["messages"][index][0] = channel_message = await channel_message

                            elif not isinstance(author_message, discord.Message):
                                session["messages"][index][1] = author_message = await author_message
                            if channel_message.id == message.id:

                                content = f"**{message.author.name}**:\n{message.content}"

                                # make sure message isn't too long
                                if len(content) > 2000:
                                    content = content[:2000]

                                asyncio.create_task( author_message.edit(content=content) )
                                breakOut = True
                                break
                    if breakOut:
                        break
            
            elif not message.guild and message.author == ctx.author:
                breakOut = False

                for session in self.control_sessions:

                    if session["author"] == ctx.author:

                        for index, both_messages in enumerate(session["messages"]):
                            channel_message, author_message = both_messages

                            # to convert finished task to message
                            if not isinstance(channel_message, discord.Message):
                                session["messages"][index][0] = channel_message = await channel_message

                            elif not isinstance(author_message, discord.Message):
                                session["messages"][index][1] = author_message = await author_message

                            if author_message.id == message.id:

                                asyncio.create_task( channel_message.edit(content=message.content) )
                                breakOut = True
                                break
                    if breakOut:
                        break
                            

                            
    async def control_deleting(self, ctx):

        while True:
            message = await self.client.wait_for('message_delete', check=lambda m: not m.author.bot)

            if message.channel == ctx.channel:
                
                breakOut = False
                for session in self.control_sessions:
                    if session["channel"] == ctx.channel:

                        for index, both_messages in enumerate(session["messages"]):
                            channel_message, author_message = both_messages

                            # to convert finished task to message
                            if not isinstance(channel_message, discord.Message):
                                session["messages"][index][0] = channel_message = await channel_message

                            elif not isinstance(author_message, discord.Message):
                                session["messages"][index][1] = author_message = await author_message

                            if channel_message.id == message.id:

                                asyncio.create_task( author_message.delete() )
                                session["messages"].pop(index)
                                breakOut = True
                                break
                    if breakOut:
                        break
            
            elif not message.guild and message.author == ctx.author:
                breakOut = False

                for session in self.control_sessions:

                    if session["author"] == ctx.author:

                        for index, both_messages in enumerate(session["messages"]):
                            channel_message, author_message = both_messages

                            # to convert finished task to message
                            if not isinstance(channel_message, discord.Message):
                                session["messages"][index][0] = channel_message = await channel_message

                            elif not isinstance(author_message, discord.Message):
                                session["messages"][index][1] = author_message = await author_message

                            if author_message.id == message.id:

                                asyncio.create_task( channel_message.delete() )
                                session["messages"].pop(index)
                                breakOut = True
                                break
                    if breakOut:
                        break

    async def control_input(self, ctx):
        while True:
            
            message = await self.client.wait_for('message', check=lambda m: not m.author.bot)

            if not message.guild and message.author == ctx.author:

                if "@everyone" in message.content or "@here" in message.content:
                    await message.author.send("You cannot ping that!")
                    continue

                # to make sure no roles are mentioned
                regex = re.compile("<@&.*>")
                matches = regex.findall(message.content)
                if matches:
                    await message.author.send("You cannot ping that!")
                    continue

                if message.content == ".stop":
                    return await message.author.send("You are no longer controlling me.")

                to_file_attachments = []
                for attachment in message.attachments:
                    to_file = await attachment.to_file()
                    to_file_attachments.append(to_file)

                channel_message_task = asyncio.create_task( ctx.send(message.content, files=to_file_attachments) )
                
                for session in self.control_sessions:
                    if session["channel"] == ctx.channel:
                        
                        session["messages"].append( [channel_message_task, message] )
                        break
            
            elif message.channel == ctx.channel:

                content = f"**{message.author.name}**:\n{message.content}"

                # make sure message isn't too long
                if len(content) > 2000:
                    content = content[:1999]

                to_file_attachments = []
                for attachment in message.attachments:
                    to_file = await attachment.to_file()
                    to_file_attachments.append(to_file)

                author_message_task = asyncio.create_task( ctx.author.send(content, files=to_file_attachments) )

                for session in self.control_sessions:
                    if session["author"] == ctx.author:
                        
                        session["messages"].append( [message, author_message_task] )
                        break

    
    @commands.command()
    async def sell(self, ctx, *, item=None):

        author = ctx.author

        if not author.premium_since:
            await ctx.send("You don't have __premium__. Get __premium__ by boosting the server!")
            return
        
        async with self.client.pool.acquire() as db:

            if not await db.jail_heist_check(ctx, ctx.author):
                return

            if not item: 
                await ctx.send("Incorrect command usage:\n`.sell item`")
                return

            items = await db.fetch('SELECT name, article, price FROM shop')

            item = item.lower()

            for shopitem in items:
                if item == shopitem[0]:
                    picked_item = shopitem
                    break

            else:
                await ctx.send(f"There is no such item called **{item}**.")
                return


            if item not in await db.get_member_val(author.id, 'items'):
                await ctx.send(f"You do not own {picked_item[1]}**{picked_item[0]}**.")
                return

            await db.remove_item(author.id, item)
            await ctx.send(f'**{author.name}** sold {picked_item[1]}**{picked_item[0]}** for ${picked_item[2]//2}.')

            money = await db.get_member_val(ctx.author.id, 'money')
            money += picked_item[2]//2
            await db.set_member_val(ctx.author.id, 'money', money)

            



def setup(client):
    client.add_cog(Premium(client))