# pylint: disable=import-error

import discord
from discord.ext import commands
from discord.ext.commands import BadArgument, CommandNotFound
import json
import time
import sqlite3
import asyncio
from sqlite3 import Error
from datetime import timezone 
import os


# To import from different path
import sys
sys.path.insert(1 , os.getcwd())

from utils import timestring



modroles = [692952463501819984, 706952785362681906, 714584510523768903, 714676918175137814]

def modChannel(ctx):
    return ctx.channel.id == 714585657808257095

def reportChannel(ctx):
    return ctx.channel.id == 723985222412140584

def increment(userid, offense):
    conn = sqlite3.connect('./storage/databases/offenses.db')
    c = conn.cursor()
    try:
        c.execute(f'SELECT {offense} FROM offenses WHERE id = ?', (userid,))
        number = c.fetchone()[0]
    except:
        warns = mutes = kicks = bans = 0
        if offense == 'warns':
            warns = 1

        elif offense == 'mutes':
            mutes = 1

        elif offense == 'kicks':
            kicks = 1

        elif offense == 'bans':
            bans = 1
        

        c.execute('INSERT INTO offenses (id, warns, mutes, kicks, bans) VALUES (?, ?, ?, ?, ?)', (userid, warns, mutes, kicks, bans))

    else:
        number += 1
        c.execute(f'UPDATE offenses SET {offense} = ? WHERE id = ?', (number, userid))

    conn.commit()
    conn.close()

def decrement(userid, offense):
    conn = sqlite3.connect('./storage/databases/offenses.db')
    c = conn.cursor()
    c.execute(f'SELECT {offense} FROM offenses WHERE id = ?', (userid,))
    number = c.fetchone()[0]
    if number > 0:
        number -= 1
    c.execute(f'UPDATE offenses SET {offense} = ? WHERE id = ?', (number, userid))
    conn.commit()
    conn.close()

