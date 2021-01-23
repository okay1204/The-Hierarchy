# pylint: disable=import-error, anomalous-backslash-in-string
import discord
from discord.ext import commands
import time
import os
import random
import asyncio
import sqlite3

# To import from different path
import sys
sys.path.insert(1 , os.getcwd())

from utils import bot_check, splittime, timestring, log_command

class Leveling(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.last_messages = {}

        asyncio.create_task(self.rank_leaderboard())

    async def cog_check(self, ctx):
        if ctx.channel.category.id != self.client.rightCategory:
            return False
        else:
            return True

    async def rank_leaderboard(self):

        channel = self.client.get_channel(746062853244715008)
        message = await channel.fetch_message(746063162708721815)

        embed = discord.Embed(color=0x3e41de, title="⭐ Rank Leaderboard ⭐")
        
        conn = sqlite3.connect('./storage/databases/hierarchy.db')
        c = conn.cursor()
        c.execute('SELECT id, level FROM members ORDER BY level DESC')
        users = c.fetchall()
        conn.close()

        guild = self.client.mainGuild
        users = list(filter(lambda x: guild.get_member(x[0]), users))

        for x in range(10):

            medal = ''
            if x == 0:
                medal = ' 🥇'
            elif x == 1:
                medal = ' 🥈'
            elif x == 2:
                medal = ' 🥉'

            embed.add_field(name='\_\_\_\_\_\_\_', value=f"{x+1}. <@{users[x][0]}>{medal} - {users[x][1]}", inline=False)
        
        await message.edit(embed=embed)



    @commands.Cog.listener()
    async def on_message(self, message):
        
        if not message.guild or message.author.bot: return

        elif message.content.startswith(('.level', '.rank')): return

        userid = str(message.author.id)

        counts = False


        if userid not in self.last_messages:
            self.last_messages[userid] = time.time()
            counts = True
        
        elif self.last_messages[userid] + 30 < time.time():
            self.last_messages[userid] = time.time()
            counts = True

        
        if counts:
            level = read_value(message.author.id, 'level')
            progress = read_value(message.author.id, ' progress')

            if level > 10:
                points = random.randint(1,3)
            else:
                randmin = 12 - level
                randmax = 15 - level

                points = random.randint(randmin, randmax)
            

            progress += points


            if progress >= 100:
                level += 1
                write_value(message.author.id, 'level', level)

                progress -= 100

                embed = discord.Embed(color=0x3e41de, title="⏫ Level Up!", description=f"Advanced to level {level} and earned $15! Keep going to unlock more features!")
                embed.set_author(name=message.author.name, icon_url=message.author.avatar_url_as(static_format="jpg"))

                await message.channel.send(embed=embed)

                money = read_value(message.author.id, 'money')
                money += 15
                write_value(message.author.id, 'money', money)
                

                asyncio.create_task(self.rank_leaderboard())




            write_value(message.author.id, 'progress', progress)

    @commands.command(aliases=["level"])
    async def rank(self, ctx, *, member:discord.Member=None):
        
        if not member:
            member = ctx.author
        
        else:
            if not await bot_check(self.client, ctx, member):
                return
        
        level = read_value(member.id, 'level')

        embed = discord.Embed(color=0x3e41de)
        embed.set_author(name=member.name, icon_url=member.avatar_url_as(static_format='jpg'))
        embed.add_field(name=f"Level {level}", value=f"{read_value(member.id, 'progress')}% of the way to level {level + 1}.")
        await ctx.send(embed=embed)

            






def setup(client):
    client.add_cog(Leveling(client))