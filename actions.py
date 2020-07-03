import asyncio
import json
import random
import sqlite3
import time
from sqlite3 import Error

import discord
from discord.ext import commands

from utils import *


class actions(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command()
    @commands.check(rightCategory)
    async def work(self, ctx):
        author = ctx.author
        jailtime = read_value('members', 'id', author.id, 'jailtime')
        workc = read_value('members', 'id', author.id, 'workc')
        isworking = read_value('members', 'id', author.id, 'isworking')
        if jailtime > time.time():
            await ctx.send(f'You are still in jail for {splittime(jailtime)}.')
            return
        elif workc > time.time():
            await ctx.send(f'You must wait {splittime(workc)} before you can work again.')
            return
        elif isworking== "True":
            await ctx.send(f'You are already working.')
            return
        heist = open_json()
        if heist["heistv"] == author.id:
            await ctx.send(f"You are currently being targeted for a heist.")
            return
        if author.id in heist["heistp"]:
            await ctx.send(f"You are participating in a heist right now.")
            return
        write_value('members', 'id', author.id, 'isworking', "'True'")
        flag = 0
        premium = read_value('members', 'id', author.id, 'premium')
        if premium == "True":
            premium = True
        else:
            premium = False
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
                opening = open('englishwords.txt')
                words = opening.read()
                wordlist = words.splitlines()
                ucolors = ['\U0001f534','\U000026aa','\U0001f7e1',
                          '\U0001f7e3','\U0001f7e0','\U0001f535',
                          '\U0001f7e4','\U0001f7e2']
                colorfinder = [{'code':'\U0001f534','name':'red'},
                               {'code':'\U000026aa','name':'white'},
                               {'code':'\U0001f7e1','name':'yellow'},
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
                def check(m):
                        return m.channel == ctx.channel and m.author == ctx.author
                try:
                    submission = await self.client.wait_for('message', check=check, timeout=5)
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
        money = read_value('members', 'id', author.id, 'money')
        money += earnings
        write_value('members', 'id', author.id, 'money', money)
        update_total(author.id)
        workc = int(time.time()) + 3600
        write_value('members', 'id', author.id, 'workc', workc)
        write_value('members', 'id', author.id, 'isworking', "'False'")
        await leaderboard(self.client)
        await rolecheck(self.client, author.id)


    @commands.command()
    @commands.check(rightCategory)
    async def bail(self, ctx, member:discord.Member=None):
        author = ctx.author
        if not member:
            await ctx.send("Enter a user to bail.")
            return
        if member==author:
            await ctx.send("You can't bail yourself.")
            return

        jailtime = read_value('members', 'id', author.id, 'jailtime')
        if jailtime > time.time():
            await ctx.send(f'You are still in jail for {splittime(jailtime)}.')
            return
        
        heist = open_json()
        if heist["heistv"] == author.id:
            await ctx.send(f"You are currently being targeted for a heist.")
            return
        if author.id in heist["heistp"]:
            await ctx.send(f"You are participating in a heist right now.")
            return
        if member.id==698771271353237575:
            await ctx.send("Why me?")
            return
        if member.bot == True:
            await ctx.send("Bots don't play!")
            return
        jailtime = read_value('members', 'id', member.id, 'jailtime')
        if jailtime < time.time():
            await ctx.send(f"**{member.name}** is not in jail.")
            return
        else:
            bailprice = int((jailtime-time.time())/3600*40)

        money = read_value('members', 'id', author.id, 'money')
        if bailprice > money:
            await ctx.send("You don't have enough money for that.")
            return
        else:
            money -= bailprice
            write_value('members', 'id', author.id, 'money', money)
            update_total(author.id)
            await ctx.send(f'💸 **{author.name}** spent ${bailprice} to bail **{member.name}**. 💸')
            write_value('members', 'id', member.id, 'jailtime', int(time.time()))
        await leaderboard(self.client)
        await rolecheck(self.client, member.id)
        await rolecheck(self.client, author.id)

                
    @commands.command()
    @commands.check(rightCategory)
    async def pay(self, ctx, member:discord.Member=None, amount=None):
        author = ctx.author
        jailtime = read_value('members', 'id', author.id, 'jailtime')
        if jailtime > time.time():
            await ctx.send(f'You are still in jail for {splittime(jailtime)}.')
            return
        heist = open_json()
        if heist["heistv"] == author.id:
            await ctx.send(f"You are currently being targeted for a heist.")
            return
        if author.id in heist["heistp"]:
            await ctx.send(f"You are participating in a heist right now.")
            return
        if read_value('members', 'id', author.id, 'isfighting') == 'True':
            await ctx.send('You already have a fight request pending, or are fighting someone.')
            return
        if member==None:
            await ctx.send("Enter a user to pay.")
            return
        if member.id==698771271353237575:
            await ctx.send("Why me?")
            return
        if member.bot == True:
            await ctx.send("Bots don't play!")
            return
        if member == author:
            await ctx.send(f"You can't pay yourself.")
            return
        if amount==None:
            await ctx.send("Set an amount to pay.")
            return
        money = read_value('members', 'id', author.id, 'money')
        if amount.lower()=='all':
            amount = money
            if amount == 0:
                await ctx.send("You don't have any money to pay.")
                return
        try:
            amount = int(amount)
        except:
            await ctx.send("Enter a valid amount.")
            return
        if amount < 1:
            await ctx.send("Enter a valid number.")
            return

        if money < amount:
            await ctx.send("You don't have enough money for that.")
        else:
            money -= amount
            write_value('members', 'id', author.id, 'money', money)
            update_total(author.id)
            money = read_value('members', 'id', member.id, 'money')
            money += amount
            write_value('members', 'id', member.id, 'money', money)
            update_total(author.id)
            update_total(member.id)
            await ctx.send(f"**{author.name}** payed **{member.name}** ${amount}.")
        await leaderboard(self.client)
        await rolecheck(self.client, author.id)
        await rolecheck(self.client, member.id)

    @commands.command()
    @commands.check(rightCategory)
    async def steal(self, ctx, member:discord.Member=None, amount=None):
        author = ctx.author
        jailtime = read_value('members', 'id', author.id, 'jailtime')
        if jailtime > time.time():
            await ctx.send(f'You are still in jail for {splittime(jailtime)}.')
            return
        heist = open_json()
        if heist["heistv"] == author.id:
            await ctx.send(f"You are currently being targeted for a heist.")
            return
        if author.id in heist["heistp"]:
            await ctx.send(f"You are participating in a heist right now.")
            return
        if member==None:
            await ctx.send("Enter a member to steal from.")
            return
        if member.id==698771271353237575:
            await ctx.send("Why me?")
            return
        if member.bot == True:
            await ctx.send("Bots don't play!")
            return
        if member == author:
            await ctx.send(f"You can't steal from yourself.")
            return
        if amount==None:
            await ctx.send("Set an amount to steal.")
            return
        try:
            amount=int(amount)
        except:
            await ctx.send("Enter a valid amount from 1-200.")
            return
        if amount < 1 or amount > 200:
            await ctx.send("Enter an amount from 1-200.")
            return
        stealc = read_value('members', 'id', author.id, 'stealc')
        if stealc > time.time():
            await ctx.send(f'You must wait {splittime(stealc)} before you can steal again.')
            return

        guild = self.client.get_guild(692906379203313695)
        if member.id not in around(guild, author.id, 3):
            await ctx.send(f"This user is not within a range of 3 from you.")
            if read_value('members', 'id', author.id, 'rangeinformed') == "False":
                image = discord.File('stealinfo.png')
                await ctx.send("*Not sure what this means?*\n**Use the .around command. You may steal from anyone who up to 3 places above you or below you.**", file=image)
                write_value('members', 'id', author.id, 'rangeinformed', '"True"')
            return


        for itema in in_use(member.id):
            if itema['name'] == 'padlock':
                remove_use('padlock', member.id)
                stealc = int(time.time()) + 10800
                write_value('members', 'id', author.id, 'stealc', stealc)
                if random.randint(1,4) == 1:
                    for item in in_use(author.id):
                        if item['name'] == 'gun':
                            if random.randint(1,2) == 1:
                                await ctx.send(f"**{member.name}** had a padlock in use and **{author.name}** broke the padlock instead. They were also caught but got away with their gun.")
                                return
                    await ctx.send(f"**{member.name}** had a padlock in use and **{author.name}** broke the padlock instead. They were also caught and jailed for 1h 30m.")
                    jailtime = int(time.time()) + 5400
                    write_value('members', 'id', author.id, 'jailtime', jailtime)
                else:
                    await ctx.send(f"**{member.name}** had a padlock in use and **{author.name}** broke the padlock instead.")
                return
        money = read_value('members', 'id', member.id, 'money')
        if money < amount:
            await ctx.send("This user does not have that much money in cash.")

        else:
            stealc = int(time.time()) + 10800
            write_value('members', 'id', author.id, 'stealc', stealc)
            randomer = amount - 23
            if randomer <= 0:
                randomer = random.randint(1,10)
            if random.randint(1,200) <= randomer:
                for item in in_use(author.id):
                    if item['name'] == 'gun':
                        if random.randint(1,2) == 1:
                            await ctx.send(f"**{author.name}** was caught stealing but got away with their gun.")
                            await rolecheck(self.client, author.id)
                            await rolecheck(self.client, member.id)
                            return
                jailtime = int(int(time.time()) + amount*100.5)
                write_value('members', 'id', author.id, 'jailtime', jailtime)
                await ctx.send(f'**{author.name}** was caught stealing and sent to jail for {splittime(jailtime)}.')
                    
            else:
                await ctx.send(f"**{author.name}** successfully stole ${amount} from **{member.name}**.")
                money -= amount
                write_value('members', 'id', member.id, 'money', money)
                update_total(member.id)
                money = read_value('members', 'id', author.id, 'money')
                money += amount
                write_value('members', 'id', author.id, 'money', money)
                update_total(author.id)
        await leaderboard(self.client)
        await rolecheck(self.client, author.id)
        await rolecheck(self.client, member.id)

        
    @commands.command(aliases=['dep'])
    @commands.check(rightCategory)
    async def deposit(self, ctx, amount=None):
        author = ctx.author
        jailtime = read_value('members', 'id', author.id, 'jailtime')
        if jailtime > time.time():
            await ctx.send(f'You are still in jail for {splittime(jailtime)}.')
            return
        bankc = read_value('members', 'id', author.id, 'bankc')
        if bankc > time.time():
            await ctx.send(f'You must wait {splittime(bankc)} before you can access your bank again.')
            return
        heist = open_json()
        if heist["heistv"] == author.id:
            await ctx.send(f"You are currently being targeted for a heist.")
            return
        if author.id in heist["heistp"]:
            await ctx.send(f"You are participating in a heist right now.")
            return
        if read_value('members', 'id', author.id, 'isfighting') == 'True':
            await ctx.send('You already have a fight request pending, or are fighting someone.')
            return
        if not amount:
            await ctx.send(f"Enter an amount of money to deposit.")
            return
        money = read_value('members', 'id', author.id, 'money')
        if amount.lower()=='all':
            amount = money
            if amount == 0:
                await ctx.send("You don't have any money to deposit.")
                return
        try:
            amount=int(amount)
        except:
            await ctx.send(f"Enter a valid amount of money to deposit.")
            return
        if amount <= 0:
            await ctx.send(f"Enter a valid amount of money to deposit.")
            return
        if amount > money:
            await ctx.send("You do not have that much cash.")
            return
        else:
            money -= amount
            bank = read_value('members', 'id', author.id, 'bank')
            bank += amount
            bankc = int(time.time()) + 600
            write_value('members', 'id', author.id, 'money', money)
            write_value('members', 'id', author.id, 'bank', bank)
            write_value('members', 'id', author.id, 'bankc', bankc)
            hbank = read_value('members', 'id', author.id, 'hbank')
            if bank > hbank:
                write_value('members', 'id', author.id, 'hbank', bank)
            await ctx.send(f"🏦 Deposited ${amount} to your bank. 🏦")


    @commands.command(aliases=['with'])
    @commands.check(rightCategory)
    async def withdraw(self, ctx, amount=None):
        author = ctx.author
        jailtime = read_value('members', 'id', author.id, 'jailtime')
        if jailtime > time.time():
            await ctx.send(f'You are still in jail for {splittime(jailtime)}.')
            return
        bankc = read_value('members', 'id', author.id, 'bankc')
        if bankc > time.time():
            await ctx.send(f'You must wait {splittime(bankc)} before you can access your bank again.')
            return
        heist = open_json()
        if heist["heistv"] == author.id:
            await ctx.send(f"You are currently being targeted for a heist.")
            return
        if author.id in heist["heistp"]:
            await ctx.send(f"You are participating in a heist right now.")
            return
        if read_value('members', 'id', author.id, 'isfighting') == 'True':
            await ctx.send('You already have a fight request pending, or are fighting someone.')
            return
        if not amount:
            await ctx.send(f"Enter an amount of money to withdraw.")
            return
        bank = read_value('members', 'id', author.id, 'bank')
        if amount.lower()=='all':
            amount = bank
            if amount == 0:
                await ctx.send("You don't have any money to withdraw.")
                return
        try:
            amount=int(amount)
        except:
            await ctx.send(f"Enter a valid amount of money to withdraw.")
            return
        if amount <= 0:
            await ctx.send(f"Enter a valid amount of money to withdraw.")
            return
        if amount > bank:
            await ctx.send("You do not have that much money in your bank.")
            return
        else:
            money = read_value('members', 'id', author.id, 'money')
            money += amount
            bank -= amount
            bankc = int(time.time()) + 600
            write_value('members', 'id', author.id, 'money', money)
            write_value('members', 'id', author.id, 'bank', bank)
            write_value('members', 'id', author.id, 'bankc', bankc)
            await ctx.send(f"🏦 Withdrew ${amount} from your bank. 🏦")


    @commands.command()
    @commands.check(rightCategory)
    async def heist(self, ctx, action=None, member:discord.Member=None):
        author = ctx.author
        guild = self.client.get_guild(692906379203313695)
        heist = open_json()
        
        jailtime = read_value('members', 'id', author.id, 'jailtime')        
        if jailtime > time.time():
            await ctx.send(f'You are still in jail for {splittime(jailtime)}.')
            return
        if not action:
            await ctx.send(f'Enter an action.')
            return
        conn = sqlite3.connect('hierarchy.db')
        c = conn.cursor()
        c.execute(f'SELECT cooldown FROM heist')
        heistc = c.fetchone()
        conn.close()
        heistc = heistc[0]

        if action.lower() == "start":
            if heistc > time.time():
                await ctx.send(f'Everyone must wait {splittime(heistc)} before another heist be made.')
                return
            elif heist["oheist"] == "True":
                await ctx.send(f'There is already an ongoing heist.')
                return
            elif not member:
                await ctx.send(f'Enter a member to heist from.')
                return
            elif author == member:
                await ctx.send(f"You can't heist yourself.")
                return
            elif member.id==698771271353237575:
                await ctx.send("Why me?")
                return
            elif member.bot == True:
                await ctx.send("Bots don't play!")
                return
            bank = read_value('members', 'id', member.id, 'bank')
            if bank < 100:
                await ctx.send(f'The victim must have at least $100 in their bank in order to be heisted from.')
                return
            await ctx.send(f'Heist started. You have two minutes to gather at least two more people to join the heist.')
            heist["heistv"] = member.id
            heist["oheist"] = "True"
            heist["heistp"].append(author.id)
            heist["heistl"] = ctx.channel.id
            heist["heistt"] = 120
            write_json(heist)

        elif action.lower() == "join":
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
            write_json(heist)
            
        elif action.lower() == "leave":
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
            write_json(heist)

        elif action.lower() == "cancel":
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
                write_json(heist)

        elif action.lower() == "list":
            if heist["oheist"] == "False":
                await ctx.send(f"There is no ongoing heist right now.")
                return
            embed = discord.Embed(color=0xff1414)
            embed.set_author(name=f'Heist on {guild.get_member(heist["heistv"]).name}')
            for person in heist["heistp"]:
                embed.add_field(value=f'{guild.get_member(person).name}', name='__________', inline=True)
            await ctx.send(embed=embed)
            write_json(heist)

        else:
            await ctx.send("Enter a valid heist action.")
      

    @commands.command(aliases=['purchase'])
    @commands.check(rightCategory)
    async def buy(self, ctx, item=None):
        author = ctx.author
        jailtime = read_value('members', 'id', author.id, 'jailtime')        
        if jailtime > time.time():
            await ctx.send(f'You are still in jail for {splittime(jailtime)}.')
            return
        if not item:
            await ctx.send(f'Enter an item.')
            return
        heist = open_json()
        if heist["heistv"] == author.id:
            await ctx.send(f"You are currently being targeted for a heist.")
            return
        if author.id in heist["heistp"]:
            await ctx.send(f"You are participating in a heist right now.")
            return
         
        items = []
        conn = sqlite3.connect('hierarchy.db')
        c = conn.cursor()
        c.execute('SELECT name, price FROM shop')
        temp = c.fetchall()
        conn.close()
        for p in temp:
            items.append({'name':p[0],'cost':p[1]})
        for x in items:
            if x["name"] == item.lower():
                money = read_value('members', 'id', author.id, 'money')
                if money < x["cost"]:
                    await ctx.send("You don't have enough money for that.")
                    return
                storage = read_value('members', 'id', author.id, 'storage')
                if len(read_value('members', 'id', author.id, 'items').split()) >= storage:
                    await ctx.send(f"You can only carry a maximum {storage} items.")
                    return
                money -= x["cost"]
                write_value('members', 'id', author.id, 'money', money)
                update_total(author.id)
                add_item(x['name'], author.id)
                await ctx.send(f"**{author.name}** purchased **{x['name'].capitalize()}** for ${x['cost']}.")
                await rolecheck(self.client, author.id)
                await leaderboard(self.client)
                return
            
        await ctx.send(f"There is no such item called {item}.")


    @commands.command()
    @commands.check(rightCategory)
    async def use(self, ctx, item=None):
        author = ctx.author
        jailtime = read_value('members', 'id', author.id, 'jailtime')        
        if item.lower() != 'pass':
            if jailtime > time.time():
                await ctx.send(f'You are still in jail for {splittime(jailtime)}.')
                return
        if not item:
            await ctx.send(f'Enter an item.')
            return
        heist = open_json()
        if heist["heistv"] == author.id:
            await ctx.send(f"You are currently being targeted for a heist.")
            return
        if author.id in heist["heistp"]:
            await ctx.send(f"You are participating in a heist right now.")
            return
        items = ["padlock", "backpack", "gun", "pass"]
        if item.lower() not in items:
            await ctx.send(f"There is no such item called {item}.")
            return
        elif item.lower() not in read_value('members', 'id', author.id, 'items').split():
            await ctx.send(f"You do not own {item.capitalize()}.")
            return
        inuse = in_use(author.id)
        for x in inuse:
            if x["name"] == item.lower():
                await ctx.send(f"You already have {item.capitalize()} in use.")
                return

        if item.lower() == 'padlock':
            timer = int(time.time()) + 172800
            add_use('padlock', timer, author.id)
            remove_item('padlock', author.id)
            await ctx.send(f"**{author.name}** used **{item.capitalize()}**.")
        if item.lower() == 'gun':
            timer = int(time.time()) + 46800
            add_use('gun', timer, author.id)
            remove_item('gun', author.id)
            await ctx.send(f"**{author.name}** used **{item.capitalize()}**.")
        if item.lower() == 'backpack':
            storage = read_value('members', 'id', author.id, 'storage')
            storage += 1
            write_value('members', 'id', author.id, 'storage', storage)
            remove_item('backpack', author.id)
            await ctx.send(f"**{author.name}** used **{item.capitalize()}**.")
            await ctx.send(f"You can now carry up to {storage} items.")
        if item.lower() == 'pass':
            jailtime = read_value('members', 'id', author.id, 'jailtime')
            if jailtime < time.time():
                await ctx.send('You are not in jail.')
                return
            else:
                bailprice = int(int(jailtime-time.time())/3600*40)
                money = read_value('members', 'id', author.id, 'money')
                if bailprice > money:
                    await ctx.send(f'You must have at least ${bailprice} to bail yourself.')
                else:
                    money -= bailprice
                    write_value('members', 'id', author.id, 'money', money)
                    write_value('members', 'id', author.id, 'jailtime', int(time.time()))
                    remove_item('pass', author.id)
                    await ctx.send(f"**{author.name}** used **{item.capitalize()}**.")
                    await ctx.send(f'💸 You bailed yourself for ${bailprice}. 💸')

    @commands.command()
    @commands.check(rightCategory)
    async def discard(self, ctx, item=None):
        author = ctx.author
        jailtime = read_value('members', 'id', author.id, 'jailtime')        
        if jailtime > time.time():
            await ctx.send(f'You are still in jail for {splittime(jailtime)}.')
            return
        if not item:
            await ctx.send(f'Enter an item.')
            return
        heist = open_json()
        if heist["heistv"] == author.id:
            await ctx.send(f"You are currently being targeted for a heist.")
            return
        if author.id in heist["heistp"]:
            await ctx.send(f"You are participating in a heist right now.")
            return
        items = ["padlock", "backpack", "gun", "pass"]
        if item.lower() not in items:
            await ctx.send(f"There is no such item called {item}.")
            return
        elif item.lower() not in read_value('members', 'id', author.id, 'items').split():
            await ctx.send(f"You do not own {item.capitalize()}.")
            return
        remove_item(item.lower() , author.id)
        await ctx.send(f'**{author.name}** discarded {item.capitalize()}.')
        
    @commands.command()
    @commands.check(rightCategory)
    async def daily(self, ctx):
        author = ctx.author
        dailytime = read_value('members', 'id', author.id, 'dailytime')
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
            streak = read_value('members', 'id', author.id, 'dailystreak')

        reward = rewards[streak]
        streak += 1
        nextreward = rewards[streak]

        if streak < 7:
            
            if streak != 6:
                await ctx.send(f"You've earned ${reward}. Come back tomorrow for ${nextreward}!\n*Current streak: {streak}*")
            
            else:
                await ctx.send(f"You've earned ${reward}. Come back tomorrow for ${nextreward}, along with a random shop item!\n*Current streak: {streak}*")

            money = read_value('members', 'id', author.id, 'money')
            money += reward
            write_value('members', 'id', author.id, 'money', money)
            await rolecheck(self.client, author.id)
            await leaderboard(self.client)

        else:

            skip = False
            storage = read_value('members', 'id', author.id, 'storage')
            if len(read_value('members', 'id', author.id, 'items').split()) >= storage:
                await ctx.send(f"You can only carry a maximum {storage} items. Do you want to discard the shop item you recieve automatically? (Yes/No)")
                try:
                    answer = await self.client.wait_for('message', check=lambda m: m.channel == ctx.channel and m.author == author, timeout=20)
                    if answer.content.lower() == 'yes':
                        skip = True
                    else:
                        await ctx.send('Reward not taken.')
                        return
                except asyncio.TimeoutError:
                    await ctx.send(f"Took too long: Reward not taken.")
                    return


            # Grabbing shop item
            if not skip:

                conn = sqlite3.connect('hierarchy.db')
                c = conn.cursor()
                c.execute('SELECT name FROM shop')
                items = c.fetchall()
                conn.close()
                item = random.choice(items)
                item = item[0]
                

                await ctx.send(f"You've earned ${reward}, along with a {item}!\n*Streak reset to 0.*")
                add_item(item, author.id)

            else:
                await ctx.send(f"You've earned ${reward}!\n*Streak reset to 0.*")
            streak = 0
            write_value('members', 'id', author.id, 'dailystreak', 0)
            money = read_value('members', 'id', author.id, 'money')
            money += reward
            write_value('members', 'id', author.id, 'money', money)
            await rolecheck(self.client, author.id)
            await leaderboard(self.client)

        write_value('members', 'id', author.id, 'dailystreak', streak)
        if timeDifference <= -2:
            dailytime = int(time.time()) + 86400
        else:
            dailytime += 86400
        write_value('members', 'id', author.id, 'dailytime', dailytime)
        update_total(author.id)

    @commands.command()
    @commands.check(rightCategory)
    async def boost(self, ctx):
        author = ctx.author
        premium = read_value('members', 'id', author.id, 'premium')
        if premium == 'False':
            await ctx.send("You don't have __premium__. Get __premium__ by boosting the server!")
            return
            
        boosts = read_value('members', 'id', author.id, 'boosts')
        if boosts <= 0:
            await ctx.send("You're don't have any boosts.")
            return
        
        timers = ["workc", "jailtime", "stealc", "rpsc", "bankc", "dailytime"]
        for timer in timers:
            current = read_value('members', 'id', author.id, timer)
            current -= 3600
            write_value('members', 'id', author.id, timer, current)

        boosts -= 1
        write_value('members', 'id', author.id, "boosts", boosts)
        await ctx.send('⏱️ You boosted 1 hour! ⏱️')

    @commands.command()
    @commands.check(rightCategory)
    async def claim(self, ctx):
        author = ctx.author

        jailtime = read_value('members', 'id', author.id, 'jailtime')        
        if jailtime > time.time():
            await ctx.send(f'You are still in jail for {splittime(jailtime)}.')
            return

        heist = open_json()
        if heist["heistv"] == author.id:
            await ctx.send(f"You are currently being targeted for a heist.")
            return

        if author.id in heist["heistp"]:
            await ctx.send(f"You are participating in a heist right now.")
            return

        with open('wallet.json') as json_file:
            walletinfo = json.load(json_file)
        
        if walletinfo["channel"] == ctx.channel.id:
            earnings = random.randint(40,70)
            money = read_value('members', 'id', author.id, 'money')
            money += earnings
            write_value('members', 'id', author.id, "money", money)
            update_total(author.id)
            await ctx.send(f"**{author.name}** claimed the wallet and earned ${earnings}.")

            newinfo = {}
            newinfo["timer"] = int(time.time()) + random.randint(21600, 25200)
            newinfo["channel"] = 0
            newinfo["continue"] = "True"
            with open('wallet.json','w') as json_file:
                json.dump(newinfo, json_file, indent=2)
        else:
            await ctx.send("There is no wallet in this channel.")

    @bail.error 
    @steal.error
    @heist.error
    @pay.error
    async def member_not_found_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send("Member not found.")
        else:
            print(error)
            



def setup(client):
    client.add_cog(actions(client))
