# pylint: disable=import-error

import discord
from discord.ext import commands
import os
import sqlite3
from sqlite3 import Error
# To import from different path
import sys
sys.path.insert(1 , os.getcwd())

from utils import (read_value, write_value, update_total, leaderboard,
rolecheck, splittime, open_heist, bot_check, in_use, jail_heist_check, around,
remove_item, remove_use, add_item, write_heist, add_use)


class events(commands.Cog):

    def __init__(self, client):
        self.client = client

    async def cog_check(self, ctx):
        if ctx.channel.category.id != self.client.rightCategory:
            return False
        else:
            return True

    @commands.command()
    async def eventprog(self, ctx, member:discord.Member=None):
        if not member:
            member = ctx.author
        
        if not await bot_check(self.client, ctx, member):
            return

        conn = sqlite3.connect('./storage/databases/events.db')
        c = conn.cursor()
        try:
            c.execute("SELECT total FROM members WHERE id = ?", (member.id,))
            oldTotal = c.fetchone()[0]
        except:
            oldTotal = 0
        conn.close()

        newTotal = read_value(member.id, 'total')

        difference = newTotal - oldTotal

        if difference >= 0:
            await ctx.send(f"**{member.name}** has gained ${difference} since the beginning of the event.")
        else:
            difference *= -1
            await ctx.send(f"**{member.name}** has lost ${difference} since the beginning of the event.")

    @commands.command()
    async def eventlead(self, ctx):
        guild = self.client.mainGuild
        embed = discord.Embed(color = 0x2495ff)
        embed.set_author(name='🌟 Event Leaderboard 🌟')
        conn = sqlite3.connect('./storage/databases/hierarchy.db')
        c = conn.cursor()
        c.execute('SELECT id, total FROM members ORDER BY id')
        new_hierarchy = c.fetchall()
        conn.close()

        conn = sqlite3.connect('./storage/databases/events.db')
        c = conn.cursor()
        c.execute('SELECT id, total FROM members ORDER BY id')
        old_hierarchy = c.fetchall()
        conn.close()

        old_ids = list(map(lambda x: x[0], old_hierarchy))
        x = 0
        while len(new_hierarchy) > len(old_hierarchy):
            if new_hierarchy[x][0] not in old_ids:
                old_hierarchy.insert(x, (new_hierarchy[x]))
            x += 1

        differences = []
        for x in range(len(new_hierarchy)):


            differences.append( (new_hierarchy[x][0] , new_hierarchy[x][1] - old_hierarchy[x][1]) )


        differences = list(filter(lambda x: guild.get_member(x[0]), differences))
        differences = sorted(differences, key=lambda k: k[1], reverse=True)



        for x in range(5):
            member = guild.get_member(differences[x][0])
            if x == 0:
                embed.add_field(name='__________',value=f'1. {member.mention} 🥇 - ${differences[x][1]}',inline=False)
            elif x == 1:
                embed.add_field(name='__________',value=f'2. {member.mention} 🥈 - ${differences[x][1]}',inline=False)
            elif x == 2:
                embed.add_field(name='__________',value=f'3. {member.mention} \U0001f949 - ${differences[x][1]}',inline=False)
            else:
                embed.add_field(name='__________',value=f'{x+1}. {member.mention} - ${differences[x][1]}',inline=False)


        await ctx.send(embed=embed)

    @commands.command()
    async def eventleadm(self, ctx):
        guild = self.client.mainGuild
        embed = discord.Embed(color = 0x2495ff)
        embed.set_author(name='🌟 Event Leaderboard 🌟')
        conn = sqlite3.connect('./storage/databases/hierarchy.db')
        c = conn.cursor()
        c.execute('SELECT id, total FROM members ORDER BY id')
        new_hierarchy = c.fetchall()
        conn.close()

        conn = sqlite3.connect('./storage/databases/events.db')
        c = conn.cursor()
        c.execute('SELECT id, total FROM members ORDER BY id')
        old_hierarchy = c.fetchall()
        conn.close()

        old_ids = list(map(lambda x: x[0], old_hierarchy))
        x = 0
        while len(new_hierarchy) > len(old_hierarchy):
            if new_hierarchy[x][0] not in old_ids:
                old_hierarchy.insert(x, (new_hierarchy[x]))
            x += 1

        differences = []
        for x in range(len(new_hierarchy)):


            differences.append( (new_hierarchy[x][0] , new_hierarchy[x][1] - old_hierarchy[x][1]) )


        differences = list(filter(lambda x: guild.get_member(x[0]), differences))
        differences = sorted(differences, key=lambda k: k[1], reverse=True)




        for x in range(5):
            member = guild.get_member(differences[x][0])
            if x == 0:
                embed.add_field(name='__________',value=f'1. {member.name} 🥇 - ${differences[x][1]}',inline=False)
            elif x == 1:
                embed.add_field(name='__________',value=f'2. {member.name} 🥈 - ${differences[x][1]}',inline=False)
            elif x == 2:
                embed.add_field(name='__________',value=f'3. {member.name} \U0001f949 - ${differences[x][1]}',inline=False)
            else:
                embed.add_field(name='__________',value=f'{x+1}. {member.name} - ${differences[x][1]}',inline=False)


        await ctx.send(embed=embed)


    @commands.command()
    async def eventaround(self, ctx, find=None, member:discord.Member=None):
        if find == None:
            find = 3
        try:
            find = int(find)
        except:
            await ctx.send('Enter a valid number from 1-25')
            return
        if find < 1 or find > 25:
            await ctx.send('Enter a number from 1-25.')
            return
        if not member:
            author = ctx.author

        if not await bot_check(self.client, ctx, member):
            return

        else:
            author = member

        author2 = ctx.author
        userid = author.id
        guild = self.client.mainGuild
        
        conn = sqlite3.connect('./storage/databases/hierarchy.db')
        c = conn.cursor()
        c.execute('SELECT id, total FROM members')
        new_hierarchy = c.fetchall()
        conn.close()

        conn = sqlite3.connect('./storage/databases/events.db')
        c = conn.cursor()
        c.execute('SELECT id, total FROM members')
        old_hierarchy = c.fetchall()
        conn.close()



        old_ids = list(map(lambda x: x[0], old_hierarchy))
        x = 0
        while len(new_hierarchy) > len(old_hierarchy):
            if new_hierarchy[x][0] not in old_ids:
                old_hierarchy.insert(x, (new_hierarchy[x]))
            x += 1

        differences = []
        for x in range(len(new_hierarchy)):


            differences.append( (new_hierarchy[x][0] , new_hierarchy[x][1] - old_hierarchy[x][1]) )


        differences = list(filter(lambda x: guild.get_member(x[0]), differences))
        differences = sorted(differences, key=lambda k: k[1], reverse=True)



        ids = list(map(lambda x: x[0], differences))


        index = ids.index(userid)

        lower_index = index-find

        if lower_index < 0:
            lower_index = 0

        higher_index = index+find+1
        length = len(differences)

        if higher_index > length:
            higher_index = length

        result = differences[lower_index:higher_index]

        avatar = author.avatar_url_as(static_format='jpg',size=256)
        embed = discord.Embed(color=0x2495ff)
        embed.set_author(name=f"🌟 Around {author.name} 🌟",icon_url=avatar)

        place = ids.index(result[0][0])+1
        for person in result:
            member2 = guild.get_member(person[0])
            medal = ''
            mk = ''
            if place == 1:
                medal = '🥇 '
            elif place == 2:
                medal = '🥈 '
            elif place == 3:
                medal = '🥉 '
            if author.id == person[0]:
                mk = '**'
            embed.add_field(name='__________', value=f'{mk}{place}. {member2.mention} {medal}- ${person[1]}{mk}', inline=False)
            place += 1
        if find > 5:
            await ctx.send('Embed too large, check your DMs.')
            await author2.send(embed=embed)
        else:
            await ctx.send(embed=embed)

    @commands.command()
    async def eventaroundm(self, ctx, find=None, member:discord.Member=None):
        if find == None:
            find = 3
        try:
            find = int(find)
        except:
            await ctx.send('Enter a valid number from 1-25')
            return
        if find < 1 or find > 25:
            await ctx.send('Enter a number from 1-25.')
            return
        if not member:
            author = ctx.author

        if not await bot_check(self.client, ctx, member):
            return

        else:
            author = member

        author2 = ctx.author
        userid = author.id
        guild = self.client.mainGuild
        
        conn = sqlite3.connect('./storage/databases/hierarchy.db')
        c = conn.cursor()
        c.execute('SELECT id, total FROM members')
        new_hierarchy = c.fetchall()
        conn.close()

        conn = sqlite3.connect('./storage/databases/events.db')
        c = conn.cursor()
        c.execute('SELECT id, total FROM members')
        old_hierarchy = c.fetchall()
        conn.close()



        old_ids = list(map(lambda x: x[0], old_hierarchy))
        x = 0
        while len(new_hierarchy) > len(old_hierarchy):
            if new_hierarchy[x][0] not in old_ids:
                old_hierarchy.insert(x, (new_hierarchy[x]))
            x += 1

        differences = []
        for x in range(len(new_hierarchy)):


            differences.append( (new_hierarchy[x][0] , new_hierarchy[x][1] - old_hierarchy[x][1]) )


        differences = list(filter(lambda x: guild.get_member(x[0]), differences))
        differences = sorted(differences, key=lambda k: k[1], reverse=True)



        ids = list(map(lambda x: x[0], differences))


        index = ids.index(userid)

        lower_index = index-find

        if lower_index < 0:
            lower_index = 0

        higher_index = index+find+1
        length = len(differences)

        if higher_index > length:
            higher_index = length

        result = differences[lower_index:higher_index]

        avatar = author.avatar_url_as(static_format='jpg',size=256)
        embed = discord.Embed(color=0x2495ff)
        embed.set_author(name=f"🌟 Around {author.name} 🌟",icon_url=avatar)

        place = ids.index(result[0][0])+1
        for person in result:
            member2 = guild.get_member(person[0])
            medal = ''
            mk = ''
            if place == 1:
                medal = '🥇 '
            elif place == 2:
                medal = '🥈 '
            elif place == 3:
                medal = '🥉 '
            if author.id == person[0]:
                mk = '**'
            embed.add_field(name='__________', value=f'{mk}{place}. {member2.name} {medal}- ${person[1]}{mk}', inline=False)
            place += 1
        if find > 5:
            await ctx.send('Embed too large, check your DMs.')
            await author2.send(embed=embed)
        else:
            await ctx.send(embed=embed)

def setup(client):
    client.add_cog(events(client))
