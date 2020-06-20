import discord
from discord.ext import commands, tasks
import asyncio
import sqlite3
from sqlite3 import Error
from utils import *


client = commands.Bot(command_prefix = '.')
client.remove_command('help')


@client.event
async def on_ready():
    print(f"Logged in as {client.user}.\nID: {client.user.id}")
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="for members"))



@client.command()
@commands.check(adminCheck)
async def memberupdate(ctx):
    guild = client.get_guild(692906379203313695)
    membercountchannel = client.get_channel(719716526101364778)
    membercount = len(list(filter(lambda x: not guild.get_member(x.id).bot ,guild.members)))
    await membercountchannel.edit(name=f"Members: {membercount}")
    await ctx.send('Successfully updated member count.')

@client.event
async def on_member_join(member):
    guild = client.get_guild(692906379203313695)
    if member.bot:
        botrole = guild.get_role(706026795413143553)
        await member.add_roles(botrole)
        return
    channel = client.get_channel(692956542437425153)
    poor = guild.get_role(692952611141451787)
    alreadyin = False
    await channel.send(f"Hey {member.mention}, welcome to **The Hierarchy**! Please check <#692951648410140722> before you do anything else!")
    await member.add_roles(poor)
    conn = sqlite3.connect('hierarchy.db')
    c = conn.cursor()
    c.execute('SELECT id FROM members')
    users = c.fetchall()
    for person in users:
        if member.id == person[0]:
            alreadyin = True
    
    membercountchannel = client.get_channel(719716526101364778)
    membercount = int(membercountchannel.name.split()[1])
    membercount += 1
    await membercountchannel.edit(name=f"Members: {membercount}")
        
                    
    if alreadyin == False:
        c.execute(f'INSERT INTO members (id) VALUES ({member.id})')
        conn.commit()

    conn.close()


@client.event
async def on_member_remove(member):
    if member.bot:
        return
    channel = client.get_channel(692956542437425153)

    await channel.send(f"{member.mention} has left **The Hierarchy**. Too bad for him/her.")

    membercountchannel = client.get_channel(719716526101364778)
    membercount = int(membercountchannel.name.split()[1])
    membercount -= 1
    await membercountchannel.edit(name=f"Members: {membercount}")

client.run("NzE1Mzc2MTUwMDk1OTg2NzE5.Xs8UEQ.eX1Ybm1Sl_rEV08NWT-zwyZbT8A")

