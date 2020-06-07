import discord
from discord.ext import commands, tasks
import time
import sqlite3
from sqlite3 import Error
import random
from utils import *



client = commands.Bot(command_prefix = '.')
client.remove_command('help')

@client.event
async def on_ready():
    print(f"Logged in as {client.user}.\nID: {client.user.id}")
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="the timers"))
    eventtimer.start()

async def tax():
    channel = client.get_channel(698403873374601237)
    guild = client.get_guild(692906379203313695)
    conn = sqlite3.connect('hierarchy.db')
    c = conn.cursor()
    c.execute('SELECT id, money, bank, total FROM members')
    users = c.fetchall()
    conn.close()
    for person in users:
        money = person[1]
        bank = person[2]
        total = person[3]
        tax = int(total * 0.03)
        if tax > 100:
            tax = 100
        if bank >= tax:
            bank -= tax
            write_value('members', 'id', person[0], 'bank', bank)
        elif bank < tax:
            extra = tax - bank
            bank = 0
            if extra > money:
                money = 0
            elif extra <= money:
                money -= extra
        write_value('members', 'id', person[0], 'bank', bank)
        update_total(person[0])
    taxping = guild.get_role(698321954742075504)
    await channel.send(f"{taxping.mention} A 3% tax has been collected. *(No more than $100 was taken from your account)*")

async def bank():
    channel = client.get_channel(698403873374601237)
    guild = client.get_guild(692906379203313695)
    conn = sqlite3.connect('hierarchy.db')
    c = conn.cursor()
    c.execute('SELECT id, money, bank, total FROM members')
    users = c.fetchall()
    conn.close()
    for person in users:
        money = person[1]
        bank = person[2]
        total = person[3]
        tax = int(total * 0.06)
        if tax > 200:
            tax = 200
        if bank >= tax:
            bank -= tax
            write_value('members', 'id', person[0], 'bank', bank)
        elif bank < tax:
            extra = tax - bank
            bank = 0
            if extra > money:
                money = 0
            elif extra <= money:
                money -= extra
        write_value('members', 'id', person[0], 'bank', bank)
        update_total(person[0])
        write_value('members', 'id', person[0], 'hbank', bank)
    bankping = guild.get_role(698322063206776972)
    await channel.send(f"{bankping.mention} A 6% bank fee has been collected. *(No more than $200 was taken from your account)*")

async def shopchange():
    channel = client.get_channel(710211979360338020)
    conn = sqlite3.connect('hierarchy.db')
    c = conn.cursor()
    c.execute('SELECT * FROM shop')
    stats = c.fetchall()
    embed = discord.Embed(color=0x30ff56)
    embed.set_author(name='Shop')
    guild = client.get_guild(692906379203313695)
    shopping = guild.get_role(716818790947618857)
    x = 1
    text = f"{shopping.mention}"
    for stat in stats:
        change = ""
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
        
        if change is 'up':
            newmax = stat[1] + 5
            if newmax > stat[4]:
                newmax = stat[4]
            newprice = random.randint(stat[1], newmax)
      
        if change is 'down':
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


        c.execute(f"UPDATE shop SET price = {newprice} WHERE name = '{stat[0]}'")
        c.execute(f"UPDATE shop SET last = '{change}' WHERE name = '{stat[0]}'")

        embed.add_field(name=f'{x}. ${newprice} - {stat[0].capitalize()} {stat[6]}', value=f'{stat[5]}', inline=False)
        x += 1


    await channel.send(text)
    shopchannel = client.get_channel(702654620291563600)
    message = await shopchannel.fetch_message(717499489627275337)
    await message.edit(embed=embed)
    conn.commit()
    conn.close()

@tasks.loop(minutes=1)
async def eventtimer():
    embed = discord.Embed(color=0x442391)
    feechannel = client.get_channel(698322322834063430)
    shopchannel = client.get_channel(710211730797756477)
    feemessage = await feechannel.fetch_message(717456264967487548)
    shopmessage = await shopchannel.fetch_message(717456265730719794)
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
        await tax()
    
    embed.add_field(name="Tax collection",value=f'{minisplittime(taxtime)}',inline=False)
    
    if banktime == 0:
        await bank()
        embed.add_field(name="Bank fee collection",value='12h 0m',inline=False)
    else:
        embed.add_field(name="Bank fee collection",value=f'{minisplittime(banktime)}',inline=False)

    embed2 = discord.Embed(color=0x30ff56)
    embed2.set_author(name='Shop change times')
    if shoptime == 0:
        await shopchange()
        embed2.add_field(name='__________', value='3h 0m', inline=False)
    else:
        embed2.add_field(name='__________', value=f'{minisplittime(shoptime)}', inline=False)
            
    await feemessage.edit(embed=embed)
    await shopmessage.edit(embed=embed2)

client.run('NzE3NDUzNzcwMDM1ODIyNjk0.Xtai8Q._cKaZZOZ310tnNLCihSKp85NJGs')