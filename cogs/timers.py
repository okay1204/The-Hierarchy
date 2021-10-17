# pylint: disable=import-error

import nextcord
from nextcord.ext import commands, tasks
import time
import random
import os
import json
import asyncio

# To import from different path
import sys
sys.path.insert(1 , os.getcwd())

from utils import bot_check, splittime, timestring, log_command, minisplittime

class Timers(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.eventtimer.start() # noqa pylint: disable=no-member

    def cog_unload(self):
        self.eventtimer.cancel() # noqa pylint: disable=no-member

    async def tax(self):

        channel = self.client.get_channel(698403873374601237)
        guild = self.client.mainGuild

        
        async with self.client.pool.acquire() as db:
            await db.execute(
            '''
            WITH tax AS (
            SELECT id, LEAST(FLOOR((bank+money)*0.03), 100) AS tax_amount
                FROM members
            )
            UPDATE members m
            SET bank = GREATEST(m.bank - t.tax_amount, 0),
                money = 
                CASE
                    WHEN t.tax_amount > m.bank THEN GREATEST(m.money + m.bank - t.tax_amount, 0)
                    ELSE m.money
                END
            FROM tax t
            WHERE t.id = m.id;
            ''')
        

        taxping = guild.get_role(698321954742075504)
        await channel.send(f"{taxping.mention} A 3% tax has been collected. *(No more than $100 was taken from your account)*")

    async def bank(self):
        channel = self.client.get_channel(698403873374601237)
        guild = self.client.mainGuild

        async with self.client.pool.acquire() as db:
            await db.execute(
            '''
            WITH fee AS (
            SELECT id, LEAST(FLOOR(bank*0.06), 200) AS fee_amount
                FROM members
            )
            UPDATE members m
            SET bank = GREATEST(m.bank - f.fee_amount, 0),
                hbank = GREATEST(m.bank - f.fee_amount, 0),
                money = 
                CASE
                    WHEN f.fee_amount > m.bank THEN GREATEST(m.money + m.bank - f.fee_amount, 0)
                    ELSE m.money
                END
            FROM fee f
            WHERE f.id = m.id;
            ''')

        bankping = guild.get_role(698322063206776972)
        await channel.send(f"{bankping.mention} A 6% bank fee has been collected. *(No more than $200 was taken from your account)*")

    async def shopchange(self):

        channel = self.client.get_channel(710211979360338020)

        async with self.client.pool.acquire() as db:

            async with db.transaction():
                stats = await db.fetch('SELECT * FROM shop')


                embed = nextcord.Embed(color=0x30ff56, title='Shop')
                guild = self.client.mainGuild
                shopping = guild.get_role(716818790947618857)


                x = 1
                text = f"{shopping.mention}"

                for name, price, last, minimum, maximum, desc, emoji, article in stats: # noqa pylint: disable=unused-variable

                    if last == 'down':
                        if random.randint(1,3) == 1:
                            change = 'up'
                        else:
                            change = 'down'
                    if last == 'up':
                        if random.randint(1,3) == 1:
                            change = 'down'
                        else:
                            change = 'up'
                    
                    if change == 'up':
                        newmax = price + 5
                        if newmax > maximum:
                            newmax = maximum
                        newprice = random.randint(price, newmax)
                
                    elif change == 'down':
                        newmin = price - 5
                        if newmin < minimum:
                            newmin = minimum
                        newprice = random.randint(newmin, price)
                    

                    if newprice > price:
                        text = f'{text}\n{name.capitalize()}: ⏫ ${newprice-price} *${price} -> ${newprice}*'
                    elif newprice < price:
                        text = f'{text}\n{name.capitalize()}: ⏬ ${price-newprice} *${price} -> ${newprice}*'
                    if newprice == price:
                        text = f'{text}\n{name.capitalize()}: No change'


                    await db.execute("UPDATE shop SET price = $1, last = $2 WHERE name = $3", newprice, change, name)

                    embed.add_field(name=f'{x}. ${newprice} - {name.capitalize()} {emoji}', value=desc, inline=False)
                    x += 1


        await channel.send(text)
        shopchannel = self.client.get_channel(702654620291563600)

        # this tends to randomly fail for no reason so keep doing it until it works
        while True:
            try:
                message = await shopchannel.fetch_message(740680266086875243)
                break
            except nextcord.nextcordServerError:
                await asyncio.sleep(2)
                continue


        await message.edit(embed=embed)

    async def boosts(self):

        async with self.client.pool.acquire() as db:

            async with db.transaction():

                users = await db.fetch('SELECT id, boosts FROM members')

                guild = self.client.mainGuild

                for userid, boosts in users:

                    if (member := guild.get_member(userid)):
                        if not member.premium_since:
                            continue

                    else: continue


                    if boosts < 3:
                        boosts += 1
                        await db.set_member_val(userid, 'boosts', boosts)
                
                timewarpchannel = self.client.get_channel(727729749375320095)
                guild = self.client.mainGuild
                timewarpping = guild.get_role(727725637317427332)

                await timewarpchannel.send(f"{timewarpping.mention} Boosts have been given out to premium members.")



    @tasks.loop(minutes=1)
    async def eventtimer(self):

        embed = nextcord.Embed(color=0x442391)

        # this tends to randomly fail for no reason so keep doing it until it works

        feechannel = self.client.get_channel(698322322834063430)

        while True:
            try:
                feemessage = await feechannel.fetch_message(740013720301731880)
                break
            except nextcord.nextcordServerError:
                await asyncio.sleep(2)
                continue

        shopchannel = self.client.get_channel(710211730797756477)

        while True:
            try:
                shopmessage = await shopchannel.fetch_message(740013721371410474)
                break
            except nextcord.nextcordServerError:
                await asyncio.sleep(2)
                continue


        premiumchannel = self.client.get_channel(727727716539039824)

        while True:
            try:
                premiummessage = await premiumchannel.fetch_message(740013722642153543)
                break
            except nextcord.nextcordServerError:
                await asyncio.sleep(2)
                continue

        
        embed.set_author(name="Fee collection times")
        taxtime = time.localtime()
        minutes = taxtime[4] + taxtime[3]*60
        taxtime = 1440-minutes

        banktime = time.localtime()
        minutes = banktime[4] + banktime[3]*60
        banktime = 720-minutes

        shoptime = time.localtime()
        minutes = shoptime[4] + shoptime[3]*60
        shoptime = 0
        times = [0,180,360,540,720,900,1080,1260]

        for x in times:
            if minutes > x and minutes < x+180:
                shoptime = x+180

        shoptime -= minutes
        if minutes in times:
            shoptime = 0

        if banktime < 0 or banktime == 720:
            banktime = 1440-minutes
            if banktime == 1440:
                banktime = 0

        if taxtime == 1440:
            await self.tax()
        
        embed.add_field(name="Tax collection",value=f'{minisplittime(taxtime)}',inline=False)

        embed3 = nextcord.Embed(color=0xff61d7, title="Boost timer")

        if banktime == 0:
            await self.bank()
            embed.add_field(name="Bank fee collection",value='12h 0m',inline=False)
            await  self.boosts()
            embed3.add_field(name="__________",value='12h 0m',inline=False)
        else:
            embed.add_field(name="Bank fee collection",value=f'{minisplittime(banktime)}',inline=False)
            embed3.add_field(name="__________",value=f'{minisplittime(banktime)}',inline=False)

        embed2 = nextcord.Embed(color=0x30ff56, title='Shop change timer')
        if shoptime == 0:
            await self.shopchange()
            embed2.add_field(name='__________', value='3h 0m', inline=False)
        else:
            embed2.add_field(name='__________', value=f'{minisplittime(shoptime)}', inline=False)
                
        await feemessage.edit(embed=embed)
        await shopmessage.edit(embed=embed2)
        await premiummessage.edit(embed=embed3)

        with open('./storage/jsons/wallet.json') as json_file:
            walletinfo = json.load(json_file)
        
        if time.time() >= walletinfo["timer"] and walletinfo["continue"] == "True":
            category = self.client.get_channel(692949972764590160)
            channels = category.text_channels
            special_channels = [706953015415930941, 714585657808257095, 723945572708384768]
            channels = list(filter(lambda x: x.id not in special_channels, channels))
            channel = random.choice(channels)
            await channel.send("A wallet has been dropped in this channel! Type `.claim` to pick it up.")
            newinfo = {}
            newinfo["timer"] = walletinfo["timer"]
            newinfo["channel"] = channel.id
            newinfo["continue"] = "False"
            with open('./storage/jsons/wallet.json','w') as json_file:
                json.dump(newinfo, json_file, indent=2)

        elif time.time() >= walletinfo["timer"] + 21600 and walletinfo["continue"] == "False":
            channel = self.client.get_channel(walletinfo["channel"])
            await channel.send("The wallet in this channel was lost...")
            newinfo = {}
            newinfo["timer"] = int(time.time()) + random.randint(600, 1200)
            newinfo["channel"] = 0
            newinfo["continue"] = "True"
            with open('./storage/jsons/wallet.json','w') as json_file:
                json.dump(newinfo, json_file, indent=2)



def setup(client):
    client.add_cog(Timers(client))