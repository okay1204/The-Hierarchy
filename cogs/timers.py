# pylint: disable=import-error

import discord
from discord.ext import commands, tasks
import time
import sqlite3
from sqlite3 import Error
import random
import os
import json
import asyncio

# To import from different path
import sys
sys.path.insert(1 , os.getcwd())

from utils import (write_value, read_value, minisplittime)




class timers(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.eventtimer.start() # noqa pylint: disable=no-member

    def cog_unload(self):
        self.eventtimer.cancel() # noqa pylint: disable=no-member

    async def tax(self):

        channel = self.client.get_channel(698403873374601237)
        guild = self.client.mainGuild

        conn = sqlite3.connect('./storage/databases/hierarchy.db')
        c = conn.cursor()
        c.execute('SELECT id, money, bank FROM members')
        users = c.fetchall()
        conn.close()

        for userid, money, bank in users:

            total = money + bank

            tax = int(total * 0.03)

            if tax > 200:
                tax = 200
            if bank >= tax:
                bank -= tax

                
            elif bank < tax:

                extra = tax - bank
                bank = 0
                if extra > money:
                    money = 0
                elif extra <= money:
                    money -= extra

            conn = sqlite3.connect('./storage/databases/hierarchy.db')
            c = conn.cursor()
            c.execute("UPDATE members SET bank = ?, hbank = ? WHERE id = ?", (bank, bank, userid))

        taxping = guild.get_role(698321954742075504)
        await channel.send(f"{taxping.mention} A 3% tax has been collected. *(No more than $200 was taken from your account)*")

    async def bank(self):
        channel = self.client.get_channel(698403873374601237)
        guild = self.client.mainGuild

        conn = sqlite3.connect('./storage/databases/hierarchy.db')
        c = conn.cursor()
        c.execute('SELECT id, money, bank FROM members')
        users = c.fetchall()
        conn.close()

        for userid, money, bank in users:

            tax = int(bank * 0.06)

            if tax > 200:
                tax = 200
            if bank >= tax:
                bank -= tax

                
            elif bank < tax:

                extra = tax - bank
                bank = 0
                if extra > money:
                    money = 0
                elif extra <= money:
                    money -= extra

            conn = sqlite3.connect('./storage/databases/hierarchy.db')
            c = conn.cursor()
            c.execute("UPDATE members SET bank = ?, hbank = ? WHERE id = ?", (bank, bank, userid))

        bankping = guild.get_role(698322063206776972)
        await channel.send(f"{bankping.mention} A 6% bank fee has been collected. *(No more than $200 was taken from your account)*")

    async def shopchange(self):
        channel = self.client.get_channel(710211979360338020)
        conn = sqlite3.connect('./storage/databases/shop.db')
        c = conn.cursor()
        c.execute('SELECT * FROM shop')
        stats = c.fetchall()
        embed = discord.Embed(color=0x30ff56, title='Shop')
        guild = self.client.mainGuild
        shopping = guild.get_role(716818790947618857)
        x = 1
        text = f"{shopping.mention}"
        for stat in stats:

            if stat[2] == 'down':
                if random.randint(1,3) == 1:
                    change = 'up'
                else:
                    change = 'down'
            if stat[2] == 'up':
                if random.randint(1,3) == 1:
                    change = 'down'
                else:
                    change = 'up'
            
            if change == 'up':
                newmax = stat[1] + 5
                if newmax > stat[4]:
                    newmax = stat[4]
                newprice = random.randint(stat[1], newmax)
        
            elif change == 'down':
                newmin = stat[1] - 5
                if newmin < stat[3]:
                    newmin = stat[3]
                newprice = random.randint(newmin, stat[1])
            

            if newprice > stat[1]:
                text = f'{text}\n{stat[0].capitalize()}: ⏫ ${newprice-stat[1]} *${stat[1]} -> ${newprice}*'
            elif newprice < stat[1]:
                text = f'{text}\n{stat[0].capitalize()}: ⏬ ${stat[1]-newprice} *${stat[1]} -> ${newprice}*'
            if newprice == stat[1]:
                text = f'{text}\n{stat[0].capitalize()}: No change'


            c.execute(f"UPDATE shop SET price = {newprice}, last = '{change}' WHERE name = '{stat[0]}'")

            embed.add_field(name=f'{x}. ${newprice} - {stat[0].capitalize()} {stat[6]}', value=stat[5], inline=False)
            x += 1

        conn.commit()
        conn.close()

        await channel.send(text)
        shopchannel = self.client.get_channel(702654620291563600)
        message = await shopchannel.fetch_message(740680266086875243)
        await message.edit(embed=embed)

    async def boosts(self):
        conn = sqlite3.connect('./storage/databases/hierarchy.db')
        c = conn.cursor()
        c.execute('SELECT id, boosts FROM members')
        users = c.fetchall()
        conn.close()

        guild = self.client.mainGuild

        for userid, boosts in users:

            if (member := guild.get_member(userid)):
                if not member.premium_since:
                    continue
            else: continue


            if boosts < 3:
                boosts += 1
                write_value(userid, 'boosts', boosts)
        
        timewarpchannel = self.client.get_channel(727729749375320095)
        guild = self.client.mainGuild
        timewarpping = guild.get_role(727725637317427332)
        await timewarpchannel.send(f"{timewarpping.mention} Boosts have been given out to premium members.")



    @tasks.loop(minutes=1)
    async def eventtimer(self):

        embed = discord.Embed(color=0x442391)

        feechannel = self.client.get_channel(698322322834063430)
        feemessage = await feechannel.fetch_message(740013720301731880)


        shopchannel = self.client.get_channel(710211730797756477)
        shopmessage = await shopchannel.fetch_message(740013721371410474)


        premiumchannel = self.client.get_channel(727727716539039824)
        premiummessage = await premiumchannel.fetch_message(740013722642153543)

        
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
        embed3 = discord.Embed(color=0xff61d7, title="Boost timer")

        if banktime == 0:
            await self.bank()
            embed.add_field(name="Bank fee collection",value='12h 0m',inline=False)
            await  self.boosts()
            embed3.add_field(name="__________",value='12h 0m',inline=False)
        else:
            embed.add_field(name="Bank fee collection",value=f'{minisplittime(banktime)}',inline=False)
            embed3.add_field(name="__________",value=f'{minisplittime(banktime)}',inline=False)

        embed2 = discord.Embed(color=0x30ff56, title='Shop change timer')
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
    client.add_cog(timers(client))