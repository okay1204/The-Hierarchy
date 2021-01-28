# pylint: disable=import-error, anomalous-backslash-in-string
import discord
from discord.ext import commands, tasks
import json
import time
import datetime
import os
import asyncio
import random

# To import from different path
import sys
sys.path.insert(1 , os.getcwd())

from utils import bot_check, splittime, timestring, log_command

money_requirement = 3000

async def get_christmas_value(db, id, value):

    # inserting row if not exists
    await db.execute('INSERT INTO hierarchy.christmas (id) VALUES ($1) ON CONFLICT (id) DO NOTHING;', id)
    return await db.fetchval(f'SELECT {value} FROM hierarchy.christmas WHERE id = $1;', id)

async def set_christmas_value(db, id, value, overwrite):

    await db.execute('INSERT INTO hierarchy.christmas (id) VALUES ($1) ON CONFLICT (id) DO NOTHING;', id)
    await db.execute(f'UPDATE hierarchy.christmas SET {value} = $1 WHERE id = $2;', overwrite, id)

    

async def find_next_drop(db):

    total_bal = await db.fetchval('SELECT SUM(increase) FROM hierarchy.christmas;')

    drops = total_bal // money_requirement

    if drops == 0:
        return drops


    interval = 1440/drops

    drop_times = [drop_number * interval for drop_number in range(1, drops+1)]

    now = datetime.datetime.utcnow()
    minutes = (now.hour * 60) + now.minute

    for drop_time in drop_times:
        if minutes < drop_time:
            return (drop_time - minutes) * 60

