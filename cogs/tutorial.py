# pylint: disable=import-error

import asyncio
import json
import random
import sqlite3
import time
import os
import datetime
from sqlite3 import Error

import discord
from discord.ext import commands
from discord.ext.commands import BadArgument, CommandNotFound, MaxConcurrencyReached

# To import from different path
import sys
sys.path.insert(1 , os.getcwd())

from utils import (read_value, write_value, update_total, leaderboard,
rolecheck, splittime, open_heist, bot_check, in_use, jail_heist_check, around,
remove_item, remove_use, add_item, write_heist, add_use)

class tutorial(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_message(self, message):
        # DM check
        if not message.guild:
            if message.content.lower() == "tutorial":
                for task in asyncio.all_tasks():
                    if str(task.get_name()) == f"tutorial {message.author.id}":
                        await message.channel.send('You already have a tutorial in progress.')
                        return
                asyncio.create_task(self.tutorial(message), name=f"tutorial {message.author.id}")

            
            if message.content.lower() == "cancel":
                for task in asyncio.all_tasks():
                    if str(task.get_name()) == f"tutorial {message.author.id}":
                        await message.channel.send('Cancelled tutorial.')
                        task.cancel()
                        return

    async def tutorial(self, message):

        dmchannel = message.channel
        category = self.client.get_channel(692949972764590160)
        channels = category.text_channels

        async def channel_check(channel):
            special_channels = [706953015415930941, 714585657808257095, 723945572708384768]
            if channel.id in special_channels:
                return False
            else:
                async for msg in channel.history(limit=1):
                    secondspast = int(datetime.datetime.utcnow().timestamp()-msg.created_at.timestamp())
                if secondspast <= 60:
                    return False
                else:
                    return True
                    
        acceptedChannels = []
        for channel in channels:
            check = await channel_check(channel)
            if check:
                acceptedChannels.append(channel)

        if len(acceptedChannels) == 0:
            await dmchannel.send('All bot command channels are busy right now, sorry! Try again later.')
            return
        
        channel = random.choice(acceptedChannels)
        await dmchannel.send(f"Tutorial started! You may cancel it by DMing me `cancel` at any time. Please head on over to {channel.mention}.")
        
        guild = self.client.get_guild(692906379203313695)
        author = guild.get_member(message.author.id)

        async with channel.typing():
            await asyncio.sleep(5)
        
        await channel.send(f"Welcome to The Hierarchy, {author.mention}! This is a game of collecting as much money as you can.")

        async with channel.typing():
            await asyncio.sleep(5)
        


        for role in author.roles:
            if role.id == 692952611141451787:
                guild_role = guild.get_role(692952611141451787) # Poor
                break
            elif role.id == 692952792016355369:
                guild_role = guild.get_role(692952792016355369) # Middle
                break
            elif role.id == 692952919947083788:
                guild_role = guild.get_role(692952919947083788) # Rich
                break

        rolemessage = await channel.send('_ _')
        await rolemessage.edit(content=f"First off, let's talk about your role. You currently have the {guild_role.mention} role. This role signifies how rich you are compared to the average amount of money in the server.")

        async with channel.typing():
            await asyncio.sleep(10)

        await channel.send("Let's get you started with the basics.")

        client_member = guild.get_member(self.client.user.id)

        async with channel.typing():
            await asyncio.sleep(3)

        if read_value(author.id, 'workc') < time.time() and read_value(author.id, 'jailtime') < time.time():        
            canWork = True

        elif read_value(author.id, 'workc') >= time.time():
            await channel.send("Hm.. you already seem to have used the `.work` command. Since you already know about it, let's move on then.")
            canWork = False
        else:
            await channel.send("Well, it looks like you're in jail. It looks like we will have to skip majority of the tutorial.")
            canWork = False

        
        if canWork: 

            await channel.send("Start off by typing `.work`. Be ready though, there will be some minigames coming your way.")

            while True:
                try:
                    message = await self.client.wait_for('message', check=lambda x: x.author == author and x.guild == guild, timeout=60)
                except asyncio.TimeoutError:
                    await channel.send("Tutorial cancelled due to inactivity.")
                    return
                if message.content == '.work' or message.content.startswith('.work '):
                    channel = message.channel
                    break

            while True:
                try:
                    message = await self.client.wait_for('message', check=lambda x: x.author == client_member and x.channel == channel, timeout=60)
                except asyncio.TimeoutError:
                    await channel.send("Hmm... something went wrong. Please start the tutorial again.")
                    return
                if 'worked and' in message.content:
                    break

        async with channel.typing():
            await asyncio.sleep(5)
        
        await channel.send("You can check your balance with `.balance`. Try that now.")

        while True:
            try:
                message = await self.client.wait_for('message', check=lambda x: x.author == author and x.guild == guild, timeout=60)
            except asyncio.TimeoutError:
                await channel.send("Tutorial cancelled due to inactivity.")
                return
            if message.content == '.bal' or message.content == '.balance':
                channel = message.channel
                break

        async with channel.typing():
            await asyncio.sleep(3)

        await channel.send("Next, let's steal from someone!")

        async with channel.typing():
            await asyncio.sleep(3)

        if read_value(author.id, 'stealc') < time.time() and read_value(author.id, 'jailtime') < time.time():        
            canSteal = True

        elif read_value(author.id, 'stealc') >= time.time():
            await channel.send("Hm.. you already seem to have used the `.steal` command. Since you already know about it, let's move on then.")
            canSteal = False
        else:
            await channel.send("Well, it looks like you're in jail. Perhaps you already tried to steal from someone and got jailed already?")
            canSteal = False

        if canSteal:
            await channel.send("First, we will have to see who is in your place range. To do this, use `.around`.")
            while True:
                try:
                    message = await self.client.wait_for('message', check=lambda x: x.author == author and x.guild == guild, timeout=60)
                except asyncio.TimeoutError:
                    await channel.send("Tutorial cancelled due to inactivity.")
                    return
                if message.content == '.around' or message.content.startswith('.around '):
                    channel = message.channel
                    break
            
            async with channel.typing():
                await asyncio.sleep(8)

            image = discord.File('./storage/images/stealinfo.png')
            await channel.send("When stealing, you can only steal from those that are up to 3 places above you or up to 3 places below you. Refer to this diagram:", file=image)
            
            async with channel.typing():
                await asyncio.sleep(15)


            aroundbug = discord.File('./storage/images/aroundbug.png')
            await channel.send("**If this is what you saw when you did `.around`, or you saw something like @invalid-user, it is a common mobile bug. Try using `.aroundm` instead.**", file=aroundbug)

            async with channel.typing():
                await asyncio.sleep(12)

            await channel.send("Now, let's try it out!")

            async with channel.typing():
                await asyncio.sleep(3)

            #Quick checks to make sure they didn't spoof the system
            spoofed = False
            if read_value(author.id, 'stealc') >= time.time():
                await channel.send("You already used `.steal`... what a shame.")
                spoofed = True
            elif read_value(author.id, 'jailtime') >= time.time():
                await channel.send("Well, it looks like you're in jail. Perhaps you already tried to steal from someone and got jailed already?")
                spoofed = True
            
            if not spoofed:
                await channel.send(f"Use `.steal @mention amount` to steal from someone. Make sure you replace `@mention` with the member you want to steal from, and `amount` with the amount you want to steal.\n\n***Wait!*** When you choose an amount to steal, you may choose a number from 1-200 (as long as the person you are stealing from has enough cash). However, the more you try to steal, the higher chance you have of being jailed.\n\nAn example of this command is:\n.steal {client_member.mention} 100\n\nTry out this command now (not the example!).")
                breakOut = False
                while True:
                    try:
                        message = await self.client.wait_for('message', check=lambda x: x.author == author and x.guild == guild, timeout=120)
                    except asyncio.TimeoutError:
                        await channel.send("Tutorial cancelled due to inactivity.")
                        return
                    if message.content.startswith('.steal '):
                        channel = message.channel
                        while True:
                            try:
                                message = await self.client.wait_for('message', check=lambda x: x.author == client_member and x.channel == channel, timeout=60)
                            except asyncio.TimeoutError:
                                await channel.send("Hmm... something went wrong. Please start the tutorial again.")
                                return
                            if author.name in message.content:
                                breakOut = True
                            break

                    if breakOut:
                        break
            
        async with channel.typing():
            await asyncio.sleep(5)

        await channel.send(f"And that's about it! Of course, these are only the basics to get you started. However, there is a shop, fee collection, banking system, and so much more! Feel free to explore these on your own. Looking through {self.client.commandsChannel.mention} and {self.client.gameInfoChannel.mention} will help you a lot.\n\n*Please consider boosting the server, it will also grant you some premium features such as boosting time!*")

        async with channel.typing():
            await asyncio.sleep(15)

        await channel.send("Have fun, and good luck!")
    


def setup(client):
    client.add_cog(tutorial(client))