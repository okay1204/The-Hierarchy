# pylint: disable=import-error, anomalous-backslash-in-string


import asyncio
import random
import json
import time
import os
import datetime
import aiohttp
import string
import difflib
import re
import praw
import discord

from discord.ext import commands, tasks
from discord.ext.commands import BadArgument, CommandNotFound, MaxConcurrencyReached

# To import from different path
import sys
sys.path.insert(1 , os.getcwd())

from utils import bot_check, splittime, timestring, log_command
import authinfo



class Fun(commands.Cog):

    def __init__(self, client):
        self.client = client

        self.scramble_cooldowns = {}


    async def cog_check(self, ctx):

        if ctx.command.name == "meme":
            return ctx.channel.id == 759162810906312725

        if ctx.channel.category.id != self.client.rightCategory:
            return False
        else:
            return True

    @commands.Cog.listener()
    async def on_message(self, message):
        counting = self.client.get_channel(721444345353470002)
        sentences = self.client.get_channel(721475839153143899)
        scramble = self.client.get_channel(759219821103153182)

        if message.author.bot: return

        # Endless counting channel

        if message.channel == counting:

            #Grabing last number
            async with self.client.pool.acquire() as db:
                currentnumber = await db.fetchval('SELECT number FROM fun.counting;')


                nextnumber = currentnumber + 1
                if message.content.lower() == 'next':
                    return await counting.send(f"**{nextnumber}**")
                    
                elif message.content.startswith(('.warn', '.kick', '.ban', '.report')):
                    return

                elif str(nextnumber) in message.content:

                    #Writing number
                    await db.execute("UPDATE fun.counting SET number = $1;", nextnumber)
                    await db.execute("UPDATE fun.counting SET lastmsgid = $1;", message.id)

                else:
                    await message.delete()
                    await counting.send(f"Your message must have the next number in it, {message.author.mention}.", delete_after=3)

                return
        
        
        #For sentences
        elif message.channel == sentences:



            if message.content.startswith(('.warn', '.kick', '.ban', '.report')):
                return

            elif " " in message.content or "\n" in message.content:
                await message.delete()
                await sentences.send(f"You can't send two words in one message, {message.author.mention}.", delete_after=3)
                return


            async with self.client.pool.acquire() as db:
                prevauthor = await db.fetchval('SELECT prevauthor FROM fun.sentences;')


                if message.author.id == prevauthor:
                    await message.delete()
                    await sentences.send(f"You can't send two messages in a row, {message.author.mention}.", delete_after=3)

                else:
                    #Writing data
                    await db.execute("UPDATE fun.sentences SET prevauthor = $1;", message.author.id)
                    await db.execute("UPDATE fun.sentences SET lastmsgid = $1;", message.id)
                    
                return


        elif message.channel == scramble:

            if message.author.id in self.scramble_cooldowns and self.scramble_cooldowns[message.author.id] > time.time():
                await message.delete()
                await scramble.send(f"You must wait {self.scramble_cooldowns[message.author.id] - int(time.time())} seconds before you can type again, {message.author.mention}.", delete_after=3)
                return


            done = False
            if message.content.lower().endswith(" - done"):
                done = True
                # removes the done part
                message.content = message.content[:list(message.content).index("-")]

                # get rid of the final space
                message.content = message.content.strip()


            if " " in message.content or "\n" in message.content or "-" in message.content and not done: 
                await message.delete()
                await scramble.send(f"You cannot use spaces in the word, {message.author.mention}.", delete_after=3)
                return
            
            async with self.client.pool.acquire() as db:
                prev_word = await db.fetchval("SELECT word FROM fun.scramble;")

                if prev_word == message.content and not done:
                    await message.delete()
                    await scramble.send(f"You cannot repeat the same thing, {message.author.mention}.", delete_after=3)
                    return

                elif len(prev_word) == len(message.content): # changed a letter

                    found_difference = False

                    for index, letter in enumerate(prev_word):

                        if letter != message.content[index]:

                            if found_difference:
                                await message.delete()
                                await scramble.send(f"Check the pins how how to play, {message.author.mention}.", delete_after=3)
                                return
                            
                            found_difference = True
                        
                    if not done:
                        await db.execute("UPDATE fun.scramble SET word = $1, lastmsgid = $2", message.content, message.id)


                elif len(prev_word) - len(message.content) == 1: # removed a letter
                    
                    for x in range(len(prev_word)):
                        temp = list(prev_word)
                        temp.pop(x)
                        if "".join(temp) == message.content:
                            break
                    
                    else:
                        await message.delete()
                        await scramble.send(f"Check the pins how how to play, {message.author.mention}.", delete_after=3)
                        return

                    if not done:
                        await db.execute("UPDATE fun.scramble SET word = $1, lastmsgid = $2", message.content, message.id)


                elif len(prev_word) - len(message.content) == -1: # added a letter
                    
                    for x in range(len(message.content)):

                        temp = list(message.content)
                        temp.pop(x)

                        if "".join(temp) == prev_word:
                            break
                    
                    else:
                        await message.delete()
                        await scramble.send(f"Check the pins how how to play, {message.author.mention}.", delete_after=3)
                        return

                    if not done:
                        await db.execute("UPDATE fun.scramble SET word = $1, lastmsgid = $2", message.content, message.id)

                
                else:
                    await message.delete()
                    await scramble.send(f"Check the pins how how to play, {message.author.mention}.", delete_after=3)
                    return

                
                self.scramble_cooldowns[message.author.id] = int(time.time()) + 10


                if done:
                    await message.add_reaction("✅")


                    # generate random word
                    word = ""
                    for x in range(random.randint(4, 10)): word += random.choice(string.ascii_lowercase)
                    
                    sent_message = await scramble.send(word)

                    await db.execute("UPDATE fun.scramble SET word = $1, lastmsgid = $2;", word, sent_message.id)
                    return


    @commands.Cog.listener()
    async def on_raw_message_edit(self, payload):

        counting = 721444345353470002
        sentences = 721475839153143899
        scramble = 759219821103153182

        if payload.channel_id == counting:
            counting = self.client.get_channel(721444345353470002)
            message = await counting.fetch_message(payload.message_id)

            #Grabing data
            async with self.client.pool.acquire() as db:
                currentnumber, lastmsgid = await db.fetchrow('SELECT number, lastmsgid FROM fun.counting;')

            if str(currentnumber) not in message.content and payload.message_id == lastmsgid:
                await message.delete()


        elif payload.channel_id == sentences:
            sentences = self.client.get_channel(sentences)
            message = await sentences.fetch_message(payload.message_id)

            #Grabing data from here
            async with self.client.pool.acquire() as db:
                lastmsgid = await db.fetchval('SELECT lastmsgid FROM fun.sentences;')

            if " " in message.content or "\n" in message.content and payload.message_id == lastmsgid:
                await message.delete()


        elif payload.channel_id == scramble:
            scramble = self.client.get_channel(scramble)

            async with self.client.pool.acquire() as db:

                lastmsgid = await db.fetchval('SELECT lastmsgid FROM fun.scramble;')

                if payload.message_id == lastmsgid:
                    message = await scramble.fetch_message(payload.message_id)
                    await message.delete()

                    async for message in scramble.history():
                        if not message.author.bot and not message.content.endswith(' - done'):
                            word, lastmsgid = message.content, message.id
                            break

                    await db.execute('UPDATE scramble SET word = $1, lastmsgid = $2', word, lastmsgid)



    @commands.Cog.listener()
    async def on_raw_message_delete(self, payload):


        counting = 721444345353470002
        sentences = 721475839153143899
        scramble = 759219821103153182

        if payload.channel_id == counting:

            counting = self.client.get_channel(counting)

            #Grabing last message
            async with self.client.pool.acquire() as db:

                lastmsgid = await db.execute('SELECT lastmsgid FROM fun.counting;')

                if payload.message_id == lastmsgid:
                    async for message in counting.history(limit=100):
                        if message.content.lower() == "next" or message.author.bot or message.content.startswith(('.warn', '.kick', '.ban', '.report')):
                            continue
                        else:
                            newmsg = message
                            break


                    await db.execute('UPDATE fun.counting SET lastmsgid = $1', newmsg.id)
                    
                    await db.execute('UPDATE fun.counting SET number = number - 1')

                    


        elif payload.channel_id == sentences:
            sentences = self.client.get_channel(sentences)
            #Grabing last message

            async with self.client.pool.acquire() as db:
                lastmsgid = await db.fetchval('SELECT lastmsgid FROM fun.sentences;')


                if payload.message_id == lastmsgid:
                    async for message in sentences.history(limit=100):
                        if message.author.bot or message.content.startswith(('.warn', '.kick', '.ban', '.report')):
                            continue
                        else:
                            newmsg = message
                            break
                        
                    await db.execute('UPDATE sentences SET lastmsgid = $1, prevauthor = $2', newmsg.id, newmsg.author.id)

        elif payload.channel_id == scramble:

            scramble = self.client.get_channel(scramble)

            async with self.client.pool.acquire() as db:

                lastmsgid = await db.fetchval('SELECT lastmsgid FROM fun.scramble')

                if payload.message_id == lastmsgid:

                    async for message in scramble.history():
                        if not message.author.bot and not message.content.endswith(' - done'):
                            word, lastmsgid = message.content, message.id
                            break

                    await db.execute('UPDATE fun.scramble SET word = $1, lastmsgid = $2', word, lastmsgid)
                




    @commands.command()
    @commands.max_concurrency(1, per=commands.BucketType.channel)
    async def meme(self, ctx):     

        async with ctx.channel.typing():
            
            try:
                sub = self.client.reddit.subreddit('dankmemes')
            except:
                # reconnect to reddit because it auto disconnects after a while

                self.client.reddit = praw.Reddit(
                    client_id = os.environ.get("reddit_client_id"),
                    client_secret = os.environ.get("reddit_client_secret"),
                    password = os.environ.get("reddit_password"),
                    username = os.environ.get("reddit_username"),
                    user_agent = os.environ.get("reddit_user_agent")
                )

                sub = self.client.reddit.subreddit('dankmemes')
                
            post = random.choice(list(sub.hot()))

            post_url = f"https://www.reddit.com/r/dankmemes/comments/{post.id}"

            title = post.title[:256]        

            embed = discord.Embed(
                title = title,
                url = post_url
            )

            embed.set_image(url=post.url)

            embed.set_footer(
                text = f"{post.num_comments} 💬 | {post.score} 👍"
            )

        await ctx.send(embed=embed)


def setup(client):
    client.add_cog(Fun(client))