class admin(commands.Cog):

    def __init__(self, client):
        self.client = client

        with open('./storage/jsons/mutes.json') as f:
            mutes = json.load(f)
        
        for mute in mutes:

            asyncio.create_task(self.wait_until_unmute(mute, mutes[mute]), name=f"unmute {mute}")
    
    def cog_unload(self):

        for task in asyncio.all_tasks():
            if task.get_name().startswith("unmute "):
                task.cancel()

    
    async def wait_until_unmute(self, userid, duration):

        duration = duration - int(time.time())
        if duration < 0:
            duration = 0


        await asyncio.sleep(duration)

        guild = self.client.mainGuild

        member = guild.get_member(int(userid))
        if member:
            mute_role = guild.get_role(743255783055163392)
            await member.remove_roles(mute_role)

        with open('./storage/jsons/mutes.json') as f:
            mutes = json.load(f)
        
        del mutes[userid]

        with open(f'./storage/jsons/mutes.json', 'w') as f:
            json.dump(mutes, f, indent=2)
        

    @commands.command()
    @commands.has_any_role(*modroles)
    async def warn(self, ctx, member:discord.Member=None, reason="None", messageid=None, channel:discord.TextChannel=None):

        if not member:
            await ctx.send("Incorrect command usage:\n`.warn member \"(reason)\" (messageid) (textchannel)`")
            return

        author = ctx.author

        if author.top_role <= member.top_role:
            await ctx.send('This member has a higher or same role as you.')
            return

        #Grabbing next id

        with open(f'./storage/jsons/auditcount.json') as json_file:
            auditcount = json.load(json_file)

        auditid = auditcount["count"]
        auditcount["count"] += 1

        with open(f'./storage/jsons/auditcount.json', 'w') as f:
            json.dump(auditcount, f, indent=2)


        #Building embed
        datetime = str(ctx.message.created_at.utcnow())
        embed = discord.Embed(color=0xf56451, title=f"User Warned", description=f"Reason: {reason}")
        member_avatar = member.avatar_url_as(static_format='jpg')
        embed.set_author(name=f"{member.name}#{member.discriminator}", icon_url=member_avatar)
        author_avatar = author.avatar_url_as(static_format='jpg')
        embed.set_footer(text=f'By {author.name}#{author.discriminator} • {datetime}', icon_url=author_avatar)
        embed.add_field(name='User ID:', value=member.id, inline=True)
        embed.add_field(name='Audit ID:', value=auditid, inline=True)
        if messageid != None:
            try:
                if channel == None:
                    message = await ctx.channel.fetch_message(messageid)
                else:
                    message = await channel.fetch_message(messageid)
                content = message.content
                embed.add_field(name='Message ID:', value=messageid, inline=True)
            except:
                content = "Error: Message not found"
                pass
        else:
            content = None
        await ctx.send(embed=embed)
        await member.send(f'You were warned by {author.mention} for: {reason}')
        embed.add_field(name='Jump Url', value=f"[Click Here]({ctx.message.jump_url})")
        audit_log_channel = self.client.get_channel(723339632145596496)
        await audit_log_channel.send(embed=embed)


        #Saving warn data
        try:
            with open(f'./storage/member-audits/{member.id}.json') as json_file:
                audits = json.load(json_file)
            
            with open(f'./storage/member-audits/{member.id}.json','w') as f:
                    
                if content == None:
                    audits.append({'audit id':auditid, 'action':'warn', 'reason':reason, 'date':datetime, 'jump link':ctx.message.jump_url})
                    json.dump(audits, f, indent=2)
                else:
                    audits.append({'audit id':auditid, 'action':'warn', 'reason':reason, 'date':datetime, 'jump link':ctx.message.jump_url, 'message content':content})
                    json.dump(audits, f, indent=2)
        except: 

            with open(f'./storage/member-audits/{member.id}.json','w') as f:
                if content == None:
                    json.dump([{'audit id':auditid, 'action':'warn', 'reason':reason, 'date':datetime, 'jump link':ctx.message.jump_url}], f, indent=2)
                else:
                    json.dump([{'audit id':auditid, 'action':'warn', 'reason':reason, 'date':datetime, 'jump link':ctx.message.jump_url, 'message content':content}], f, indent=2)
        
        #Adding to count
        increment(member.id, 'warns')

    @commands.command()
    @commands.has_any_role(*modroles)
    async def mute(self, ctx, member:discord.Member=None, duration=None, reason="None", messageid=None, channel:discord.TextChannel=None):

        if not member or not duration:
            await ctx.send("Incorrect command usage:\n`.mute member \"duration\" \"(reason)\" (messageid) (textchannel)`")
            return
        

        seconds = timestring(duration)

        if not seconds:
            await ctx.send("Duration must be in this format: `1d 2h 3m 4s`")
            return


        author = ctx.author

        if author.top_role <= member.top_role:
            await ctx.send('This member has a higher or same role as you.')
            return

        #Grabbing next id

        with open(f'./storage/jsons/auditcount.json') as json_file:
            auditcount = json.load(json_file)

        auditid = auditcount["count"]
        auditcount["count"] += 1

        with open(f'./storage/jsons/auditcount.json', 'w') as f:
            json.dump(auditcount, f, indent=2)


        #Building embed
        datetime = str(ctx.message.created_at.utcnow())
        embed = discord.Embed(color=0xf56451, title=f"User Muted", description=f"Reason: {reason}")
        member_avatar = member.avatar_url_as(static_format='jpg')
        embed.set_author(name=f"{member.name}#{member.discriminator}", icon_url=member_avatar)
        author_avatar = author.avatar_url_as(static_format='jpg')
        embed.set_footer(text=f'By {author.name}#{author.discriminator} • {datetime}', icon_url=author_avatar)
        embed.add_field(name='User ID:', value=member.id, inline=True)
        embed.add_field(name='Audit ID:', value=auditid, inline=True)
        embed.add_field(name='Duration', value=duration, inline=True)
        if messageid != None:
            try:
                if channel == None:
                    message = await ctx.channel.fetch_message(messageid)
                else:
                    message = await channel.fetch_message(messageid)
                content = message.content
                embed.add_field(name='Message ID:', value=messageid, inline=True)
            except:
                content = "Error: Message not found"
                pass
        else:
            content = None
        await ctx.send(embed=embed)
        embed.add_field(name='Jump Url', value=f"[Click Here]({ctx.message.jump_url})")
        audit_log_channel = self.client.get_channel(723339632145596496)
        await audit_log_channel.send(embed=embed)

        guild = self.client.mainGuild
        mute_role = guild.get_role(743255783055163392)

        await member.add_roles(mute_role)

        # Saving when mute will end

        with open(f'./storage/jsons/mutes.json') as f:
            mutes = json.load(f)

        time_to_mute = int(time.time()) + seconds
        mutes[str(member.id)] = time_to_mute

        with open(f'./storage/jsons/mutes.json','w') as f:
            json.dump(mutes, f, indent=2)

        asyncio.create_task(self.wait_until_unmute(str(member.id), time_to_mute), name=f"unmute {member.id}")



        #Saving mute data
        try:
            with open(f'./storage/member-audits/{member.id}.json') as json_file:
                audits = json.load(json_file)
            
            with open(f'./storage/member-audits/{member.id}.json','w') as f:
                    
                if content == None:
                    audits.append({'audit id':auditid, 'action':'mute', 'duration': duration, 'reason':reason, 'date':datetime, 'jump link':ctx.message.jump_url})
                    json.dump(audits, f, indent=2)
                else:
                    audits.append({'audit id':auditid, 'action':'mute', 'duration': duration, 'reason':reason, 'date':datetime, 'jump link':ctx.message.jump_url, 'message content':content})
                    json.dump(audits, f, indent=2)
        except: 

            with open(f'./storage/member-audits/{member.id}.json','w') as f:
                if content == None:
                    json.dump([{'audit id':auditid, 'action':'mute', 'duration': duration, 'reason':reason, 'date':datetime, 'jump link':ctx.message.jump_url}], f, indent=2)
                else:
                    json.dump([{'audit id':auditid, 'action':'mute', 'duration': duration, 'reason':reason, 'date':datetime, 'jump link':ctx.message.jump_url, 'message content':content}], f, indent=2)
        
        #Adding to count
        increment(member.id, 'mutes')

    @commands.command()
    @commands.check(modChannel)
    @commands.has_any_role(*modroles)
    async def unmute(self, ctx, member:discord.Member=None, *, reason="None"):
        
        if not member:
            await ctx.send("Incorrect command usage:\n`.unmute member \"(reason)\" (messageid) (textchannel)`")
            return
        

        author = ctx.author

        if author.top_role <= member.top_role:
            await ctx.send('This member has a higher or same role as you.')
            return

        # Checking if not muted

        with open(f'./storage/jsons/mutes.json') as f:
            mutes = json.load(f)

        if str(member.id) not in mutes:
            await ctx.send("This user is not muted.")
            return

        #Grabbing next id

        with open(f'./storage/jsons/auditcount.json') as json_file:
            auditcount = json.load(json_file)

        auditid = auditcount["count"]
        auditcount["count"] += 1

        with open(f'./storage/jsons/auditcount.json', 'w') as f:
            json.dump(auditcount, f, indent=2)


        #Building embed
        datetime = str(ctx.message.created_at.utcnow())
        embed = discord.Embed(color=0xf56451, title=f"User Unmuted", description=f"Reason: {reason}")
        member_avatar = member.avatar_url_as(static_format='jpg')
        embed.set_author(name=f"{member.name}#{member.discriminator}", icon_url=member_avatar)
        author_avatar = author.avatar_url_as(static_format='jpg')
        embed.set_footer(text=f'By {author.name}#{author.discriminator} • {datetime}', icon_url=author_avatar)
        embed.add_field(name='User ID:', value=member.id, inline=True)
        embed.add_field(name='Audit ID:', value=auditid, inline=True)

        await ctx.send(embed=embed)
        embed.add_field(name='Jump Url', value=f"[Click Here]({ctx.message.jump_url})")
        audit_log_channel = self.client.get_channel(723339632145596496)
        await audit_log_channel.send(embed=embed)

        guild = self.client.mainGuild
        mute_role = guild.get_role(743255783055163392)

        await member.remove_roles(mute_role)

        # Removing mute duration

        with open(f'./storage/jsons/mutes.json') as f:
            mutes = json.load(f)

        del mutes[str(member.id)]

        with open(f'./storage/jsons/mutes.json','w') as f:
            json.dump(mutes, f, indent=2)

        # Cancelling unmute task, if any

        for task in asyncio.all_tasks():
            if task.get_name() == f'unmute {member.id}':
                task.cancel()
                break



        #Saving unmute data
        try:
            with open(f'./storage/member-audits/{member.id}.json') as json_file:
                audits = json.load(json_file)
            
            with open(f'./storage/member-audits/{member.id}.json','w') as f:
                    
                audits.append({'audit id':auditid, 'action':'unmute', 'reason':reason, 'date':datetime, 'jump link':ctx.message.jump_url})
                json.dump(audits, f, indent=2)
        except: 

            with open(f'./storage/member-audits/{member.id}.json','w') as f:

                json.dump([{'audit id':auditid, 'action':'unmute', 'reason':reason, 'date':datetime, 'jump link':ctx.message.jump_url}], f, indent=2)
        

        

        

    @commands.command()
    @commands.has_any_role(*modroles)
    async def kick(self, ctx, member:discord.Member=None, reason="None", messageid=None, channel:discord.TextChannel=None):
        if not member:
            await ctx.send("Incorrect command usage:\n`.kick member \"(reason)\" (messageid) (textchannel)`")
            return

        author = ctx.author

        if author.top_role <= member.top_role:
            await ctx.send('This member has a higher or same role as you.')
            return

        #Grabbing next id

        with open(f'./storage/jsons/auditcount.json') as json_file:
            auditcount = json.load(json_file)

        auditid = auditcount["count"]
        auditcount["count"] += 1

        with open(f'./storage/jsons/auditcount.json', 'w') as f:
            json.dump(auditcount, f, indent=2)


        #Building embed
        datetime = str(ctx.message.created_at.utcnow())
        embed = discord.Embed(color=0xf56451, title=f"User Kicked", description=f"Reason: {reason}")
        member_avatar = member.avatar_url_as(static_format='jpg')
        embed.set_author(name=f"{member.name}#{member.discriminator}", icon_url=member_avatar)
        author_avatar = author.avatar_url_as(static_format='jpg')
        embed.set_footer(text=f'By {author.name}#{author.discriminator} • {datetime}', icon_url=author_avatar)
        embed.add_field(name='User ID:', value=member.id, inline=True)
        embed.add_field(name='Audit ID:', value=auditid, inline=True)
        if messageid != None:
            try:
                if channel == None:
                    message = await ctx.channel.fetch_message(messageid)
                else:
                    message = await channel.fetch_message(messageid)
                content = message.content
                embed.add_field(name='Message ID:', value=messageid, inline=True)
            except:
                content = "Error: Message not found"
                pass
        else:
            content = None
        await ctx.send(embed=embed)
        rules = self.client.get_channel(704925578326966316)
        rule_invite = await rules.create_invite(max_uses=1, reason='Kicked, invited back.')
        rule_invite = str(rule_invite)
        await member.send(f'You were kicked by {author.mention} for: {reason}\n\nHere is a new invite link to join back: {rule_invite}')
        await member.kick(reason=reason)
        embed.add_field(name='Jump Url', value=f"[Click Here]({ctx.message.jump_url})")
        audit_log_channel = self.client.get_channel(723339632145596496)
        await audit_log_channel.send(embed=embed)


        #Saving kick data
        try:
            with open(f'./storage/member-audits/{member.id}.json') as json_file:
                audits = json.load(json_file)
            
            with open(f'./storage/member-audits/{member.id}.json','w') as f:

                if content == None:
                    audits.append({'audit id':auditid, 'action':'kick', 'reason':reason, 'date':datetime, 'jump link':ctx.message.jump_url})
                    json.dump(audits, f, indent=2)
                else:
                    audits.append({'audit id':auditid, 'action':'kick', 'reason':reason, 'date':datetime, 'jump link':ctx.message.jump_url, 'message content':content})
                    json.dump(audits, f, indent=2)
        except: 

            with open(f'./storage/member-audits/{member.id}.json','w') as f:
                if content == None:
                    json.dump([{'audit id':auditid, 'action':'kick', 'reason':reason, 'date':datetime, 'jump link':ctx.message.jump_url}], f, indent=2)
                else:
                    json.dump([{'audit id':auditid, 'action':'kick', 'reason':reason, 'date':datetime, 'jump link':ctx.message.jump_url, 'message content':content}], f, indent=2)

        #Adding to count
        increment(member.id, 'kicks')


    @commands.command()
    @commands.has_any_role(*modroles)
    async def ban(self, ctx, member:discord.Member=None, reason="None", messageid=None, daysdelete=0, channel:discord.TextChannel=None):
        if not member:
            await ctx.send("Incorrect command usage:\n`.ban member (reason) \"(messageid)\" (daystodelete) (textchannel)`")
            return

        author = ctx.author

        if author.top_role <= member.top_role:
            await ctx.send('This member has a higher or same role as you.')
            return

        try:
            daysdelete = int(daysdelete)
        except:
            await ctx.send('Enter a valid amount of days of messages to delete.')
            return

        if daysdelete < 0 or daysdelete > 7:
            await ctx.send('Enter an amount of days of messages to delete from 0-7')
            return

        #Grabbing next id

        with open(f'./storage/jsons/auditcount.json') as json_file:
            auditcount = json.load(json_file)

        auditid = auditcount["count"]
        auditcount["count"] += 1

        with open(f'./storage/jsons/auditcount.json', 'w') as f:
            json.dump(auditcount, f, indent=2)


        #Building embed
        datetime = str(ctx.message.created_at.utcnow())
        embed = discord.Embed(color=0xf56451, title=f"User Banned", description=f"Reason: {reason}")
        member_avatar = member.avatar_url_as(static_format='jpg')
        embed.set_author(name=f"{member.name}#{member.discriminator}", icon_url=member_avatar)
        author_avatar = author.avatar_url_as(static_format='jpg')
        embed.set_footer(text=f'By {author.name}#{author.discriminator} • {datetime}', icon_url=author_avatar)
        embed.add_field(name='User ID:', value=member.id, inline=True)
        embed.add_field(name='Audit ID:', value=auditid, inline=True)
        if messageid != None:
            try:
                if channel == None:
                    message = await ctx.channel.fetch_message(messageid)
                else:
                    message = await channel.fetch_message(messageid)
                content = message.content
                embed.add_field(name='Message ID:', value=messageid, inline=True)
            except:
                content = "Error: Message not found"
                pass
        else:
            content = None
        await ctx.send(embed=embed)
        await member.send(f'You were banned by {author.mention} for: {reason}\n\nIf you want to make an appeal, you may do so here: https://forms.gle/W1Vna4EAHmvs4bzB9')
        await member.ban(reason=reason, delete_message_days=daysdelete)
        embed.add_field(name='Jump Url', value=f"[Click Here]({ctx.message.jump_url})")
        audit_log_channel = self.client.get_channel(723339632145596496)
        await audit_log_channel.send(embed=embed)


        #Saving ban data
        try:
            with open(f'./storage/member-audits/{member.id}.json') as json_file:
                audits = json.load(json_file)
            
            with open(f'./storage/member-audits/{member.id}.json','w') as f:

                if content == None:
                    audits.append({'audit id':auditid, 'action':'ban', 'reason':reason, 'date':datetime, 'jump link':ctx.message.jump_url})
                    json.dump(audits, f, indent=2)
                else:
                    audits.append({'audit id':auditid, 'action':'ban', 'reason':reason, 'date':datetime, 'jump link':ctx.message.jump_url, 'message content':content})
                    json.dump(audits, f, indent=2)
        except: 

            with open(f'./storage/member-audits/{member.id}.json','w') as f:
                if content == None:
                    json.dump([{'audit id':auditid, 'action':'ban', 'reason':reason, 'date':datetime, 'jump link':ctx.message.jump_url}], f, indent=2)
                else:
                    json.dump([{'audit id':auditid, 'action':'ban', 'reason':reason, 'date':datetime, 'jump link':ctx.message.jump_url, 'message content':content}], f, indent=2)

        #Adding to count
        increment(member.id, 'bans')


    @commands.command()
    @commands.check(modChannel)
    @commands.has_any_role(*modroles)
    async def unban(self, ctx, member:int=None, *, reason="None"):

        if not member:
            await ctx.send("Incorrect command usage:\n`.unban member (reason)`")
            return


        try:
            member = await self.client.fetch_user(member)
        except:
            await ctx.send('Member not found.')
            return

        author = ctx.author

        #Grabbing next id
        guild = self.client.mainGuild

        with open(f'./storage/jsons/auditcount.json') as json_file:
            auditcount = json.load(json_file)

        auditid = auditcount["count"]
        auditcount["count"] += 1

        with open(f'./storage/jsons/auditcount.json', 'w') as f:
            json.dump(auditcount, f, indent=2)


        banned = False
        #Unbanning member
        bans = await guild.bans()
        for ban in bans:
            if ban.user.id == member.id:
                await guild.unban(member)
                banned = True
                break
            
        if not banned:
            await ctx.send('Member is not banned.')
            return


        #Building embed
        datetime = str(ctx.message.created_at.utcnow())
        embed = discord.Embed(color=0xf56451, title=f"User Unbanned", description=f"Reason: {reason}")
        member_avatar = member.avatar_url_as(static_format='jpg')
        embed.set_author(name=f"{member.name}#{member.discriminator}", icon_url=member_avatar)
        author_avatar = author.avatar_url_as(static_format='jpg')
        embed.set_footer(text=f'By {author.name}#{author.discriminator} • {datetime}', icon_url=author_avatar)
        embed.add_field(name='User ID:', value=member.id, inline=True)
        embed.add_field(name='Audit ID:', value=auditid, inline=True)

        await ctx.send(embed=embed)
        



        #Sending to audit log
        embed.add_field(name='Jump Url', value=f"[Click Here]({ctx.message.jump_url})")
        audit_log_channel = self.client.get_channel(723339632145596496)
        await audit_log_channel.send(embed=embed)


        #Saving unban data
        try:
            with open(f'./storage/member-audits/{member.id}.json') as json_file:
                audits = json.load(json_file)
            
            with open(f'./storage/member-audits/{member.id}.json','w') as f:
                audits.append({'audit id':auditid, 'action':'unban', 'reason':reason, 'date':datetime, 'jump link':ctx.message.jump_url})
                json.dump(audits, f, indent=2)
        except: 

            with open(f'./storage/member-audits/{member.id}.json','w') as f:
                json.dump([{'audit ID':auditid, 'action':'unban', 'reason':reason, 'date':datetime, 'jump link':ctx.message.jump_url}], f, indent=2)


    @commands.command()
    @commands.check(modChannel)
    @commands.has_any_role(*modroles)
    async def history(self, ctx, member:int=None, page=1):

        if not member:
            await ctx.send("Incorrect command usage:\n`.history member (page)`")
            return
        try:
            member = await self.client.fetch_user(member)
        except:
            await ctx.send('Member not found.')
            return

        try:
            page = int(page)
            if page <= 0:
                await ctx.send('Enter a valid page number.')
        except:
            await ctx.send('Enter a valid page number.')
        try:
            with open(f'./storage/member-audits/{member.id}.json') as json_file:
                temp_audit = json.load(json_file)
            
            
            temp_audit = temp_audit[::-1]
            audit = [temp_audit[x:x+3] for x in range(0, len(temp_audit), 3)]
            for x in audit:
                x = x[::-1]
            pages = len(audit)

            try:
                audit = audit[page-1]
                audit = audit[::-1]
                for pairs in audit:
                    embed = discord.Embed(color=0xf56451)
                    memberavatar = member.avatar_url_as(static_format='jpg')
                    embed.set_author(name=f'{member.name} (Page: {page}/{pages})', icon_url=memberavatar)
                    for cur_audit, value in pairs.items():

                        if cur_audit == "message content" and len(value) <= 1024:
                            value = value[:1024]

                        elif cur_audit == "jump link":
                            value = f"[Click Here]({value})"

                        embed.add_field(name=cur_audit, value=value)


                    await ctx.send(embed=embed)
            except:
                await ctx.send('This member does not have that many pages.')

        except:
            await ctx.send('Member has no audit history.')


    @commands.command()
    @commands.check(modChannel)
    @commands.has_any_role(*modroles)
    async def revoke(self, ctx, member=None, audit_id=None):
        
        if not member or not audit_id:
            await ctx.send("Incorrect command usage:\n`.revoke member auditid`")
            return

        #Fetching member
        try:
            member = await commands.MemberConverter().convert(ctx, member)

            if ctx.author.top_role <= member.top_role:
                await ctx.send('This member has a higher or same role as you.')
                return
        except:
            try:
                member = int(member)
                member = await self.client.fetch_user(member)
            except:
                await ctx.send('Member not found.')
                return


        #Verifying audit id
        try:
            audit_id = int(audit_id)
        except:
            await ctx.send('Enter a valid audit ID.')
            return

        try:
            with open(f'./storage/member-audits/{member.id}.json') as json_file:
                audits = json.load(json_file)
        except:
            await ctx.send('Audit not found.')
            return
        
        revoked = False
        for audit in audits:
            if audit["audit id"] == audit_id:
                action = audit["action"]
                audits.remove(audit)
                revoked = True
                break
        
        if not revoked:
            await ctx.send('Audit not found.')
            return
        
        if len(audits) == 0:
            filename = os.path.join(os.getcwd(), f'storage/member-audits/{member.id}.json')
            os.remove(filename)
        else:
            with open(f'./storage/member-audits/{member.id}.json','w') as f:
                json.dump(audits, f, indent=2)

        #Removing from count
        action += 's'
        if action not in ("unmutes", "unbans"):
            decrement(member.id, action)

        await ctx.send(f'Audit {audit_id} successfully revoked from {member.name}#{member.discriminator}.')


    @commands.command()
    @commands.check(modChannel)
    @commands.has_any_role(*modroles)
    async def offensecount(self, ctx, member=None):


        if not member:
            await ctx.send("Incorrect command usage:\n`.offensecount member`")
            return
        
        #Fetching member
        try:
            member = await commands.MemberConverter().convert(ctx, member)
        except:
            try:
                member = int(member)
                member = await self.client.fetch_user(member)
            except:
                await ctx.send('Member not found.')
                return

        conn = sqlite3.connect('./storage/databases/offenses.db')
        c = conn.cursor()
        try:
            c.execute('SELECT warns, kicks, bans, mutes FROM offenses WHERE id = ?', (member.id,))
            warns, kicks, bans, mutes = c.fetchone()
        except:
            warns = kicks = bans = mutes = 0
        conn.close()

        await ctx.send(f'{member.name}#{member.discriminator} offense count:\nWarns: {warns}\nKicks: {kicks}\nBans: {bans}\nMutes: {mutes}')

    @commands.command()
    @commands.has_any_role(*modroles)
    async def purge(self, ctx, amount=None, channel:discord.TextChannel=None):
        if not amount:
            amount = 5

        try:
            amount = int(amount)
        except:
            await ctx.send('Enter a valid amount of messages to purge.')
            return
        if not channel:
            amount += 1
            await ctx.channel.purge(limit=amount)
        else:
            if channel.category.id != 692949458551439370 and channel.category.id != 721444286591139963 and channel.category.id != 692949972764590160:
                await ctx.send('Invalid channel.')
                return
            await channel.purge(limit=amount)
            await ctx.send(f"{amount} messages cleared from {channel.mention}.")

    @commands.command()
    @commands.check(modChannel)
    @commands.has_any_role(692952463501819984, 706952785362681906, 714584510523768903, 714676918175137814)
    async def fullmessage(self, ctx, member=None, audit_id=None):

        if not member or not audit_id:
            await ctx.send("Incorrect command usage:\n`.fullmessage member auditid`")
            return

        #Verifying audit id
        try:
            audit_id = int(audit_id)
        except:
            await ctx.send('Enter a valid audit ID.')
            return

        #Fetching member
        try:
            member = await commands.MemberConverter().convert(ctx, member)
        except:
            try:
                member = int(member)
                member = await self.client.fetch_user(member)
            except:
                await ctx.send('Member not found.')
                return

        try:
            with open(f'./storage/member-audits/{member.id}.json') as json_file:
                audits = json.load(json_file)
        except:
            await ctx.send('Audit not found.')
            return
        
        for audit in audits:
            if audit["audit id"] == audit_id:
                if "message content" in audit.keys():
                    message = await ctx.send('_ _')
                    await message.edit(content=audit["message content"])
                else:
                    await ctx.send("Audit does not have message content recorded.")
                return

        await ctx.send("Audit not found.")
        
    @commands.command()
    async def report(self, ctx, member:discord.Member=None, *, reason="Not Specified"):
        
        if not member:
            await ctx.send("Incorrect command usage:\n`.report member (reason)`")
            return

        elif member.bot:
            await ctx.send("You cannot report bots..")

        author = ctx.author
        if member == author:
            await ctx.send("You can't report yourself.")
            return
        
        # Getting report cooldown
        conn = sqlite3.connect('./storage/databases/offenses.db')
        c = conn.cursor()
        try:
            c.execute('SELECT reportc FROM offenses WHERE id = ?', (member.id,))
            member_reportc = c.fetchone()[0]
        except:
            c.execute('INSERT INTO offenses (id) VALUES (?)', (member.id,))
            conn.commit()
            member_reportc = 0
        conn.close()

        if time.time() < member_reportc:
            await ctx.send('That member has already been reported.')
            return
        
        reportc = int(time.time()) + 7200

        conn = sqlite3.connect('./storage/databases/offenses.db')
        c = conn.cursor()
        c.execute('UPDATE offenses SET reportc = ? WHERE id = ?', (reportc, member.id))
        conn.commit()
        conn.close()

        with open(f'./storage/jsons/auditcount.json') as json_file:
            auditcount = json.load(json_file)

        auditid = auditcount["count"]
        auditcount["count"] += 1

        with open(f'./storage/jsons/auditcount.json', 'w') as f:
            json.dump(auditcount, f, indent=2)

        #Building and sending embed
        embed = discord.Embed(color=0xf56451, title="User Reported", description=f"Reason: {reason}")
        datetime = str(ctx.message.created_at.utcnow())
        member_avatar = member.avatar_url_as(static_format='jpg')
        embed.set_author(name=f"{member.name}#{member.discriminator}", icon_url=member_avatar)
        author_avatar = author.avatar_url_as(static_format='jpg')
        embed.set_footer(text=f'By {author.name}#{author.discriminator} • {datetime}', icon_url=author_avatar)
        embed.add_field(name='User ID:', value=member.id, inline=True)
        embed.add_field(name='Audit ID:', value=auditid, inline=True)
        await ctx.send(embed=embed)
        
        embed.add_field(name='Jump Url', value=f"[Click Here]({ctx.message.jump_url})")
        report_channel = self.client.get_channel(723985222412140584)

        guild = self.client.mainGuild
        owner = guild.get_role(692952463501819984)
        admin = guild.get_role(706952785362681906)
        mod = guild.get_role(714584510523768903)
        trial_mod = guild.get_role(714676918175137814)
        await report_channel.send(content=f"{owner.mention} {admin.mention} {mod.mention} {trial_mod.mention}",embed=embed)

    @commands.command()
    @commands.check(reportChannel)
    async def close(self, ctx, member=None):
        if not member:
            await ctx.send("Incorrect command usage:\n`.close member`")
            return
        
        #Fetching member
        try:
            member = await commands.MemberConverter().convert(ctx, member)
        except:
            try:
                member = int(member)
                member = await self.client.fetch_user(member)
            except:
                await ctx.send('Member not found.')
                return

        # Getting report cooldown
        conn = sqlite3.connect('./storage/databases/offenses.db')
        c = conn.cursor()
        try:
            c.execute('SELECT reportc FROM offenses WHERE id = ?', (member.id,))
            read_reportc = c.fetchone()[0]
        except:
            read_reportc = 0
        conn.close()


        if read_reportc == 0:
            await ctx.send(f"Report for {member.name}#{member.discriminator} is already closed.")
            return

        elif time.time() < read_reportc:
            await ctx.send(f"Closed report for {member.name}#{member.discriminator}.")

        elif time.time() > read_reportc:
            await ctx.send(f"Closed report for {member.name}#{member.discriminator}. (Report was already auto-closed.)")

        # Setting report cooldown to zero
        conn = sqlite3.connect('./storage/databases/offenses.db')
        c = conn.cursor()
        c.execute('UPDATE offenses SET reportc = 0 WHERE id = ?', (member.id,))
        conn.commit()
        conn.close()


    # Events

    @commands.Cog.listener() # Applications
    async def on_message(self, message):
        if not message.author.bot and message.channel.id == 716720359818133534:
            submissions = self.client.get_channel(716724583767474317)
            to_file_attachments = []
            for attachment in message.attachments:
                to_file = await attachment.to_file()
                to_file_attachments.append(to_file)

            await submissions.send(f"By {message.author.mention}:")
            await submissions.send(f"{message.content}", files=to_file_attachments)
            await message.delete()
            await message.channel.send(f"{message.author.mention}, your application was successfully submitted.")

    

def setup(client):
    client.add_cog(admin(client))