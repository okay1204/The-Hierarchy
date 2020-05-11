import discord
import json
import time
import sqlite3
from sqlite3 import Error

def read_value(table, where, what, value):
    conn = sqlite3.connect('hierarchy.db')
    c = conn.cursor()
    c.execute(f'SELECT {value} FROM {table} WHERE {where} = {what}')
    reading = c.fetchone()
    conn.close()
    reading = reading[0]
    return reading

def write_value(table, where, what, value, overwrite):
    conn = sqlite3.connect('hierarchy.db')
    c = conn.cursor()
    c.execute(f"UPDATE {table} SET {value} = {overwrite} WHERE {where} = {what}")
    conn.commit()
    conn.close()


def update_total(userid):
    money = read_value('members', 'id', userid, 'money')
    bank = read_value('members', 'id', userid, 'bank')
    total = money + bank
    conn = sqlite3.connect('hierarchy.db')
    c = conn.cursor()
    c.execute(f'UPDATE members SET total = {total} WHERE id = {userid}')
    conn.commit()
    conn.close()


def in_use(userid):
    inuse = read_value('members', 'id', userid, 'inuse').split()
    items = []
    for x in inuse:
        try:
            x = int(x)
            citem["timer"] = x
            if citem["timer"] < time.time():
                continue
            items.append(citem)
        except:
            citem = {'name':x}
    inusetext = ""
    for item in items:
        inusetext = f"{inusetext} {item['name']} {item['timer']}"
    inusetext = f"'{inusetext}'"
    write_value('members', 'id', userid, 'inuse', inusetext)
    return items

def add_item(name, userid):
    items = read_value('members', 'id', userid, 'items').split()
    itemtext = name
    for item in items:
        itemtext = f"{itemtext} {item}"
    itemtext = f"'{itemtext}'"
    write_value('members', 'id', userid, 'items', itemtext)

def remove_item(name, userid):
    items = read_value('members', 'id', userid, 'items').split()
    itemtext = ""
    done = False
    for item in items:
        if item == name and done == False:
            done = True
            continue
        itemtext = f"{itemtext} {item}"
    itemtext = f"'{itemtext}'"
    write_value('members', 'id', userid, 'items', itemtext)


def add_use(name, timer, userid):
    inuse = in_use(userid)
    inuse.append({'name':name, 'timer':timer})
    inusetext = ""
    for item in inuse:
        inusetext = f"{inusetext} {item['name']} {item['timer']}"
    inusetext = f"'{inusetext}'"
    write_value('members', 'id', userid, 'inuse', inusetext)



def remove_use(name, userid):
    inuse = in_use(userid)
    for item in inuse:
        if item["name"] == name:
            inuse.remove(item)
    inusetext = ""
    for item in inuse:
        inusetext = f"{inusetext} {item['name']} {item['timer']}"
    inusetext = f"'{inusetext}'"
    write_value('members', 'id', userid, 'inuse', inusetext)

    
def write_json(data): 
    with open('heist.json','w') as f: 
        json.dump(data, f, indent=2)

def open_json():
    with open('heist.json') as json_file:
        heist = json.load(json_file)
    return heist

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

    

async def rightCategory(ctx):
    return ctx.channel.category.id == 692949972764590160

async def debugCheck(ctx):
    return ctx.channel.id == 704109366529491005

async def adminCheck(ctx):
    return ctx.channel.id == 706953015415930941


async def leaderboard(client):
    hierarchy = open_json()
    guild = client.get_guild(692906379203313695)
    channel = client.get_channel(692955859109806180)
    message = await channel.fetch_message(698775209024552975)
    embed = discord.Embed(color = 0xffd24a)
    embed.set_author(name='\U0001f3c6 Leaderboard \U0001f3c6')
    conn = sqlite3.connect('hierarchy.db')
    c = conn.cursor()
    c.execute('SELECT id, total FROM members')
    hierarchy = c.fetchall()
    conn.close()
    sorted_list = sorted(hierarchy, key=lambda k: k[1], reverse=True)
    sorted_list = tuple(filter(lambda x: guild.get_member(x[0]) is not None, sorted_list))
    for x in range(5):
        member = guild.get_member(sorted_list[x][0])
        if x == 0:
            embed.add_field(name='__________',value=f'1. {member.mention} \U0001f947 - ${sorted_list[x][1]}',inline=False)
            continue
        if x == 1:
            embed.add_field(name='__________',value=f'2. {member.mention} \U0001f948 - ${sorted_list[x][1]}',inline=False)
            continue
        if x == 2:
            embed.add_field(name='__________',value=f'3. {member.mention} \U0001f949 - ${sorted_list[x][1]}',inline=False)
            continue
        embed.add_field(name='__________',value=f'{x+1}. {member.mention} - ${sorted_list[x][1]}',inline=False)


    await message.edit(embed=embed)

async def rolecheck(client, user):
    hierarchy = open_json()
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
    conn = sqlite3.connect('hierarchy.db')
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
        totalmoney += read_value('members', 'id', person[0], 'total')
    average = int(totalmoney/active)
    haverage = average + average/2
    laverage = average - average/2
    total = read_value('members', 'id', user, 'total')
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
