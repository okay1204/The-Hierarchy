# pylint: disable=import-error, anomalous-backslash-in-string


import asyncio
import random
import json
import sqlite3
import time
import os
import datetime
import aiohttp
import difflib
import re
from sqlite3 import Error

import discord
from discord.ext import commands, tasks
from discord.ext.commands import BadArgument, CommandNotFound, MaxConcurrencyReached

# To import from different path
import sys
sys.path.insert(1 , os.getcwd())

from utils import level_check, read_value


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
            message = await counting.fetch_message(payload.message_id)
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
            sentences = self.client.get_channel(sentences)
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
        await ctx.send("Incorrect command usage:\n`.gang list/which/about/members/membersm/create/invite/uninvite/settings/leave/promote/kick/disband`")


    @gang.command(name="list")
    @commands.max_concurrency(1, per=commands.BucketType.member)
    async def gang_list(self, ctx, page=1):

        try:
            page = int(page)
            if page < 1:
                await ctx.send("Page not found.")
                return
        except:
            await ctx.send("Incorrect command usage:\n`.gang list pagenumber`")
            return
        

        conn = sqlite3.connect('./storage/databases/gangs.db')
        c = conn.cursor()
        c.execute('SELECT name, created_at FROM gangs')
        gangs = c.fetchall()
        conn.close()

        if len(gangs) == 0:
            await ctx.send("There are no existing gangs.")
            return

        regex = re.compile("\..*")

        gangs = sorted(gangs, key=lambda gang: int(datetime.datetime.strptime(regex.sub('', gang[1][2:]), '%y-%m-%d %H:%M:%S').timestamp()))
        
        gangs = list(map(lambda gang: gang[0], gangs))
        
        gangs = [gangs[x:x+6] for x in range(0, len(gangs), 6)]
        
        if page > len(gangs):
            await ctx.send("Page not found.")
            return
        
        embed = discord.Embed(color=0xffe6a1, title="Gangs")

        for gang in gangs[page-1]:
            embed.add_field(name="_\_\_\_\_\_\_\_", value=gang, inline=True)
        
        embed.set_footer(text=f"Page {page}/{len(gangs)}")

        await ctx.send(embed=embed)

    @gang.command()
    @commands.max_concurrency(1, per=commands.BucketType.member)
    async def which(self, ctx, member:discord.Member=None):

        if not member:
            member = ctx.author

        conn = sqlite3.connect('./storage/databases/gangs.db')
        c = conn.cursor()
        c.execute('SELECT name, owner, members FROM gangs')
        gangs = c.fetchall()
        conn.close()

        for gang in gangs:
            
            if member.id == gang[1]:
                await ctx.send(f"**{member.name}** owns the gang **{gang[0]}**.")
                return

            elif str(member.id) in gang[2].split():
                await ctx.send(f"**{member.name}** is in the gang **{gang[0]}**.")
                return

        await ctx.send(f"**{member.name}** is not in a gang.")

        

        

    @gang.command()
    @commands.max_concurrency(1, per=commands.BucketType.member)
    async def about(self, ctx, *, name=None):
        
        if not name:
            conn = sqlite3.connect('./storage/databases/gangs.db')
            c = conn.cursor()
            c.execute('SELECT name, owner, members FROM gangs')
            gangs = c.fetchall()
            conn.close()

            for gang in gangs:
                if ctx.author.id == gang[1] or str(ctx.author.id) in gang[2].split():
                    name = gang[0]
                    break
            
            if not name:
                await ctx.send("You are not in a gang.")
                return



        conn = sqlite3.connect('./storage/databases/gangs.db')
        c = conn.cursor()
        try:
            c.execute('SELECT owner, description, created_at, role_id, color, img_location FROM gangs WHERE name = ?', (name,))
            owner, description, created_at, role_id, color, img_location = c.fetchone()
            conn.close()
        except:
            c.execute('SELECT name FROM gangs')
            gangs = c.fetchall()
            conn.close()
            gangs = list(map(lambda gang: gang[0], gangs))
            close = difflib.get_close_matches(name, gangs, n=3, cutoff=0.5)
            

            if len(close) > 0:
                
                close = list(map(lambda word: f"`{word}`", close))

                text = "\n".join(close)

                text = f"There is no gang called **{name}**. Did you mean:\n{text}"

            else:
                
                text = f"There is no gang called **{name}**."
            
            await ctx.send(text) 


            return
        
        # Converts into hexadecimal
        color = int(color, 16)
        if not description:
            description = "No description set."

        guild = self.client.mainGuild
        
        if role_id:
            role = guild.get_role(role_id)
            description = f"Role: {role.mention}\n{description}"

        # Convert string to datetime
        created_at = datetime.datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S.%f')

        embed = discord.Embed(color=color, title=name, description=description, timestamp=created_at)

        owner = guild.get_member(owner)
        embed.set_author(name=f"Owner: {owner.name}", icon_url=owner.avatar_url_as(static_format='jpg'))

        embed.set_footer(text="Created at")

        if img_location:
            filename = img_location.split('/')[-1]
            f = discord.File(img_location, filename=filename)
            embed.set_image(url=f'attachment://{filename}')
            await ctx.send(embed=embed, file=f)
        else:
            await ctx.send(embed=embed)

    @gang.command()
    async def members(self, ctx, *, name=None):
        
        if not name:
            conn = sqlite3.connect('./storage/databases/gangs.db')
            c = conn.cursor()
            c.execute('SELECT name, owner, members FROM gangs')
            gangs = c.fetchall()
            conn.close()

            for gang in gangs:
                if ctx.author.id == gang[1] or str(ctx.author.id) in gang[2].split():
                    name = gang[0]
                    break
            
            if not name:
                await ctx.send("You are not in a gang.")
                return



        conn = sqlite3.connect('./storage/databases/gangs.db')
        c = conn.cursor()
        try:
            c.execute('SELECT owner, members, color, img_location FROM gangs WHERE name = ?', (name,))
            owner, members, color, img_location = c.fetchone()
            conn.close()
        except:
            c.execute('SELECT name FROM gangs')
            gangs = c.fetchall()
            conn.close()
            gangs = list(map(lambda gang: gang[0], gangs))
            close = difflib.get_close_matches(name, gangs, n=3, cutoff=0.5)
            

            if len(close) > 0:
                
                close = list(map(lambda word: f"`{word}`", close))

                text = "\n".join(close)

                text = f"There is no gang called **{name}**. Did you mean:\n{text}"

            else:
                
                text = f"There is no gang called **{name}**."
            
            await ctx.send(text) 

            return
        
        # Converts into hexadecimal
        color = int(color, 16)

        guild = self.client.mainGuild

        if members:
            members = members.split()
            members = list(map(lambda id: f"<@{id}>", members))
            members = "\n".join(members)
        else:
            members = "No members."

        embed = discord.Embed(color=color, title=name, description=members)

        owner = guild.get_member(owner)
        embed.set_author(name=f"Owner: {owner.name}", icon_url=owner.avatar_url_as(static_format='jpg'))

        if img_location:
            filename = img_location.split('/')[-1]
            f = discord.File(img_location, filename=filename)
            embed.set_image(url=f'attachment://{filename}')
            await ctx.send(embed=embed, file=f)
        else:
            await ctx.send(embed=embed)
        


    @gang.command()
    async def membersm(self, ctx, *, name=None):
        
        if not name:
            conn = sqlite3.connect('./storage/databases/gangs.db')
            c = conn.cursor()
            c.execute('SELECT name, owner, members FROM gangs')
            gangs = c.fetchall()
            conn.close()

            for gang in gangs:
                if ctx.author.id == gang[1] or str(ctx.author.id) in gang[2].split():
                    name = gang[0]
                    break
            
            if not name:
                await ctx.send("You are not in a gang.")
                return



        conn = sqlite3.connect('./storage/databases/gangs.db')
        c = conn.cursor()
        try:
            c.execute('SELECT owner, members, color, img_location FROM gangs WHERE name = ?', (name,))
            owner, members, color, img_location = c.fetchone()
            conn.close()
        except:
            c.execute('SELECT name FROM gangs')
            gangs = c.fetchall()
            conn.close()
            gangs = list(map(lambda gang: gang[0], gangs))
            close = difflib.get_close_matches(name, gangs, n=3, cutoff=0.5)
            

            if len(close) > 0:
                
                close = list(map(lambda word: f"`{word}`", close))

                text = "\n".join(close)

                text = f"There is no gang called **{name}**. Did you mean:\n{text}"

            else:
                
                text = f"There is no gang called **{name}**."
            
            await ctx.send(text) 

            return
        
        # Converts into hexadecimal
        color = int(color, 16)

        guild = self.client.mainGuild

        if members:
            members = members.split()
            members = list(map(lambda userid: guild.get_member(int(userid)).name, members))
            members = "\n".join(members)
        else:
            members = "No members."

        embed = discord.Embed(color=color, title=name, description=members)

        owner = guild.get_member(owner)
        embed.set_author(name=f"Owner: {owner.name}", icon_url=owner.avatar_url_as(static_format='jpg'))

        if img_location:
            filename = img_location.split('/')[-1]
            f = discord.File(img_location, filename=filename)
            embed.set_image(url=f'attachment://{filename}')
            await ctx.send(embed=embed, file=f)
        else:
            await ctx.send(embed=embed)
        


    @gang.command()
    async def create(self, ctx, *, name=None):

        if not await level_check(ctx, ctx.author.id, 3, "be in a gang"):
            return
        
        if not name:
            await ctx.send("Incorrect command usage:\n`.gang create gangname`")
            return
        
        conn = sqlite3.connect('./storage/databases/gangs.db')
        c = conn.cursor()
        c.execute('SELECT name, owner, members FROM gangs')
        gangs = c.fetchall()
        conn.close()
        for gang in gangs:
            if ctx.author.id == gang[1]:
                await ctx.send("You already own a gang.")
                return
            
            elif str(ctx.author.id) in gang[2].split():
                await ctx.send("You are already in another gang.")
                return
            
            elif name == gang[0]:
                await ctx.send("A gang with that name already exists.")
                return
        

        conn = sqlite3.connect('./storage/databases/gangs.db')
        c = conn.cursor()
        c.execute('INSERT INTO gangs (name, owner, created_at) VALUES (?, ?, ?)', (name, ctx.author.id, datetime.datetime.utcnow()))
        conn.commit()
        conn.close()
        await ctx.send(f"Successfully created gang: **{name}**")

    
    @gang.command()
    async def invite(self, ctx, member:discord.Member=None):


        if not member:
            await ctx.send("Incorrect command usage:\n`.gang invite member`")
            return

        elif member == ctx.author:
            await ctx.send("You can't invite yourself.")
            return

        elif read_value(member.id, 'level') < 3:
            await ctx.send(f"**{member.name}** must be at least level 3 in order to be in a gang.")
            return

        conn = sqlite3.connect('./storage/databases/gangs.db')
        c = conn.cursor()
        c.execute('SELECT name, members, all_invite, owner, img_location, color FROM gangs')
        gangs = c.fetchall()
        conn.close()

        gangname = None

    

        for gang in gangs:


            if str(ctx.author.id) in gang[1].split() or ctx.author.id == gang[3]:

                if str(member.id) in gang[1].split():
                    await ctx.send("This user is already in your gang.")
                    return

                elif member.id == gang[3]:
                    await ctx.send("This user is the owner of your gang.")
                    return


                if gang[2] == "True" or gang[3] == ctx.author.id:
                    gangname = gang[0]
                    img_location = gang[4]
                    color = int(gang[5], 16)
                else:
                    await ctx.send("All invite is disabled for your gang.")
                    return

                break

            elif str(member.id) in gang[1].split() or member.id == gang[3]:
                await ctx.send("This user is already in another gang.")
                return
            
        
        if not gangname: 
            await ctx.send("You are not in a gang.")
            return

        for gang in gangs:
            
            if (str(member.id) in gang[1].split() or member.id == gang[3]) and gang[0] != gangname:
                await ctx.send("This user is already in another gang.")
                return

        for task in asyncio.all_tasks():
            if task.get_name() == f'gang invite {ctx.author.id} {member.id}':
                await ctx.send("You already sent an invite to this user.")
                return
        
        asyncio.create_task(self.invite_req_task(ctx, member, gangname, img_location, color), name=f"gang invite {ctx.author.id} {member.id}")




    async def invite_req_task(self, ctx, member, gangname, img_location, color):

        embed = discord.Embed(color=color, title="Gang invite", description=f"To: {member.mention}\nFrom {ctx.author.mention}\nGang: {gangname}")


        if img_location:
            filename = img_location.split('/')[-1]
            f = discord.File(img_location, filename=filename)
            embed.set_image(url=f'attachment://{filename}')
            message = await ctx.send(embed=embed, file=f)

        else:
            message = await ctx.send(embed=embed)
        await message.add_reaction('✅')
        await message.add_reaction('❌')
        try:
            reaction, user = await self.client.wait_for('reaction_add', check=lambda reaction, user: (str(reaction.emoji) == '✅' or str(reaction.emoji) == '❌') and reaction.message.id == message.id and user == member, # noqa pylint: disable=unused-variable
             timeout=300)
        except asyncio.TimeoutError:
            await ctx.send(f"Gang invite to **{member.name}** timed out.")
            return

        if str(reaction.emoji) == '✅':
            conn = sqlite3.connect('./storage/databases/gangs.db')
            c = conn.cursor()
            c.execute('SELECT name, members, owner, role_id FROM gangs')
            gangs = c.fetchall()
            conn.close()

            for gang in gangs:
                
                if str(member.id) in gang[1].split() or member.id == gang[2]:
                    await ctx.send("You already in a gang.")
                    return

                elif gang[0] == gangname:
                    members = gang[1].split()
                    role_id = gang[3]
                    break
                

            members.append(str(member.id))
            members = " ".join(members)
            conn = sqlite3.connect('./storage/databases/gangs.db')
            c = conn.cursor()
            c.execute('UPDATE gangs SET members = ? WHERE name = ?', (members, gangname))
            conn.commit()
            conn.close()

            await ctx.send(f"**{member.name}** joined **{gangname}**.")

            if role_id:
                guild = self.client.mainGuild
                role = guild.get_role(role_id)

                await member.add_roles(role)

            
            


            
        else:
            await ctx.send(f"**{member.name}** denied the invite to **{gangname}**.")

    @gang.command()
    async def uninvite(self, ctx, member:discord.Member=None):
        if not member:
            await ctx.send("Incorrect command usage:\n`.gang uninvite member`")
            return

        for task in asyncio.all_tasks():
            if task.get_name() == f'gang invite {ctx.author.id} {member.id}':
                task.cancel()
                await ctx.send(f"Invite to **{member.name}** cancelled.")
                return
        await ctx.send(f"You do not have a pending invite for **{member.name}**.")

    @gang.group(invoke_without_command=True)
    async def settings(self, ctx):
        await ctx.send("Incorrect command usage:\n`.gang settings rename/description/icon/role/color/allinvite`")
    
    @settings.command()
    @commands.max_concurrency(1, per=commands.BucketType.member)
    async def rename(self, ctx, *, name=None):
        
        if not name:
            await ctx.send("Incorrect command usage:\n`.gang settings rename newname`")
            return
        
        conn = sqlite3.connect('./storage/databases/gangs.db')
        c = conn.cursor()
        c.execute('SELECT name, owner, members, role_id FROM gangs')
        gangs = c.fetchall()
        conn.close()

        for gang in gangs:
            
            if str(ctx.author.id) in gang[2].split():
                await ctx.send(f"You do not own the gang **{gang[0]}**.")
                return

            elif gang[0] == name:
                await ctx.send(f"A gang called {name} already exists.")
                return
            
            elif ctx.author.id == gang[1]:

                if gang[3]:
                    guild = self.client.mainGuild
                    role = guild.get_role(gang[3])

                    await role.edit(name=name)

                conn = sqlite3.connect('./storage/databases/gangs.db')
                c = conn.cursor()
                c.execute('UPDATE gangs SET name = ? WHERE name = ?', (name, gang[0]))
                conn.commit()
                conn.close()


                await ctx.send(f"Gang name updated from {gang[0]} to {name}.")
                
                return

                
            
        await ctx.send("You are not in a gang.")


    @settings.command()
    @commands.max_concurrency(1, per=commands.BucketType.member)
    async def description(self, ctx, *, description=None):

        if not description:
            await ctx.send("Incorrect command usage:\n`.gang settings description newdescription`")
            return
        
        conn = sqlite3.connect('./storage/databases/gangs.db')
        c = conn.cursor()
        c.execute('SELECT name, owner, members FROM gangs')
        gangs = c.fetchall()
        conn.close()

        for gang in gangs:
            
            if str(ctx.author.id) in gang[2].split():
                await ctx.send(f"You do not own the gang **{gang[0]}**.")
                return

            
            elif ctx.author.id == gang[1]:

                conn = sqlite3.connect('./storage/databases/gangs.db')
                c = conn.cursor()
                c.execute('UPDATE gangs SET description = ? WHERE name = ?', (description, gang[0]))
                conn.commit()
                conn.close()

                await ctx.send(f"Gang description successfully updated.")
                
                return

                
            
        await ctx.send("You are not in a gang.")

    
    @settings.command()
    @commands.max_concurrency(1, per=commands.BucketType.member)
    async def icon(self, ctx, *, image_link=None):

        if not image_link and not ctx.message.attachments:
            await ctx.send("Incorrect command usage:\n`.gang settings icon imagelink` or `.gang settings icon` *with the image attached.*\n`.gang settings icon delete` to delete icon.")
            return
        
        conn = sqlite3.connect('./storage/databases/gangs.db')
        c = conn.cursor()
        c.execute('SELECT name, owner, members, img_location FROM gangs')
        gangs = c.fetchall()
        conn.close()

        for gang in gangs:
            
            if str(ctx.author.id) in gang[2].split():
                await ctx.send(f"You do not own the gang **{gang[0]}**.")
                return

            
            elif ctx.author.id == gang[1]:

                if image_link:

                    if image_link.lower() == 'delete':
                        conn = sqlite3.connect('./storage/databases/gangs.db')
                        c = conn.cursor()
                        c.execute('SELECT img_location FROM gangs WHERE name = ?', (gang[0],))

                        img_location = c.fetchone()[0]

                        if not img_location:
                            conn.close()
                            await ctx.send("Your gang does not have an icon saved.")
                            return
                        

                        c.execute('UPDATE gangs SET img_location = null WHERE name = ?', (gang[0],))
                        conn.commit()
                        conn.close()

                       

                        os.remove(img_location)

                        await ctx.send("Successfully deleted gang icon.")
                        return
                            
                # to get a free file name

                if not gang[3]:

                    files = [f for f in os.listdir('./storage/images/gang-icons') if os.path.isfile(os.path.join('./storage/images/gang-icons', f))]
                    files = list(map(lambda filename: os.path.splitext(filename)[0], files))
                    
                    save_path = gang[0].lower().replace(' ', '_')
                    regex = re.compile('[^a-zA-Z1-9_]')

                    save_path = regex.sub('', save_path)

                    if save_path in files:
                        number = 1
                        save_path += f'({number})'
                        while save_path in files:
                            save_path = save_path.replace(f'({number})', f'({number+1})')
                            number += 1

                    save_path = f"./storage/images/gang-icons/{save_path}"
                
                else:
                    
                    save_path = os.path.splitext(gang[3])[0]
                
                


                # to download the image

                if image_link:

                    try:
                        async with aiohttp.ClientSession() as session:

                            async with session.get(image_link) as resp:

                                allowed_formats = ['png', 'jpg', 'jpeg', 'gif']
                                allowed_formats = list(map(lambda extension: f"image/{extension}", allowed_formats))

                                if resp.content_type not in allowed_formats:
                                    await ctx.send("Only files with `.png`, `.jpg`, `jpeg`, and `gif` file extensions are supported.")
                                    return

                                data = await resp.read()

                                img_location = f"{save_path}.{resp.content_type.split('/')[1]}"

                                with open(img_location, "wb") as f:
                                    f.write(data)
                                    
                    except aiohttp.client_exceptions.InvalidURL:
                        await ctx.send("Invalid image link.")
                        return

                
                else:
                    image = ctx.message.attachments[0]
                    if not image.filename.endswith(('png', 'jpg', 'jpeg', 'gif')):
                        await ctx.send("Only files with `.png`, `.jpg`, `jpeg`, and `gif` file extensions are supported.")
                        return

                    img_location = save_path + os.path.splitext(image.filename)[1]

                    await image.save(fp=img_location)
                    


                conn = sqlite3.connect('./storage/databases/gangs.db')
                c = conn.cursor()
                c.execute('UPDATE gangs SET img_location = ? WHERE name = ?', (img_location, gang[0]))
                gangs = c.fetchall()
                conn.commit()
                conn.close()

                await ctx.send(f"Gang icon successfully updated.")
                
                return

                
            
        await ctx.send("You are not in a gang.")


    @settings.command()
    @commands.max_concurrency(1, per=commands.BucketType.member)
    async def role(self, ctx, action = ''):
        
        action = action.lower()

        if action != 'create' and action != 'delete':
            await ctx.send("Incorrect command usage:\n`.gang settings role create/delete`")
            return

        conn = sqlite3.connect('./storage/databases/gangs.db')
        c = conn.cursor()
        c.execute('SELECT name, owner, members, color, role_id FROM gangs')
        gangs = c.fetchall()
        conn.close()


        for gang in gangs:
            
            if str(ctx.author.id) in gang[2].split():
                await ctx.send(f"You do not own the gang **{gang[0]}**.")
                return

            
            elif ctx.author.id == gang[1]:

                members = gang[2].split()
                
    

                guild = self.client.mainGuild

                if action == 'create':

                    # owner counts as one also
                    if len(members) < 2:
                        await ctx.send("You must have at least three members in your gang to create a role.")
                        return

                    if gang[4]:
                        await ctx.send("You already have a gang role.")
                        return

                    color = discord.Color(int(gang[3], 16))
                    role = await guild.create_role(reason="Gang role created", name=gang[0], color=color, mentionable=True)

                    conn = sqlite3.connect('./storage/databases/gangs.db')
                    c = conn.cursor()
                    c.execute('UPDATE gangs SET role_id = ? WHERE name = ?', (role.id, gang[0]))
                    conn.commit()
                    conn.close()

                    members.append(gang[1])
                    members = list(map(lambda member: guild.get_member(int(member)), members))
                    members = list(filter(lambda member: member, members))
                    

                    await ctx.send(f"Your gang role, {role.mention}, was successfully created.")

                    for member in members:
                        await member.add_roles(role)
                
                else:

                    if not gang[4]:
                        await ctx.send("Your gang does not have a role.")
                        return


                    conn = sqlite3.connect('./storage/databases/gangs.db')
                    c = conn.cursor()
                    c.execute('UPDATE gangs SET role_id = null WHERE name = ?', (gang[0],))
                    conn.commit()
                    conn.close()

                    await ctx.send(f"Your gang role has been deleted.")


                
                return

                
            
        await ctx.send("You are not in a gang.")

    @settings.command()
    async def color(self, ctx, color=None):
        

        if not color:
            await ctx.send("Incorrect command usage:\n`.gang settings color #ffffff`\nWhere `#ffffff` is the hex color code.")
            return

        conn = sqlite3.connect('./storage/databases/gangs.db')
        c = conn.cursor()
        c.execute('SELECT name, owner, members, role_id FROM gangs')
        gangs = c.fetchall()
        conn.close()

        for gang in gangs:
            
            if str(ctx.author.id) in gang[2].split():
                await ctx.send(f"You do not own the gang **{gang[0]}**.")
                return

            
            elif ctx.author.id == gang[1]:

                color = color.replace('#', '')

                if len(color) != 6:
                    await ctx.send("Enter a valid hex color code.")
                    return

                try:
                    color_code = int(color, 16)

                    if color_code > 16777215 or color_code < 0: # equivalent to ffffff
                        await ctx.send("Enter a valid hex color code.")
                        return

                except:
                    await ctx.send("Enter a valid hex color code.")
                    return

                conn = sqlite3.connect('./storage/databases/gangs.db')
                c = conn.cursor()
                c.execute('UPDATE gangs SET color = ? WHERE name = ?', (color, gang[0]))
                conn.commit()
                conn.close()



                await ctx.send(f"Gang color set to #{color}.")

                if gang[3]:
                    guild = self.client.mainGuild
                    role = guild.get_role(gang[3])
                    
                    await role.edit(color=discord.Color(color_code))
                
                return

                
            
        await ctx.send("You are not in a gang.")

    @settings.command()
    async def allinvite(self, ctx, state=''):

        state = state.lower()

        if state != 'on' and state != 'off':
            await ctx.send("Incorrect command usage:\n`.gang settings allinvite on/off`")
            return

        if state == 'on':
            state = 'True'
        else:
            state = 'False'

        conn = sqlite3.connect('./storage/databases/gangs.db')
        c = conn.cursor()
        c.execute('SELECT name, owner, members FROM gangs')
        gangs = c.fetchall()
        conn.close()

        for gang in gangs:
            
            if str(ctx.author.id) in gang[2].split():
                await ctx.send(f"You do not own the gang **{gang[0]}**.")
                return

            
            elif ctx.author.id == gang[1]:

                conn = sqlite3.connect('./storage/databases/gangs.db')
                c = conn.cursor()
                c.execute('UPDATE gangs SET all_invite = ? WHERE name = ?', (state, gang[0]))
                conn.commit()
                conn.close()

                if state == 'True':
                    state = 'enabled'
                else:
                    state = 'disabled'

                await ctx.send(f"All invite {state}.")
                
                return

                
            
        await ctx.send("You are not in a gang.")

        
        


    @gang.command()
    @commands.max_concurrency(1, per=commands.BucketType.member)
    async def leave(self, ctx):

        conn = sqlite3.connect('./storage/databases/gangs.db')
        c = conn.cursor()
        c.execute('SELECT name, owner, members, role_id FROM gangs')
        gangs = c.fetchall()
        conn.close()

        for gang in gangs:

            if ctx.author.id == gang[1]:
                await ctx.send("You own this gang.")
                return


            elif str(ctx.author.id) in gang[2].split():

                await ctx.send(f"Are you sure you want to leave **{gang[0]}**? Respond with `yes` or `y` to proceed.")

                try:
                    response = await self.client.wait_for('message', check=lambda message: message.channel == ctx.channel and message.author == ctx.author, timeout=20)
                except:
                    await ctx.send("Leave cancelled due to inactivity.")
                    return
                
                response = response.content.lower()

                if response == 'yes' or response == 'y':

                    conn = sqlite3.connect('./storage/databases/gangs.db')
                    c = conn.cursor()
                    c.execute('SELECT members FROM gangs WHERE name = ?', (gang[0],))

                    members = c.fetchone()[0].split()
                    members.remove(str(ctx.author.id))
                    members = " ".join(members)

                    c.execute('UPDATE gangs SET members = ? WHERE name = ?', (members, gang[0]))
                    
                    conn.commit()
                    conn.close()

                    await ctx.send(f"**{ctx.author.name}** has left **{gang[0]}**.")

                    if gang[3]:
                        guild = self.client.mainGuild
                        role = guild.get_role(gang[3])

                        await ctx.author.remove_roles(role)

                        members = members.split()
                        if len(members) < 2:
                            await role.delete(reason="Gang role deleted")

                            conn = sqlite3.connect('./storage/databases/gangs.db')
                            c = conn.cursor()
                            c.execute('UPDATE gangs SET role_id = null WHERE name = ?', (gang[0],))
                            conn.commit()
                            conn.close()

                else:
                    await ctx.send("Leave cancelled.")
                
                return


        

        await ctx.send("You are not in a gang.")

    @gang.command()
    @commands.max_concurrency(1, per=commands.BucketType.member)
    async def promote(self, ctx, member:discord.Member=None):

        if not member:
            await ctx.send("Incorrect command usage:\n`.gang promote member`")
            return


        conn = sqlite3.connect('./storage/databases/gangs.db')
        c = conn.cursor()
        c.execute('SELECT name, owner, members FROM gangs')
        gangs = c.fetchall()
        conn.close()

        for gang in gangs:

            if str(ctx.author.id) in gang[2].split():
                await ctx.send("You do not own this gang.")
                return


            elif ctx.author.id == gang[1]:

                members = gang[2].split()
                if str(member.id) not in members:
                    await ctx.send("This user is not in your gang.")
                    return

                await ctx.send(f"Are you sure you want to promote **{member.name}** to the gang owner? Respond with `yes` or `y` to proceed.")

                try:
                    response = await self.client.wait_for('message', check=lambda message: message.channel == ctx.channel and message.author == ctx.author, timeout=20)
                except:
                    await ctx.send("Promotion cancelled due to inactivity.")
                    return
                
                response = response.content.lower()

                if response == 'yes' or response == 'y':

                    members.remove(str(member.id))
                    members.append(str(ctx.author.id))
                    
                    members = " ".join(members)

                    conn = sqlite3.connect('./storage/databases/gangs.db')
                    c = conn.cursor()
                    c.execute('UPDATE gangs SET members = ? WHERE name = ?', (members, gang[0]))
                    c.execute('UPDATE gangs SET owner = ? WHERE name = ?', (member.id, gang[0]))
                    conn.commit()
                    conn.close()

                    await ctx.send(f"**{member.name}** was promoted to the gang owner by **{ctx.author.name}**.")

                else:
                    await ctx.send("Promotion cancelled.")
                
                return


        

        await ctx.send("You are not in a gang.")


    @gang.command()
    @commands.max_concurrency(1, per=commands.BucketType.member)
    async def kick(self, ctx, member:discord.Member=None):

        if not member:
            await ctx.send("Incorrect command usage:\n`.gang kick member`")
            return


        conn = sqlite3.connect('./storage/databases/gangs.db')
        c = conn.cursor()
        c.execute('SELECT name, owner, members, role_id FROM gangs')
        gangs = c.fetchall()
        conn.close()

        for gang in gangs:

            if str(ctx.author.id) in gang[2].split():
                await ctx.send("You do not own this gang.")
                return


            elif ctx.author.id == gang[1]:

                members = gang[2].split()
                if str(member.id) not in members:
                    await ctx.send("This user is not in your gang.")
                    return

                await ctx.send(f"Are you sure you want to kick **{member.name}** from the gang? Respond with `yes` or `y` to proceed.")

                try:
                    response = await self.client.wait_for('message', check=lambda message: message.channel == ctx.channel and message.author == ctx.author, timeout=20)
                except:
                    await ctx.send("Disband cancelled due to inactivity.")
                    return
                
                response = response.content.lower()

                if response == 'yes' or response == 'y':

                    guild = self.client.mainGuild

                    members.remove(str(member.id))

                    if gang[3]: # role id

                        role = guild.get_role(gang[3])

                        await member.remove_roles(role)

                        if len(members) < 2:
                    
                            await role.delete(reason="Gang role deleted")
                            
                            conn = sqlite3.connect('./storage/databases/gangs.db')
                            c = conn.cursor()
                            c.execute('UPDATE gangs SET role_id = null WHERE name = ?', (gang[0],))
                            conn.commit()
                            conn.close()
                            
                    
                    members = " ".join(members)

                    conn = sqlite3.connect('./storage/databases/gangs.db')
                    c = conn.cursor()
                    c.execute('UPDATE gangs SET members = ? WHERE name = ?', (members, gang[0]))
                    conn.commit()
                    conn.close()

                    await ctx.send(f"**{member.name}** was kicked from **{gang[0]}**.")

                else:
                    await ctx.send("Kick cancelled.")
                
                return


        

        await ctx.send("You are not in a gang.")


    @gang.command()
    @commands.max_concurrency(1, per=commands.BucketType.member)
    async def disband(self, ctx):

        conn = sqlite3.connect('./storage/databases/gangs.db')
        c = conn.cursor()
        c.execute('SELECT name, owner, members, role_id, img_location FROM gangs')
        gangs = c.fetchall()
        conn.close()

        for gang in gangs:

            if str(ctx.author.id) in gang[2].split():
                await ctx.send("You do not own this gang.")
                return


            elif ctx.author.id == gang[1]:

                await ctx.send(f"Are you sure you want to disband **{gang[0]}**? Respond with the gang name to proceed.")

                try:
                    response = await self.client.wait_for('message', check=lambda message: message.channel == ctx.channel and message.author == ctx.author, timeout=20)
                except:
                    await ctx.send("Disband cancelled due to inactivity.")
                    return
                
                response = response.content.lower()

                if response == gang[0].lower():

                    if gang[3]: # role id
                        guild = self.client.mainGuild
                        role = guild.get_role(gang[3])

                        await role.delete(reason="Gang role deleted")
                    
                    if gang[4]:
                        os.remove(gang[4])

                    conn = sqlite3.connect('./storage/databases/gangs.db')
                    c = conn.cursor()
                    c.execute('DELETE FROM gangs WHERE name = ?', (gang[0],))
                    conn.commit()
                    conn.close()

                    await ctx.send(f"The gang **{gang[0]}** has been disbanded.")

                else:
                    await ctx.send("Disband cancelled.")
                
                return


        

        await ctx.send("You are not in a gang.")


        
        



def setup(client):
    client.add_cog(fun(client))