# pylint: disable=import-error

import discord
from discord.ext import commands
import sqlite3
import random
import time

import os
# To import from different path
import sys
sys.path.insert(1 , os.getcwd())

from utils import (log_command, splittime, bot_check)

class halloween(commands.Cog):

    def __init__(self, client):
        self.client = client


    async def cog_check(self, ctx):
        if ctx.channel.category.id != self.client.rightCategory:
            return False
        else:
            return True


    @commands.command()
    async def writehalloween(self, ctx):

        if ctx.channel.id != self.client.adminChannel: return

        with open('./storage/text/englishwords.txt') as f:
            word = random.choice(f.read().splitlines())
        # for confirmation
        await ctx.send(f"Are you sure you want to save all balances? Type `{word}` to proceed.")

        try:
            response = await self.client.wait_for('message', check=lambda m: m.channel == ctx.channel and m.author == ctx.author, timeout=20)
        except:
            return await ctx.send("Save timed out.")

        if response.content.lower() != word.lower(): return await ctx.send("Save cancelled.")
        
        conn = sqlite3.connect('./storage/databases/hierarchy.db')
        c = conn.cursor()
        c.execute("DROP TABLE IF EXISTS halloween;")
        c.execute("CREATE TABLE halloween (id INTEGER PRIMARY KEY, pumpkins INTEGER DEFAULT 100, cooldown INTEGER DEFAULT 0);")
        c.execute("""
        INSERT INTO halloween
        (id, pumpkins)
        SELECT id, 
        CASE
            WHEN members.money + members.bank > 0 THEN 100
            ELSE 0
        END
        FROM members;""")
        conn.commit()
        conn.close()

        await ctx.send("Reset all pumpkins.")
        await log_command(self.client, ctx)


    @commands.command()
    async def pumpkins(self, ctx, *, member:discord.Member=None):

        if not member:
            member = ctx.author

        conn = sqlite3.connect('./storage/databases/hierarchy.db')
        c = conn.cursor()

        c.execute("SELECT pumpkins FROM halloween WHERE id = ?", (member.id,))
        pumpkins = c.fetchone()

        if not pumpkins:
            c.execute("INSERT INTO halloween (id) VALUES (?)", (member.id,))
            conn.commit()
            pumpkins = 100
        else:
            pumpkins = pumpkins[0]

        conn.close()

        embed = discord.Embed(color=0xff8519, description=f"🎃  {pumpkins} Pumpkins  🎃")
        embed.set_author(name=f"{member.name}'s pumpkins", icon_url=member.avatar_url_as(static_format='jpg'))
        
        await ctx.send(embed=embed)

    
    @commands.command(aliases=["plead", "pumpkinlead", "hlead"])
    async def halloweenlead(self, ctx):

        guild = self.client.mainGuild


        embed = discord.Embed(color = 0xff8519)
        embed.set_author(name='🎃 Halloween Leaderboard 🎃')


        conn = sqlite3.connect('./storage/databases/hierarchy.db')
        c = conn.cursor()
        c.execute("""
        SELECT members.id,
        CASE 
            WHEN halloween.pumpkins IS NULL THEN 100
            ELSE halloween.pumpkins
        END
        FROM members
        LEFT JOIN halloween
        ON members.id = halloween.id;""")
        hierarchy = c.fetchall()
        conn.close()

        hierarchy = list(filter(lambda x: guild.get_member(x[0]), hierarchy))
        hierarchy.sort(key=lambda member: member[1], reverse=True)

        for x in range(5):

            if x == 0:
                embed.add_field(name='__________',value=f'1. <@{hierarchy[x][0]}> 🥇 - {hierarchy[x][1]} 🎃',inline=False)
            elif x == 1:
                embed.add_field(name='__________',value=f'2. <@{hierarchy[x][0]}> 🥈 - {hierarchy[x][1]} 🎃',inline=False)
            elif x == 2:
                embed.add_field(name='__________',value=f'3. <@{hierarchy[x][0]}> 🥉 - {hierarchy[x][1]} 🎃',inline=False)
            else:
                embed.add_field(name='__________',value=f'{x+1}. <@{hierarchy[x][0]}> - {hierarchy[x][1]} 🎃',inline=False)


        await ctx.send(embed=embed)


    @commands.command(aliases=["pleadm", "pumpkinleadm", "hleadm"])
    async def halloweenleadm(self, ctx):

        guild = self.client.mainGuild


        embed = discord.Embed(color = 0xff8519)
        embed.set_author(name='🎃 Halloween Leaderboard 🎃')


        conn = sqlite3.connect('./storage/databases/hierarchy.db')
        c = conn.cursor()
        c.execute("""
        SELECT members.id,
        CASE 
            WHEN halloween.pumpkins IS NULL THEN 100
            ELSE halloween.pumpkins
        END
        FROM members
        LEFT JOIN halloween
        ON members.id = halloween.id;""")
        hierarchy = c.fetchall()
        conn.close()

        hierarchy = list(filter(lambda x: guild.get_member(x[0]), hierarchy))
        hierarchy.sort(key=lambda member: member[1], reverse=True)

        for x in range(5):
            member = guild.get_member(hierarchy[x][0])

            if x == 0:
                embed.add_field(name='__________',value=f'1. {member.name} 🥇 - {hierarchy[x][1]} 🎃',inline=False)
            elif x == 1:
                embed.add_field(name='__________',value=f'2. {member.name} 🥈 - {hierarchy[x][1]} 🎃',inline=False)
            elif x == 2:
                embed.add_field(name='__________',value=f'3. {member.name} 🥉 - {hierarchy[x][1]} 🎃',inline=False)
            else:
                embed.add_field(name='__________',value=f'{x+1}. {member.name} - {hierarchy[x][1]} 🎃',inline=False)


        await ctx.send(embed=embed)


    @commands.command(aliases=["paround", "haround", "pumpkinaround"])
    async def halloweenaround(self, ctx, find=None, *, member:discord.Member=None):


        if not member: 
            member = ctx.author
        
        if not await bot_check(self.client, ctx, member):
            return

        if not find:
            find = 3
        try:
            find = int(find)

        except:
            await ctx.send('Incorrect command usage:\n`.around (range) (member)`')
            return

        if find < 1 or find > 12:
            await ctx.send('Enter a number from 1-12 for `range`.')
            return

        userid = member.id
        guild = self.client.mainGuild


        conn = sqlite3.connect('./storage/databases/hierarchy.db')
        c = conn.cursor()
        c.execute("""
        SELECT members.id,
        CASE 
            WHEN halloween.pumpkins IS NULL THEN 100
            ELSE halloween.pumpkins
        END
        FROM members
        LEFT JOIN halloween
        ON members.id = halloween.id;""")
        hierarchy = c.fetchall()
        conn.close()

        hierarchy = list(filter(lambda x: guild.get_member(x[0]), hierarchy))
        hierarchy.sort(key=lambda member: member[1], reverse=True)

        ids = list(map(lambda x: x[0], hierarchy))

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

        avatar = member.avatar_url_as(static_format='jpg')
        embed = discord.Embed(color=0xff8519)
        embed.set_author(name=f"🎃 Around {member.name} 🎃",icon_url=avatar)

        place = ids.index(result[0][0])+1
        for person in result:

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
            embed.add_field(name='__________', value=f'{mk}{place}. <@{person[0]}> {medal}- {person[1]}{mk} 🎃', inline=False)
            place += 1


        if find > 5:
            await ctx.send('Embed too large, check your DMs.')
            await ctx.author.send(embed=embed)

        else:
            await ctx.send(embed=embed)


    @commands.command(aliases=["paroundm", "haroundm", "pumpkinaroundm"])
    async def halloweenaroundm(self, ctx, find=None, *, member:discord.Member=None):


        if not member: 
            member = ctx.author
        
        if not await bot_check(self.client, ctx, member):
            return

        if not find:
            find = 3
        try:
            find = int(find)

        except:
            await ctx.send('Incorrect command usage:\n`.around (range) (member)`')
            return

        if find < 1 or find > 12:
            await ctx.send('Enter a number from 1-12 for `range`.')
            return

        userid = member.id
        guild = self.client.mainGuild


        conn = sqlite3.connect('./storage/databases/hierarchy.db')
        c = conn.cursor()
        c.execute("""
        SELECT members.id,
        CASE 
            WHEN halloween.pumpkins IS NULL THEN 100
            ELSE halloween.pumpkins
        END
        FROM members
        LEFT JOIN halloween
        ON members.id = halloween.id;""")
        hierarchy = c.fetchall()
        conn.close()

        hierarchy = list(filter(lambda x: guild.get_member(x[0]), hierarchy))
        hierarchy.sort(key=lambda member: member[1], reverse=True)

        ids = list(map(lambda x: x[0], hierarchy))

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

        avatar = member.avatar_url_as(static_format='jpg')
        embed = discord.Embed(color=0xff8519)
        embed.set_author(name=f"🎃 Around {member.name} 🎃",icon_url=avatar)

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


            embed.add_field(name='__________', value=f'{mk}{place}. {current_member.name} {medal}- {person[1]}{mk} 🎃', inline=False)
            place += 1


        if find > 5:
            await ctx.send('Embed too large, check your DMs.')
            await ctx.author.send(embed=embed)

        else:
            await ctx.send(embed=embed)

    @commands.command(aliases=["ptime", "htime", "pumpkintime"])
    async def halloweentime(self, ctx, *, member:discord.Member=None):

        if not member:
            member = ctx.author

        
        conn = sqlite3.connect('./storage/databases/hierarchy.db')
        c = conn.cursor()

        c.execute("SELECT cooldown FROM halloween WHERE id = ?", (member.id,))
        cooldown = c.fetchone()

        if not cooldown:
            c.execute("INSERT INTO halloween (id) VALUES (?)", (member.id,))
            conn.commit()
            cooldown = 0
        else:
            cooldown = cooldown[0]

        conn.close()

        if cooldown > int(time.time()):
            await ctx.send(f"🎃  **{member.name}** has {splittime(cooldown)} left until they can steal pumpkins.  🎃")
        else:
            await ctx.send(f"🎃  **{member.name}** can steal pumpkins.  🎃")




def setup(client):
    client.add_cog(halloween(client))