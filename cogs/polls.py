# pylint: disable=import-error

import discord
from discord.ext import commands, tasks
import sqlite3
from sqlite3 import Error
import time
import os

# To import from different path
import sys
sys.path.insert(1 , os.getcwd())

from utils import bot_check, splittime, timestring, log_command


class Polls(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.polltracker.start() # noqa pylint: disable=no-member

    def cog_unload(self):
        self.polltracker.cancel() # noqa pylint: disable=no-member

    async def cog_check(self, ctx):
        return ctx.channel.id == self.client.adminChannel

    @tasks.loop(minutes=1)
    async def polltracker(self):
        conn = sqlite3.connect('./storage/databases/polls.db')
        c = conn.cursor()
        c.execute('SELECT * FROM polls')
        polls = c.fetchall()
        pollchannel = self.client.get_channel(698009727803719757)
        for poll in polls:
            message = await pollchannel.fetch_message(poll[2])    
            text = message.content
            text = text[::-1]
            if poll[1] < time.time() and poll[1] != 0:
                c.execute(f"DELETE FROM polls WHERE name = '{poll[0]}'")
                index = text.index('\n')
                text = text[index:]
                text = text[::-1]
                results = ""
                for reaction in message.reactions:
                    temp = f"{str(reaction.emoji)}: {reaction.count-1}   "
                    results = f"{results}{temp}"
                text = f'{text}**Poll closed. Results:**\n\n{results}'
                await message.edit(content=text)
                await message.clear_reactions()


            elif poll[1] > time.time() and poll[1] != 0:
                index = text.index('\n')
                text = text[index:]
                text = text[::-1]
                text = f"{text}**Time left: {minisplittime(int(int(poll[1]-time.time())/60))}**"
                await message.edit(content=text)
        conn.commit()
        conn.close()


    @commands.command()
    async def startpoll(self, ctx, option=None, timer=None, name=None):
        author = ctx.author
        pollchannel = self.client.get_channel(698009727803719757)
        #2\N{combining enclosing keycap} is 2 emoji and so on
        #\N{keycap ten} is 10 emoji
        
        if not option or not timer or not name:
            await ctx.send('Incorrect command usage:\n`.startpoll options timer name`')
            return

        try:
            option = int(option)
        except:
            await ctx.send('Enter a number from 1-9 for your poll options.')
            return
        if option < 1 or option > 9:
            await ctx.send('Enter a number from 1-9 for your poll options.')
            return

        timer = timestring(timer)
        if not timer:
            await ctx.send("Timer must be in this format: `1d 2h 3m 4s`")
            return
        timer //= 60

        conn = sqlite3.connect('./storage/databases/polls.db')
        c = conn.cursor()
        c.execute('SELECT name, time FROM polls')
        polls = c.fetchall()
        conn.close()
        names = []
        for x in polls:
            names.append(x[0])
        if name in names:
            await ctx.send(f'You already have a poll called {name}.')
            return
        def check(m):
            return m.channel == ctx.channel and m.author == author
        await ctx.send("Enter your message for the poll:")
        poll = await self.client.wait_for('message',check=check)
        content = poll.content
        await ctx.send(f"Poll made in {pollchannel.mention}.")
        guild = self.client.mainGuild
        pollping = guild.get_role(716818729987473408)
        if timer != 0:
            message = await pollchannel.send(f"{pollping.mention}\n`{name}:`\n\n{content}\n\n**Time left: {minisplittime(timer)}**")
        elif timer == 0:
            message = await pollchannel.send(f'{pollping.mention}\n`{name}:`\n\n{content}')
        if option != 1:
            for x in range(option):
                await message.add_reaction(f'{x+1}\N{combining enclosing keycap}')
        elif option == 1:
            await message.add_reaction('✅')
            await message.add_reaction('❌')
        conn = sqlite3.connect('./storage/databases/polls.db')
        c = conn.cursor()
        expires = int(time.time()) + timer*60
        if timer == 0:
            expires = 0
        c.execute(f"INSERT INTO polls (name, time, id) VALUES ('{name}', {expires}, {message.id})")
        conn.commit()
        conn.close()

    @commands.command()
    async def polllist(self, ctx):
        conn = sqlite3.connect('./storage/databases/polls.db')
        c = conn.cursor()
        c.execute('SELECT name, time FROM polls')
        polls = c.fetchall()
        conn.close()
        poll_list = []
        for x in polls:
            poll_list.append({'name':x[0],'time':x[1]})
        polltext = ""
        for x in poll_list:
            if x['time'] > 0:
                timeleft = minisplittime(int(int(x['time']-time.time())/60))
            else:
                timeleft = 'Infinite'

            temp = f"`{x['name']}`: {timeleft}"
            polltext += f"\n{temp}"
        try:
            await ctx.send(polltext)
        except:
            await ctx.send('There are no ongoing polls.')

    @commands.command()
    async def cancelpoll(self, ctx, name=None, *, reason=None):
        if not name:
            await ctx.send('Incorrect command usage:\n`.cancelpoll name (reason)`')
            return
        pollchannel = self.client.get_channel(698009727803719757)
        conn = sqlite3.connect('./storage/databases/polls.db')
        c = conn.cursor()
        c.execute('SELECT name, id FROM polls')
        polls = c.fetchall()
        conn.close()
        names = []
        pollinfo = []
        for x in polls:
            names.append(x[0])
            pollinfo.append({'name':x[0],'id':x[1]})
        if name not in names:
            await ctx.send(f'There is no poll called {name}.')
            return
        for poll in pollinfo:
            if poll['name'] == name:
                message = await pollchannel.fetch_message(poll['id'])
                conn = sqlite3.connect('./storage/databases/polls.db')
                c = conn.cursor()
                c.execute(f"DELETE FROM polls WHERE name = '{poll['name']}'")
                conn.commit()
                conn.close()
                break
        text = message.content
        text = text[::-1]
        index = text.index('\n')
        text = text[index:]
        text = text[::-1]
        if not reason:
            text = f'{text}**Poll cancelled.**'
        else:
            text = f'{text}**Poll cancelled:** {reason}'
        await message.edit(content=text)
        await message.clear_reactions()
        await ctx.send(f"{name} poll cancelled.")

    @commands.command()
    async def closepoll(self, ctx, name=None):
        if not name:
            await ctx.send('Incorrect command usage:\n`.closepoll name`')
            return
        pollchannel = self.client.get_channel(698009727803719757)
        conn = sqlite3.connect('./storage/databases/polls.db')
        c = conn.cursor()
        c.execute('SELECT name, id FROM polls')
        polls = c.fetchall()
        conn.close()
        names = []
        pollinfo = []
        for x in polls:
            names.append(x[0])
            pollinfo.append({'name':x[0],'id':x[1]})
        if name not in names:
            await ctx.send(f'There is no poll called {name}.')
            return
        for poll in pollinfo:
            if poll['name'] == name:
                message = await pollchannel.fetch_message(poll['id'])
                conn = sqlite3.connect('./storage/databases/polls.db')
                c = conn.cursor()
                c.execute(f"DELETE FROM polls WHERE name = '{poll['name']}'")
                conn.commit()
                conn.close()
                break
        text = message.content
        text = text[::-1]
        index = text.index('\n')
        text = text[index:]
        text = text[::-1]
        results = ""
        for reaction in message.reactions:
            temp = f"{str(reaction.emoji)}: {reaction.count-1}   "
            results = f"{results}{temp}"
        text = f'{text}**Poll closed. Results:**\n\n{results}'
        await message.edit(content=text)
        await message.clear_reactions()
        await ctx.send(f"{name} poll closed.")

    


    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.channel_id == 698009727803719757: # Poll channel
            if payload.user_id != self.client.user.id:
                pollchannel = self.client.get_channel(698009727803719757)
                message = await pollchannel.fetch_message(payload.message_id)
                for reaction in message.reactions:
                    if str(reaction.emoji) != str(payload.emoji):
                        await self.client.http.remove_reaction(payload.channel_id, payload.message_id, reaction.emoji, payload.user_id)



def setup(client):
    client.add_cog(Polls(client))