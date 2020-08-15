# pylint: disable=import-error
import discord
from discord.ext import commands
import time
import os
import random

# To import from different path
import sys
sys.path.insert(1 , os.getcwd())

from utils import read_value, write_value, bot_check

class leveling(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.last_messages = {}

    async def cog_check(self, ctx):
        if ctx.channel.category.id != self.client.rightCategory:
            return False
        else:
            return True

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

                embed = discord.Embed(color=0x3e41de, title="Level up", description=f"Advanced to level {level}! Keep going to unlock more features!")
                embed.set_author(name=message.author.name, icon_url=message.author.avatar_url_as(static_format="jpg"))

                await message.channel.send(embed=embed)


            write_value(message.author.id, 'progress', progress)

    @commands.command(aliases=["level"])
    async def rank(self, ctx, member:discord.Member=None):
        
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
    client.add_cog(leveling(client))