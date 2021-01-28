# pylint: disable=import-error

import asyncio
import json
import random
import asyncpg
import time
import os

import discord
from discord.ext import commands
from discord.ext.commands import BadArgument, CommandNotFound, MaxConcurrencyReached

from cogs.extra.itemuse import ItemUses

# To import from different path
import sys
sys.path.insert(1 , os.getcwd())

from utils import bot_check, splittime, timestring, log_command


class Actions(commands.Cog):

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
    async def bail(self, ctx, *, member:discord.Member=None):


        async with self.client.pool.acquire() as db:

            if not await db.level_check(ctx, ctx.author.id, 2, "bail someone"): return

            if member.id == ctx.author.id:
                await ctx.send("You can't bail yourself.")

                if 'pass' in await db.get_member_val(ctx.author.id, 'items'):
                    await asyncio.sleep(2)
                    await ctx.send("*Have a pass? Use the command `.use pass` to use it.*")

                return

            if not await db.jail_heist_check(ctx, ctx.author): return

            if not member: 
                await ctx.send("Incorrect command usage:\n`.bail member`")
                return

            # No heist jail check function here because of special command
            
            if self.client.heist:

                if self.client.heist["victim"] == ctx.author.id: return await ctx.send(f"You are currently being targeted for a heist.")

                elif ctx.author.id in self.client.heist["participants"]: return await ctx.send(f"You are participating in a heist right now.")


            jailtime = await db.get_member_val(member.id, 'jailtime')
            if jailtime < time.time(): 
                await ctx.send(f"**{member.name}** is not in jail.")
                return
            else:
                bailprice = self.client.bailprice(jailtime)


            money = await db.get_member_val(ctx.author.id, 'money')
            if bailprice > money:
                await ctx.send("You don't have enough money for that.")
                return

            else:
                money -= bailprice

                await db.set_member_val(ctx.author.id, 'money', money)
                await ctx.send(f'💸 **{ctx.author.name}** spent ${bailprice} to bail **{member.name}**. 💸')
                await db.set_member_val(member.id, 'jailtime', 0)

            await db.leaderboard()
            await db.rolecheck(member.id)
            await db.rolecheck(ctx.author.id)

                
    @commands.command()
    async def pay(self, ctx, member:discord.Member=None, amount=None):


        async with self.client.pool.acquire() as db:

            if not await db.event_disabled(ctx):
                return

            if not await db.jail_heist_check(ctx, ctx.author):
                return

            if not member or not amount: 
                await ctx.send("Incorrect command usage:\n`.pay member amount`")
                return
            
            if not await bot_check(self.client, ctx, member):
                return

            if member.id == ctx.author.id:
                await ctx.send(f"You can't pay yourself.")
                return

            if not await db.member_event_check(ctx, member.id): return


            money = await db.get_member_val(ctx.author.id, 'money')

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
                await db.set_member_val(ctx.author.id, 'money', money)


                money = await db.get_member_val(member.id, 'money')
                money += amount
                await db.set_member_val(member.id, 'money', money)

                await ctx.send(f"**{ctx.author.name}** payed **{member.name}** ${amount}.")

            await db.leaderboard()
            await db.rolecheck(ctx.author.id)
            await db.rolecheck(member.id)


    @commands.command()
    @commands.max_concurrency(1, per=commands.BucketType.member)
    async def steal(self, ctx, member:discord.Member=None, amount=None):


        async with self.client.pool.acquire() as db:

            if not await db.jail_heist_check(ctx, ctx.author):
                return

            if not member or not amount: 
                await ctx.send("Incorrect command usage:\n`.steal member amount`")
                return
            
            if not await bot_check(self.client, ctx, member):
                return

            if member.id == ctx.author.id:
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

            stealc = await db.get_member_val(ctx.author.id, 'stealc')
            if stealc > time.time():
                return await ctx.send(f'You must wait {splittime(stealc)} before you can steal again.')

            if member.id not in await db.around(ctx.author.id, 3):

                await ctx.send(f"This user is not within a range of 3 from you.")



                if not await db.get_member_val(ctx.author.id, 'rangeinformed'):

                    await asyncio.sleep(3)
                    image = discord.File('./storage/images/stealinfo.png')
                    await ctx.send("*Not sure what this means?*\n**Use the .around command. You may steal from anyone who up to 3 places above you or below you.**", file=image)
                    await db.set_member_val(ctx.author.id, 'rangeinformed', True)

                return

            money = await db.get_member_val(member.id, 'money')
            if money < amount:
                return await ctx.send("This user does not have that much money in cash.") # linked to tutorial, change tutorial if this message changes
                

            # gang warning
            gang_info = await db.fetchrow('SELECT owner, members FROM gangs WHERE owner = $1 OR $1 = ANY(members);', ctx.author.id)

            if gang_info:
                owner, members = gang_info
            else:
                owner = None
                members = []


            if member.id in members or member.id == owner:

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



            if 'padlock' in await db.in_use(member.id):

                await db.remove_use(member.id, 'padlock')
                stealc = int(time.time()) + 10800
                await db.set_member_val(ctx.author.id, 'stealc', stealc)

                # 1 in 4 chance
                if not random.getrandbits(2):

                    if 'gun' in await db.in_use(ctx.author.id):

                        # 1 in 2 chance
                        if random.getrandbits(1):
                            await ctx.send(f"**{member.name}** had a padlock in use and **{ctx.author.name}** broke the padlock instead. They were also caught but got away with their gun.")
                            return

                    await ctx.send(f"**{member.name}** had a padlock in use and **{ctx.author.name}** broke the padlock instead. They were also caught and jailed for 1h 30m.")
                    jailtime = int(time.time()) + 5400

                    await db.set_member_val(ctx.author.id, 'jailtime', jailtime)

                else:
                    await ctx.send(f"**{member.name}** had a padlock in use and **{ctx.author.name}** broke the padlock instead.")
                
                return

            else:

                stealc = int(time.time()) + 10800

                await db.set_member_val(ctx.author.id, 'stealc', stealc)

                randomer = amount - 23

                if randomer <= 0:
                    randomer = random.randint(1,10)

                if random.randint(1,200) <= randomer:

                    if 'gun' in await db.in_use(ctx.author.id):

                        if random.getrandbits(1):
                            return await ctx.send(f"**{ctx.author.name}** was caught stealing but got away with their gun.")
                            

                    jailtime = int(int(time.time()) + amount*100.5)
                    await db.set_member_val(ctx.author.id, 'jailtime', jailtime)

                    await ctx.send(f'**{ctx.author.name}** was caught stealing and sent to jail for {splittime(jailtime)}.') # message linked with tutorial
                        
                else:
                    await ctx.send(f"**{ctx.author.name}** successfully stole ${amount} from **{member.name}**.") # message linked with tutorial

                    money -= amount
                    await db.set_member_val(member.id, 'money', money)
                    money = await db.get_member_val(ctx.author.id, 'money')
                    money += amount
                    await db.set_member_val(ctx.author.id, 'money', money)

            await db.leaderboard()
            await db.rolecheck(ctx.author.id)
            await db.rolecheck(member.id)

        
    @commands.command(aliases=['dep'])
    async def deposit(self, ctx, amount=None):
        
        async with self.client.pool.acquire() as db:
        
            if not await db.level_check(ctx, ctx.author.id, 2, "use the bank"):
                return

            if not await db.jail_heist_check(ctx, ctx.author):
                return

            bankc = await db.get_member_val(ctx.author.id, 'bankc')
            if bankc > time.time():
                await ctx.send(f'You must wait {splittime(bankc)} before you can access your bank again.')
                return

            if not amount: 
                await ctx.send("Incorrect command usage:\n`.deposit amount`")
                return
            

            money = await db.get_member_val(ctx.author.id, 'money')

            if amount.lower() == 'all':

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
                bank = await db.get_member_val(ctx.author.id, 'bank')
                bank += amount
                bankc = int(time.time()) + 600
                
                await db.set_member_val(ctx.author.id, 'money', money)
                await db.set_member_val(ctx.author.id, 'bank', bank)
                await db.set_member_val(ctx.author.id, 'bankc', bankc)

                hbank = await db.get_member_val(ctx.author.id, 'hbank')

                if bank > hbank:
                    await db.set_member_val(ctx.author.id, 'hbank', bank)

                await ctx.send(f"🏦 Deposited ${amount} to your bank. 🏦")


    @commands.command(aliases=['with'])
    async def withdraw(self, ctx, amount=None):

        async with self.client.pool.acquire() as db:

            if not await db.level_check(ctx, ctx.author.id, 2, "use the bank"):
                return

            if not await db.jail_heist_check(ctx, ctx.author):
                return        

            bankc = await db.get_member_val(ctx.author.id, 'bankc')

            if bankc > time.time():
                await ctx.send(f'You must wait {splittime(bankc)} before you can access your bank again.')
                return

            if not amount: 
                await ctx.send("Incorrect command usage:\n`.withdraw amount`")
                return

            bank = await db.get_member_val(ctx.author.id, 'bank')

            if amount.lower() == 'all':
                amount = bank
                if amount == 0:
                    await ctx.send("You don't have any money to withdraw.")
                    return

            try:
                amount=int(amount)
            except:
                return await ctx.send(f"Incorrect command usage:\n`.withdraw amount`")
                

            if amount <= 0:
                return await ctx.send(f"Enter an amount greater than 0.")
                
            if amount > bank:
                return await ctx.send("You do not have that much money in your bank.")
                

            else:
                money = await db.get_member_val(ctx.author.id, 'money')

                money += amount
                bank -= amount
                bankc = int(time.time()) + 600
                await db.set_member_val(ctx.author.id, 'money', money)
                await db.set_member_val(ctx.author.id, 'bank', bank)
                await db.set_member_val(ctx.author.id, 'bankc', bankc)

                await ctx.send(f"🏦 Withdrew ${amount} from your bank. 🏦")



    @commands.command(aliases=['purchase'])
    @commands.max_concurrency(1, per=commands.BucketType.member)
    async def buy(self, ctx, *, item=None):

        async with self.client.pool.acquire() as db:

            if not await db.level_check(ctx, ctx.author.id, 4, "use items"):
                return

            if not await db.jail_heist_check(ctx, ctx.author):
                return

            if not item: 
                return await ctx.send("Incorrect command usage:\n`.buy item`")
            
        
            temp = await db.fetch('SELECT name, price, article, emoji FROM shop;')

            items = list(map(lambda x: {'name':x[0], 'cost':x[1], 'article': x[2], 'emoji': x[3]}, temp))


            for x in items:

                if x["name"] == item.lower():

                    money = await db.get_member_val(ctx.author.id, 'money')

                    with open('./storage/jsons/mode.json') as f:
                        mode = json.load(f)

                    if ctx.author.premium_since and mode == "event" and await db.get_member_val(ctx.author.id, 'in_event') == "True":
                        await ctx.send("*Premium perks are disabled during events*")
                        await asyncio.sleep(0.5)

                    elif ctx.author.premium_since:
                        x["cost"] -= int(x["cost"] * 0.3)


                    if money < x["cost"]:
                        
                        bank = await db.get_member_val(ctx.author.id, 'bank')

                        if bank + money >= x["cost"] and await db.get_member_val(ctx.author.id, 'bankc') < time.time():

                            missing = x["cost"] - money
                            await ctx.send(f"Would you like to automatically withdraw the missing ${missing} from your bank? Respond with `yes` or `y` to proceed.")

                            try:
                                response = await self.client.wait_for('message', check=lambda msg: msg.ctx.author == ctx.author and msg.channel == ctx.channel, timeout=20)

                            except asyncio.TimeoutError:
                                await ctx.send("Bank withdrawal timed out.")
                                return
                            
                            response = response.content.lower()
                            if response == 'yes' or response == 'y':
                                bank -= missing
                                money += missing

                                await db.set_member_val(ctx.author.id, 'bank', bank)
                                await db.set_member_val(ctx.author.id, 'money', money)
                                await db.set_member_val(ctx.author.id, 'bankc', 600)

                                await ctx.send(f"Withdrew ${missing} from your bank.")
                                await asyncio.sleep(1)

                            else:
                                await ctx.send("Bank withdrawal cancelled.")
                                return
                            

                        else:
                            await ctx.send("You don't have enough money for that.")
                            return

                    storage = await db.get_member_val(ctx.author.id, 'storage')

                    if len(await db.get_member_val(ctx.author.id, 'items')) >= storage:
                        await ctx.send(f"You can only carry a maximum of {storage} items.")
                        return

                    money -= x["cost"]
                    await db.set_member_val(ctx.author.id, 'money', money)
                    
                    await db.add_item(ctx.author.id, x['name'])

                    await ctx.send(f"**{ctx.author.name}** purchased {x['article']}{x['emoji']} **{x['name']}** for ${x['cost']}.")

                    await db.rolecheck(ctx.author.id)
                    await db.leaderboard()
                    return
                
            await ctx.send(f"There is no such item called **{item}**.")


    @commands.command()
    async def use(self, ctx, *, item=None):

        async with self.client.pool.acquire() as db:

            if not await db.level_check(ctx, ctx.author.id, 4, "use items"):
                return

            jailtime = await db.get_member_val(ctx.author.id, 'jailtime')     
            # Don't use jail heist check here because pass is an exception   

            if item:
                if item.lower() != 'pass':
                    if jailtime > time.time():
                        return await ctx.send(f'You are still in jail for {splittime(jailtime)}.')
                        

            if self.client.heist:

                if self.client.heist["victim"] == ctx.author.id: return await ctx.send(f"You are currently being targeted for a heist.")

                elif ctx.author.id in self.client.heist["participants"]: return await ctx.send(f"You are participating in a heist right now.")


            if not item:
                return await ctx.send("Incorrect command usage:\n`.use item`")

            temp = await db.fetch('SELECT name, article, emoji FROM shop')
            

            items = list(map(lambda x: {'name': x[0], 'article': x[1], 'emoji': x[2]}, temp))

            item = item.lower()

            for shopitem in items:
                if item in shopitem.values():
                    article = shopitem['article']
                    emoji = shopitem['emoji']
                    break
            else:
                await ctx.send(f"There is no such item called **{item}**.")
                return


            if item not in await db.get_member_val(ctx.author.id, 'items'):
                return await ctx.send(f"You do not own {article}{emoji} **{item}**.")

            if item in await db.in_use(ctx.author.id):
                return await ctx.send(f"You already have {article}{emoji} **{item}** in use.")
                
            await ItemUses(self.client, db).dispatch(ctx, item)
        

    @commands.command()
    async def give(self, ctx, member: discord.Member=None, *, item=None):

        async with self.client.pool.acquire() as db:

            if not await db.event_disabled(ctx):
                return
        
            if not member or not item:
                return await ctx.send("Incorrect command usage:\n`.give member item`")

            elif not await db.jail_heist_check(ctx, ctx.author): return
            
            elif not await bot_check(self.client, ctx, member): return

            elif await db.get_member_val(member.id, 'level') < 4:
                await ctx.send(f"**{member.name}** must be at least level 4 in order to use items.")
                return

            if not await db.member_event_check(ctx, member.id): return
            

            items = await db.fetch('SELECT name, article, emoji FROM shop;')

            item = item.lower()

            for shopitem in items:
                if item == shopitem[0]:
                    picked_item = shopitem
                    break
            else:
                await ctx.send(f"There is no such item called **{item}**.")
                return

            if item not in await db.get_member_val(ctx.author.id, 'items'):
                await ctx.send(f"You do not own {picked_item[1]}{picked_item[2]} **{picked_item[0]}**.")
                return

            elif len(await db.get_member_val(member.id, 'items')) >= await db.get_member_val(member.id, 'storage'):
                await ctx.send(f"**{member.name}**'s item inventory is full.")
                return

            await db.remove_item(ctx.author.id, item)
            await db.add_item(member.id, item)
        
        await ctx.send(f"You gave {picked_item[1]}{picked_item[2]} **{picked_item[0]}** to **{member.name}**.")
    

    @commands.command()
    async def discard(self, ctx, *, item=None):

        async with self.client.pool.acquire() as db:
        
            if not await db.jail_heist_check(ctx, ctx.author):
                return

            if not item: 
                return await ctx.send("Incorrect command usage:\n`.discard item`")
                

            items = await db.fetch('SELECT name, article, emoji FROM shop;')

            item = item.lower()

            for shopitem in items:
                if item == shopitem[0]:
                    picked_item = shopitem
                    break

            else:
                await ctx.send(f"There is no such item called **{item}**.")
                return


            if item not in await db.get_member_val(ctx.author.id, 'items'):
                await ctx.send(f"You do not own {picked_item[1]}{picked_item[2]} **{picked_item[0]}**.")
                return


            await db.remove_item(ctx.author.id, item)
            await ctx.send(f'**{ctx.author.name}** discarded {picked_item[1]}{picked_item[2]} **{picked_item[0]}**.')
        

    @commands.command()
    @commands.max_concurrency(1, per=commands.BucketType.member)
    async def daily(self, ctx):

        async with self.client.pool.acquire() as db:

            dailytime = await db.get_member_val(ctx.author.id, 'dailytime')

            if not dailytime:
                dailytime = int(time.time())-1

            timeDifference = int(dailytime - time.time()) // 86400 # Number of seconds in a day 

            rewards = [40, 50, 60, 70, 80, 90, 100, 0]

            if timeDifference >= 0:
                await ctx.send(f"You must wait {splittime(dailytime)} before you can claim your next reward.")
                return

            elif timeDifference <= -2:
                streak = 0

            else:
                streak = await db.get_member_val(ctx.author.id, 'dailystreak')

            reward = rewards[streak]
            streak += 1
            nextreward = rewards[streak]

            if streak < 7:
                
                if streak != 6:
                    await ctx.send(f"You've earned ${reward}. Come back tomorrow for ${nextreward}!\n*Current streak: {streak}*")
                
                else:
                    level = await db.get_member_val(ctx.author.id, 'level')
                    if level >= 4:
                        await ctx.send(f"You've earned ${reward}. Come back tomorrow for ${nextreward}, along with a random shop item!\n*Current streak: {streak}*")
                    else:
                        await ctx.send(f"You've earned ${reward}. Come back tomorrow for ${nextreward}!\n*Current streak: {streak}*")

                money = await db.get_member_val(ctx.author.id, 'money')
                money += reward
                await db.set_member_val(ctx.author.id, 'money', money)

                await db.rolecheck(ctx.author.id)
                await db.leaderboard()

            else:

                skip = False
                storage = await db.get_member_val(ctx.author.id, 'storage')
                level = await db.get_member_val(ctx.author.id, 'level')

                if level >= 4:
                    if len(await db.get_member_val(ctx.author.id, 'items')) >= storage:

                        await ctx.send(f"You can only carry a maximum {storage} items. Do you want to discard the shop item you recieve automatically? (Yes/No)")
                        try:
                            answer = await self.client.wait_for('message', check=lambda m: m.channel == ctx.channel and m.ctx.author == ctx.author, timeout=20)
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


                        items = await db.fetch('SELECT name, article, emoji FROM shop;')
                        
                        # excluding thingy because thats garbage
                        for item in items:
                            if item[0] == "thingy": 
                                items.remove(item)
                                break

                        item, article, emoji = random.choice(items)
                        

                        await ctx.send(f"You've earned ${reward}, along with {article}{emoji} **{item}**!\n*Streak reset to 0.*")
                        await db.add_item(ctx.author.id, item)

                    else:
                        await ctx.send(f"You've earned ${reward}!\n*Streak reset to 0.*")
                else:
                    await ctx.send(f"You've earned ${reward}!\n*Streak reset to 0.*")

                streak = 0
                await db.set_member_val(ctx.author.id, 'dailystreak', 0)
                money = await db.get_member_val(ctx.author.id, 'money')
                money += reward
                await db.set_member_val(ctx.author.id, 'money', money)
                await db.rolecheck(ctx.author.id)
                await db.leaderboard()

            await db.set_member_val(ctx.author.id, 'dailystreak', streak)

            if timeDifference <= -2:
                dailytime = int(time.time()) + 86400
            else:
                dailytime += 86400

            await db.set_member_val(ctx.author.id, 'dailytime', dailytime)

    @commands.command()
    async def claim(self, ctx):
        
        async with self.client.pool.acquire() as db:


            if not await db.jail_heist_check(ctx, ctx.author):
                return

            with open('./storage/jsons/wallet.json') as json_file:
                walletinfo = json.load(json_file)
            
            if walletinfo["channel"] == ctx.channel.id:
                earnings = random.randint(100,150)
                money = await db.get_member_val(ctx.author.id, 'money')
                money += earnings
                await db.set_member_val(ctx.author.id, "money", money)
                await db.leaderboard()
                await ctx.send(f"**{ctx.author.name}** claimed the wallet and earned ${earnings}.")

                newinfo = {}
                newinfo["timer"] = int(time.time()) + random.randint(21600, 25200)
                newinfo["channel"] = 0
                newinfo["continue"] = "True"
                with open('./storage/jsons/wallet.json','w') as json_file:
                    json.dump(newinfo, json_file, indent=2)
            else:
                await ctx.send("There is no wallet in this channel.")


def setup(client):
    client.add_cog(Actions(client))