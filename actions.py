import discord
from discord.ext import commands, tasks
import random
import json
import asyncio
import time
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
        for x in range(3):
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
                        elif order -- 2:
                            await ctx.send(f"{n3} + {n2} x {n1}")
                    if aos == 2:
                        n3 = random.randint(1,10)
                        answer = (n1 * n2) - n3
                        order = random.randint(1,2)
                        if order == 1:
                            await ctx.send(f"{n1} x {n2} - {n3}")
                        elif order -- 2:
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
                        elif order -- 2:
                            await ctx.send(f"{n3} + {n1} / {n2}")
                    if aos == 2:
                        n3 = random.randint(1,10)
                        answer = t2 - n3
                        order = random.randint(1,2)
                        if order == 1:
                            await ctx.send(f"{n1} / {n2} - {n3}")
                        elif order -- 2:
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
        if flag == 1:
            earnings = random.randint(20,35)
        if flag == 2:
            earnings = random.randint(40,50)
        if flag == 3:
            earnings = random.randint(60,70)       
        await ctx.send(f"**{author.name}** worked and successfully completed {flag} tasks, earning ${earnings}.")
        money = read_value('members', 'id', author.id, 'money')
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
        if member==None:
            await ctx.send("Enter a user to bail.")
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
            bailprice = int(jailtime/3600*40)

        money = read_value('members', 'id', author.id, 'money')
        if bailprice > money:
            await ctx.send("You don't have enough money for that.")
            return
        else:
            money -= bailprice
            write_value('members', 'id', member.id, 'money', money)
            update_total(author.id)
            await ctx.send(f'**{author.name}** spent ${bailprice} to bail **{member.name}**.')
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
        if 'padlock' in in_use(member.id):
            remove_use('padlock', member.id)
            stealc = int(time.time()) + 10800
            write_value('members', 'id', author.id, 'stealc', stealc)
            if random.randint(1,4) == 1:
                if "gun" in in_use(author.id):
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
                if 'gun' in in_use(author.id):
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
        if not amount:
            await ctx.send(f"Enter an amount of money to deposit.")
            return
        money = read_value('members', 'id', author.id, 'money')
        if amount.lower()=='all':
            amount = money
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
            await ctx.send(f"Deposited ${amount} to your bank.")



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
        if not amount:
            await ctx.send(f"Enter an amount of money to withdraw.")
            return
        bank = read_value('members', 'id', author.id, 'bank')
        if amount.lower()=='all':
            amount = bank
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
            await ctx.send(f"Withdrew ${amount} from your bank.")




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
            if heistc > 0:
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
         
        items = [{"name":"padlock", "cost":110},{"name":"backpack", "cost":100},{"name":"gun", "cost":120}]
        for x in items:
            if x["name"] == item.lower():
                money = read_value('members', 'id', author.id, 'money')
                if money < x["cost"]:
                    await ctx.send("You don't have enough money for that.")
                    return
                storage = read_value('members', 'id', author.id, 'storage')
                if len(read_value('members', 'id', author.id, 'items').split()) >= storage:
                    await ctx.send(f"You can only carry a maximum {person['storage']} items.")
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
        items = ["padlock", "backpack", "gun"]
        if item.lower() not in items:
            await ctx.send("This item does not exist.")
            return
        if item.lower() not in read_value('members', 'id', author.id, 'items').split():
            await ctx.send(f"You do not own {item.capitalize()}.")
            return
        in_use = in_use(author.id)
        for x in in_use:
            if x["name"] == item.lower():
                await ctx.send(f"You already have {item.capitalize()} in use.")
                return

        await ctx.send(f"**{author.name}** used **{item.capitalize()}**.")
        person["items"].remove(item.lower())
        if item.lower() == 'padlock':
            timer = int(time.time()) + 172800
            add_use('padlock', timer, author.id)
        if item.lower() == 'gun':
            remove_item('gun', author.id)
            timer = int(time.time()) + 46800
            add_use('gun', timer, author.id)
        if item.lower() == 'backpack':
            storage = read_value('members', 'id', author.id, 'storage')
            storage += 1
            write_value('members', 'id', author.id, 'storage', storage)
            await ctx.send(f"You can now carry up to {storage} items.")

    @commands.command()
    @commands.check(rightCategory)
    async def redeem(self, ctx):
        author = ctx.author
        tokens = read_value('members', 'id', author.id, 'tokens')
        if tokens == 0:
            await ctx.send("You don't have any tokens.")
        elif tokens > 0:
            await ctx.send(f"**{author.name}** redeemed {tokens} tokens for ${tokens*50}.")
            money = read_value('members', 'id', author.id, 'money')
            money += tokens * 50
            write_value('members', 'id', author.id, 'money', money)
            update_total(author.id)
            write_value('members', 'id', author.id, 'tokens', 0)
            await rolecheck(self.client, author.id)
            await leaderboard(self.client)




    @pay.error
    async def pay_error(self, ctx,error):
        if isinstance(error, commands.BadArgument):
            await ctx.send("Member not found.")
            
##    @steal.error
##    async def steal_error(self, ctx,error):
##        if isinstance(error, commands.BadArgument):
##            await ctx.send("Member not found.")
            
    @bail.error
    async def bail_error(self, ctx,error):
        if isinstance(error, commands.BadArgument):
            await ctx.send("Member not found.")
            
    @heist.error
    async def heist_error(self, ctx,error):
        if isinstance(error, commands.BadArgument):
            await ctx.send("Member not found.")



def setup(client):
    client.add_cog(actions(client))
