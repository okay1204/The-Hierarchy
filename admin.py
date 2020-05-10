import discord
from discord.ext import commands, tasks
import json
import time
from utils import *


class admin(commands.Cog):

    def __init__(self, client):
        self.client = client



    @commands.command()
    @commands.check(adminCheck)
    async def poll(self, ctx, option=None, timer=None, *, name=None):
        author = ctx.author
        pollchannel = self.client.get_channel(698009727803719757)
        #2\N{combining enclosing keycap} is 2 emoji and so on
        #\N{keycap ten} is 10 emoji
        if not option:
            await ctx.send("Enter a poll option.")
            return
        if not timer:
            await ctx.send("Enter a poll duration in minutes.")
            return
        if not name:
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
        
        def check(m):
            return m.channel == ctx.channel and m.author == author
        await ctx.send("Enter your message for the poll:")
        poll = await self.client.wait_for('message',check=check)
        content = poll.content
        await ctx.send(f"Poll made in {pollchannel.mention}.")
        if timer != 0:
            message = await pollchannel.send(f"`{name}:`\n\n{content}\n\n**Time left: {minisplittime(timer)}**")
        elif timer == 0:
            message = await pollchannel.send(f'`{name}:`\n\n{content}')
        if option != 1:
            for x in range(option):
                await message.add_reaction(f'{x+1}\N{combining enclosing keycap}')
        elif option == 1:
            await message.add_reaction('✅')
            await message.add_reaction('❌')
        conn = sqlite3.connect('hierarchy.db')
        c = conn.cursor()
        expires = int(time.time()) + timer*60
        c.execute(f"INSERT INTO polls (name, time, id) VALUES ('{name}', {expires}, {poll.id})")
        conn.commit()
        conn.close()


def setup(client):
    client.add_cog(admin(client))
