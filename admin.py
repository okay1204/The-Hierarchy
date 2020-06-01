import discord
from discord.ext import commands
import json
import time
import sqlite3
from sqlite3 import Error
from utils import *


class admin(commands.Cog):

    def __init__(self, client):
        self.client = client



    @commands.command()
    @commands.check(adminCheck)
    async def startpoll(self, ctx, option=None, timer=None, name=None):
        author = ctx.author
        pollchannel = self.client.get_channel(698009727803719757)
        #2\N{combining enclosing keycap} is 2 emoji and so on
        #\N{keycap ten} is 10 emoji
        if option == None:
            await ctx.send("Enter a poll option.")
            return
        if timer == None:
            await ctx.send("Enter a poll duration in minutes.")
            return
        if name == None:
            await ctx.send("Enter a poll name.")
            return
        try:
            option = int(option)
        except:
            await ctx.send('Enter a valid number from 1-9 for your poll options.')
            return
        if option < 1 or option > 9:
            await ctx.send('Enter a valid number from 1-9 for your poll options.')
            return
        try:
            timer = int(timer)
        except:
            await ctx.send('Enter a valid amount of minutes.')
            return
        if option < 0:
            await ctx.send('Enter a valid amount of minutes.')
            return
        conn = sqlite3.connect('hierarchy.db')
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
        guild = self.client.get_guild(692906379203313695)
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
        conn = sqlite3.connect('hierarchy.db')
        c = conn.cursor()
        expires = int(time.time()) + timer*60
        if timer == 0:
            expires = 0
        c.execute(f"INSERT INTO polls (name, time, id) VALUES ('{name}', {expires}, {message.id})")
        conn.commit()
        conn.close()
    
    @commands.command()
    @commands.check(adminCheck)
    async def polllist(self, ctx):
        conn = sqlite3.connect('hierarchy.db')
        c = conn.cursor()
        c.execute('SELECT name, time FROM polls')
        polls = c.fetchall()
        conn.close()
        poll_list = []
        for x in polls:
            poll_list.append({'name':x[0],'time':x[1]})
        polltext = ""
        for x in poll_list:
            temp = f"`{x['name']}`: {minisplittime(int(int(x['time']-time.time())/60))}"
            polltext = f"{polltext}\n{temp}"
        try:
            await ctx.send(polltext)
        except:
            await ctx.send('There are no ongoing polls.')

    @commands.command()
    @commands.check(adminCheck)
    async def cancelpoll(self, ctx, name=None, *, reason=None):
        if not name:
            await ctx.send('Enter the name of the poll you want to cancel.')
            return
        pollchannel = self.client.get_channel(698009727803719757)
        conn = sqlite3.connect('hierarchy.db')
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
                conn = sqlite3.connect('hierarchy.db')
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
    @commands.check(adminCheck)
    async def closepoll(self, ctx, name=None):
        if not name:
            await ctx.send('Enter the name of the poll you want to close.')
            return
        pollchannel = self.client.get_channel(698009727803719757)
        conn = sqlite3.connect('hierarchy.db')
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
                conn = sqlite3.connect('hierarchy.db')
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


def setup(client):
    client.add_cog(admin(client))
