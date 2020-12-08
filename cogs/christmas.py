# pylint: disable=import-error, anomalous-backslash-in-string
import discord
from discord.ext import commands, tasks
import json
import time
import datetime
import os
import asyncio
import sqlite3
import random

# To import from different path
import sys
sys.path.insert(1 , os.getcwd())

from utils import log_command, read_value, write_value, add_item, splittime

money_requirement = 3000

def get_christmas_value(userid, value):

    conn = sqlite3.connect('./storage/databases/hierarchy.db')
    c = conn.cursor()

    c.execute(f"SELECT {value} FROM christmas WHERE id = ?", (userid,))
    result = c.fetchone()

    if not result:
        c.execute("INSERT INTO christmas (id) VALUES (?)", (userid,))
        conn.commit()

        result = 0

    else:
        result = result[0]
    
    conn.close()
    return result

def write_christmas_value(userid, value, overwrite):

    conn = sqlite3.connect('./storage/databases/hierarchy.db')
    c = conn.cursor()

    c.execute("SELECT id FROM christmas WHERE id = ?", (userid,))
    exists = c.fetchone()

    if not exists:
        c.execute("INSERT INTO christmas (id) VALUES (?)", (userid))

    c.execute(f"UPDATE christmas SET {value} = ? WHERE id = ?", (overwrite, userid))

    conn.commit()
    conn.close()
    

def find_next_drop():

    conn = sqlite3.connect('./storage/databases/hierarchy.db')
    c = conn.cursor()
    c.execute("SELECT SUM(increase) FROM christmas;")
    total_bal = c.fetchone()[0]
    conn.close()

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
            self.timer_task = asyncio.create_task(self.gift_drop_timer(find_next_drop()))

        asyncio.create_task( self.update_stats() )
    
    def cog_unload(self):
        
        if self.timer_task and not self.timer_task.done():
            self.timer_task.cancel()
        
        if self.drop_task and not self.drop_task.done():
            self.drop_task.cancel()

    async def gift_drop_timer(self, duration):

        if duration == 0:
            return

        await asyncio.sleep(65)

        conn = sqlite3.connect('./storage/databases/hierarchy.db')
        c = conn.cursor()
        c.execute("SELECT SUM(increase) FROM christmas;")
        total_bal = c.fetchone()[0]
        conn.close()

        drops = total_bal // money_requirement

        next_time = time.time() + ((1440/drops) * 60)

        self.drop_task = asyncio.create_task(self.giftdrop( splittime(int(next_time))) )

        self.timer_task = asyncio.create_task(self.gift_drop_timer( next_time-time.time() ))
        

    async def update_stats(self):

        channel_id = 784097174136160326
        meter_id = 784097932030509096
        leaderboard_id = 784103963380678677

        conn = sqlite3.connect('./storage/databases/hierarchy.db')
        c = conn.cursor()
        try:
            c.execute("SELECT SUM(increase) FROM christmas;")
        except:
            conn.close()
            return
        total_bal = c.fetchone()[0]

        c.execute("SELECT id, increase FROM christmas ORDER BY increase DESC")
        members = c.fetchall()
        conn.close()

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

        embed = discord.Embed(color=0x03ff39, title="Contribution leaderboard")
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
        conn = sqlite3.connect('./storage/databases/shop.db')
        c = conn.cursor()
        c.execute('SELECT name FROM shop')
        shop_items = c.fetchall()
        conn.close()

        possible_rewards = []

        for item in shop_items: possible_rewards.append(item[0])

        possible_rewards.extend(['money' for _ in range(len(possible_rewards))])
        

        for member_id, count in message_count.items():
            storage_filled = False
            
            reward_count = max(1, count // random.randint(13, 18))

            rewards = []

            items = read_value(member_id, 'items').split()
            storage = read_value(member_id, 'storage')

            for _ in range(reward_count):
                reward = random.choice(possible_rewards)

                if reward == 'money':
                    reward = random.randint(50, 100)
                
                rewards.append(reward)

                # adding item to user's inventory
                if isinstance(reward, str):

                    if len(items) < storage:
                        items.append(reward)
                        add_item(reward, member_id)
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

                bal = read_value(member_id, 'money')
                bal += money
                write_value(member_id, 'money', bal)
                

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
        
        conn = sqlite3.connect('./storage/databases/hierarchy.db')
        c = conn.cursor()
        c.execute("DROP TABLE IF EXISTS christmas;")
        c.execute("CREATE TABLE christmas (id INTEGER PRIMARY KEY, total INTEGER DEFAULT 0, increase INTEGER DEFAULT 0);")
        c.execute("INSERT INTO christmas (id, total) SELECT id, money + bank FROM members;")
        conn.commit()
        conn.close()
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
            self.timer_task = asyncio.create_task(self.gift_drop_timer(find_next_drop()))
        else:
            if self.timer_task and not self.timer_task.done():
                self.timer_task.cancel()

    
    @commands.command()
    async def contribute(self, ctx):

        with open('./storage/jsons/christmas meter.json') as f:
            meter_state = json.load(f)
        
        if meter_state == "off":
            return await ctx.send("The meter can no longer be increased.")

        past_bal = get_christmas_value(ctx.author.id, 'total')
        present_bal = read_value(ctx.author.id, 'money + bank')

        difference = present_bal - past_bal

        if difference < 0:
            await ctx.send(f"You have lost ${difference * -1} since last contribution, no money was added to the meter.")
        elif difference == 0:
            await ctx.send(f"You have not gained any money since last contribution, no money was added to the meter.")
        elif difference > 0:
            await ctx.send(f"${difference} added to the meter.")

            increase = get_christmas_value(ctx.author.id, 'increase')
            increase += difference
            write_christmas_value(ctx.author.id, 'increase', increase)

            write_christmas_value(ctx.author.id, 'total', present_bal)
            
            await self.update_stats()

        
    @commands.command()
    async def stats(self, ctx):
        await ctx.send("<#784097174136160326>")


def setup(client):
    client.add_cog(Christmas(client))