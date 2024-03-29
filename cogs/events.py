# pylint: disable=import-error

import nextcord
from nextcord.ext import commands
import os
import random
import json
import asyncio
# To import from different path
import sys
sys.path.insert(1 , os.getcwd())

from utils import bot_check, splittime, timestring, log_command


class Events(commands.Cog):

    def __init__(self, client):
        self.client = client

    async def cog_check(self, ctx):
        if ctx.channel.category.id != self.client.rightCategory:
            return False
        else:
            return True

    @commands.command()
    async def writeevent(self, ctx):

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

        async with self.client.pool.acquire() as db:

            await db.execute("DROP TABLE IF EXISTS hierarchy.events;")
            await db.execute("CREATE TABLE hierarchy.events (id BIGINT PRIMARY KEY, total INTEGER DEFAULT 0);")
            await db.execute("INSERT INTO hierarchy.events (id, total) SELECT id, money + bank FROM hierarchy.members;")

        await ctx.send("Saved all balances.")
        await log_command(self.client, ctx)



    @commands.command()
    async def joinallevent(self, ctx):

        if ctx.channel.id != self.client.adminChannel: return

        await ctx.send("Are you sure you want to join all members to the event? Respond with `y` or `yes` to proceed.")

        try:
            response = await self.client.wait_for('message', check=lambda m: m.channel == ctx.channel and m.author == ctx.author, timeout=20)
        except:
            return await ctx.send("All join timed out.")

        if response.content.lower() not in ('y', 'yes'): return await ctx.send("All join cancelled.")

        async with self.client.pool.acquire() as db:
            await db.execute('UPDATE members SET in_event = TRUE;')

        await ctx.send("All members are now in the event.")
        await log_command(self.client, ctx)


    @commands.command(aliases=["leaveevent"])
    async def eventleave(self, ctx):

        with open('./storage/jsons/mode.json') as f:
            mode = json.load(f)

        if mode != "event":
            return await ctx.send("There is no ongoing event right now.")

        async with self.client.pool.acquire() as db:

            if not await db.get_member_val(ctx.author.id, 'in_event'):
                return await ctx.send("You have already left this event.")

            await ctx.send("Are you sure you want to leave the event? **You may not join the event once you leave**. Respond with `y` or `yes` to proceed.")

            try:
                response = await self.client.wait_for('message', check=lambda m: m.channel == ctx.channel and m.author == ctx.author, timeout=20)
            except asyncio.TimeoutError:
                return await ctx.send("Event leave timed out.")

            if response.content.lower() not in ('y', 'yes'):
                return await ctx.send("Event leave cancelled.")
            
            await db.set_member_val(ctx.author.id, 'in_event', False)

        await ctx.send("You have successfully left the event.")

        
        

    @commands.command()
    async def eventprog(self, ctx, *, member:nextcord.Member=None):
        if not member:
            member = ctx.author
        
        if not await bot_check(self.client, ctx, member):
            return

        async with self.client.pool.acquire() as db:

            money, in_event = await db.fetchrow("""
            SELECT members.money + members.bank - (
            CASE
                WHEN events.total IS NULL THEN 0
                ELSE events.total
            END), members.in_event
            FROM members
            LEFT JOIN events
            ON members.id = events.id
            WHERE members.id = $1;
            """, member.id)

        if not in_event:
            if member == ctx.author:
                await ctx.send("You are not participating in this event.")
            else:
                await ctx.send(f"**{member.name}** is not participating in this event.")
            return

        if money >= 0:
            await ctx.send(f"**{member.name}** has gained ${money} since the beginning of the event.")
        else:
            money *= -1
            await ctx.send(f"**{member.name}** has lost ${money} since the beginning of the event.")

    @commands.command()
    async def eventlead(self, ctx):
        guild = self.client.mainGuild


        embed = nextcord.Embed(color = 0x2495ff)
        embed.set_author(name='🌟 Event Leaderboard 🌟')

        async with self.client.pool.acquire() as db:

            hierarchy = await db.fetch("""
            SELECT members.id, members.money + members.bank - (
            CASE
                WHEN events.total IS NULL THEN 0
                ELSE events.total
            END)
            FROM members
            LEFT JOIN events
            ON members.id = events.id
            WHERE members.in_event = TRUE;
            """)

        hierarchy = list(filter(lambda x: guild.get_member(x[0]), hierarchy))
        hierarchy.sort(key=lambda member: member[1], reverse=True)

        for x in range(5):

            if x == 0:
                embed.add_field(name='__________',value=f'1. <@{hierarchy[x][0]}> 🥇 - ${hierarchy[x][1]}',inline=False)
            elif x == 1:
                embed.add_field(name='__________',value=f'2. <@{hierarchy[x][0]}> 🥈 - ${hierarchy[x][1]}',inline=False)
            elif x == 2:
                embed.add_field(name='__________',value=f'3. <@{hierarchy[x][0]}> 🥉 - ${hierarchy[x][1]}',inline=False)
            else:
                embed.add_field(name='__________',value=f'{x+1}. <@{hierarchy[x][0]}> - ${hierarchy[x][1]}',inline=False)


        await ctx.send(embed=embed)

    @commands.command()
    async def eventleadm(self, ctx):

        guild = self.client.mainGuild


        embed = nextcord.Embed(color = 0x2495ff)
        embed.set_author(name='🌟 Event Leaderboard 🌟')

        async with self.client.pool.acquire() as db:

            hierarchy = await db.fetch("""
            SELECT members.id, members.money + members.bank - (
            CASE
                WHEN events.total IS NULL THEN 0
                ELSE events.total
            END)
            FROM members
            LEFT JOIN events
            ON members.id = events.id
            WHERE members.in_event = TRUE;
            """)

        hierarchy = list(filter(lambda x: guild.get_member(x[0]), hierarchy))
        hierarchy.sort(key=lambda member: member[1], reverse=True)

        for x in range(5):
            member = guild.get_member(hierarchy[x][0])

            if x == 0:
                embed.add_field(name='__________',value=f'1. {nextcord.utils.escape_markdown(member.name)} 🥇 - ${hierarchy[x][1]}',inline=False)
            elif x == 1:
                embed.add_field(name='__________',value=f'2. {nextcord.utils.escape_markdown(member.name)} 🥈 - ${hierarchy[x][1]}',inline=False)
            elif x == 2:
                embed.add_field(name='__________',value=f'3. {nextcord.utils.escape_markdown(member.name)} 🥉 - ${hierarchy[x][1]}',inline=False)
            else:
                embed.add_field(name='__________',value=f'{x+1}. {nextcord.utils.escape_markdown(member.name)} - ${hierarchy[x][1]}',inline=False)


        await ctx.send(embed=embed)


    @commands.command()
    async def eventaround(self, ctx, find=None, *, member:nextcord.Member=None):


        if not member: 
            member = ctx.author
        
        if not await bot_check(self.client, ctx, member):
            return

        if not find:
            find = 3
        try:
            find = int(find)

        except:
            await ctx.send('Incorrect command usage:\n`.eventaround (range) (member)`')
            return

        if find < 1 or find > 12:
            await ctx.send('Enter a number from 1-12 for `range`.')
            return

        async with self.client.pool.acquire() as db:

            if not await db.get_member_val(ctx.author.id, 'in_event') and member == ctx.author:
                return await ctx.send("You are not participating in this event.")

            elif not await db.get_member_val(member.id, 'in_event'):
                return await ctx.send(f"**{member.name}** is not participating in this event.")


            userid = member.id
            guild = self.client.mainGuild

            hierarchy = await db.fetch("""
            SELECT members.id, members.money + members.bank - (
            CASE
                WHEN events.total IS NULL THEN 0
                ELSE events.total
            END)
            FROM members
            LEFT JOIN events
            ON members.id = events.id
            WHERE members.in_event = TRUE;
            """)

        hierarchy = list(filter(lambda x: guild.get_member(x[0]), hierarchy))
        hierarchy.sort(key=lambda member: member[1], reverse=True)

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

        avatar = member.avatar.with_format('jpg').url
        embed = nextcord.Embed(color=0x2495ff)
        embed.set_author(name=f"🌟 Around {member.name} 🌟",icon_url=avatar)

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
            embed.add_field(name='__________', value=f'{mk}{place}. <@{person[0]}> {medal}- ${person[1]}{mk}', inline=False)
            place += 1


        if find > 5:
            await ctx.send('Embed too large, check your DMs.')
            await ctx.author.send(embed=embed)

        else:
            await ctx.send(embed=embed)

    @commands.command()
    async def eventaroundm(self, ctx, find=None, *, member:nextcord.Member=None):

        if not member: 
            member = ctx.author
        
        if not await bot_check(self.client, ctx, member):
            return

        if not find:
            find = 3
        try:
            find = int(find)

        except:
            await ctx.send('Incorrect command usage:\n`.eventaroundm (range) (member)`')
            return

        async with self.client.pool.acquire() as db:

            if not await db.get_member_val(ctx.author.id, 'in_event') and member == ctx.author:
                return await ctx.send("You are not participating in this event.")

            elif not await db.get_member_val(member.id, 'in_event'):
                return await ctx.send(f"**{member.name}** is not participating in this event.")


            userid = member.id
            guild = self.client.mainGuild

            hierarchy = await db.fetch("""
            SELECT members.id, members.money + members.bank - (
            CASE
                WHEN events.total IS NULL THEN 0
                ELSE events.total
            END)
            FROM members
            LEFT JOIN events
            ON members.id = events.id
            WHERE members.in_event = TRUE;
            """)

        hierarchy = list(filter(lambda x: guild.get_member(x[0]), hierarchy))
        hierarchy.sort(key=lambda member: member[1], reverse=True)

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

        avatar = member.avatar.with_format('jpg').url
        embed = nextcord.Embed(color=0x2495ff)
        embed.set_author(name=f"🌟 Around {member.name} 🌟",icon_url=avatar)

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
            embed.add_field(name='__________', value=f'{mk}{place}. {nextcord.utils.escape_markdown(current_member.name)} {medal}- ${person[1]}{mk}', inline=False)
            place += 1


        if find > 5:
            await ctx.send('Embed too large, check your DMs.')
            await ctx.author.send(embed=embed)

        else:
            await ctx.send(embed=embed)

def setup(client):
    client.add_cog(Events(client))
