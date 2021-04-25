# pylint: disable=import-error

import discord
from discord.ext import commands
import json
import time
import os
from collections import Counter

# To import from different path
import sys
sys.path.insert(1 , os.getcwd())

from utils import bot_check, splittime, timestring, log_command

from datetime import datetime


class Info(commands.Cog):

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

    @commands.command(aliases=['richlist'])
    async def leaderboard(self, ctx):
        await ctx.send(self.client.leaderboardChannel.mention)

    @commands.command()
    async def shop(self, ctx):
        await ctx.send(self.client.get_channel(702654620291563600).mention)


    @commands.command(aliases=['balance'])
    async def bal(self, ctx, *, member:discord.Member=None):

        if not member: member = ctx.author
        
        if not await bot_check(self.client, ctx, member):
            return
        
        async with self.client.pool.acquire() as db:

            money, bank = await db.fetchrow('SELECT money, bank FROM members WHERE id = $1', member.id)

        avatar = member.avatar_url_as(static_format='jpg')
        
        embed = discord.Embed(color=0x57d9d0)
        embed.set_author(name=f"{member.name}'s balance",icon_url=avatar)
        embed.add_field(name="Cash",value=f'${money}', inline=True)
        embed.add_field(name="Bank", value=f'${bank}', inline=True)
        embed.add_field(name="Total", value=f'${money + bank}', inline=True)

        await ctx.send(embed=embed)
          
    @commands.command()
    async def jailtime(self, ctx, *, member:discord.Member=None):

        if not member: member = ctx.author

        if not await bot_check(self.client, ctx, member):
            return

        async with self.client.pool.acquire() as db:
            jailtime = await db.get_member_val(member.id, 'jailtime')

        if jailtime > time.time():

            bailprice = self.client.bailprice(jailtime)
            await ctx.send(f'**{member.name}** has {splittime(jailtime)} left in jail with a bail price of ${bailprice}.')

        else:
            await ctx.send(f'**{member.name}** is not in jail.')

    @commands.command()
    async def worktime(self, ctx, *, member:discord.Member=None):

        if not member: member = ctx.author

        if not await bot_check(self.client, ctx, member):
            return

        async with self.client.pool.acquire() as db:
            workc = await db.get_member_val(member.id, 'workc')
            
        if workc > time.time():
            await ctx.send(f'**{member.name}** has {splittime(workc)} left until they can work.')
        else:
            await ctx.send(f'**{member.name}** can work.')

    @commands.command()
    async def stealtime(self, ctx, *, member:discord.Member=None):

        if not member: member = ctx.author

        if not await bot_check(self.client, ctx, member):
            return

        async with self.client.pool.acquire() as db:
            stealc = await db.get_member_val(member.id, 'stealc')
            
        if stealc > time.time():
            await ctx.send(f'**{member.name}** has {splittime(stealc)} left until they can steal.')
        else:
            await ctx.send(f'**{member.name}** can steal.')

    @commands.command()
    async def banktime(self, ctx, *, member:discord.Member=None):

        if not member: member = ctx.author

        if not await bot_check(self.client, ctx, member):
            return
        
        async with self.client.pool.acquire() as db:
            bankc = await db.get_member_val(member.id, 'bankc')
            
        if bankc > time.time():
            await ctx.send(f'**{member.name}** has {splittime(bankc)} left until they can access their bank.')
        else:
            await ctx.send(f'**{member.name}** can access their bank.')

    @commands.command()
    async def heisttime(self, ctx):

        guild = self.client.mainGuild
        
        if not self.client.heist:
            
            with open("./storage/jsons/heist cooldown.json") as f:
                heistc = json.load(f)

            if heistc > time.time():
                await ctx.send(f'Everyone must wait {splittime(heistc)} before another heist can be made.')
            else:
                await ctx.send(f'A heist can be made.')

        else:

            if self.client.heist["victim"] == "bank":
                await ctx.send(f'The heist on the bank will start in {self.client.heist["start"]-int(time.time())} seconds.')
            else:
                await ctx.send(f'The heist on **{guild.get_member(self.client.heist["victim"]).name}** will start in {self.client.heist["start"]-int(time.time())} seconds.')
        
    @commands.command()
    async def place(self, ctx, *, member:discord.Member=None):

        if not member: member = ctx.author

        if not await bot_check(self.client, ctx, member):
            return


        guild = self.client.mainGuild

        async with self.client.pool.acquire() as db:
            hierarchy = await db.fetch('SELECT id, money + bank FROM members;')

        hierarchy.sort(key=lambda k: k[1], reverse=True)

        hierarchy = tuple(filter(lambda x: guild.get_member(x[0]) is not None, hierarchy))

        place = list(map(lambda hierarchy: hierarchy[0], hierarchy)).index(member.id) + 1

        await ctx.send(f"**{member.name}** is **#{place}** in The Hierarchy.")

    @commands.command(aliases=['inventory'])
    async def items(self, ctx, *, member:discord.Member=None):

        if not member: member = ctx.author

        if not await bot_check(self.client, ctx, member):
            return

        # Items

        guild = self.client.mainGuild

        avatar = guild.get_member(member.id)
        avatar = avatar.avatar_url_as(static_format='jpg')
        embed = discord.Embed(color=0x4785ff)


        async with self.client.pool.acquire() as db:

            shop_info = await db.fetch('SELECT name, emoji FROM shop;')
            item_emojis = {}

            for name, emoji in shop_info:
                item_emojis[name] = emoji

            items = await db.get_member_val(member.id, 'items')
            
            count = dict(Counter(items))
            
            for item, count in count.items():
                embed.add_field(name=discord.utils.escape_markdown("____"), value=f"{item_emojis[item]} {item.capitalize()} x{count}", inline=True)

            if not len(embed.fields):
                embed.add_field(name=discord.utils.escape_markdown("____"), value="None", inline=True)


            embed.set_author(name=f"{member.name}'s items ({len(items)}/{await db.get_member_val(member.id, 'storage')})", icon_url=avatar)

            # In use

            embed2 = discord.Embed(color=0xff8000)
            embed2.set_author(name=f"{member.name}'s items in use",icon_url=avatar)

            inuse = await db.in_use(member.id)

        for item, timer in inuse.items():
            embed2.add_field(name=discord.utils.escape_markdown("____"), value=f'{item_emojis[item]} {item.capitalize()}: {splittime(timer)}', inline=False)

        if not embed2.fields:
            embed2.add_field(name=discord.utils.escape_markdown("____"), value="None", inline=False)
    
        await ctx.send(embed=embed)
        await ctx.send(embed=embed2)

    @commands.command()
    async def around(self, ctx, find=None, *, member:discord.Member=None):

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

        async with self.client.pool.acquire() as db:
            hierarchy = await db.fetch('SELECT id, money + bank FROM members WHERE money + bank > 0 ORDER BY money + bank DESC;')

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

        avatar = member.avatar_url_as(static_format='jpg')
        embed = discord.Embed(color=0xffd24a)
        embed.set_author(name=f"Around {member.name}",icon_url=avatar)

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
    async def aroundm(self, ctx, find=None, *, member:discord.Member=None):
        
        if not member: 
            member = ctx.author
        

        if not await bot_check(self.client, ctx, member):
            return


        if not find:
            find = 3
        try:
            find = int(find)

        except:
            await ctx.send('Incorrect command usage:\n`.aroundm (range) (member)`')
            return

        if find < 1 or find > 12:
            await ctx.send('Enter a number from 1-12 for `range`.')
            return


        userid = member.id
        guild = self.client.mainGuild

        async with self.client.pool.acquire() as db:
            hierarchy = await db.fetch('SELECT id, money + bank FROM members WHERE money + bank > 0 ORDER BY money + bank DESC;')

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

        avatar = member.avatar_url_as(static_format='jpg')
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
            embed.add_field(name='__________', value=f'{mk}{place}. {discord.utils.escape_markdown(current_member.name)} {medal}- ${person[1]}{mk}', inline=False)
            place += 1


        if find > 5:
            await ctx.send('Embed too large, check your DMs.')
            await ctx.author.send(embed=embed)

        else:
            await ctx.send(embed=embed)

    @commands.command()
    async def dailyinfo(self, ctx, *, member:discord.Member=None):
        if not member: member = ctx.author

        if not await bot_check(self.client, ctx, member):
            return

        async with self.client.pool.acquire() as db:
            streak = await db.get_member_val(member.id, 'dailystreak')

        await ctx.send(f"**{member.name}**'s streak: {streak}")

    @commands.command()
    async def profile(self, ctx, member:discord.Member =None):
        
        if not member:
            member = ctx.author
        
        if not await bot_check(self.client, ctx, member):
            return

        status = str(member.status)
        
        if status == "offline":
            status = "<:offline:747627832624283720> Offline"
        elif status == "online":
            status = "<:online:747627823551873045> Online"
        elif status == "dnd":
            status = "<:do_not_disturb:747627854358904894> Do Not Disturb"
        elif status == "idle":
            status = "<:idle:747627839565856789> Idle"

        # get gang

        async with self.client.pool.acquire() as db:
            gang = await db.fetchval(f'SELECT name FROM gangs WHERE $1 = ANY(members) OR owner = $1;', member.id)


            if not gang:
                gang = "None"

            embed = discord.Embed(color=0xffa047, title=f"{member.name}#{member.discriminator}", description=f"""ID: {member.id}
Status: {status}

Money: ${await db.get_member_val(member.id, 'money + bank')}
Gang: {gang}
    """, timestamp=member.joined_at)
            embed.set_footer(text="Joined at")

        embed.set_thumbnail(url=member.avatar_url_as(static_format='jpg'))
        
        await ctx.send(embed=embed)


    
    @commands.group(aliases=["collectables"], invoke_without_command=True)
    async def award(self, ctx):
        await ctx.send("Incorrect command usage:\n`.award about/list`")
    

    @award.command(name="list")
    async def awards_list(self, ctx, member:discord.Member=None, page=1):

        if not member:
            member = ctx.author

        if isinstance(page, str):
            if page.isdigit():
                page = int(page)
            else:
                return await ctx.send("Enter a valid page number.")

        async with self.client.pool.acquire() as db:
            award_ids = await db.fetchval('SELECT awards FROM members WHERE id = $1', member.id)

            if not award_ids:
                embed = discord.Embed(color=0x19a83f, description="None")
                embed.set_author(name=f"{member.name}'s awards", icon_url=member.avatar_url_as(static_format='jpg'))
                await ctx.send(embed=embed)
                return

            awards = await db.fetch('SELECT name, short_description FROM awards WHERE id = ANY($1);', award_ids)


        # dividing into lists of 5
        awards = [awards[x:x+5] for x in range(0, len(awards), 5)]

        embed = discord.Embed(color=0x19a83f)
        embed.set_author(name=f"{member.name}'s awards", icon_url=member.avatar_url_as(static_format='jpg'))

        if page > len(awards):
            return await ctx.send("There are not that many pages.")

        
        for index, award in enumerate(awards[page-1]):

            name, short_description = award

            embed.add_field(name=f"{(page-1)*5 + index + 1}. {name}", value=short_description, inline=False)

        embed.set_footer(text=f"Page {page}/{len(awards)}")

        
        await ctx.send(embed=embed)


    @award.command()
    async def about(self, ctx, *, award_name=None):

        if not award_name:
            return await ctx.send("Incorrect command usage:\n`.award about awardname`")


        async with self.client.pool.acquire() as db:
            award = await db.fetchrow('SELECT name, color, long_description, image_link FROM awards WHERE LOWER(name) = $1;', award_name.lower())


        if not award:
            return await ctx.send(f"There is no award called **{award_name}**.")


        name, color, long_description, image_link = award

        embed = discord.Embed(color=color, title=name, description=long_description)
        embed.set_image(url=image_link)

        await ctx.send(embed=embed)


    @commands.command(aliases=['steallog'])
    async def steallogs(self, ctx, *, member: discord.Member=None):

        if not member:
            member = ctx.author

        if not await bot_check(self.client, ctx, member):
            return


        async with self.client.pool.acquire() as db:

            steal_logs = json.loads(await db.get_member_val(member.id, 'steal_logs'))

        embed = discord.Embed(color=0x57d9d0)
        embed.set_author(name=f"{member.name}'s steal logs", icon_url=member.avatar_url_as(static_format='jpg'))

        for log in steal_logs:

            created_at = datetime.strptime(log['created_at'], '%Y-%m-%d %H:%M:%S.%f')

            difference_delta = (datetime.utcnow() - created_at)
            seconds = difference_delta.seconds + difference_delta.days*86400

            minutes, seconds = divmod(seconds, 60)
            hours, minutes = divmod(minutes, 60)
            days, hours = divmod(hours, 24)
            weeks, days = divmod(days, 7)
            # aproximate number of weeks in a month
            months, weeks = tuple(int(x) for x in divmod(weeks, 4.34524))
            years, months = divmod(months, 12)


            all_times = [years, months, weeks, days, hours, minutes, seconds]

            if not any(all_times[:5]):
                time_difference = f"{minutes}m {seconds}s"

            elif not any(all_times[:4]):
                time_difference = f"{hours}h"

            elif not any(all_times[:3]):
                time_difference = f"{days}d"

            elif not any(all_times[:2]):

                time_difference = f"{weeks} week"
                if weeks != 1:
                    time_difference += "s"

            elif not any(all_times[:1]):

                time_difference = f"{months} month"
                if months != 1:
                    time_difference += "s"

            else:
                time_difference = f"{years} year"
                if years != 1:
                    time_difference += "s"

            embed.add_field(name=discord.utils.escape_markdown("____"), value=f"{log['text']} *{time_difference} ago*\n[Jump]({log['jump_url']})", inline=False)

        if not embed.fields:
            embed = discord.Embed(color=0x57d9d0, description="None")
            embed.set_author(name=f"{member.name}'s steal logs", icon_url=member.avatar_url_as(static_format='jpg'))

        await ctx.send(embed=embed)



def setup(client):
    client.add_cog(Info(client))



