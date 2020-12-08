# pylint: disable=anomalous-backslash-in-string

import discord
import json
import time
import sqlite3
from collections import Counter
from datetime import datetime

# DATABASE FUNCTIONS

def read_value(userid, value):
    conn = sqlite3.connect('./storage/databases/hierarchy.db')
    c = conn.cursor()
    try:
        c.execute(f'SELECT {value} FROM members WHERE id = ?', (userid,))
        reading = c.fetchone()[0]
    except:
        c.execute(f"INSERT INTO members (id) VALUES (?)", (userid,))
        c.execute(f'SELECT {value} FROM members WHERE id = ?', (userid,))
        reading = c.fetchone()[0]
        conn.commit()
    conn.close()
    return reading

def write_value(userid, value, overwrite):
    conn = sqlite3.connect('./storage/databases/hierarchy.db')
    c = conn.cursor()
    c.execute(f"UPDATE members SET {value} = ? WHERE id = ?", (overwrite, userid))
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

async def jail_heist_check(client, ctx, member):

    jailtime = read_value(member.id, 'jailtime')
    if jailtime > time.time():
        await ctx.send(f'You are still in jail for {splittime(jailtime)}.')
        return False

    if client.heist:
        if client.heist["victim"] == member.id:
            await ctx.send(f"You are being targeted by heist.")
            return False
        
        elif member.id in client.heist["participants"]:
            await ctx.send(f"You are participating in a heist.")
            return False
    
    return True

async def event_disabled(ctx):

    if ctx.bot.get_cog('Christmas'):
        await ctx.send("This command is disabled during the Christmas event.")
        return False

    with open('./storage/jsons/mode.json') as f:
        mode = json.load(f)

    if mode == "event":
        if read_value(ctx.author.id, 'in_event') == "True":
            await ctx.send("This command is disabled during events.\nUse `.eventleave` to leave the event, **however you may not join back once you leave**.")
            return False

        return True

    else:
        return True

async def member_event_check(ctx, userid):

    with open('./storage/jsons/mode.json') as f:
        mode = json.load(f)

    if mode == "event":

        if read_value(userid, 'in_event') == "True":
            await ctx.send("This user is participating in the event.")
            return False

        return True

    else:
        return True


# CHECK FUNCTIONS

# ITEM FUNCTIONS

def in_use(userid):
    inuse = read_value(userid, 'inuse').split()
    items = {}
    inusetext = ""
    
    if len(inuse) != 0:
        for x in range(0, len(inuse), 2):
            if int(inuse[x+1]) <= time.time():
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

    itemtext = " ".join(items)

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

# TIME FUNCTIONS

def splittime(seconds):
    seconds -= int(time.time())

    minutes = seconds // 60
    rseconds = seconds % 60

    hours = minutes // 60
    rminutes = minutes % 60

    return f"{hours}h {rminutes}m {rseconds}s"

def minisplittime(minutes):

    hours = minutes // 60
    rminutes = minutes % 60
    
    return f"{hours}h {rminutes}m"

def timestring(string):
    string = string.lower().split()
    total = 0
    keys = {'d': 86400, 'h': 3600, 'm': 60, 's': 1}

    try:
        for combo in string:

            if not combo.endswith(tuple(keys)):
                raise ValueError()
            
            for key in keys:
                if combo.endswith(key):
                    total += int(combo[:-1]) * keys[key]
                    break

    except:
        total = None
    
    return total

# TIME FUNCTIONS


# MISC

async def level_check(ctx, userid, required_level, use_what):

    level = read_value(userid, 'level')
    
    if level < required_level:
        await ctx.send(f"You must be at least level {required_level} in order to {use_what}.")
        return False
    else:
        return True

def around(guild, userid, find):
    conn = sqlite3.connect('./storage/databases/hierarchy.db')
    c = conn.cursor()
    c.execute('SELECT id, money + bank AS total FROM members WHERE total > 0 ORDER BY total DESC')
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

    embed = discord.Embed(color = 0xffd24a, title='\U0001f3c6 Leaderboard \U0001f3c6')
    conn = sqlite3.connect('./storage/databases/hierarchy.db')
    c = conn.cursor()
    c.execute('SELECT id, money + bank AS total FROM members ORDER BY total DESC')
    hierarchy = c.fetchall()
    conn.close()

    hierarchy = list(filter(lambda x: guild.get_member(x[0]), hierarchy))
    for x in range(10):

        medal = ''
        if x == 0:
            medal = ' 🥇'
        elif x == 1:
            medal = ' 🥈'
        elif x == 2:
            medal = ' 🥉'

        embed.add_field(name='\_\_\_\_\_\_\_',value=f'{x+1}. <@{hierarchy[x][0]}>{medal} - ${hierarchy[x][1]}',inline=False)


    await client.leaderboardMessage.edit(embed=embed)

async def rolecheck(client, user):

    guild = client.mainGuild

    poor = guild.get_role(692952611141451787)
    middle = guild.get_role(692952792016355369)
    rich = guild.get_role(692952919947083788)

    conn = sqlite3.connect('./storage/databases/hierarchy.db')
    c = conn.cursor()
    c.execute('SELECT id, money + bank AS total FROM members WHERE total != 0')
    hierarchy = c.fetchall()
    conn.close()

    hierarchy = list(filter(lambda member: guild.get_member(member[0]), hierarchy))

    members = len(list(filter(lambda member: member.id in map(lambda user: user[0], hierarchy) and not member.bot, guild.members)))

    totalmoney = sum(map(lambda member: member[1], hierarchy))

    average = int(totalmoney/members)

    haverage = average + average/2
    laverage = average - average/2

    total = read_value(user, 'money + bank')
    member = guild.get_member(user)

    for role in member.roles:
        
        if role.id == poor.id:
            pass

    if total < laverage:
        if poor.id not in map(lambda role: role.id, member.roles):
            await member.add_roles(poor)
            await member.remove_roles(middle, rich)

    elif total < haverage:
        if middle.id not in map(lambda role: role.id, member.roles):
            await member.add_roles(middle)
            await member.remove_roles(poor, rich)

    elif total >= haverage: 
        if rich.id not in map(lambda role: role.id, member.roles):
            await member.add_roles(rich)
            await member.remove_roles(poor, middle)


async def log_command(client, ctx):

    command_logs = client.get_channel(755851445303115856)

    embed = discord.Embed(color=0xf56451, title="Command Used", timestamp=datetime.now())
    embed.set_author(name=f"{ctx.author.name}#{ctx.author.discriminator}", icon_url=ctx.author.avatar_url_as(static_format='jpg'))

    embed.add_field(name="Command", value=f"`{ctx.message.content}`")

    embed.add_field(name="Channel", value=ctx.channel.mention)

    embed.add_field(name="Jump", value=f"[Click Here]({ctx.message.jump_url})")

    await command_logs.send(embed=embed)