import discord
from discord.ext import commands
import sqlite3
import asyncio
from utils import read_value, write_value, update_total
import os
import bottoken

client = commands.Bot(command_prefix = '.')
client.remove_command('help')


@client.event
async def on_command_error(ctx, error):

    error = getattr(error, 'original', error)

    if isinstance(error, commands.CommandNotFound):
        return

    raise error


@client.event
async def on_ready():
    print(f"Logged in as {client.user}.\nID: {client.user.id}")
    await client.change_presence(status=discord.Status.online, activity=discord.Game(name='with money'))

@client.event
async def on_member_join(member):
    
    conn = sqlite3.connect('./storage/databases/featured.db')
    c = conn.cursor()
    c.execute(f'SELECT userid FROM g_{member.guild.id}')
    userids = c.fetchall()
    conn.close()

    userids = list(map(lambda user: user[0], userids))

    if member.id not in userids:
        #await asyncio.sleep(300) # five minutes
        await asyncio.sleep(1)

        
        member = member.guild.get_member(member.id) # check if they are still in server
        if not member:
            return
    

        else:

            money = read_value(member.id, 'money')
            if money == None:
                return
            money += 100
            write_value(member.id, 'money', money)
            update_total(member.id)

            try:
                await member.send(f'You have been in **{member.guild.name}** for five minutes and have recieved your price of $100!')
            except:
                pass
            


            conn = sqlite3.connect('./storage/databases/featured.db')
            c = conn.cursor()
            c.execute(f'INSERT INTO g_{member.guild.id} (userid) VALUES (?)', (member.id,))
            conn.commit()
            conn.close()






@client.event
async def on_guild_join(guild):
    
    conn = sqlite3.connect('./storage/databases/featured.db')
    c = conn.cursor()
    c.execute(f'CREATE TABLE IF NOT EXISTS g_{guild.id} (userid INTEGER PRIMARY KEY)')
    conn.commit()
    conn.close()

client.run(os.environ.get('featured'))