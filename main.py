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
                        heistamount = read_value('members', 'id', userid, 'heistamount')
                        heistamount -= 1
                        total2 += heistamount
                        write_value('members', 'id', userid, 'heistamount', heistamount)
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
    channel = client.get_channel(698322322834063430)
    pollchannel = client.get_channel(698009727803719757)
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
    conn = sqlite3.connect('hierarchy.db')
    c = conn.cursor()
    c.execute('SELECT * FROM polls')
    polls = c.fetchall()
    for poll in polls:
        if poll[1] < time.time():
            c.execute(f"DELETE FROM polls WHERE name = '{poll[0]}'")
            conn.commit()
            message = await pollchannel.fetch_message(poll[2])
            message.delete()
        else:
            message = await pollchannel.fetch_message(poll[2])
            text = message.content
            for char in text:
                if char == '\n':
                    index = text.index(char)
                    break

            text = text[index:]
            text = text[::-1]
            text = f"{text}**Time left:{minisplittime(int(poll[1]-int(time.time()))/60)}**"
            await message.edit(content=text)

    conn.close()
    
@client.event
async def on_raw_reaction_add(payload):
    guild = client.get_guild(692906379203313695)
    taxping = guild.get_role(698321954742075504)
    bankping = guild.get_role(698322063206776972)
    tokendm = guild.get_role(706589874966364191)
    channel = client.get_channel(698318226613993553)
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

@client.event
async def on_raw_reaction_remove(payload):
    guild = client.get_guild(692906379203313695)
    taxping = guild.get_role(698321954742075504)
    bankping = guild.get_role(698322063206776972)
    tokendm = guild.get_role(706589874966364191)
    channel = client.get_channel(698318226613993553)
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
    heist = open_json()
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
                updated = hinvite[1] + 1
                c.execute(f"UPDATE invites SET uses = {updated} WHERE code = '{hinvite[0]}'")
                if updated == hinvite[3]:
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
                updated = hinvite[1] + 1
                c.execute(f"UPDATE invites SET uses = {updated} WHERE code = '{hinvite[0]}'")
                inviter = guild.get_member(hinvite[4])
                if updated == hinvite[3]:
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
    heist["invites"].append({"code":invite.id,"uses":0,"expires":invite.max_age, "inviter":invite.inviter.id, "max uses":invite.max_uses})
    expires = int(time.time()) + invite.max_age
    c.execute(f'INSERT INTO invites (code, uses, expires, inviter , maxuses) VALUES ({invite.id}, 0, {expires}, {invite.inviter.id}, {invite.max_uses})')
    conn.commit()
    conn.close()
    
@client.event
async def on_invite_delete(invite):
    conn = sqlite3.connect('hierarchy.db')
    c = conn.cursor()
    try:
        c.execute(f'DELETE FROM invites WHERE code = {invite.id}')
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
