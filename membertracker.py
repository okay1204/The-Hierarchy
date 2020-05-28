import discord
from discord.ext import commands, tasks
import asyncio
import sqlite3
from sqlite3 import Error
from utils import read_value, write_value


client = commands.Bot(command_prefix = '.')
client.remove_command('help')


@client.event
async def on_ready():
    print(f"Logged in as {client.user}.\nID: {client.user.id}")

@client.event
async def on_member_join(member):
    channel = client.get_channel(692956542437425153)
    guild = client.get_guild(692906379203313695)
    if member.bot == True:
        botrole = guild.get_role(706026795413143553)
        await member.add_roles(botrole)
        return
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

        
                    
    if alreadyin == False:
        c.execute(f'INSERT INTO members (id) VALUES ({member.id})')
        conn.commit()

    conn.close()


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


client.run("NzE1Mzc2MTUwMDk1OTg2NzE5.Xs8UEQ.eX1Ybm1Sl_rEV08NWT-zwyZbT8A")

