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

from utils import (read_value, write_value, leaderboard,
rolecheck, splittime, bot_check, in_use, jail_heist_check, around,
remove_item, remove_use, add_item, add_use)

class Tutorial(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_message(self, message):
        # DM check
        if not message.guild:

            if self.client.get_cog("premium"):
                for session in self.client.get_cog("premium").control_sessions:
                    if session["author"] == message.author:
                        return

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

        async with channel.typing():
            await asyncio.sleep(3)


        if read_value(author.id, 'job'):
            await channel.send("You seem to already have applied for a job. Let's move on then.")
            canApply = False
            canWork = True

        elif (applyc := read_value(author.id, 'applyc')) > time.time():
            await channel.send(f"Looks like you can't apply for a job for another {splittime(applyc)}. Let's skip working then.")
            canApply = canWork = False

        else:
            canApply = canWork = True


        if canApply:

            await channel.send(f"To start working, you will have to apply for a job. Type `.jobs` to see a list of jobs.")


            # prompting for .jobs command
            while True:
                try:
                    message = await self.client.wait_for('message', check=lambda x: x.author == author and x.guild == guild, timeout=60)
                except asyncio.TimeoutError:
                    await channel.send("Tutorial cancelled due to inactivity.")
                    return
                if message.content == '.jobs' or message.content.startswith('.jobs '):
                    channel = message.channel
                    break

            while True:
                try:
                    message = await self.client.wait_for('message', check=lambda x: x.author == guild.me and x.channel == channel, timeout=60)
                except asyncio.TimeoutError:
                    await channel.send("Hmm... something went wrong. Please start the tutorial again.")
                    return
                if message.embeds:
                    if message.embeds[0].title == "Jobs":
                        break

            async with channel.typing():
                await asyncio.sleep(2)

            spoofed = False
            if read_value(author.id, 'applyc') > time.time() or read_value(author.id, 'job'):
                await channel.send(f"Looks like you just applied for a job... Let's skip working then.")
                spoofed = True
                canWork = False
            elif read_value(author.id, 'jailtime') > time.time():
                await channel.send(f"Well it looks like you just got yourself in jail. Let's skip working then.")
                spoofed = True
                canWork = False

            if not spoofed:
                await channel.send("The only two jobs that do not require a major to apply for are the **Garbage Collector** and the **Streamer**. Go ahead and apply for whichever job you like, based on the stats, using `.apply`.")
            
            breakOut = False
            while True:
                while True:
                    try:
                        message = await self.client.wait_for('message', check=lambda x: x.author == author and x.guild == guild, timeout=120)
                    except asyncio.TimeoutError:
                        await channel.send("Tutorial cancelled due to inactivity.")
                        return
                    if message.content == '.apply' or message.content.startswith('.apply '):
                        channel = message.channel
                        break

                while True:
                    try:
                        message = await self.client.wait_for('message', check=lambda x: x.author == guild.me and x.channel == channel, timeout=60)
                    except asyncio.TimeoutError:
                        await channel.send("Hmm... something went wrong. Please start the tutorial again.")
                        return
                    if message.content.startswith('You have successfully recieved the job'):
                        breakOut = True
                        break
                    else:
                        break
                if breakOut:
                    break

            async with channel.typing():
                await asyncio.sleep(3)

            await channel.send(f"Now that you have a job, you can start working. ***But wait!***")

            async with channel.typing():
                await asyncio.sleep(3)

            
        
        if canWork:
            if read_value(author.id, 'workc') >= time.time():
                
                async with channel.typing():
                    await asyncio.sleep(4)

                await channel.send("Hm.. you already seem to have used the `.work` command. Since you already know about it, let's move on then.")
                canWork = False
            elif read_value(author.id, 'jailtime') >= time.time():

                async with channel.typing():
                    await asyncio.sleep(4)

                await channel.send("Well, it looks like you're in jail. It looks like we will have to skip the majority of the tutorial.")
                canWork = False

        breakOut = False
        if canWork:

            await channel.send(f"When you work, a bunch of minigames are sent your way. These minigames may be a little complex at first. You may use the `.practice` command as many times as you like to practice these minigames **without penalty**.\nGo ahead and practice as many times as you like with `.practice`, and when you are ready, use `.work` to start making money.")

            while True:

                while True:
                    try:
                        message = await self.client.wait_for('message', check=lambda x: x.author == author and x.guild == guild, timeout=60)
                    except asyncio.TimeoutError:
                        await channel.send("Tutorial cancelled due to inactivity.")
                        return
                    if message.content == '.work' or message.content.startswith('.work '):
                        channel = message.channel
                        minigame_type = "work"
                        break
                    elif message.content == '.practice' or message.content.startswith('.work '):
                        channel = message.channel
                        minigame_type = "practice"
                        break

                while True:
                    try:
                        message = await self.client.wait_for('message', check=lambda x: x.author == guild.me and x.channel == channel, timeout=60)
                    except asyncio.TimeoutError:
                        await channel.send("Hmm... something went wrong. Please start the tutorial again.")
                        return
                    
                    if minigame_type == "practice" and message.content.startswith(f"**{author.name}** practiced as "):
                        await channel.send(f"Use `.practice` to practice again, and type `.work` when you're ready!")
                        break

                    elif minigame_type == "work" and message.content.startswith(f"💰 **{author.name}** worked as "):
                        breakOut = True
                        break

                
                if breakOut:
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
                await channel.send(f"Use `.steal member amount` to steal from someone. Make sure you replace `member` with the member you want to steal from, and `amount` with the amount you want to steal.\n\n***Wait!*** When you choose an amount to steal, you may choose a number from 1-200 (as long as the person you are stealing from has enough cash). However, the more you try to steal, the higher chance you have of being jailed.\n\nAn example of this command is:\n.steal {guild.me.mention} 100\n\nTry out this command now. (Not the example!)")
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
                                message = await self.client.wait_for('message', check=lambda x: x.author == guild.me and x.channel == channel, timeout=60)
                            except asyncio.TimeoutError:
                                await channel.send("Hmm... something went wrong. Please start the tutorial again.")
                                return
                            if author.name in message.content:
                                breakOut = True
                            elif message.content == 'This user does not have that much money in cash.':
                                await asyncio.sleep(2)
                                await channel.send("This user probably does not have enough money, or they are keeping their money in their bank. Don't worry about the bank for now, but try to steal from someone else. You can use `.balance member` to check the balance of another user.")
                            break

                    if breakOut:
                        break #TODO clarify that user has money in bank
            
        async with channel.typing():
            await asyncio.sleep(5)

        await channel.send(f"And that's about it! Of course, these are only the basics to get you started. However, there is a shop, fee collection, banking system, and so much more! Feel free to explore these on your own. Looking through {self.client.commandsChannel.mention} and {self.client.gameInfoChannel.mention} will help you a lot.\n\n*Please consider boosting the server, it will also grant you some premium features such as boosting time!*")

        async with channel.typing():
            await asyncio.sleep(15)

        await channel.send("Have fun, and good luck!")
    


def setup(client):
    client.add_cog(Tutorial(client))