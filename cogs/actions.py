# pylint: disable=import-error

import asyncio
import json
import random
import sqlite3
import time
import os
from sqlite3 import Error

import discord
from discord.ext import commands
from discord.ext.commands import BadArgument, CommandNotFound, MaxConcurrencyReached

from cogs.extra.itemuse import ItemUses

# To import from different path
import sys
sys.path.insert(1 , os.getcwd())

from utils import (read_value, write_value, update_total, leaderboard,
rolecheck, splittime, open_heist, bot_check, in_use, jail_heist_check, around,
remove_item, remove_use, add_item, write_heist, add_use, level_check, event_disabled)

async def heist_group_jailcheck(ctx):

    jailtime = read_value(ctx.author.id, 'jailtime')        
    if jailtime > time.time():
        await ctx.send(f'You are still in jail for {splittime(jailtime)}.')
        return False
    return True


class actions(commands.Cog):

    def __init__(self, client):
        self.client = client


    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):

        error = getattr(error, 'original', error)

        if isinstance(error, MaxConcurrencyReached):
            if ctx.command.name == 'work':
                await ctx.send("Someone is already working in this channel.")
                

    async def cog_check(self, ctx):
        if ctx.channel.category.id != self.client.rightCategory:
            return False
        else:
            return True


    @commands.command()
    @commands.max_concurrency(1, per=commands.BucketType.channel)
    async def work(self, ctx):
        author = ctx.author

        
        if not await jail_heist_check(ctx, ctx.author):
            return

        workc = read_value(author.id, 'workc')
        if workc > time.time():
            await ctx.send(f'You must wait {splittime(workc)} before you can work again.')
            return

        flag = 0

        with open('./storage/jsons/mode.json') as f:
            mode = json.load(f)

        if ctx.author.premium_since and mode != "event":
            premium = True
        else:
            premium = False

        if ctx.author.premium_since and mode == "event":
            await ctx.send("*Premium perks are disabled during events*")
            await asyncio.sleep(2)

        for x in range(5):
            if x >= 3 and not premium:
                break
            elif x == 3 and premium:
                await ctx.send(f"**{author.name}** has __premium__ and gets two extra tasks!")
                await asyncio.sleep(2)
                
            task = random.randint(1,2)
            await ctx.send("Get ready...")
            await asyncio.sleep(3)
            if task == 1:
                opening = open('./storage/other/englishwords.txt')
                words = opening.read()
                wordlist = words.splitlines()
                ucolors = ['\U0001f534','\U000026aa',
                          '\U0001f7e3','\U0001f7e0','\U0001f535',
                          '\U0001f7e4','\U0001f7e2']
                colorfinder = [{'code':'\U0001f534','name':'red'},
                               {'code':'\U000026aa','name':'white'},
                               {'code':'\U0001f7e3','name':'purple'},
                               {'code':'\U0001f7e0','name':'orange'},
                               {'code':'\U0001f535','name':'blue'},
                               {'code':'\U0001f7e4','name':'brown'},
                               {'code':'\U0001f7e2','name':'green'}]
                pairs = []
                messagecontent = '**Memorize this!**\n'
                for y in range(3):
                    rcolor = random.choice(ucolors)
                    rword = random.choice(wordlist)
                    pairs.append({'color':rcolor,'word':rword})
                    wordlist.pop(wordlist.index(rword))
                    ucolors.pop(ucolors.index(rcolor))
                    addmessage = f'{pairs[y]["color"]}  {pairs[y]["word"]}'
                    messagecontent = f'{messagecontent}\n{addmessage}'
                message = await ctx.send(messagecontent)
                await asyncio.sleep(3)
                ask = random.randint(1,2)
                pair = random.randint(0,2)
                for color in colorfinder:
                    if color["code"] == pairs[pair]["color"]:
                        colorname = color["name"]
                def check(m):
                    return m.channel == ctx.channel and m.author == ctx.author
                if ask == 1:
                    await message.edit(content=f"What color was next to {pairs[pair]['word']}?")
                    try:
                        answer = await self.client.wait_for('message', check=check, timeout=20)
                        if answer.content.lower() != colorname:
                            await ctx.send(f"Incorrect. The answer was {colorname}.\n{flag}/{x+1} tasks successful.")
                        elif answer.content.lower() == colorname:
                            flag += 1
                            await ctx.send(f"Correct.\n{flag}/{x+1} tasks successful.")
                    except asyncio.TimeoutError:
                        await ctx.send(f"Took too long. The answer was {colorname}.\n{flag}/{x+1} tasks successful.")
                elif ask == 2:
                    await message.edit(content=f"What word was next to {colorname}?")
                    try:
                        answer = await self.client.wait_for('message', check=check, timeout=20)
                        if answer.content.lower() != pairs[pair]["word"].lower():
                            await ctx.send(f"Incorrect. The answer was {pairs[pair]['word']}.\n{flag}/{x+1} tasks successful.")
                        elif answer.content.lower() == pairs[pair]["word"].lower():
                            flag += 1
                            await ctx.send(f"Correct.\n{flag}/{x+1} tasks successful.")
                    except asyncio.TimeoutError:
                        await ctx.send(f"Took too long. The answer was {pairs[pair]['word']}.\n{flag}/{x+1} tasks successful.")
                await asyncio.sleep(2)
                
            if task == 2:
                await ctx.send("Solve this in 5 seconds:")
                mod = random.randint(1,2)
                aos = random.randint(1,2)
                if mod == 1:
                    n1 = random.randint(2,9)
                    n2 = random.randint(2,9)
                    if aos == 1:
                        n3 = random.randint(1,10)
                        answer = (n1 * n2) + n3
                        order = random.randint(1,2)
                        if order == 1:
                            await ctx.send(f"{n1} x {n2} + {n3}")
                        elif order == 2:
                            await ctx.send(f"{n3} + {n2} x {n1}")
                    if aos == 2:
                        n3 = random.randint(1,10)
                        answer = (n1 * n2) - n3
                        order = random.randint(1,2)
                        if order == 1:
                            await ctx.send(f"{n1} x {n2} - {n3}")
                        elif order == 2:
                            await ctx.send(f"-{n3} + {n2} x {n1}")

                if mod == 2:
                    t1 = random.randint(2,9)
                    t2 = random.randint(2,9)
                    t3 = t1 * t2
                    n1 = t3
                    n2 = t1
                    if aos == 1:
                        n3 = random.randint(1,10)
                        answer = t2 + n3
                        order = random.randint(1,2)
                        if order == 1:
                            await ctx.send(f"{n1} / {n2} + {n3}")
                        elif order == 2:
                            await ctx.send(f"{n3} + {n1} / {n2}")
                    if aos == 2:
                        n3 = random.randint(1,10)
                        answer = t2 - n3
                        order = random.randint(1,2)
                        if order == 1:
                            await ctx.send(f"{n1} / {n2} - {n3}")
                        elif order == 2:
                            await ctx.send(f"-{n3} + {n1} / {n2}")
                try:
                    submission = await self.client.wait_for('message', check=lambda m: m.channel == ctx.channel and m.author == ctx.author, timeout=5)
                    answer = str(answer)
                    submission = str(submission.content)
                    if submission == answer:
                        flag += 1
                        await ctx.send(f'Correct.\n{flag}/{x+1} tasks successful.')
                    elif submission != answer:
                        await ctx.send(f'Incorrect. The answer was {answer}.\n{flag}/{x+1} tasks successful.')
                except asyncio.TimeoutError:
                    await ctx.send(f'Times up! The answer was {answer}.\n{flag}/{x+1} tasks successful.')
                await asyncio.sleep(2)
            

        




        if flag == 0:
            earnings = random.randint(10,20)
        elif flag == 1:
            earnings = random.randint(20,35)
        elif flag == 2:
            earnings = random.randint(40,50)
        elif flag == 3:
            earnings = random.randint(60,70)
        elif flag == 4:
            earnings = random.randint(70,80)
        elif flag == 5:
            earnings = random.randint(80,90)        
        await ctx.send(f"💰 **{author.name}** worked and successfully completed {flag} tasks, earning ${earnings}. 💰")
        money = read_value(author.id, 'money')
        money += earnings
        write_value(author.id, 'money', money)
        update_total(author.id)
        workc = int(time.time()) + 3600
        write_value(author.id, 'workc', workc)
        await leaderboard(self.client)
        await rolecheck(self.client, author.id)


    @commands.command()
    async def bail(self, ctx, member:discord.Member=None):

        author = ctx.author

        if not await level_check(ctx, author.id, 2, "bail someone"):
            return

        if member==author:
            await ctx.send("You can't bail yourself.")

            if 'pass' in read_value(author.id, 'items').split():
                await asyncio.sleep(2)
                await ctx.send("*Have a pass? Use the command `.use pass` to use it.*")

            return

        if not await jail_heist_check(ctx, ctx.author):
            return

        if not member: 
            await ctx.send("Incorrect command usage:\n`.bail member`")
            return

        # No heist jail check function here because of special command
        
        heist = open_heist()
        if heist["heistv"] == ctx.author.id:
            await ctx.send(f"You are currently being targeted for a heist.")
            return

        if ctx.author.id in heist["heistp"]:
            await ctx.send(f"You are participating in a heist right now.")
            return

        jailtime = read_value(member.id, 'jailtime')
        if jailtime < time.time():
            await ctx.send(f"**{member.name}** is not in jail.")
            return
        else:
            bailprice = self.client.bailprice(jailtime)

        money = read_value(author.id, 'money')
        if bailprice > money:
            await ctx.send("You don't have enough money for that.")
            return
        else:
            money -= bailprice
            write_value(author.id, 'money', money)
            update_total(author.id)
            await ctx.send(f'💸 **{author.name}** spent ${bailprice} to bail **{member.name}**. 💸')
            write_value(member.id, 'jailtime', int(time.time()))
        await leaderboard(self.client)
        await rolecheck(self.client, member.id)
        await rolecheck(self.client, author.id)

                
    @commands.command()
    @commands.check(event_disabled)
    async def pay(self, ctx, member:discord.Member=None, amount=None):
        author = ctx.author

        if not await jail_heist_check(ctx, ctx.author):
            return

        if not member or not amount: 
            await ctx.send("Incorrect command usage:\n`.pay member amount`")
            return
        
        if not await bot_check(self.client, ctx, member):
            return

        if member == author:
            await ctx.send(f"You can't pay yourself.")
            return


        money = read_value(author.id, 'money')
        if amount.lower() == 'all':
            amount = money
            if not amount:
                await ctx.send("You don't have any money to pay.")
                return
        try:
            amount = int(amount)
        except:
            await ctx.send("Incorrect command usage:\n`.pay member amount`")
            return
        if amount <= 0:
            await ctx.send("Enter an amount above 0.")
            return

        if money < amount:
            await ctx.send("You don't have enough money for that.")
        else:

            money -= amount
            write_value(author.id, 'money', money)
            update_total(author.id)


            money = read_value(member.id, 'money')
            money += amount
            write_value(member.id, 'money', money)



            update_total(author.id)
            update_total(member.id)
            await ctx.send(f"**{author.name}** payed **{member.name}** ${amount}.")

        await leaderboard(self.client)
        await rolecheck(self.client, author.id)
        await rolecheck(self.client, member.id)

    @commands.command()
    @commands.max_concurrency(1, per=commands.BucketType.member)
    async def steal(self, ctx, member:discord.Member=None, amount=None):
        author = ctx.author


        if not await jail_heist_check(ctx, ctx.author):
            return

        if not member or not amount: 
            await ctx.send("Incorrect command usage:\n`.steal member amount`")
            return
        
        if not await bot_check(self.client, ctx, member):
            return


        if member == author:
            await ctx.send(f"You can't steal from yourself.")
            return

        try:
            amount=int(amount)

        except:
            await ctx.send("Incorrect command usage:\n`.steal member amount`")
            return

        if amount < 1 or amount > 200:
            await ctx.send("Enter an amount from 1-200.")
            return

        stealc = read_value(author.id, 'stealc')
        if stealc > time.time():
            await ctx.send(f'You must wait {splittime(stealc)} before you can steal again.')
            return

        guild = self.client.mainGuild
        if member.id not in around(guild, author.id, 3):
            await ctx.send(f"This user is not within a range of 3 from you.")
            if read_value(author.id, 'rangeinformed') == "False":
                await asyncio.sleep(5)
                image = discord.File('./storage/images/stealinfo.png')
                await ctx.send("*Not sure what this means?*\n**Use the .around command. You may steal from anyone who up to 3 places above you or below you.**", file=image)
                write_value(author.id, 'rangeinformed', '"True"')
            return

        # gang warning
        conn = sqlite3.connect('./storage/databases/gangs.db')
        c = conn.cursor()
        c.execute('SELECT owner, members FROM gangs')
        gangs = c.fetchall()
        conn.close()

        money = read_value(member.id, 'money')
        if money < amount:
            await ctx.send("This user does not have that much money in cash.") # linked to tutorial, change tutorial if this message changes
            return

        for owner, members in gangs:

            if str(ctx.author.id) in members or ctx.author.id == owner:

                if str(member.id) in members or member.id == owner:

                    await ctx.send("This user is in your gang. Are you sure you want to continue? Respond with `y` or `yes` to proceed.")

                    try:
                        response = await self.client.wait_for('message', check=lambda m: m.author == ctx.author and m.channel == ctx.channel, timeout=20)
                    except asyncio.TimeoutError:
                        await ctx.send("Steal timed out.")
                        return
                    
                    response = response.content.lower()

                    if response == 'y' or response == 'yes':
                        await ctx.send("Steal proceeded.")
                        await asyncio.sleep(1)
                    else:
                        await ctx.send("Steal cancelled.")
                        return



        if 'padlock' in in_use(member.id):
            remove_use('padlock', member.id)
            stealc = int(time.time()) + 10800
            write_value(author.id, 'stealc', stealc)
            if random.randint(1,4) == 1:
                if 'gun' in in_use(author.id):
                    if random.randint(1,2) == 1:
                        await ctx.send(f"**{member.name}** had a padlock in use and **{author.name}** broke the padlock instead. They were also caught but got away with their gun.")
                        return
                await ctx.send(f"**{member.name}** had a padlock in use and **{author.name}** broke the padlock instead. They were also caught and jailed for 1h 30m.")
                jailtime = int(time.time()) + 5400
                write_value(author.id, 'jailtime', jailtime)
            else:
                await ctx.send(f"**{member.name}** had a padlock in use and **{author.name}** broke the padlock instead.")
            return

        else:
            stealc = int(time.time()) + 10800
            write_value(author.id, 'stealc', stealc)
            randomer = amount - 23
            if randomer <= 0:
                randomer = random.randint(1,10)
            if random.randint(1,200) <= randomer:
                if 'gun' in in_use(author.id):
                    if random.randint(1,2) == 1:
                        await ctx.send(f"**{author.name}** was caught stealing but got away with their gun.")
                        await rolecheck(self.client, author.id)
                        await rolecheck(self.client, member.id)
                        return
                jailtime = int(int(time.time()) + amount*100.5)
                write_value(author.id, 'jailtime', jailtime)
                await ctx.send(f'**{author.name}** was caught stealing and sent to jail for {splittime(jailtime)}.')
                    
            else:
                await ctx.send(f"**{author.name}** successfully stole ${amount} from **{member.name}**.")
                money -= amount
                write_value(member.id, 'money', money)
                update_total(member.id)
                money = read_value(author.id, 'money')
                money += amount
                write_value(author.id, 'money', money)
                update_total(author.id)
        await leaderboard(self.client)
        await rolecheck(self.client, author.id)
        await rolecheck(self.client, member.id)

        
    @commands.command(aliases=['dep'])
    async def deposit(self, ctx, amount=None):
        author = ctx.author
        
        if not await level_check(ctx, author.id, 2, "use the bank"):
            return

        if not await jail_heist_check(ctx, ctx.author):
            return

        bankc = read_value(author.id, 'bankc')
        if bankc > time.time():
            await ctx.send(f'You must wait {splittime(bankc)} before you can access your bank again.')
            return

        if not amount: 
            await ctx.send("Incorrect command usage:\n`.deposit amount`")
            return
        

        money = read_value(author.id, 'money')
        if amount.lower()=='all':
            amount = money
            if amount == 0:
                await ctx.send("You don't have any money to deposit.")
                return
        try:
            amount=int(amount)
        except:
            await ctx.send("Incorrect command usage:\n`.deposit amount`")
            return
        if amount <= 0:
            await ctx.send(f"Enter an amount greater than 0.")
            return
        if amount > money:
            await ctx.send("You do not have that much cash.")
            return
        else:
            money -= amount
            bank = read_value(author.id, 'bank')
            bank += amount
            bankc = int(time.time()) + 600
            write_value(author.id, 'money', money)
            write_value(author.id, 'bank', bank)
            write_value(author.id, 'bankc', bankc)
            hbank = read_value(author.id, 'hbank')
            if bank > hbank:
                write_value(author.id, 'hbank', bank)
            await ctx.send(f"🏦 Deposited ${amount} to your bank. 🏦")


    @commands.command(aliases=['with'])
    async def withdraw(self, ctx, amount=None):
        author = ctx.author

        if not await level_check(ctx, author.id, 2, "use the bank"):
            return

        if not await jail_heist_check(ctx, ctx.author):
            return        

        bankc = read_value(author.id, 'bankc')
        if bankc > time.time():
            await ctx.send(f'You must wait {splittime(bankc)} before you can access your bank again.')
            return

        if not amount: 
            await ctx.send("Incorrect command usage:\n`.withdraw amount`")
            return

        bank = read_value(author.id, 'bank')
        if amount.lower()=='all':
            amount = bank
            if amount == 0:
                await ctx.send("You don't have any money to withdraw.")
                return
        try:
            amount=int(amount)
        except:
            await ctx.send(f"Incorrect command usage:\n`.withdraw amount`")
            return
        if amount <= 0:
            await ctx.send(f"Enter an amount greater than 0.")
            return
        if amount > bank:
            await ctx.send("You do not have that much money in your bank.")
            return
        else:
            money = read_value(author.id, 'money')
            money += amount
            bank -= amount
            bankc = int(time.time()) + 600
            write_value(author.id, 'money', money)
            write_value(author.id, 'bank', bank)
            write_value(author.id, 'bankc', bankc)
            await ctx.send(f"🏦 Withdrew ${amount} from your bank. 🏦")




    @commands.group(invoke_without_command=True)
    async def heist(self, ctx):
        
        await ctx.send(f'Incorrect command usage:\n`.heist start/join/list/leave/cancel`')

    @heist.command()
    @commands.check(heist_group_jailcheck)
    async def start(self, ctx, *, member:discord.Member=None):
        conn = sqlite3.connect('./storage/databases/heist.db')
        c = conn.cursor()
        c.execute(f'SELECT cooldown FROM heist')
        heistc = c.fetchone()[0]
        conn.close()

        heist = open_heist()
        author = ctx.author

        if heistc > time.time():
                await ctx.send(f'Everyone must wait {splittime(heistc)} before another heist be made.')
                return
        elif heist["oheist"] == "True":
            await ctx.send(f'There is already an ongoing heist.')
            return
        elif not member:
            await ctx.send(f'Incorrect command usage:\n`.heist start member`')
            return
        elif author == member:
            await ctx.send(f"You can't heist yourself.")
            return
        
        if not await bot_check(self.client, ctx, member):
            return

        bank = read_value(member.id, 'bank')
        if bank < 100:
            await ctx.send(f'The victim must have at least $100 in their bank in order to be heisted from.')
            return
        await ctx.send(f'Heist started. You have two minutes to gather at least two more people to join the heist.')
        heist["heistv"] = member.id
        heist["oheist"] = "True"
        heist["heistp"].append(author.id)
        heist["heistl"] = ctx.channel.id
        heist["heistt"] = 120
        write_heist(heist)

    @heist.command()
    @commands.check(heist_group_jailcheck)
    async def join(self, ctx):
        heist = open_heist()
        author = ctx.author
        guild = self.client.mainGuild

        if heist["heistv"] == author.id:
                await ctx.send(f"You are the target of this heist.")
                return
        if heist["oheist"] == "False":
            await ctx.send(f"There is no ongoing heist right now.")
            return
        if author.id in heist["heistp"]:
            await ctx.send(f"You are already in this heist.")
            return
        heist["heistp"].append(author.id)
        await ctx.send(f'**{author.name}** has joined the heist on **{guild.get_member(heist["heistv"]).name}**.')
        write_heist(heist)

    @heist.command()
    @commands.check(heist_group_jailcheck)
    async def leave(self, ctx):
        heist = open_heist()
        author = ctx.author
        guild = self.client.mainGuild

        if heist["oheist"] == "False":
            await ctx.send(f"There is no ongoing heist right now.")
            return
        if author.id not in heist["heistp"]:
            await ctx.send("You aren't participating in a heist.")
            return
        if heist["heistp"][0] == author.id:
            await ctx.send("You are leading this heist.")
            return
        heist["heistp"].remove(author.id)
        await ctx.send(f'**{author.name}** has left the heist on **{guild.get_member(heist["heistv"]).name}**.')
        write_heist(heist)

    @heist.command()
    @commands.check(heist_group_jailcheck)
    async def cancel(self, ctx):
        heist = open_heist()
        author = ctx.author

        if heist["oheist"] == "False":
            await ctx.send(f"There is no ongoing heist right now.")
            return
        if author.id not in heist["heistp"]:
            await ctx.send("You aren't participating in a heist.")
            return
        if heist["heistp"][0] != author.id:
            await ctx.send("You are not leading this heist.")
            return
        elif heist["heistp"][0] == author.id:
            heist["heistv"] = 0
            heist["heistt"] = 0
            heist["heistp"] = []
            heist["heistl"] = 0
            heist["oheist"] = "False"
            await ctx.send("Heist cancelled: Heist cancelled by leader.")
            write_heist(heist)


    @heist.command(name="list")
    @commands.check(heist_group_jailcheck)
    async def heist_list(self, ctx):
        heist = open_heist()
        guild = self.client.mainGuild

        if heist["oheist"] == "False":
                await ctx.send(f"There is no ongoing heist right now.")
                return

        embed = discord.Embed(color=0xff1414)
        embed.set_author(name=f'Heist on {guild.get_member(heist["heistv"]).name}')
        for person in heist["heistp"]:
            embed.add_field(value=f'{guild.get_member(person).name}', name='__________', inline=True)
        await ctx.send(embed=embed)
        write_heist(heist)

    @commands.command(aliases=['purchase'])
    @commands.max_concurrency(1, per=commands.BucketType.member)
    async def buy(self, ctx, *, item=None):
        author = ctx.author

        if not await level_check(ctx, author.id, 4, "use items"):
            return

        if not await jail_heist_check(ctx, ctx.author):
            return

        if not item: 
            await ctx.send("Incorrect command usage:\n`.buy item`")
            return
        
         
        conn = sqlite3.connect('./storage/databases/shop.db')
        c = conn.cursor()
        c.execute('SELECT name, price, article FROM shop')
        temp = c.fetchall()
        conn.close()

        items = list(map(lambda x: {'name':x[0], 'cost':x[1], 'article': x[2]}, temp))

        for x in items:

            if x["name"] == item.lower():

                money = read_value(author.id, 'money')

                with open('./storage/jsons/mode.json') as f:
                    mode = json.load(f)

                if ctx.author.premium_since and mode == "event":
                    await ctx.send("*Premium perks are disabled during events*")
                    await asyncio.sleep(2)

                elif ctx.author.premium_since:
                    x["cost"] -= int(x["cost"] * 0.3)

                if money < x["cost"]:
                    
                    bank = read_value(author.id, 'bank')
                    if bank + money >= x["cost"] and read_value(author.id, 'bankc') < time.time():
                        missing = x["cost"] - money
                        await ctx.send(f"Would you like to automatically withdraw the missing ${missing} from your bank? Respond with `yes` or `y` to proceed.")

                        try:
                            response = await self.client.wait_for('message', check=lambda msg: msg.author == author and msg.channel == ctx.channel, timeout=20)
                        except asyncio.TimeoutError:
                            await ctx.send("Bank withdrawal timed out.")
                            return
                        
                        response = response.content.lower()
                        if response == 'yes' or response == 'y':
                            bank -= missing
                            money += missing
                            write_value(author.id, 'bank', bank)
                            write_value(author.id, 'money', money)
                            write_value(author.id, 'bankc', 600)
                            await ctx.send(f"Withdrew ${missing} from your bank.")
                            await asyncio.sleep(1)

                        else:
                            await ctx.send("Bank withdrawal cancelled.")
                            return
                        

                    else:
                        await ctx.send("You don't have enough money for that.")
                        return

                storage = read_value(author.id, 'storage')

                if len(read_value(author.id, 'items').split()) >= storage:
                    await ctx.send(f"You can only carry a maximum of {storage} items.")
                    return

                money -= x["cost"]
                write_value(author.id, 'money', money)
                update_total(author.id)
                add_item(x['name'], author.id)
                await ctx.send(f"**{author.name}** purchased {x['article']}**{x['name']}** for ${x['cost']}.")
                await rolecheck(self.client, author.id)
                await leaderboard(self.client)
                return
            
        await ctx.send(f"There is no such item called \"{item}\".")


    @commands.command()
    async def use(self, ctx, *, item=None):
        author = ctx.author

        if not await level_check(ctx, author.id, 4, "use items"):
            return

        jailtime = read_value(author.id, 'jailtime')     
        # Don't use checks here because pass is an exception   

        if item:
            if item.lower() != 'pass':
                if jailtime > time.time():
                    await ctx.send(f'You are still in jail for {splittime(jailtime)}.')
                    return

        heist = open_heist()
        if heist["heistv"] == author.id:
            await ctx.send(f"You are currently being targeted for a heist.")
            return
        if author.id in heist["heistp"]:
            await ctx.send(f"You are participating in a heist right now.")
            return

        if not item:
            await ctx.send("Incorrect command usage:\n`.use item`")
            return
            
        conn = sqlite3.connect('./storage/databases/shop.db')
        c = conn.cursor()
        c.execute('SELECT name, article FROM shop')
        items = c.fetchall()
        conn.close()

        items = list(map(lambda x: {'name': x[0], 'article': x[1]}, items))

        item = item.lower()

        exists = False
        for shopitem in items:
            if item in shopitem.values():
                exists = True
                break

        if not exists:
            await ctx.send(f"There is no such item called \"{item}\".")
            return

        for shopitem in items:
            if item == shopitem['name']:
                article = shopitem['article']
                break

        if item not in read_value(author.id, 'items').split():
            await ctx.send(f"You do not own {article}**{item}**.")
            return

        if item in in_use(author.id):
            await ctx.send(f"You already have {article}**{item}** in use.")
            return
            
        await ItemUses(self.client).dispatch(ctx, item)
        

    @commands.command()
    @commands.check(event_disabled)
    async def give(self, ctx, member: discord.Member=None, *, item=None):
        
        if not member or not item:
            await ctx.send("Incorrect command usage:\n`.give member item`")
            return

        elif not await jail_heist_check(ctx, ctx.author): return
        
        elif not await bot_check(self.client, ctx, member): return

        elif read_value(member.id, 'level') < 4:
            await ctx.send(f"**{member.name}** must be at least level 4 in order to use items.")
            return
        
        conn = sqlite3.connect('./storage/databases/shop.db')
        c = conn.cursor()
        c.execute('SELECT name, article FROM shop')
        items = c.fetchall()
        conn.close()

        item = item.lower()

        for shopitem in items:
            if item == shopitem[0]:
                picked_item = shopitem
                break
        else:
            await ctx.send(f"There is no such item called **{item}**.")
            return

        if item not in read_value(ctx.author.id, 'items').split():
            await ctx.send(f"You do not own {picked_item[1]}**{picked_item[0]}**.")
            return

        elif len(read_value(member.id, 'items').split()) >= read_value(member.id, 'storage'):
            await ctx.send(f"**{member.name}**'s item inventory is full.")
            return

        remove_item(item, ctx.author.id)
        add_item(item, member.id)
        await ctx.send(f"You gave {picked_item[1]}**{picked_item[0]}** to **{member.name}**.")
    

    @commands.command()
    async def discard(self, ctx, *, item=None):
        author = ctx.author

        
        if not await jail_heist_check(ctx, ctx.author):
            return

        if not item: 
            await ctx.send("Incorrect command usage:\n`.discard item`")
            return

        conn = sqlite3.connect('./storage/databases/shop.db')
        c = conn.cursor()
        c.execute('SELECT name, article FROM shop')
        items = c.fetchall()
        conn.close()

        item = item.lower()

        for shopitem in items:
            if item == shopitem[0]:
                picked_item = shopitem
                break

        else:
            await ctx.send(f"There is no such item called **{item}**.")
            return


        if item not in read_value(author.id, 'items').split():
            await ctx.send(f"You do not own {picked_item[1]}**{picked_item[0]}**.")
            return

        remove_item(item, author.id)
        await ctx.send(f'**{author.name}** discarded {picked_item[1]}**{picked_item[0]}**.')
        
    @commands.command()
    @commands.max_concurrency(1, per=commands.BucketType.member)
    async def daily(self, ctx):
        author = ctx.author
        dailytime = read_value(author.id, 'dailytime')
        if dailytime == 0:
            dailytime = int(time.time())-1
        timeDifference = int(dailytime - time.time())// 86400 # Number of seconds in a day 
        rewards = [40, 50, 60, 70, 80, 90, 100, 0]
        if timeDifference >= 0:
            await ctx.send(f"You must wait {splittime(dailytime)} before you can claim your next reward.")
            return

        elif timeDifference <= -2:
            streak = 0

        else:
            streak = read_value(author.id, 'dailystreak')

        reward = rewards[streak]
        streak += 1
        nextreward = rewards[streak]

        if streak < 7:
            
            if streak != 6:
                await ctx.send(f"You've earned ${reward}. Come back tomorrow for ${nextreward}!\n*Current streak: {streak}*")
            
            else:
                level = read_value(author.id, 'level')
                if level >= 4:
                    await ctx.send(f"You've earned ${reward}. Come back tomorrow for ${nextreward}, along with a random shop item!\n*Current streak: {streak}*")
                else:
                    await ctx.send(f"You've earned ${reward}. Come back tomorrow for ${nextreward}!\n*Current streak: {streak}*")

            money = read_value(author.id, 'money')
            money += reward
            write_value(author.id, 'money', money)
            await rolecheck(self.client, author.id)
            await leaderboard(self.client)

        else:

            skip = False
            storage = read_value(author.id, 'storage')
            level = read_value(author.id, 'level')

            if level >= 4:
                if len(read_value(author.id, 'items').split()) >= storage:
                    await ctx.send(f"You can only carry a maximum {storage} items. Do you want to discard the shop item you recieve automatically? (Yes/No)")
                    try:
                        answer = await self.client.wait_for('message', check=lambda m: m.channel == ctx.channel and m.author == author, timeout=20)
                        if answer.content.lower() == 'yes' or answer.content.lower() == 'y':
                            skip = True
                        else:
                            await ctx.send('Reward not taken.')
                            return
                    except asyncio.TimeoutError:
                        await ctx.send(f"Took too long: Reward not taken.")
                        return


                # Grabbing shop item
                if not skip:

                    conn = sqlite3.connect('./storage/databases/shop.db')
                    c = conn.cursor()
                    c.execute('SELECT name, article FROM shop')
                    items = c.fetchall()
                    conn.close()
                    item = random.choice(items)
                    item, article = item
                    

                    await ctx.send(f"You've earned ${reward}, along with {article}**{item}**!\n*Streak reset to 0.*")
                    add_item(item, author.id)

                else:
                    await ctx.send(f"You've earned ${reward}!\n*Streak reset to 0.*")
            else:
                await ctx.send(f"You've earned ${reward}!\n*Streak reset to 0.*")
            streak = 0
            write_value(author.id, 'dailystreak', 0)
            money = read_value(author.id, 'money')
            money += reward
            write_value(author.id, 'money', money)
            await rolecheck(self.client, author.id)
            await leaderboard(self.client)

        write_value(author.id, 'dailystreak', streak)
        if timeDifference <= -2:
            dailytime = int(time.time()) + 86400
        else:
            dailytime += 86400
        write_value(author.id, 'dailytime', dailytime)
        update_total(author.id)

    @commands.command()
    async def claim(self, ctx):
        author = ctx.author

        if not await jail_heist_check(ctx, ctx.author):
            return

        with open('./storage/jsons/wallet.json') as json_file:
            walletinfo = json.load(json_file)
        
        if walletinfo["channel"] == ctx.channel.id:
            earnings = random.randint(100,150)
            money = read_value(author.id, 'money')
            money += earnings
            write_value(author.id, "money", money)
            update_total(author.id)
            await leaderboard(self.client)
            await ctx.send(f"**{author.name}** claimed the wallet and earned ${earnings}.")

            newinfo = {}
            newinfo["timer"] = int(time.time()) + random.randint(21600, 25200)
            newinfo["channel"] = 0
            newinfo["continue"] = "True"
            with open('./storage/jsons/wallet.json','w') as json_file:
                json.dump(newinfo, json_file, indent=2)
        else:
            await ctx.send("There is no wallet in this channel.")


def setup(client):
    client.add_cog(actions(client))