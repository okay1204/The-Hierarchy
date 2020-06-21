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
    conn = sqlite3.connect('hierarchy.db')
    c = conn.cursor()
    c.execute('UPDATE members SET isworking="False"')
    c.execute('UPDATE members SET isfighting="False"')
    conn.commit()
    conn.close()
    await leaderboard(client)
    

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
    try:
        if message.channel.category == client.get_channel(692949972764590160):
            if message.content.startswith('pls'):
                helpchannel = client.get_channel(692950528417595453)
                await message.channel.send(f"Hey, this server isn't ran by Dank Memer, it's a custom bot! Check {helpchannel.mention} for a list of commands.")
    except:
        pass
    
    if message.channel.id == 723644542275813386:
        boost_channel=client.get_channel(723645417253896234)
        await boost_channel.send(f'HUGE Thank you to {message.author.mention} for boosting the server, we greatly appreciate it! Enjoy the premium perks!')

    await client.process_commands(message)

client.load_extension('debug')        
client.load_extension('info')
client.load_extension('games')
client.load_extension('actions')
client.load_extension('gambling')
client.load_extension('misc')
client.run('Njk4NzcxMjcxMzUzMjM3NTc1.XpKrfw.2bt069XC42fFvaUQQdfprVM7omc')
