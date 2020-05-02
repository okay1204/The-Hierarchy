import discord
from discord.ext import commands, tasks
import random
import json
import time
import asyncio
from utils import *



client = commands.Bot(command_prefix = '.')
client.remove_command('help')


@client.event
async def on_ready():
    print("Bot ready")
    guild = client.get_guild(692906379203313695)
    await client.change_presence(activity=discord.Game(name='with money'))
    timer.start()
    eventtimer.start()
    hierarchy = open_json()
    for person in hierarchy:
        person["total"] = person["money"] + person["bank"]
        person["isworking"] = "False"
    write_json(hierarchy)

async def tax():
    hierarchy = open_json()
    channel = client.get_channel(698403873374601237)
    guild = client.get_guild(692906379203313695)
    for person in hierarchy:
        tax = person["total"] * 0.03
        tax = int(tax)
        if tax > 100:
            tax = 100
        if person["bank"] >= tax:
            person["bank"] -= tax
        elif person["bank"] < tax:
            extra = tax - person["bank"]
            person["bank"] = 0
            if extra > person["money"]:
                person["money"] = 0
            elif extra <= person["money"]:
                person["money"] -= extra
        person["total"] = person["money"] + person["bank"]
    taxping = guild.get_role(698321954742075504)
    await channel.send(f"{taxping.mention} A 3% tax has been collected. *(No more than $100 was taken from your account)*")
    write_json(hierarchy)
    await leaderboard(client)


async def bank():
    hierarchy = open_json()
    channel = client.get_channel(698403873374601237)
    guild = client.get_guild(692906379203313695)
    for person in hierarchy:
        bank = person["hbank"] * 0.1
        bank = int(bank)
        if bank > 200:
            bank = 200
        if person["bank"] >= bank:
            person["bank"] -= bank
        elif person["bank"] < bank:
            extra = bank - person["bank"]
            person["bank"] = 0
            if extra > person["money"]:
                person["money"] = 0
            elif extra <= person["money"]:
                person["money"] -= extra
        person["total"] = person["money"] + person["bank"]
        person["hbank"] = person["bank"]
    bankping = guild.get_role(698322063206776972)
    await channel.send(f"{bankping.mention} A 10% bank fee has been collected. *(No more than $200 was taken from your account)*")
    write_json(hierarchy)
    await leaderboard(client)

            
@tasks.loop(seconds=1)
async def timer():
    hierarchy = open_json()
    hierarchystats = open_json2()
    for person in hierarchy:
        if person["workc"] > 0:
            person["workc"] -= 1
        if person["jailtime"] > 0:
            person["jailtime"] -= 1
        if person["stealc"] > 0:
            person["stealc"] -= 1
        if person["rpsc"] > 0:
            person["rpsc"] -= 1
        if person["bankc"] > 0:
            person["bankc"] -= 1
        for item in person["inuse"]:
            if "timer" in item:
                if item["timer"] > 0:
                    item["timer"] -= 1
                    if item["timer"] == 0:
                        itemindex = person["inuse"].index(item)
                        person["inuse"].pop(itemindex)
                
    if hierarchystats["heistc"] > 0:
        hierarchystats["heistc"] -= 1
    if hierarchystats["heistt"] > 0:
        hierarchystats["heistt"] -= 1
        if hierarchystats["heistt"] == 0:
            channel = client.get_channel(int(hierarchystats["heistl"]))
            if len(hierarchystats["heistp"]) < 3:
                hierarchystats["heistl"] = "None"
                hierarchystats["oheist"] = "False"
                hierarchystats["heistp"] = []
                hierarchystats["heistv"] = "None"
                await channel.send("Heist cancelled: Not enough people joined.")
            else:
                guild = client.get_guild(692906379203313695)
                total = 0
                for person in hierarchy:
                    if int(person["user"]) in hierarchystats["heistp"]:
                        person["heistamount"] = random.randint(40,50)
                        total += person["heistamount"]
                for person in hierarchy:
                    if hierarchystats["heistv"] == person["user"]:
                        while person["bank"] < total:
                            total2 = 0
                            for person2 in hierarchy:
                                if int(person2["user"]) in hierarchystats["heistp"]:
                                    person2["heistamount"] -= 1
                                    total2 += person2["heistamount"]
                                    total = total2
                embed = discord.Embed(color=0xed1f1f)
                embed.set_author(name="Heist results")
                for person in hierarchy:
                    if int(person["user"]) in hierarchystats["heistp"]:
                        if random.randint(1,4) == 1:
                            gotaway = False
                            for item in person["inuse"]:
                                    if item["name"] == "gun":
                                        if random.randint(1,2) == 1:
                                            embed.add_field(name=f'{guild.get_member(int(person["user"])).name}', value=f'Caught, got away with their gun.', inline=True)
                                            gotaway = True
                            if gotaway == False:
                                embed.add_field(name=f'{guild.get_member(int(person["user"])).name}', value=f'Caught, jailed for 3h.', inline=True)
                                person["jailtime"] = 10800
                            await rolecheck(client, int(person["user"]))
                        else:
                            embed.add_field(name=f'{guild.get_member(int(person["user"])).name}', value=f'Got away with ${person["heistamount"]}.')
                            person["money"] += person["heistamount"]
                            person["total"] = person["money"] + person["bank"]
                            for person2 in hierarchy:
                                if person2["user"] == hierarchystats["heistv"]:
                                    person2["bank"] -= person["heistamount"]
                                    person2["total"] = person2["bank"] + person2["money"]
                                    break
                for person in hierarchy:
                    if person["user"] == hierarchystats["heistv"]:
                        await rolecheck(client, int(person["user"]))
                        break

                channel = client.get_channel(int(hierarchystats["heistl"]))
                await channel.send(embed=embed)
                hierarchystats["heistv"] = "None"
                hierarchystats["heistt"] = 0
                hierarchystats["heistp"] = []
                hierarchystats["heistl"] = "None"
                hierarchystats["oheist"] = "False"
                hierarchystats["heistc"] = 9000
                write_json(hierarchy)
                write_json2(hierarchystats)
                await leaderboard(client)
                return
                
    write_json(hierarchy)
    write_json2(hierarchystats)

