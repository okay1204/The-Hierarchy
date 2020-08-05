# pylint: disable=import-error

import asyncio
import json
import random
import sqlite3
import time
import os
import datetime
from sqlite3 import Error

import discord
from discord.ext import commands, tasks
from discord.ext.commands import BadArgument, CommandNotFound, MaxConcurrencyReached


#Defining own read and write for different database
def read_gang(userid, value):
    conn = sqlite3.connect('./storage/databases/gangs.db')
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

def write_gang(userid, value, overwrite):
    conn = sqlite3.connect('./storage/databases/gangs.db')
    c = conn.cursor()
    c.execute(f"UPDATE members SET {value} = ? WHERE id = ?", (overwrite, userid))
    conn.commit()
    conn.close()

class fun(commands.Cog):

    def __init__(self, client):
        self.client = client


    async def cog_check(self, ctx):
        if ctx.channel.category.id != self.client.rightCategory:
            return False
        else:
            return True

    @commands.Cog.listener()
    async def on_message(self, message):
        counting = self.client.get_channel(721444345353470002)
        sentences = self.client.get_channel(721475839153143899)
        #Endless counting channel
        if message.author.bot:
            return



        if message.channel == counting:
            content = message.content
            #Grabing last number from here
            conn = sqlite3.connect('./storage/databases/fun.db')
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
                conn = sqlite3.connect('./storage/databases/fun.db')
                c = conn.cursor()
                c.execute(f"UPDATE counting SET number = ?", (nextnumber,))
                c.execute(f"UPDATE counting SET lastmsgid = ?", (message.id,))
                conn.commit()
                conn.close()
                #to here
            else:
                await message.delete()
                await counting.send(f"Your message must have the next number in it, {message.author.mention}.", delete_after=3)
            return
        
        
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
            conn = sqlite3.connect('./storage/databases/fun.db')
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
                conn = sqlite3.connect('./storage/databases/fun.db')
                c = conn.cursor()
                c.execute("UPDATE sentences SET prevauthor = ?", (authorid,))
                c.execute("UPDATE sentences SET lastmsgid = ?", (message.id,))
                conn.commit()
                conn.close()
                #to here
            return


    @commands.Cog.listener()
    async def on_raw_message_edit(self, payload):
        counting = 721444345353470002
        sentences = 721475839153143899
        if payload.channel_id == counting:
            counting = self.client.get_channel(721444345353470002)
            message = await counting.fetch_message(self, payload.message_id)
            #Grabing data from here
            conn = sqlite3.connect('./storage/databases/fun.db')
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
            sentences = self.client.get_channel(sentences)
            message = await sentences.fetch_message(payload.message_id)
            #Grabing data from here
            conn = sqlite3.connect('./storage/databases/fun.db')
            c = conn.cursor()
            c.execute('SELECT lastmsgid FROM sentences')
            lastmsgid = c.fetchone()
            conn.close()
            lastmsgid = lastmsgid[0] 
            #to here
            if " " in message.content and payload.message_id == lastmsgid:
                await message.delete()

    @commands.Cog.listener()
    async def on_raw_message_delete(self, payload):
        counting = 721444345353470002
        sentences = 721475839153143899
        if payload.channel_id == counting:
            counting = self.client.get_channel(counting)
            #Grabing last message from here
            conn = sqlite3.connect('./storage/databases/fun.db')
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
                conn = sqlite3.connect('./storage/databases/fun.db')
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
            sentences = self.client.get_channel(self, sentences)
            #Grabing last message from here
            conn = sqlite3.connect('./storage/databases/fun.db')
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
                conn = sqlite3.connect('./storage/databases/fun.db')
                c = conn.cursor()
                c.execute("UPDATE sentences SET lastmsgid = ?", (newmsg.id,))
                c.execute("UPDATE sentences SET prevauthor = ?", (newmsg.author.id,))
                conn.commit()
                conn.close()
                #to here

    
    @commands.group(invoke_without_command=True)
    async def gang(self, ctx):
        await ctx.send("Incorrect command usage:\n`.gang create/settings/join/leave/disband`")

    @gang.command()
    async def create(self, ctx, name=None):
        
        if not name:
            await ctx.send("Incorrect command usage:\n`.gang create gangname`")
            return
        
        conn = sqlite3.connect('./storage/databases/gangs.db')
        c = conn.cursor()
        try:
            c.execute('INSERT INTO gangs (name, owner, created_at) VALUES (?, ?, ?)', (name, ctx.author.id, datetime.datetime.utcnow()))
            conn.commit()
        except Exception as e:

            if str(e).endswith('name'):
                await ctx.send("A gang with that name already exists.")

            else:
                await ctx.send("You already own another gang.")
        else:
            await ctx.send(f"Successfully created gang: {name}")
        finally:
            conn.close()

    @gang.group(invoke_without_command=True)
    async def settings(self, ctx):
        pass
    
        


def setup(client):
    client.add_cog(fun(client))