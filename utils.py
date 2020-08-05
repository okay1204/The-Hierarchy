import discord
import json
import time
import sqlite3
from collections import Counter
from sqlite3 import Error


# DATABASE FUNCTIONS

def read_value(userid, value):
    conn = sqlite3.connect('./storage/databases/hierarchy.db')
    c = conn.cursor()
    try:
        c.execute(f'SELECT {value} FROM members WHERE id = ?', (userid,))
        reading = c.fetchone()[0]
    except:
        c.execute(f"INSERT INTO members (id) VALUE (?)", (userid,))
        c.execute(f'SELECT {value} FROM members WHERE id = ?', (userid,))
        reading = c.fetchone()[0]
    conn.close()
    return reading

def write_value(userid, value, overwrite):
    conn = sqlite3.connect('./storage/databases/hierarchy.db')
    c = conn.cursor()
    c.execute(f"UPDATE members SET {value} = ? WHERE id = ?", (overwrite, userid))
    conn.commit()
    conn.close()


def update_total(userid):
    money = read_value(userid, 'money')
    bank = read_value(userid, 'bank')
    total = money + bank
    conn = sqlite3.connect('./storage/databases/hierarchy.db')
    c = conn.cursor()
    c.execute(f'UPDATE members SET total = {total} WHERE id = {userid}')
    conn.commit()
    conn.close()

# DATABASE FUNCTIONS


# CHECK FUNCTIONS

async def bot_check(client, ctx, member):

    if member.id == client.user.id:
        await ctx.send("Why me?")
        return False

    elif member.bot:
        await ctx.send("Bots don't play!")
        return False
    
    else:
        return True

async def jail_heist_check(ctx, member):

    jailtime = read_value(member.id, 'jailtime')
    if jailtime > time.time():
        await ctx.send(f'You are still in jail for {splittime(jailtime)}.')
        return False
    
    heist = open_heist()
    if heist["heistv"] == member.id:
        await ctx.send(f"You are currently being targeted for a heist.")
        return False

    if member.id in heist["heistp"]:
        await ctx.send(f"You are participating in a heist right now.")
        return False
    
    return True



# CHECK FUNCTIONS

# ITEM FUNCTIONS

def in_use(userid):
    inuse = read_value(userid, 'inuse').split()
    items = {}
    inusetext = ""
    
    if len(inuse) != 0:
        for x in range(0, len(inuse), 2):
            if int(inuse[x+1]) > time.time():
                continue
            items[inuse[x]] = int(inuse[x+1])

        for item in items:
            inusetext += f"{item} {items[item]} "

        inusetext = f"{inusetext[:len(inusetext)-1]}"

    write_value(userid, 'inuse', inusetext)
    return items

def add_item(name, userid):
    items = read_value(userid, 'items').split()
    itemtext = f"{name} " 
    for item in items:
        itemtext += f"{item} "
    itemtext = f"{itemtext[:len(itemtext)-1]}"
    write_value(userid, 'items', itemtext)

def remove_item(name, userid):
    items = read_value(userid, 'items').split()

    items.remove(name)

    itemtext = ""
    for item in items:
        itemtext += f"{item} "
    itemtext = f"{itemtext[:len(itemtext)-1]}"
    write_value(userid, 'items', itemtext)


def add_use(name, timer, userid):
    inuse = in_use(userid)
    inuse[name] = timer
    inusetext = ""
    for item in inuse:
        inusetext += f"{item} {inuse[item]} "
    inusetext = f"{inusetext[:len(inusetext)-1]}"
    write_value(userid, 'inuse', inusetext)


def remove_use(name, userid):
    inuse = in_use(userid)
    del inuse[name]
    inusetext = ""
    for item in inuse:
        inusetext += f"{item} {inuse[item]} "
    inusetext = f"{inusetext[:len(inusetext)-1]}"
    write_value(userid, 'inuse', inusetext)

# ITEM FUNCTIONS

# HEIST FUNCTIONS
    
def write_heist(data): 
    with open('./storage/jsons/heist.json','w') as f: 
        json.dump(data, f, indent=2)