@tasks.loop(seconds=60)
async def eventtimer():
    embed = discord.Embed(color=0x442391)
    channel = client.get_channel(698322322834063430)
    feemessage = await channel.fetch_message(698775208663973940)
    embed.set_author(name="Fee collection times")
    taxtime = time.localtime()
    minutes = taxtime[4] + taxtime[3]*60
    taxtime = 1440-minutes
    banktime = time.localtime()
    minutes = banktime[4] + banktime[3]*60
    banktime = 720-minutes
    if banktime < 0 or banktime == 720:
        banktime = 1440-minutes
        if banktime == 1440:
            banktime = 0
    if taxtime == 1440:
        await tax()
        embed.add_field(name="Tax collection",value=f'{minisplittime(taxtime)}',inline=False)
    else:
        embed.add_field(name="Tax collection",value=f'{minisplittime(taxtime)}',inline=False)
    if banktime == 0:
        await bank()
        embed.add_field(name="Bank fee collection",value=f'{minisplittime(banktime)}',inline=False)
    else:
        embed.add_field(name="Bank fee collection",value=f'{minisplittime(banktime)}',inline=False)
    await feemessage.edit(embed=embed)


    
@client.event
async def on_raw_reaction_add(payload):
    guild = client.get_guild(692906379203313695)
    taxping = guild.get_role(698321954742075504)
    bankping = guild.get_role(698322063206776972)
    channel = client.get_channel(698318226613993553)
    if payload.message_id == 698774871949181039:
        user = payload.user_id
        user = guild.get_member(user)
        await user.add_roles(taxping)
    if payload.message_id == 698774872628789328:
        user = payload.user_id
        user = guild.get_member(user)
        await user.add_roles(bankping)

@client.event
async def on_raw_reaction_remove(payload):
    guild = client.get_guild(692906379203313695)
    taxping = guild.get_role(698321954742075504)
    bankping = guild.get_role(698322063206776972)
    channel = client.get_channel(698318226613993553)
    if payload.message_id == 698774871949181039:
        user = payload.user_id
        user = guild.get_member(user)
        await user.remove_roles(taxping)
    if payload.message_id == 698774872628789328:
        user = payload.user_id
        user = guild.get_member(user)
        await user.remove_roles(bankping)
        
        
@client.event
async def on_member_join(member):
    channel = client.get_channel(692956542437425153)
    guild = client.get_guild(692906379203313695)
    poor = member.guild.get_role(692952611141451787)
    await channel.send(f"Hey {member.mention}, welcome to **The Hierarchy**! Please check <#692951648410140722> before you do anything else!")
    await member.add_roles(poor)
    alreadyin = False
    hierarchy = open_json()
    memberid = str(member.id)
    for person in hierarchy:
        if memberid == person["user"]:
            alreadyin = True
            
    if alreadyin == False:
        memberid = str(member.id)
        person = {'user':memberid,'money':0, 'workc':0, 'jailtime': 0, 'stealc': 0, 'rpsc': 0, 'bank': 0, 'bankc': 0, 'total': 0, 'hbank': 0, 'heistamount': 0, 'items':[], 'inuse':[], 'storage':2, 'isworking':'False'}
        hierarchy.append(person)
        write_json(hierarchy)
    await leaderboard(client)
    

@client.event
async def on_member_remove(member):
    channel = client.get_channel(692956542437425153)
    guild = client.get_guild(692906379203313695)
    inaudit = False
    async for entry in guild.audit_logs(limit=1):
        if entry.action == discord.AuditLogAction.ban or entry.action == discord.AuditLogAction.kick:
            inaudit = True
        if entry.action == discord.AuditLogAction.kick:
            await channel.send(f"**{entry.user.name}** kicked {entry.target.mention} from the server.")
        if entry.action == discord.AuditLogAction.ban:
            await channel.send(f"**{entry.user.name}** banned {entry.target.mention} from the server.")
    if inaudit == False:
        await channel.send(f"{member.mention} has left **The Hierarchy**. Too bad for him/her.")
    await leaderboard(client)
    





client.load_extension('debug')        
client.load_extension('info')
client.load_extension('games')
client.load_extension('actions')
client.run('Njk4NzcxMjcxMzUzMjM3NTc1.XpKrfw.2bt069XC42fFvaUQQdfprVM7omc')
