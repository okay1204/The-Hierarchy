import discord
from discord.ext import commands, tasks
import random
import json
import time
import asyncio
import sqlite3
from sqlite3 import Error
from utils import *



client = commands.Bot(command_prefix = '.')
client.remove_command('help')


@client.event
async def on_ready():
    print(f"Logged in as {client.user}.\nID: {client.user.id}")
    statuschannel = client.get_channel(698384786460246147)
    statusmessage = await statuschannel.fetch_message(698775210173923429)
    for x in statusmessage.embeds:
        green = discord.Color(0x42f57b)
        red = discord.Color(0xff5254)
        if x.color == green:
            await client.change_presence(status=discord.Status.online, activity=discord.Game(name='with money'))
        elif x.color == red:
            await client.change_presence(status=discord.Status.dnd, activity=discord.Game(name='UNDER DEVELOPMENT'))
    heisttimer.start()
    eventtimer.start()
    conn = sqlite3.connect('hierarchy.db')
    c = conn.cursor()
    c.execute('UPDATE members SET isworking="False"')
    c.execute('UPDATE members SET isfighting="False"')
    conn.commit()
    conn.close()
    await leaderboard(client)
    
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
    await leaderboard(client)

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
    await leaderboard(client)

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
    message = await shopchannel.fetch_message(702906494022058084)
    await message.edit(embed=embed)
    conn.commit()
    conn.close()

@tasks.loop(seconds=1)
async def heisttimer():
    heist = open_json()
    if heist["heistt"] > 0:
        heist["heistt"] -= 1
        write_json(heist)
        if heist["heistt"] == 0:
            channel = client.get_channel(heist["heistl"])
            if len(heist["heistp"]) < 3:
                heist["heistl"] = 0
                heist["oheist"] = "False"
                heist["heistp"] = []
                heist["heistv"] = 0
                write_json(heist)
                await channel.send("Heist cancelled: Not enough people joined.")
            else:
                guild = client.get_guild(692906379203313695)
                total = 0
                for userid in heist["heistp"]:
                    heistamount = random.randint(40,50)
                    write_value('members', 'id', userid, 'heistamount', heistamount)
                    total += heistamount
                    
                while read_value('members', 'id', heist['heistv'], 'bank') < total:
                    total2 = 0
                    for userid2 in heist["heistp"]:
                        heistamount = read_value('members', 'id', userid2, 'heistamount')
                        heistamount -= 1
                        total2 += heistamount
                        write_value('members', 'id', userid2, 'heistamount', heistamount)
                        total = total2
                            
                embed = discord.Embed(color=0xed1f1f)
                embed.set_author(name="Heist results")
                for userid in heist["heistp"]:
                    if random.randint(1,4) == 1:
                        gotaway = False
                        for item in in_use(userid):
                            if item["name"] == "gun":
                                if random.randint(1,2) == 1:
                                    embed.add_field(name=f'{guild.get_member(userid).name}', value=f'Caught, got away with their gun.', inline=True)
                                    gotaway = True
                        if gotaway == False:
                            embed.add_field(name=f'{guild.get_member(userid).name}', value=f'Caught, jailed for 3h.', inline=True)
                            jailtime = int(time.time()) + 10800
                            write_value('members', 'id', userid, 'jailtime', jailtime)
                        await rolecheck(client, userid)
                    else:
                        heistamount = read_value("members", "id", userid, "heistamount")
                        embed.add_field(name=f'{guild.get_member(userid).name}', value=f'Got away with ${heistamount}.')
                        money = read_value("members", "id", userid, "money")
                        money += heistamount
                        write_value("members", "id", userid, "money", money)
                        update_total(userid)
                        bank = read_value("members", "id", heist["heistv"], "bank")
                        bank -= heistamount
                        write_value("members", "id", heist["heistv"], "bank", bank)
                        update_total(heist["heistv"])

                await rolecheck(client, heist["heistv"])

                channel = client.get_channel(heist["heistl"])
                await channel.send(embed=embed)
                heist["heistv"] = "None"
                heist["heistt"] = 0
                heist["heistp"] = []
                heist["heistl"] = "None"
                heist["oheist"] = "False"
                write_json(heist)
                conn = sqlite3.connect('hierarchy.db')
                c = conn.cursor()
                c.execute(f"UPDATE heist SET cooldown = {int(time.time())+9000}")
                conn.commit()
                conn.close()
                await leaderboard(client)

@tasks.loop(minutes=1)
async def eventtimer():
    embed = discord.Embed(color=0x442391)
    feechannel = client.get_channel(698322322834063430)
    pollchannel = client.get_channel(698009727803719757)
    shopchannel = client.get_channel(710211730797756477)
    feemessage = await feechannel.fetch_message(698775208663973940)
    shopmessage = await shopchannel.fetch_message(710213879707336805)
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
    conn = sqlite3.connect('hierarchy.db')
    c = conn.cursor()
    c.execute('SELECT * FROM polls')
    polls = c.fetchall()
    for poll in polls:
        message = await pollchannel.fetch_message(poll[2])    
        text = message.content
        text = text[::-1]
        if poll[1] < time.time() and poll[1] != 0:
            c.execute(f"DELETE FROM polls WHERE name = '{poll[0]}'")
            index = text.index('\n')
            text = text[index:]
            text = text[::-1]
            results = ""
            for reaction in message.reactions:
                temp = f"{str(reaction.emoji)}: {reaction.count-1}   "
                results = f"{results}{temp}"
            text = f'{text}**Poll closed. Results:**\n\n{results}'
            await message.edit(content=text)
            await message.clear_reactions()


        elif poll[1] > time.time() and poll[1] != 0:
            index = text.index('\n')
            text = text[index:]
            text = text[::-1]
            text = f"{text}**Time left: {minisplittime(int(int(poll[1]-time.time())/60))}**"
            await message.edit(content=text)
    conn.commit()
    conn.close()
    
        
@client.event
async def on_member_join(member):
    await asyncio.sleep(0.1)
    await leaderboard(client)


@client.event
async def on_member_remove(member):
    await asyncio.sleep(0.1)
    await leaderboard(client)

@client.event
async def on_message(message):
    if not message.author.bot and message.channel.id == 716720359818133534:
        submissions = client.get_channel(716724583767474317)
        await submissions.send(f"By {message.author.mention}: \n{message.content}")
        await message.delete()
        await message.channel.send(f"{message.author.mention}, your application was successfully submitted.")
    
    await client.process_commands(message)

client.load_extension('debug')        
client.load_extension('info')
client.load_extension('games')
client.load_extension('actions')
client.load_extension('admin')
client.load_extension('gambling')
client.run('Njk4NzcxMjcxMzUzMjM3NTc1.XpKrfw.2bt069XC42fFvaUQQdfprVM7omc')