class Christmas(commands.Cog):
    
    def __init__(self, client):
        self.client = client
        self.timer_task = None
        self.drop_task = None

        with open('./storage/jsons/christmas meter.json') as f:
            meter_state = json.load(f)
        
        if meter_state == "off":
            asyncio.create_task(self.start_timer_task())

        asyncio.create_task( self.update_stats() )

    async def start_timer_task(self):
        async with self.client.pool.acquire() as db:
            self.timer_task = asyncio.create_task(self.gift_drop_timer(await find_next_drop(db)))
    
    def cog_unload(self):
        
        if self.timer_task and not self.timer_task.done():
            self.timer_task.cancel()
        
        if self.drop_task and not self.drop_task.done():
            self.drop_task.cancel()

    async def gift_drop_timer(self, duration):

        if duration == 0:
            return

        await asyncio.sleep(duration)

        async with self.client.pool.acquire() as db:
            total_bal = await db.fetchval('SELECT SUM(increase) FROM hierarchy.christmas;')

        drops = total_bal // money_requirement

        next_time = time.time() + ((1440/drops) * 60)

        self.drop_task = asyncio.create_task(self.giftdrop( splittime(int(next_time))) )

        self.timer_task = asyncio.create_task(self.gift_drop_timer( next_time-time.time() ))
        

    async def update_stats(self):

        channel_id = 784097174136160326
        meter_id = 784097932030509096
        leaderboard_id = 784103963380678677

        async with self.client.pool.acquire() as db:
            total_bal = await db.fetchval('SELECT SUM(increase) FROM hierarchy.christmas;')

            members = await db.fetch('SELECT id, increase FROM hierarchy.christmas ORDER BY increase DESC;')

        drops = total_bal // money_requirement
        progress = total_bal - (money_requirement*drops)
        percentage = int(progress/money_requirement*100)

        meter = ""
        for _ in range(percentage//5):
            meter += "#"
        
        while len(meter) < 20:
            meter += "."
        
        meter = f"`{meter}`"


        channel = self.client.get_channel(channel_id)
        meter_message = await channel.fetch_message(meter_id)

        embed = discord.Embed(
            color=0x03ff39,
            title="Holiday Meter",
            description=f"🎁 **Gift drops per day: {drops}** 🎁\n\n💸 Total money: ${total_bal} 💸\n\nProgress to another gift drop:\n{meter}\n${progress}/${money_requirement}")

        await meter_message.edit(embed=embed)


        # leaderboard

        embed = discord.Embed(color=0x03ff39, title="🎄 Contribution leaderboard 🎄")
        leaderboard_message = await channel.fetch_message(leaderboard_id)

        for x in range(5):

            if x == 0:
                embed.add_field(name='__________',value=f'1. <@{members[x][0]}> 🥇 - ${members[x][1]}',inline=False)
            elif x == 1:
                embed.add_field(name='__________',value=f'2. <@{members[x][0]}> 🥈 - ${members[x][1]}',inline=False)
            elif x == 2:
                embed.add_field(name='__________',value=f'3. <@{members[x][0]}> 🥉 - ${members[x][1]}',inline=False)
            else:
                embed.add_field(name='__________',value=f'{x+1}. <@{members[x][0]}> - ${members[x][1]}',inline=False)
        
        await leaderboard_message.edit(embed=embed)


    async def giftdrop(self, next_drop):

        channel_id = 784497145708937277
        channel = self.client.get_channel(channel_id)

        guild = self.client.mainGuild

        await channel.send("🎁 ***A GIFT DROP HAS BEGUN*** 🎁\n\n**SPAM IN THIS CHANNEL AS MUCH AS YOU CAN TO COLLECT GIFTS AND EARN REWARDS**\n**YOU HAVE 60 SECONDS**")


        overwrites = channel.overwrites_for(self.client.mainGuild.default_role)
        overwrites.send_messages = True

        await channel.set_permissions(self.client.mainGuild.default_role, overwrite=overwrites)

        message_count = {}

        end_time = time.time() + 60

        while end_time > time.time():

            try:
                message = await self.client.wait_for('message', check=lambda msg: msg.channel == channel, timeout=1)
            except asyncio.TimeoutError:
                continue

            if message.author.id not in message_count.keys():
                message_count[message.author.id] = 1
            else:
                message_count[message.author.id] += 1
        

        overwrites = channel.overwrites_for(self.client.mainGuild.default_role)
        overwrites.send_messages = None

        await channel.set_permissions(self.client.mainGuild.default_role, overwrite=overwrites)
        

        embed = discord.Embed(
            color=0x03ff39,
            title="Gift Drop Results"
        )

        # getting shop items
        async with self.client.pool.acquire() as db:
            shop_items = await db.fetch('SELECT name FROM shop;')

            possible_rewards = []

            for item in shop_items: possible_rewards.append(item[0])

            possible_rewards.extend(['money' for _ in range(len(possible_rewards))])
            

            for member_id, count in message_count.items():
                storage_filled = False
                
                reward_count = max(1, count // random.randint(13, 18))

                rewards = []

                items = await db.get_member_val(member_id, 'items')
                storage = await db.get_member_val(member_id, 'storage')

                for _ in range(reward_count):
                    reward = random.choice(possible_rewards)

                    if reward == 'money':
                        reward = random.randint(50, 100)
                    
                    rewards.append(reward)

                    # adding item to user's inventory
                    if isinstance(reward, str):

                        if len(items) < storage:
                            items.append(reward)
                            await db.add_item(member_id, reward)
                        else:
                            storage_filled = True

                
                
                item_count = {}
                money = 0

                for reward in rewards:
                    
                    # if it is an item
                    if isinstance(reward, str):
                        if reward not in item_count.keys():
                            item_count[reward] = 1
                        else:
                            item_count[reward] += 1

                    # if an amount of money
                    else:
                        money += reward
                        
                formatted = []
                
                if money:
                    formatted.append(f"+${money}")

                    bal = await db.get_member_val(member_id, 'money')
                    bal += money
                    await db.set_member_val(member_id, 'money', bal)
                    

                for name, count in item_count.items():
                    formatted.append(f'x{count} {name.capitalize()}')

                if storage_filled:
                    formatted.append("**Not all items were given because of storage limit**")

                embed.add_field(
                    name=guild.get_member(member_id).name,
                    value="\n".join(formatted)
                )

            if not embed.fields:
                embed = discord.Embed(
                color=0x03ff39,
                title="Gift Drop Results",
                description="None"
            )

            await channel.send(embed=embed)

            await channel.send(f"_ _\n\n**Next gift drop in {next_drop}**")




    async def cog_check(self, ctx):

        if ctx.command.name != "snowball":
            if ctx.channel.category.id in (692949972764590160, 692949458551439370, 757374291028213852, 716729977223119018):
                return True

        if ctx.channel.category.id != self.client.rightCategory:
            return False
        else:
            return True

    @commands.command()
    async def christmasupdate(self, ctx):

        if ctx.channel.id != self.client.adminChannel: return

        await self.update_stats()
        await ctx.send("Updated Christmas stats.")

    @commands.command()
    async def writechristmas(self, ctx):

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
            await db.execute("DROP TABLE IF EXISTS hierarchy.christmas;")
            await db.execute("CREATE TABLE hierarchy.christmas (id BIGINT PRIMARY KEY, total INTEGER DEFAULT 0, increase INTEGER DEFAULT 0);")
            await db.execute("INSERT INTO hierarchy.christmas (id, total) SELECT id, money + bank FROM members;")

        await ctx.send("Reset all balances.")
        
        await log_command(self.client, ctx)

    
    @commands.command()
    async def christmasmeter(self, ctx, state=""):

        state = state.lower()

        if state not in ("on", "off"):
            return await ctx.send("Incorrect command usage:\n`.christmasmeter on/off`")

        with open('./storage/jsons/christmas meter.json', 'w') as f:
            json.dump(state, f)
        
        await ctx.send(f"Christmas meter switched {state}.")

        if state == "off":
            async with self.client.pool.acquire() as db:
                self.timer_task = asyncio.create_task(self.gift_drop_timer(await find_next_drop(db)))
        else:
            if self.timer_task and not self.timer_task.done():
                self.timer_task.cancel()

        await log_command(self.client, ctx)

    
    @commands.command()
    async def contribute(self, ctx):

        with open('./storage/jsons/christmas meter.json') as f:
            meter_state = json.load(f)
        
        if meter_state == "off":
            return await ctx.send("The meter can no longer be increased.")

        async with self.client.pool.acquire() as db:
            past_bal = await get_christmas_value(db, ctx.author.id, 'total')
            present_bal = await db.get_member_val(ctx.author.id, 'money + bank')

            difference = present_bal - past_bal

            if difference < 0:
                await ctx.send(f"You have lost ${difference * -1} since last contribution, no money was added to the meter.")
            elif difference == 0:
                await ctx.send(f"You have not gained any money since last contribution, no money was added to the meter.")
            elif difference > 0:
                await ctx.send(f"${difference} added to the meter.")

                increase = await get_christmas_value(db, ctx.author.id, 'increase')
                increase += difference
                await set_christmas_value(db, ctx.author.id, 'increase', increase)

                await set_christmas_value(db, ctx.author.id, 'total', present_bal)
                
                await self.update_stats()

        
    @commands.command()
    async def stats(self, ctx):
        await ctx.send("<#784097174136160326>")


    @commands.command()
    async def cprog(self, ctx, *, member:discord.Member=None):

        if not member:
            member = ctx.author
        
        if not await bot_check(self.client, ctx, member):
            return


        async with self.client.pool.acquire() as db:
            money = await get_christmas_value(db, member.id, 'increase')

        
        await ctx.send(f"**{member.name}** has contributed ${money} to the Christmas event.")

    @commands.command()
    async def caround(self, ctx, find=None, *, member:discord.Member=None):


        if not member: 
            member = ctx.author
        
        if not await bot_check(self.client, ctx, member):
            return

        if not find:
            find = 3
        try:
            find = int(find)

        except:
            await ctx.send('Incorrect command usage:\n`.caround (range) (member)`')
            return

        if find < 1 or find > 12:
            await ctx.send('Enter a number from 1-12 for `range`.')
            return




        userid = member.id
        guild = self.client.mainGuild

        async with self.client.pool.acquire() as db:
            hierarchy = await db.fetch('SELECT id, increase FROM christmas;')

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

        avatar = member.avatar_url_as(static_format='jpg')
        embed = discord.Embed(color=0x03ff39, title=f"🎄 Around {member.name} 🎄", icon_url=avatar)

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
    async def caroundm(self, ctx, find=None, *, member:discord.Member=None):


        if not member: 
            member = ctx.author
        
        if not await bot_check(self.client, ctx, member):
            return

        if not find:
            find = 3
        try:
            find = int(find)

        except:
            await ctx.send('Incorrect command usage:\n`.caroundm (range) (member)`')
            return

        if find < 1 or find > 12:
            await ctx.send('Enter a number from 1-12 for `range`.')
            return



        userid = member.id
        guild = self.client.mainGuild


        async with self.client.pool.acquire() as db:
            hierarchy = await db.fetch('SELECT id, increase FROM christmas;')

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

        avatar = member.avatar_url_as(static_format='jpg')
        embed = discord.Embed(color=0x03ff39, title=f"🎄 Around {member.name} 🎄", icon_url=avatar)

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
    async def snowball(self, ctx, *, member: discord.Member=None):

        if not member:
            return await ctx.send("Incorrect command usage:\n`.snowball member`")
        
        await ctx.send(f"**{ctx.author.name}** snowballed **{member.name}**\n\nhaha dumb")


def setup(client):
    client.add_cog(Christmas(client))