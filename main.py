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
    print("Bot ready")
    await client.change_presence(activity=discord.Game(name='with money'))
    heisttimer.start()
    eventtimer.start()
    conn = sqlite3.connect('hierarchy.db')
    c = conn.cursor()
    c.execute('UPDATE members SET isworking="False"')
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
    x = 1
    text = ""
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
            text = f'{text}\n{stat[0].capitalize()}: ⏫ ${newprice-stat[1]}'
        elif newprice < stat[1]:
            text = f'{text}\n{stat[0].capitalize()}: ⏬ ${stat[1]-newprice}'
        if newprice == stat[1]:
            text = f'{text}\n{stat[0].capitalize()}: No change.'


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

                



@tasks.loop(seconds=60)
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
    times = [180,360,540,720,900,1080,1260]
    for x in times:
        if minutes > x and minutes < x+180:
            shoptime = x+180
    if minutes in times:
        minutes = 0
    shoptime -= minutes
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
async def on_raw_reaction_add(payload):
    guild = client.get_guild(692906379203313695)
    taxping = guild.get_role(698321954742075504)
    bankping = guild.get_role(698322063206776972)
    tokendm = guild.get_role(706589874966364191)
    pollchannel = client.get_channel(698009727803719757)
    if payload.message_id == 698774871949181039:
        user = payload.user_id
        user = guild.get_member(user)
        await user.add_roles(taxping)
    if payload.message_id == 698774872628789328:
        user = payload.user_id
        user = guild.get_member(user)
        await user.add_roles(bankping)
    if payload.message_id == 706589449043181730:
        user = payload.user_id
        user = guild.get_member(user)
        await user.add_roles(tokendm)
    if payload.channel_id == 698009727803719757:
        if payload.user_id != 698771271353237575:
            message = await pollchannel.fetch_message(payload.message_id)
            for reaction in message.reactions:
                if str(reaction.emoji) != str(payload.emoji):
                    await client.http.remove_reaction(payload.channel_id, payload.message_id, reaction.emoji, payload.user_id)

@client.event
async def on_raw_reaction_remove(payload):
    guild = client.get_guild(692906379203313695)
    taxping = guild.get_role(698321954742075504)
    bankping = guild.get_role(698322063206776972)
    tokendm = guild.get_role(706589874966364191)
    if payload.message_id == 698774871949181039:
        user = payload.user_id
        user = guild.get_member(user)
        await user.remove_roles(taxping)
    if payload.message_id == 698774872628789328:
        user = payload.user_id
        user = guild.get_member(user)
        await user.remove_roles(bankping)
    if payload.message_id == 706589449043181730:
        user = payload.user_id
        user = guild.get_member(user)
        await user.remove_roles(tokendm)  
        
@client.event
async def on_member_join(member):
    channel = client.get_channel(692956542437425153)
    guild = client.get_guild(692906379203313695)
    poor = guild.get_role(692952611141451787)
    if member.bot == True:
        return
    alreadyin = False
    await channel.send(f"Hey {member.mention}, welcome to **The Hierarchy**! Please check <#692951648410140722> before you do anything else!")
    await member.add_roles(poor)
    conn = sqlite3.connect('hierarchy.db')
    c = conn.cursor()
    c.execute('SELECT id FROM members')
    users = c.fetchall()
    c.execute('SELECT code, uses, expires, maxuses, inviter FROM invites')
    invites = c.fetchall()
    for person in users:
        if member.id == person[0]:
            alreadyin = True
    await asyncio.sleep(1)
    codes = []
    for ginvite in await guild.invites():
        codes.append(ginvite.id)

    if alreadyin == True:
        for hinvite in invites:
            if hinvite[2] < time.time() and hinvite[2] != 0:
                c.execute(f"DELETE FROM invites WHERE code = '{hinvite[0]}'")
                return
            for ginvite in await guild.invites():
                if ginvite.id == hinvite[0]:
                    cuses = ginvite.uses
            if (hinvite[0] not in codes) and hinvite[3] == 1:
                cuses = 1
            if hinvite[1] < cuses:
                c.execute(f"UPDATE invites SET uses = {cuses} WHERE code = '{hinvite[0]}'")
                if cuses == hinvite[3]:
                    c.execute(f"DELETE FROM invites WHERE code = '{hinvite[0]}'")
        conn.commit()
        conn.close()
                    
    if alreadyin == False:
        c.execute(f'INSERT INTO members (id) VALUES ({member.id})')
        for hinvite in invites:
            if hinvite[2] < time.time() and hinvite[2] != 0:
                c.execute(f"DELETE FROM invites WHERE code = '{hinvite[0]}'")
                return
            for ginvite in await guild.invites():
                if ginvite.id == hinvite[0]:
                    cuses = ginvite.uses
            if (hinvite[0] not in codes) and hinvite[3] == 1:
                cuses = 1
            if hinvite[1] < cuses:
                c.execute(f"UPDATE invites SET uses = {cuses} WHERE code = '{hinvite[0]}'")
                inviter = guild.get_member(hinvite[4])
                if cuses == hinvite[3]:
                    c.execute(f"DELETE FROM invites WHERE code = '{hinvite[0]}'")
                conn.commit()
                conn.close()
                tokens = read_value('members', 'id', inviter.id, 'tokens')
                tokens += 1
                write_value('members', 'id', inviter.id, 'tokens', tokens)
                dmrole = guild.get_role(706589874966364191)
                for r in guild.get_member(inviter.id).roles:
                    if r == dmrole:
                        await inviter.send(f"You recieved a token because {member.mention} used your invite.")
                
    await leaderboard(client)
    

@client.event
async def on_member_remove(member):
    channel = client.get_channel(692956542437425153)
    guild = client.get_guild(692906379203313695)
    inaudit = False
    await asyncio.sleep(0.1)
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


@client.event
async def on_invite_create(invite):
    conn = sqlite3.connect('hierarchy.db')
    c = conn.cursor() 
    expires = int(time.time()) + invite.max_age
    c.execute(f"INSERT INTO invites (code, uses, expires, inviter , maxuses) VALUES ('{invite.id}', 0, {expires}, {invite.inviter.id}, {invite.max_uses})")
    conn.commit()
    conn.close()
    
@client.event
async def on_invite_delete(invite):
    conn = sqlite3.connect('hierarchy.db')
    c = conn.cursor()
    try:
        c.execute(f"DELETE FROM invites WHERE code = '{invite.id}'")
    except:
        pass
    conn.commit()
    conn.close()



client.load_extension('debug')        
client.load_extension('info')
client.load_extension('games')
client.load_extension('actions')
client.load_extension('admin')
client.run('Njk4NzcxMjcxMzUzMjM3NTc1.XpKrfw.2bt069XC42fFvaUQQdfprVM7omc')
