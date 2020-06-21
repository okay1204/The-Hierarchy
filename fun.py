import discord
from discord.ext import commands, tasks
import asyncio
import sqlite3
from sqlite3 import Error

client = commands.Bot(command_prefix = '.')
client.remove_command('help')

#Defining own read and write for different database
def read_value(table, where, what, value):
    conn = sqlite3.connect('fun.db')
    c = conn.cursor()
    c.execute(f'SELECT {value} FROM {table} WHERE {where} = ?', (what,))
    reading = c.fetchone()
    conn.close()
    reading = reading[0]
    return reading

def write_value(table, where, what, value, overwrite):
    conn = sqlite3.connect('fun.db')
    c = conn.cursor()
    c.execute(f"UPDATE {table} SET {value} = {overwrite} WHERE {where} = ?", (what,))
    conn.commit()
    conn.close()

@client.event
async def on_ready():
    print(f"Logged in as {client.user}.\nID: {client.user.id}")
    await client.change_presence(status=discord.Status.online, activity=discord.Game(name=' '))

@client.event
async def on_message(message):
    counting = client.get_channel(721444345353470002)
    sentences = client.get_channel(721475839153143899)
     #Endless counting channel
    if message.author.bot:
        return



    if message.channel == counting:
        content = message.content
        #Grabing last number from here
        conn = sqlite3.connect('fun.db')
        c = conn.cursor()
        c.execute('SELECT number FROM counting')
        currentnumber = c.fetchone()
        conn.close()
        currentnumber = currentnumber[0] 
        #to here
        nextnumber = currentnumber + 1
        if content.lower() == 'next':
            await counting.send(f"**{nextnumber}**")
            return
        elif message.content.startswith('.warn') or message.content.startswith('.kick') or message.content.startswith('.ban') or message.content.startswith('.report'):
            return
        elif str(nextnumber) in content:
            #Writing number from here
            conn = sqlite3.connect('fun.db')
            c = conn.cursor()
            c.execute(f"UPDATE counting SET number = ?", (nextnumber,))
            c.execute(f"UPDATE counting SET lastmsgid = ?", (message.id,))
            conn.commit()
            conn.close()
            #to here
        else:
            await message.delete()
            await counting.send(f"Your message must have the next number in it, {message.author.mention}.", delete_after=3)
    
    
    #For sentences
    elif message.channel == sentences:
        content = message.content
        if message.content.startswith('.warn') or message.content.startswith('.kick') or message.content.startswith('.ban') or message.content.startswith('.report'):
            return
        elif " " in content:
            await message.delete()
            await sentences.send(f"You can't send two words in one message, {message.author.mention}.", delete_after=3)
            return
        #Grabing last author from here
        conn = sqlite3.connect('fun.db')
        c = conn.cursor()
        c.execute('SELECT prevauthor FROM sentences')
        prevauthor = c.fetchone()
        conn.close()
        prevauthor = prevauthor[0] 
        #to here
        authorid = message.author.id
        if authorid == prevauthor:
            await message.delete()
            await sentences.send(f"You can't send two messages in a row, {message.author.mention}.", delete_after=3)
        else:
            #Writing data from here
            conn = sqlite3.connect('fun.db')
            c = conn.cursor()
            c.execute("UPDATE sentences SET prevauthor = ?", (authorid,))
            c.execute("UPDATE sentences SET lastmsgid = ?", (message.id,))
            conn.commit()
            conn.close()
            #to here

@client.event
async def on_raw_message_edit(payload):
    counting = 721444345353470002
    sentences = 721475839153143899
    if payload.channel_id == counting:
        counting = client.get_channel(721444345353470002)
        message = await counting.fetch_message(payload.message_id)
        #Grabing data from here
        conn = sqlite3.connect('fun.db')
        c = conn.cursor()
        c.execute('SELECT number FROM counting')
        currentnumber = c.fetchone()
        c.execute('SELECT lastmsgid FROM counting')
        lastmsgid = c.fetchone()
        conn.close()
        currentnumber = currentnumber[0]
        lastmsgid = lastmsgid[0] 
        #to here
        if str(currentnumber) not in message.content and payload.message_id == lastmsgid:
            await message.delete()


    if payload.channel_id == sentences :
        sentences = client.get_channel(sentences)
        message = await sentences.fetch_message(payload.message_id)
        #Grabing data from here
        conn = sqlite3.connect('fun.db')
        c = conn.cursor()
        c.execute('SELECT lastmsgid FROM sentences')
        lastmsgid = c.fetchone()
        conn.close()
        lastmsgid = lastmsgid[0] 
        #to here
        if " " in message.content and payload.message_id == lastmsgid:
            await message.delete()

@client.event
async def on_raw_message_delete(payload):
    counting = 721444345353470002
    sentences = 721475839153143899
    if payload.channel_id == counting:
        counting = client.get_channel(counting)
        #Grabing last message from here
        conn = sqlite3.connect('fun.db')
        c = conn.cursor()
        c.execute('SELECT lastmsgid FROM counting')
        lastmsgid = c.fetchone()
        conn.close()
        lastmsgid = lastmsgid[0] 
        #to here
        if payload.message_id == lastmsgid:
            async for message in counting.history(limit=100):
                if message.content.lower() == "next" or message.author.bot or message.content.startswith('.warn') or message.content.startswith('.kick') or message.content.startswith('.ban') or message.content.startswith('.report'):
                    continue
                else:
                    newmsg = message
                    break
            #Writing new data from here
            conn = sqlite3.connect('fun.db')
            c = conn.cursor()
            c.execute("UPDATE counting SET lastmsgid = ?", (newmsg.id,))
            #Grabing last number from here
            c.execute('SELECT number FROM counting')
            number = c.fetchone()
            number = number[0]
            number -= 1
            #to here
            c.execute("UPDATE counting SET number = ?", (number,))
            conn.commit()
            conn.close()
            #to here


    elif payload.channel_id == sentences:
        sentences = client.get_channel(sentences)
        #Grabing last message from here
        conn = sqlite3.connect('fun.db')
        c = conn.cursor()
        c.execute('SELECT lastmsgid FROM sentences')
        lastmsgid = c.fetchone()
        conn.close()
        lastmsgid = lastmsgid[0] 
        #to here
        if payload.message_id == lastmsgid:
            async for message in sentences.history(limit=100):
                if message.author.bot or message.content.startswith('.warn') or message.content.startswith('.kick') or message.content.startswith('.ban') or message.content.startswith('.report'):
                    continue
                else:
                    newmsg = message
                    break
            #Writing new data from here
            conn = sqlite3.connect('fun.db')
            c = conn.cursor()
            c.execute("UPDATE sentences SET lastmsgid = ?", (newmsg.id,))
            c.execute("UPDATE sentences SET prevauthor = ?", (newmsg.author.id,))
            conn.commit()
            conn.close()
            #to here



client.run('NzIxNDQxMTM2MzU0Mzk0MTgz.XuUkjw.U1Tv-qr6q0VPzF0uRTYzg2BcV80')