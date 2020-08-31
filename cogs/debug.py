# pylint: disable=import-error

import discord
from discord.ext import commands
import json
import sqlite3
import os
from sqlite3 import Error

# To import from different path
import sys
sys.path.insert(1 , os.getcwd())

from utils import (read_value, write_value, update_total, leaderboard,
rolecheck, splittime, open_heist, bot_check, in_use, jail_heist_check, around,
remove_item, remove_use, add_item, write_heist, add_use)

class debug(commands.Cog):

    def __init__(self, client):
        self.client = client

    async def cog_check(self, ctx):
        if ctx.channel.id == self.client.adminChannel:
            return True
        else:
            return False

    @commands.command()
    async def online(self, ctx):
        guild = self.client.mainGuild
        channel = self.client.get_channel(698384786460246147)
        message = await channel.fetch_message(698775210173923429)
        embed = discord.Embed(color=0x42f57b)
        botuser = guild.get_member(self.client.user.id)
        botuser = botuser.avatar_url_as(static_format='jpg',size=256)
        embed.set_author(name="Bot ready to use.",icon_url=botuser)
        await message.edit(embed=embed)
        await ctx.send("Status updated to online.")
        await self.client.change_presence(status=discord.Status.online,activity=discord.Game(name='with money'))

    @commands.command()
    async def offline(self, ctx):
        guild = self.client.mainGuild
        channel = self.client.get_channel(698384786460246147)
        message = await channel.fetch_message(698775210173923429)
        embed = discord.Embed(color=0xff5254)
        botuser = guild.get_member(self.client.user.id)
        botuser = botuser.avatar_url_as(static_format='jpg',size=256)
        embed.set_author(name="Bot under development.",icon_url=botuser)
        await message.edit(embed=embed)
        await ctx.send("Status updated to offline.")
        await self.client.change_presence(status=discord.Status.dnd, activity=discord.Game(name='UNDER DEVELOPMENT'))

    @commands.command()
    async def mode(self, ctx, mode=''):

        mode = mode.lower()
        allowed_modes = ['normal', 'event']

        if mode not in allowed_modes:
            await ctx.send(f"Incorrect command usage:\n`.mode {'/'.join(allowed_modes)}`")
            return

        with open('./storage/jsons/mode.json','w') as f: 
            json.dump(mode, f, indent=2)

        await ctx.send(f"Mode successfully set to `{mode}`.")
    
    @commands.command()
    async def db(self, ctx, filename=None, *, command=None):

        if not filename or not command:
            await ctx.send("Incorrect command usage:\n`.db file dbcommand`.")
            return

        try:
            conn = sqlite3.connect(f'./storage/databases/{filename}.db')
            c = conn.cursor()
            c.execute(command)
            output = c.fetchall()
            conn.commit()
            conn.close()

        except Exception as error:
            
            try:
                conn.close()
            except:
                pass

            await ctx.send(f"Error:\n```{error}```")
        
        else:
            if output:
                output = str(output)
                if len(output) + 2 > 2000:
                    await ctx.send("Output too long to display.")
                else:
                    await ctx.send(f"`{output}`")
            else:
                await ctx.send(f"Command successfully executed.")

    @commands.command()
    async def json(self, ctx, *, filename=None):

        if not filename:
            await ctx.send("Incorrect command usage:\n`.json filename`.")
            return

        try:
            with open(f'./storage/jsons/{filename}.json') as f:
                output = json.load(f)

        except Exception as error:

            await ctx.send(f"Error:\n```{error}```")
        
        else:
            output = json.dumps(output, indent=2)

            if len(output) + 2 > 2000:
                await ctx.send("Output too long to display.")
            else:
                await ctx.send(f"```{output}```")

    @commands.command()
    async def shopupdate(self, ctx):

        conn = sqlite3.connect('./storage/databases/shop.db')
        c = conn.cursor()
        c.execute('SELECT name, price, desc, emoji FROM shop')
        shopitems = c.fetchall()
        conn.close()

        embed = discord.Embed(color=0x30ff56, title='Shop')

        x = 1
        for name, price, desc, emoji in shopitems:

            embed.add_field(name=f'{x}. ${price} - {name.capitalize()} {emoji}', value=desc, inline=False)

            x += 1

        shopchannel = self.client.get_channel(702654620291563600)
        message = await shopchannel.fetch_message(740680266086875243)
        await message.edit(embed=embed)

        await ctx.send("Shop successfully updated.")

    @commands.command()
    async def money(self, ctx, member: discord.Member=None, add=None):

        if not member or not add:
            await ctx.send("Incorrect command usage:\n`.money member +amount` or `.money member -amount`")
            return

        if not add.startswith('+'):
            await ctx.send("Incorrect command usage:\n`.money member +amount` or `.money member -amount`")
            return

        try:
            add = int(add)
        except:
            await ctx.send("Incorrect command usage:\n`.money member +amount` or `.money member -amount`")
            return

        
        money = read_value(member.id, 'money')
        money += add
        write_value(member.id, 'money', money)
        update_total(member.id)

        if add >= 0:
            await ctx.send(f"Added ${add} to **{member.name}**'s balance.")
        else:
            await ctx.send(f"Subtracted ${add} from **{member.name}**'s balance.")

        await rolecheck(self.client, member.id)
        await leaderboard(self.client)
        


    
def setup(client):
    client.add_cog(debug(client))
