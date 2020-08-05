# pylint: disable=import-error

import discord
from discord.ext import commands
import json
import time
import sqlite3
import os
from sqlite3 import Error
from collections import Counter

# To import from different path
import sys
sys.path.insert(1 , os.getcwd())

from utils import (read_value, write_value, update_total, leaderboard,
rolecheck, splittime, open_heist, bot_check, in_use, jail_heist_check, around,
remove_item, remove_use, add_item, write_heist, add_use)


class info(commands.Cog):

    def __init__(self, client):
        self.client = client

    async def cog_check(self, ctx):
        if ctx.channel.category.id != self.client.rightCategory:
            return False
        else:
            return True



    @commands.command()
    async def help(self, ctx):
        await ctx.send(self.client.commandsChannel.mention)

    @commands.command(aliases=['balance'])
    async def bal(self, ctx, member:discord.Member=None):

        if not member: member = ctx.author
        
        if not await bot_check(self.client, ctx, member):
            return

        money = read_value(member.id, 'money')
        bank = read_value(member.id, 'bank')
        total = read_value(member.id, 'total')

        avatar = member.avatar_url_as(static_format='jpg')
        
        embed = discord.Embed(color=0x57d9d0)
        embed.set_author(name=f"{member.name}'s balance",icon_url=avatar)
        embed.add_field(name="Cash",value=f'${money}', inline=True)
        embed.add_field(name="Bank", value=f'${bank}', inline=True)
        embed.add_field(name="Total", value=f'${total}', inline=True)

        await ctx.send(embed=embed)
          
    @commands.command()
    async def jailtime(self, ctx, member:discord.Member=None):

        if not member: member = ctx.author

        if not await bot_check(self.client, ctx, member):
            return

        jailtime = read_value(member.id, 'jailtime')

        if jailtime > time.time():

            bailprice = self.client.bailprice(jailtime)
            await ctx.send(f'**{member.name}** has {splittime(jailtime)} left in jail with a bail price of ${bailprice}.')

        else:
            await ctx.send(f'**{member.name}** is not in jail.')

    @commands.command()
    async def worktime(self, ctx, member:discord.Member=None):

        if not member: member = ctx.author

        if not await bot_check(self.client, ctx, member):
            return

        workc = read_value(member.id, 'workc')
        
        if workc > time.time():
            await ctx.send(f'**{member.name}** has {splittime(workc)} left until they can work.')
        else:
            await ctx.send(f'**{member.name}** can work.')

    @commands.command()
    async def stealtime(self, ctx, member:discord.Member=None):

        if not member: member = ctx.author

        if not await bot_check(self.client, ctx, member):
            return

        stealc = read_value(member.id, 'stealc')
        
        if stealc > time.time():
            await ctx.send(f'**{member.name}** has {splittime(stealc)} left until they can steal.')
        else:
            await ctx.send(f'**{member.name}** can steal.')

    @commands.command()
    async def banktime(self, ctx, member:discord.Member=None):

        if not member: member = ctx.author

        if not await bot_check(self.client, ctx, member):
            return

        bankc = read_value(member.id, 'bankc')
        
        if bankc > time.time():
            await ctx.send(f'**{member.name}** has {splittime(bankc)} left until they can access their bank.')
        else:
            await ctx.send(f'**{member.name}** can access their bank.')

    @commands.command()
    async def heisttime(self, ctx):

        guild = self.client.mainGuild
        heist = open_heist()

        conn = sqlite3.connect('./storage/databases/heist.db')
        c = conn.cursor()
        c.execute('SELECT cooldown FROM heist')
        heistc = c.fetchone()[0]
        conn.close()

        if heistc > time.time():
            await ctx.send(f'Everyone must wait {splittime(heistc)} before another heist can be made.')

        elif heist["heistt"] > 0:
            await ctx.send(f'The heist on **{guild.get_member(heist["heistv"]).name}** will start in {heist["heistt"]} seconds.')

        else:
            await ctx.send(f'A heist can be made.')
        
    @commands.command()
    async def place(self, ctx, member:discord.Member=None):

        if not member: member = ctx.author

        if not await bot_check(self.client, ctx, member):
            return


        guild = self.client.mainGuild


        conn = sqlite3.connect('./storage/databases/hierarchy.db')
        c = conn.cursor()
        c.execute('SELECT id, total FROM members')
        hierarchy = c.fetchall()
        conn.close()

        hierarchy = sorted(hierarchy, key=lambda k: k[1], reverse=True)

        hierarchy = tuple(filter(lambda x: guild.get_member(x[0]) is not None, hierarchy))



        for x in hierarchy:
            if member.id == x[0]:
                place = hierarchy.index(x)
        place += 1

        await ctx.send(f"**{member.name}** is **#{place}** in The Hierarchy.")

    @commands.command()
    async def items(self, ctx, member:discord.Member=None):

        if not member: member = ctx.author

        if not await bot_check(self.client, ctx, member):
            return

        # Items

        guild = self.client.mainGuild

        avatar = guild.get_member(member.id)
        avatar = avatar.avatar_url_as(static_format='jpg',size=256)
        embed = discord.Embed(color=0x4785ff)


        items = read_value(member.id, 'items').split()
        
        count = dict(Counter(items))
        
        for x in count:
            embed.add_field(name="__________", value=f"{x.capitalize()} x{count[x]}", inline=True)

        if len(embed.fields) == 0:
            embed.add_field(name='__________', value="None", inline=True)


        embed.set_author(name=f"{member.name}'s items ({len(items)}/{read_value(member.id, 'storage')})",icon_url=avatar)

        # In use

        embed2 = discord.Embed(color=0xff8000)
        embed2.set_author(name=f"{member.name}'s items in use",icon_url=avatar)
        inuse = in_use(member.id)
        for x in inuse:
            embed2.add_field(name='__________', value=f'{x.capitalize()}: {splittime(inuse[x])}', inline=False)

        if len(embed2.fields) == 0:
            embed2.add_field(name='__________', value="None", inline=False)
    
        await ctx.send(embed=embed)
        await ctx.send(embed=embed2)

    @commands.command()
    async def around(self, ctx, find=None, member:discord.Member=None):

        if not member: member = ctx.author

        if not await bot_check(self.client, ctx, member):
            return

        if not find:
            find = 3
        try:
            find = int(find)

        except:
            await ctx.send('Incorrect command usage:\n`.around (range) (member)`')
            return

        if find < 1 or find > 25:
            await ctx.send('Enter a number from 1-25 for `range`.')
            return

        else:
            member = ctx.author

        author = ctx.author


        userid = member.id
        guild = self.client.mainGuild
        conn = sqlite3.connect('./storage/databases/hierarchy.db')
        c = conn.cursor()
        c.execute('SELECT id, total FROM members WHERE total > 0 ORDER BY total DESC')
        hierarchy = c.fetchall()
        conn.close()
        hierarchy = list(filter(lambda x: guild.get_member(x[0]), hierarchy))
        ids= list(map(lambda x: x[0], hierarchy))

        try:
            index = ids.index(userid)
        except ValueError:
            hierarchy.append((userid, 0))
            ids.append(userid)
            index = ids.index(userid)


        lower_index = index-find

        if lower_index < 0:
            lower_index = 0

        higher_index = index+find+1
        length = len(hierarchy)

        if higher_index > length:
            higher_index = length

        result = hierarchy[lower_index:higher_index]

        avatar = member.avatar_url_as(static_format='jpg',size=256)
        embed = discord.Embed(color=0xffd24a)
        embed.set_author(name=f"Around {member.name}",icon_url=avatar)

        place = ids.index(result[0][0])+1
        for person in result:
            current_member = guild.get_member(person[0])
            medal = ''
            mk = ''
            if place == 1:
                medal = '🥇 '
            elif place == 2:
                medal = '🥈 '
            elif place == 3:
                medal = '🥉 '
            if member.id == person[0]:
                mk = '**'
            embed.add_field(name='__________', value=f'{mk}{place}. {current_member.mention} {medal}- ${person[1]}{mk}', inline=False)
            place += 1


        if find > 5:
            await ctx.send('Embed too large, check your DMs.')
            await author.send(embed=embed)

        else:
            await ctx.send(embed=embed)

    @commands.command()
    async def aroundm(self, ctx, find=None, member:discord.Member=None):
        
        if not member: member = ctx.author

        if not await bot_check(self.client, ctx, member):
            return

        if not find:
            find = 3
        try:
            find = int(find)

        except:
            await ctx.send('Incorrect command usage:\n`.aroundm (range) (member)`')
            return

        if find < 1 or find > 25:
            await ctx.send('Enter a number from 1-25 for `range`.')
            return

        else:
            member = ctx.author

        author = ctx.author


        userid = member.id
        guild = self.client.mainGuild
        conn = sqlite3.connect('./storage/databases/hierarchy.db')
        c = conn.cursor()
        c.execute('SELECT id, total FROM members WHERE total > 0 ORDER BY total DESC')
        hierarchy = c.fetchall()
        conn.close()
        hierarchy = list(filter(lambda x: guild.get_member(x[0]), hierarchy))
        ids= list(map(lambda x: x[0], hierarchy))

        try:
            index = ids.index(userid)
        except ValueError:
            hierarchy.append((userid, 0))
            ids.append(userid)
            index = ids.index(userid)


        lower_index = index-find

        if lower_index < 0:
            lower_index = 0

        higher_index = index+find+1
        length = len(hierarchy)

        if higher_index > length:
            higher_index = length

        result = hierarchy[lower_index:higher_index]

        avatar = member.avatar_url_as(static_format='jpg',size=256)
        embed = discord.Embed(color=0xffd24a)
        embed.set_author(name=f"Around {member.name}",icon_url=avatar)

        place = ids.index(result[0][0])+1
        for person in result:
            current_member = guild.get_member(person[0])
            medal = ''
            mk = ''
            if place == 1:
                medal = '🥇 '
            elif place == 2:
                medal = '🥈 '
            elif place == 3:
                medal = '🥉 '
            if member.id == person[0]:
                mk = '**'
            embed.add_field(name='__________', value=f'{mk}{place}. {current_member.name} {medal}- ${person[1]}{mk}', inline=False)
            place += 1


        if find > 5:
            await ctx.send('Embed too large, check your DMs.')
            await author.send(embed=embed)

        else:
            await ctx.send(embed=embed)

    @commands.command()
    async def dailyinfo(self, ctx, member:discord.Member=None):
        if not member: member = ctx.author

        if not await bot_check(self.client, ctx, member):
            return

        streak = read_value(member.id, 'dailystreak')

        await ctx.send(f"**{member.name}**'s streak: {streak}")


        

def setup(client):
    client.add_cog(info(client))