def open_heist():
    with open('./storage/jsons/heist.json') as json_file:
        heist = json.load(json_file)
    return heist

# HEIST FUNCTIONS

# TIME FUNCTIONS

def splittime(seconds):
    seconds -= time.time()
    seconds = int(seconds)
    minutes = seconds/60
    rseconds = seconds%60
    minutes = int(minutes)
    hours = minutes/60
    rminutes = minutes%60
    hours = int(hours)
    timestring = f"{hours}h {rminutes}m {rseconds}s"
    return timestring

def minisplittime(minutes):
    minutes = int(minutes)
    hours = minutes/60
    rminutes = minutes%60
    hours = int(hours)
    time = f"{hours}h {rminutes}m"
    return time

# TIME FUNCTIONS


# MISC

def around(guild, userid, find):
    conn = sqlite3.connect('./storage/databases/hierarchy.db')
    c = conn.cursor()
    c.execute('SELECT id, total FROM members WHERE total > 0 ORDER BY total DESC')
    hierarchy = c.fetchall()
    conn.close()
    hierarchy = list(filter(lambda x: guild.get_member(x[0]), hierarchy))
    ids=[]
    for x in hierarchy:
        ids.append(x[0])
    try:
        index = ids.index(userid)
    except ValueError:
        hierarchy.append((userid, 0))
        ids.append(userid)
        index = ids.index(userid)
    lower_index = index-find

    if lower_index < 0:
        lower_index = 0

    higher_index = index+find+1
    length = len(hierarchy)

    if higher_index > length:
        higher_index = length

    result = ids[lower_index:higher_index]
    return result

async def leaderboard(client):
    guild = client.get_guild(692906379203313695)

    embed = discord.Embed(color = 0xffd24a)
    embed.set_author(name='\U0001f3c6 Leaderboard \U0001f3c6')
    conn = sqlite3.connect('./storage/databases/hierarchy.db')
    c = conn.cursor()
    c.execute('SELECT id, total FROM members')
    hierarchy = c.fetchall()
    conn.close()
    sorted_list = sorted(hierarchy, key=lambda k: k[1], reverse=True)
    sorted_list = tuple(filter(lambda x: guild.get_member(x[0]), sorted_list))
    for x in range(10):
        member = guild.get_member(sorted_list[x][0])
        if x == 0:
            embed.add_field(name='__________',value=f'1. {member.mention} 🥇 - ${sorted_list[x][1]}',inline=False)
        elif x == 1:
            embed.add_field(name='__________',value=f'2. {member.mention} 🥈 - ${sorted_list[x][1]}',inline=False)
        elif x == 2:
            embed.add_field(name='__________',value=f'3. {member.mention} \U0001f949 - ${sorted_list[x][1]}',inline=False)
        else:
            embed.add_field(name='__________',value=f'{x+1}. {member.mention} - ${sorted_list[x][1]}',inline=False)


    await client.leaderboardMessage.edit(embed=embed)

async def rolecheck(client, user):

    guild = client.get_guild(692906379203313695)
    poor = guild.get_role(692952611141451787)
    middle = guild.get_role(692952792016355369)
    rich = guild.get_role(692952919947083788)
    totalmoney = 0
    bots = 0
    for member in guild.members:
        if member.bot:
            bots += 1
    active = len(guild.members)-bots
    conn = sqlite3.connect('./storage/databases/hierarchy.db')
    c = conn.cursor()
    c.execute('SELECT id, total FROM members')
    hierarchy = c.fetchall()
    conn.close()
    for person in hierarchy:
        member = guild.get_member(person[0])
        if not member:
            continue
        if person[1] == 0:
            active-=1
            continue
        totalmoney += read_value(person[0], 'total')
    average = int(totalmoney/active)
    haverage = average + average/2
    laverage = average - average/2
    total = read_value(user, 'total')
    member = guild.get_member(user)
    if total < laverage:
        await member.add_roles(poor)
        await member.remove_roles(middle, rich)
    elif total < haverage:
        await member.add_roles(middle)
        await member.remove_roles(poor, rich)
    elif total >= haverage:
        await member.add_roles(rich)
        await member.remove_roles(poor, middle)
