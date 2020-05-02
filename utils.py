import discord
import json

def write_json(data): 
    with open('hierarchy.json','w') as f: 
        json.dump(data, f, indent=2)

def write_json2(data): 
    with open('hierarchystats.json','w') as f: 
        json.dump(data, f, indent=2)

def open_json():
    with open('hierarchy.json') as json_file:
        hierarchy = json.load(json_file)
    return hierarchy

def open_json2():
    with open('hierarchystats.json') as json_file:
        hierarchystats = json.load(json_file)
    return hierarchystats


def splittime(seconds):
    minutes = seconds/60
    rseconds = seconds%60
    minutes = int(minutes)
    hours = minutes/60
    rminutes = minutes%60
    hours = int(hours)
    time = f"{hours}h {rminutes}m {rseconds}s"
    return time

def minisplittime(minutes):
    hours = minutes/60
    rminutes = minutes%60
    hours = int(hours)
    time = f"{hours}h {rminutes}m"
    return time

    

async def rightCategory(ctx):
    return ctx.channel.category.id == 692949972764590160

async def debugCheck(ctx):
    return ctx.channel.id == 704109366529491005



async def leaderboard(client):
    hierarchy = open_json()
    guild = client.get_guild(692906379203313695)
    channel = client.get_channel(692955859109806180)
    message = await channel.fetch_message(698775209024552975)
    embed = discord.Embed(color = 0xffd24a)
    embed.set_author(name='\U0001f3c6 Leaderboard \U0001f3c6')
    first = {"total":0}
    second = {"total":0}
    third = {"total":0}
    fourth = {"total":0}
    fifth = {"total":0}
    for person in hierarchy:
        member = guild.get_member(int(person["user"]))
        if not member:
            continue
        if person["total"] >= first["total"]:
            first = person
    for person in hierarchy:
        member = guild.get_member(int(person["user"]))
        if not member:
            continue
        if person["total"] >= second["total"] and person["user"] != first["user"]:
            second = person
    for person in hierarchy:
        member = guild.get_member(int(person["user"]))
        if not member:
            continue
        if person["total"] >= third["total"] and person["user"] != second["user"] and person["user"] != first["user"]:
            third = person
    for person in hierarchy:
        member = guild.get_member(int(person["user"]))
        if not member:
            continue
        if person["total"] >= fourth["total"] and person["user"] != third["user"]and person["user"] != second["user"] and person["user"] != first["user"]:
            fourth = person
    for person in hierarchy:
        member = guild.get_member(int(person["user"]))
        if not member:
            continue
        if person["total"] >= fifth["total"] and person["user"] != fourth["user"] and person["user"] != third["user"]and person["user"] != second["user"] and person["user"] != first["user"]:
            fifth = person
    embed.add_field(name='__________',value=f'1. <@{first["user"]}> \U0001f947 - ${first["total"]}',inline=False)
    embed.add_field(name='__________',value=f'2. <@{second["user"]}> \U0001f948 - ${second["total"]}',inline=False)
    embed.add_field(name='__________',value=f'3. <@{third["user"]}> \U0001f949 - ${third["total"]}',inline=False)
    embed.add_field(name='__________',value=f'4. <@{fourth["user"]}> - ${fourth["total"]}',inline=False)
    embed.add_field(name='__________',value=f'5. <@{fifth["user"]}> - ${fifth["total"]}',inline=False)
    await message.edit(embed=embed)

async def rolecheck(client, user):
    hierarchy = open_json()
    guild = client.get_guild(692906379203313695)
    poor = guild.get_role(692952611141451787)
    middle = guild.get_role(692952792016355369)
    rich = guild.get_role(692952919947083788)
    totalmoney = 0
    active = len(guild.members)-1
    for person in hierarchy:
        member = guild.get_member(int(person["user"]))
        if not member:
            continue
        if person["total"] == 0:
            active-=1
            continue
        totalmoney += person["total"]
    average = int(totalmoney/active)
    haverage = average + average/2
    laverage = average - average/2
    for person in hierarchy:
        if person["user"] == str(user):
            member = guild.get_member(int(user))
            if person["total"] < laverage:
                await member.add_roles(poor)
                await member.remove_roles(middle, rich)
            elif person["total"] < haverage:
                await member.add_roles(middle)
                await member.remove_roles(poor, rich)
            elif person["total"] >= haverage:
                await member.add_roles(rich)
                await member.remove_roles(poor, middle)
