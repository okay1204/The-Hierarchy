import discord
from discord.ext import commands, tasks
import random
import json
import asyncio
from utils import *

class actions(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command()
    @commands.check(rightCategory)
    async def work(self, ctx):
        author = ctx.author
        hierarchy = open_json()
        for person in hierarchy:
            if str(author.id) == person["user"]:
                if person["jailtime"] > 0:
                    await ctx.send(f'You are still in jail for {splittime(person["jailtime"])}.')
                    return
                elif person["workc"] > 0:
                    await ctx.send(f'You must wait {splittime(person["workc"])} before you can work again.')
                    return
                elif person["isworking"] == "True":
                    await ctx.send(f'You are already working.')
                    return
        hierarchystats = open_json2()
        if hierarchystats["heistv"] == str(author.id):
            await ctx.send(f"You are currently being targeted for a heist.")
            return
        if author.id in hierarchystats["heistp"]:
            await ctx.send(f"You are participating in a heist right now.")
            return
        for person in hierarchy:
            if str(author.id) == person["user"]:
                person["isworking"] = "True"
                write_json(hierarchy)
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
        for person in hierarchy:
            if str(author.id) == person["user"]:        
                await ctx.send(f"**{author.name}** worked and successfully completed {flag} tasks, earning ${earnings}.")
                person["money"] += earnings
                person["total"] = person["money"] + person["bank"]
                person["workc"] = 3600
                person["isworking"] = "False"
                write_json(hierarchy)
        await leaderboard(self.client)
        await rolecheck(self.client, author.id)


    @commands.command()
    @commands.check(rightCategory)
    async def bail(self, ctx, member:discord.Member=None):
        author = ctx.author
        if member==author:
            await ctx.send("You can't bail yourself.")
            return
        hierarchy = open_json()
        for person in hierarchy:
            if str(author.id) == person["user"]:
                if person["jailtime"] > 0:
                    await ctx.send(f'You are still in jail for {splittime(person["jailtime"])}.')
                    return
        hierarchystats = open_json2()
        if hierarchystats["heistv"] == str(author.id):
            await ctx.send(f"You are currently being targeted for a heist.")
            return
        if author.id in hierarchystats["heistp"]:
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
        for person in hierarchy:
            if str(member.id) == person["user"]:
                if person["jailtime"] == 0:
                    await ctx.send(f"**{member.name}** is not in jail.")
                    return
                else:
                    bailprice = int(person["jailtime"]/3600*40)
        for person in hierarchy:
            if str(author.id) == person["user"]:
                if bailprice > person["money"]:
                    await ctx.send("You don't have enough money for that.")
                    return
                else:
                    person["money"] -= bailprice
                    person["total"] = person["money"] + person["bank"]
                    await ctx.send(f'**{author.name}** spent ${bailprice} to bail **{member.name}**.')
        for person in hierarchy:
            if str(member.id) == person["user"]:
                person["jailtime"] = 0
        write_json(hierarchy)
        await leaderboard(self.client)
        await rolecheck(self.client, member.id)
        await rolecheck(self.client, author.id)

                
    @commands.command()
    @commands.check(rightCategory)
    async def pay(self, ctx, member:discord.Member=None, amount=None):
        author = ctx.author
        hierarchy = open_json()
        for person in hierarchy:
            if str(author.id) == person["user"]:
                if person["jailtime"] > 0:
                    await ctx.send(f'You are still in jail for {splittime(person["jailtime"])}.')
                    return
        hierarchystats = open_json2()
        if hierarchystats["heistv"] == str(author.id):
            await ctx.send(f"You are currently being targeted for a heist.")
            return
        if author.id in hierarchystats["heistp"]:
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
        if amount.lower()=='all':
            for person in hierarchy:
                if int(person["user"]) == author.id:
                    amount = person['money']
        try:
            amount = int(amount)
        except:
            await ctx.send("Enter a valid amount.")
            return
        if amount < 1:
            await ctx.send("Enter a valid number.")
            return
        for person in hierarchy:
            if str(author.id) == person["user"]:
                if person["money"] < amount:
                    await ctx.send("You don't have enough money for that.")
                else:
                    person["money"] -= amount
                    person["total"] = person["money"] + person["bank"]
                    for person2 in hierarchy:
                        if str(member.id) == person2["user"]:
                            person2["money"] += amount
                            person2["total"] = person2["money"] + person2["bank"]
                    await ctx.send(f"**{author.name}** payed **{member.name}** ${amount}.")
        write_json(hierarchy)
        await leaderboard(self.client)
        await rolecheck(self.client, author.id)
        await rolecheck(self.client, member.id)

    @commands.command()
    @commands.check(rightCategory)
    async def steal(self, ctx, member:discord.Member=None, amount=None):
        author = ctx.author
        hierarchy = open_json()
        for person in hierarchy:
            if str(author.id) == person["user"]:
                if person["jailtime"] > 0:
                    await ctx.send(f'You are still in jail for {splittime(person["jailtime"])}.')
                    return
        hierarchystats = open_json2()
        if hierarchystats["heistv"] == str(author.id):
            await ctx.send(f"You are currently being targeted for a heist.")
            return
        if author.id in hierarchystats["heistp"]:
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
        for person in hierarchy:
            if str(author.id) == person["user"] and person["stealc"] > 0:
                    await ctx.send(f'You must wait {splittime(person["stealc"])} before you can steal again.')
                    return
        for person in hierarchy:
            if str(member.id) == person["user"]:
                for x in person["inuse"]:
                    if x["name"] == 'padlock':
                        itemindex = person["inuse"].index(x)
                        person["inuse"].pop(itemindex)
                        for person2 in hierarchy:
                            if int(person2["user"]) == author.id:
                                person2["stealc"] = 10800
                                if random.randint(1,4) == 1:
                                    for item in person2["inuse"]:
                                        if item["name"] == "gun":
                                            if random.randint(1,2) == 1:
                                                await ctx.send(f"**{member.name}** had a padlock in use and **{author.name}** broke the padlock instead. They were also caught but got away with their gun.")
                                                write_json(hierarchy)
                                                return
                                    await ctx.send(f"**{member.name}** had a padlock in use and **{author.name}** broke the padlock instead. They were also caught and jailed for 1h 30m.")
                                    person2["jailtime"] = 5400
                                else:
                                    await ctx.send(f"**{member.name}** had a padlock in use and **{author.name}** broke the padlock instead.")
                        write_json(hierarchy)
                        return
                if person["money"] < amount:
                    await ctx.send("This user does not have that much money in cash.")
                else:
                    randomer = amount - 23
                    if randomer <= 0:
                        randomer = random.randint(1,10)
                    if random.randint(1,200) <= randomer:
                        for person2 in hierarchy:
                            if str(author.id) == person2["user"]:
                                for item in person2["inuse"]:
                                    if item["name"] == "gun":
                                        if random.randint(1,2) == 1:
                                            await ctx.send(f"**{author.name}** was caught stealing but got away with their gun.")
                                            write_json(hierarchy)
                                            await leaderboard(self.client)
                                            await rolecheck(self.client, author.id)
                                            await rolecheck(self.client, member.id)
                                            return
                                person2["jailtime"] = int(amount*100.5)
                                person2["stealc"] = 10800
                                await ctx.send(f'**{author.name}** was caught stealing and sent to jail for {splittime(person2["jailtime"])}.')
                        
                    else:
                        await ctx.send(f"**{author.name}** successfully stole ${amount} from **{member.name}**.")
                        person["money"] -= amount
                        person["total"] = person["money"] + person["bank"]
                        for person2 in hierarchy:
                            if str(author.id) == person2["user"]:
                                person2["money"] += amount
                                person2["stealc"] = 10800
                                person2["total"] = person2["money"] + person2["bank"]
        write_json(hierarchy)
        await leaderboard(self.client)
        await rolecheck(self.client, author.id)
        await rolecheck(self.client, member.id)







    @commands.command(aliases=['dep'])
    @commands.check(rightCategory)
    async def deposit(self, ctx, amount=None):
        author = ctx.author
        hierarchy = open_json()
        for person in hierarchy:
            if str(author.id) == person["user"]:
                if person["jailtime"] > 0:
                    await ctx.send(f'You are still in jail for {splittime(person["jailtime"])}.')
                    return
                if person["bankc"] > 0:
                    await ctx.send(f'You must wait {splittime(person["bankc"])} before you can access your bank again.')
                    return
        hierarchystats = open_json2()
        if hierarchystats["heistv"] == str(author.id):
            await ctx.send(f"You are currently being targeted for a heist.")
            return
        if author.id in hierarchystats["heistp"]:
            await ctx.send(f"You are participating in a heist right now.")
            return
        if not amount:
            await ctx.send(f"Enter an amount of money to deposit.")
            return
        if amount.lower()=='all':
            for person in hierarchy:
                if int(person["user"]) == author.id:
                    amount = person['money']
        try:
            amount=int(amount)
        except:
            await ctx.send(f"Enter a valid amount of money to deposit.")
            return
        if amount <= 0:
            await ctx.send(f"Enter a valid amount of money to deposit.")
            return
        for person in hierarchy:
            if person["user"] == str(author.id):
                if amount > person["money"]:
                    await ctx.send("You do not have that much cash.")
                    return
                else:
                    person["money"] -= amount
                    person["bank"] += amount
                    person["bankc"] = 600
                    if person["bank"] > person["hbank"]:
                        person["hbank"] = person["bank"]
                    await ctx.send(f"Deposited ${amount} to your bank.")
                    write_json(hierarchy)



    @commands.command(aliases=['with'])
    @commands.check(rightCategory)
    async def withdraw(self, ctx, amount=None):
        author = ctx.author
        hierarchy = open_json()
        for person in hierarchy:
            if str(author.id) == person["user"]:
                if person["jailtime"] > 0:
                    await ctx.send(f'You are still in jail for {splittime(person["jailtime"])}.')
                    return
                if person["bankc"] > 0:
                    await ctx.send(f'You must wait {splittime(person["bankc"])} before you can access your bank again.')
                    return
        hierarchystats = open_json2()
        if hierarchystats["heistv"] == str(author.id):
            await ctx.send(f"You are currently being targeted for a heist.")
            return
        if author.id in hierarchystats["heistp"]:
            await ctx.send(f"You are participating in a heist right now.")
            return
        if not amount:
            await ctx.send(f"Enter an amount of money to withdraw.")
            return
        if amount.lower()=='all':
            for person in hierarchy:
                if int(person["user"]) == author.id:
                    amount = person['bank']
        try:
            amount=int(amount)
        except:
            await ctx.send(f"Enter a valid amount of money to withdraw.")
            return
        if amount <= 0:
            await ctx.send(f"Enter a valid amount of money to withdraw.")
            return
        for person in hierarchy:
            if person["user"] == str(author.id):
                if amount > person["bank"]:
                    await ctx.send("You do not have that much money in your bank.")
                    return
                else:
                    person["money"] += amount
                    person["bank"] -= amount
                    person["bankc"] = 600
                    await ctx.send(f"Withdrew ${amount} from your bank.")
                    write_json(hierarchy)




    @commands.command()
    @commands.check(rightCategory)
    async def heist(self, ctx, action=None, member:discord.Member=None):
        author = ctx.author
        guild = self.client.get_guild(692906379203313695)
        hierarchy = open_json()
        hierarchystats = open_json2()
        for person in hierarchy:
            if str(author.id) == person["user"]:
                if person["jailtime"] > 0:
                    await ctx.send(f'You are still in jail for {splittime(person["jailtime"])}.')
                    return
        if not action:
            await ctx.send(f'Enter an action.')
        if action.lower() == "start":
            if hierarchystats["heistc"] > 0:
                await ctx.send(f'Everyone must wait {splittime(hierarchystats["heistc"])} before another heist be made.')
                return
            elif hierarchystats["oheist"] == "True":
                await ctx.send(f'There is already an ongoing heist.')
                return
            elif not member:
                await ctx.send(f'Enter a member to heist from.')
                return
            elif author == guild.get_member(member.id):
                await ctx.send(f"You can't heist from yourself.")
                return
            elif member.id==698771271353237575:
                await ctx.send("Why me?")
                return
            elif member.bot == True:
                await ctx.send("Bots don't play!")
                return
            for person in hierarchy:
                if person["user"] == str(member.id):
                    if person["bank"] < 100:
                        await ctx.send(f'The victim must have at least $100 in their bank in order to be heisted from.')
                        return
            await ctx.send(f'Heist started. You have two minutes to gather at least two more people to join the heist.')
            hierarchystats["heistv"] = str(member.id)
            hierarchystats["oheist"] = "True"
            hierarchystats["heistp"].append(author.id)
            hierarchystats["heistl"] = str(ctx.channel.id)
            hierarchystats["heistt"] = 120
            write_json2(hierarchystats)

        elif action.lower() == "join":
            if hierarchystats["heistv"] == str(author.id):
                await ctx.send(f"You are the target of this heist.")
                return
            if hierarchystats["oheist"] == "False":
                await ctx.send(f"There is no ongoing heist right now.")
                return
            if author.id in hierarchystats["heistp"]:
                await ctx.send(f"You are already in this heist.")
                return
            hierarchystats["heistp"].append(author.id)
            await ctx.send(f'**{author.name}** has joined the heist on **{guild.get_member(int(hierarchystats["heistv"])).name}**.')
            write_json2(hierarchystats)

        elif action.lower() == "leave":
            if hierarchystats["oheist"] == "False":
                await ctx.send(f"There is no ongoing heist right now.")
                return
            if author.id not in hierarchystats["heistp"]:
                await ctx.send("You aren't participating in a heist.")
                return
            if hierarchystats["heistp"][0] == author.id:
                await ctx.send("You are leading this heist.")
                return
            playerindex = hierarchystats["heistp"].index(author.id)
            hierarchystats["heistp"].pop(playerindex)
            await ctx.send(f'**{author.name}** has left the heist on **{guild.get_member(int(hierarchystats["heistv"])).name}**.')
            write_json2(hierarchystats)


        elif action.lower() == "cancel":
            if hierarchystats["oheist"] == "False":
                await ctx.send(f"There is no ongoing heist right now.")
                return
            if author.id not in hierarchystats["heistp"]:
                await ctx.send("You aren't participating in a heist.")
                return
            if hierarchystats["heistp"][0] != author.id:
                await ctx.send("You are not leading this heist.")
                return
            elif hierarchystats["heistp"][0] == author.id:
                hierarchystats["heistv"] = "None"
                hierarchystats["heistt"] = 0
                hierarchystats["heistp"] = []
                hierarchystats["heistl"] = "None"
                hierarchystats["oheist"] = "False"
                write_json2(hierarchystats)
                await ctx.send("Heist cancelled: Heist cancelled by leader.")
                return

        elif action.lower() == "list":
            if hierarchystats["oheist"] == "False":
                await ctx.send(f"There is no ongoing heist right now.")
                return
            embed = discord.Embed(color=0xff1414)
            embed.set_author(name=f'Heist on {guild.get_member(int(hierarchystats["heistv"])).name}')
            for person in hierarchystats["heistp"]:
                embed.add_field(value=f'{guild.get_member(person).name}', name='__________', inline=True)
            await ctx.send(embed=embed)

        else:
            await ctx.send("Enter a valid heist action.")
      



    @commands.command(aliases=['purchase'])
    @commands.check(rightCategory)
    async def buy(self, ctx, item=None):
        author = ctx.author
        hierarchy = open_json()
        for person in hierarchy:
            if str(author.id) == person["user"]:
                if person["jailtime"] > 0:
                    await ctx.send(f'You are still in jail for {splittime(person["jailtime"])}.')
                    return
        if not item:
            await ctx.send(f'Enter an item.')
            return
        hierarchystats = open_json2()
        if hierarchystats["heistv"] == str(author.id):
            await ctx.send(f"You are currently being targeted for a heist.")
            return
        if author.id in hierarchystats["heistp"]:
            await ctx.send(f"You are participating in a heist right now.")
            return
         
        items = [{"name":"padlock", "cost":110},{"name":"backpack", "cost":100},{"name":"gun", "cost":120}]
        for x in items:
            if x["name"] == item.lower():
                for person in hierarchy:
                    if int(person["user"]) == author.id:
                        if person["money"] < x["cost"]:
                            await ctx.send("You don't have enough money for that.")
                            return
                        if len(person["items"]) >= person["storage"]:
                            await ctx.send(f"You can only carry a maximum {person['storage']} items.")
                            return
                        person["money"] -= x["cost"]
                        person["total"] = person["money"] + person["bank"]
                        person["items"].append(x["name"])
                        await ctx.send(f"**{author.name}** purchased **{x['name'].capitalize()}** for ${x['cost']}.")
                        await rolecheck(self.client, int(person["user"]))
                        await leaderboard(self.client)
                        write_json(hierarchy)
                        return
            
        await ctx.send(f"There is no such item called {item}.")


    
    @commands.command()
    @commands.check(rightCategory)
    async def use(self, ctx, item=None):
        author = ctx.author
        hierarchy = open_json()
        for person in hierarchy:
            if str(author.id) == person["user"]:
                if person["jailtime"] > 0:
                    await ctx.send(f'You are still in jail for {splittime(person["jailtime"])}.')
                    return
        if not item:
            await ctx.send(f'Enter an item.')
            return
        hierarchystats = open_json2()
        if hierarchystats["heistv"] == str(author.id):
            await ctx.send(f"You are currently being targeted for a heist.")
            return
        if author.id in hierarchystats["heistp"]:
            await ctx.send(f"You are participating in a heist right now.")
            return
        items = ["padlock", "backpack", "gun"]
        if item.lower() not in items:
            await ctx.send("This item does not exist.")
            return
        for person in hierarchy:
            if int(person["user"]) == author.id:
                if item.lower() not in person["items"]:
                    await ctx.send(f"You do not own {item.capitalize()}.")
                    return
                for x in person["inuse"]:
                    if x["name"] == item.lower():
                        await ctx.send(f"You already have {item.capitalize()} in use.")
                        return
                if item.lower() in person["items"]:
                    await ctx.send(f"**{author.name}** used **{item.capitalize()}**.")
                    itemindex = person["items"].index(item.lower())
                    person["items"].pop(itemindex)
                    if item.lower() == 'padlock':
                        person["inuse"].append({'name':'padlock','timer':172800})
                    if item.lower() == 'gun':
                        person["inuse"].append({'name':'gun','timer':46800})
                    if item.lower() == 'backpack':
                        person["storage"] += 1
                        await ctx.send(f"You can now carry up to {person['storage']} items.")
                    write_json(hierarchy)



    @pay.error
    async def pay_error(self, ctx,error):
        if isinstance(error, commands.BadArgument):
            await ctx.send("Member not found.")
            
    @steal.error
    async def steal_error(self, ctx,error):
        if isinstance(error, commands.BadArgument):
            await ctx.send("Member not found.")
            
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
