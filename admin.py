import discord
from discord.ext import commands
import json
import time
import sqlite3
import asyncio
from sqlite3 import Error
from utils import *
from datetime import timezone

client = commands.Bot(command_prefix = '.')
client.remove_command('help')

# Remember to exclude all commands from fun bot

def moderationCommandCheck(ctx):
    return ctx.channel.id != 716720359818133534

def modChannel(ctx):
    return ctx.channel.id == 714585657808257095

def inGuild(ctx):
    return ctx.guild.id == 692906379203313695

def reportChannel(ctx):
    return ctx.channel.id == 723985222412140584

@client.event
async def on_ready():
    print(f"Logged in as {client.user}.\nID: {client.user.id}")
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="everyone"))

@client.command()
@commands.check(moderationCommandCheck)
@commands.has_any_role(692952463501819984, 706952785362681906, 714584510523768903, 714676918175137814)
async def warn(ctx, member:discord.Member=None, reason="None", messageid=None, channel:discord.TextChannel=None):

    if not member:
        await ctx.send('Enter a member to warn.')
        return

    author = ctx.author

    #Grabbing next id
    guild = client.get_guild(692906379203313695)

    with open(f'auditcount.json') as json_file:
        auditcount = json.load(json_file)

    auditid = auditcount["count"]
    auditcount["count"] += 1

    with open(f'auditcount.json', 'w') as f:
        json.dump(auditcount, f, indent=2)


    #Building embed
    datetime = str(ctx.message.created_at.utcnow())
    embed = discord.Embed(color=0xf56451, title=f"User Warned", description=f"Reason: {reason}")
    member_avatar = member.avatar_url_as(static_format='jpg',size=256)
    embed.set_author(name=f"{member.name}#{member.discriminator}", icon_url=member_avatar)
    author_avatar = author.avatar_url_as(static_format='jpg',size=256)
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
    embed.add_field(name='Jump Url', value=ctx.message.jump_url)
    audit_log_channel = client.get_channel(723339632145596496)
    await audit_log_channel.send(embed=embed)


    #Saving warn data
    try:
        with open(f'member-audits\{member.id}.json') as json_file:
            audits = json.load(json_file)
        
        with open(f'member-audits\{member.id}.json','w') as f:
                
            if content == None:
                audits.append({'audit id':auditid, 'action':'warn', 'reason':reason, 'date':datetime, 'jump link':ctx.message.jump_url})
                json.dump(audits, f, indent=2)
            else:
                audits.append({'audit id':auditid, 'action':'warn', 'reason':reason, 'date':datetime, 'jump link':ctx.message.jump_url, 'message content':content})
                json.dump(audits, f, indent=2)
    except: 

        with open(f'member-audits\{member.id}.json','w') as f:
            if content == None:
                json.dump([{'audit id':auditid, 'action':'warn', 'reason':reason, 'date':datetime, 'jump link':ctx.message.jump_url}], f, indent=2)
            else:
                json.dump([{'audit id':auditid, 'action':'warn', 'reason':reason, 'date':datetime, 'jump link':ctx.message.jump_url, 'message content':content}], f, indent=2)
    
    #Adding to count
    warn_count = read_value('members', 'id', member.id, 'warns')
    warn_count += 1
    write_value('members', 'id', member.id, 'warns', warn_count)

@client.command()
@commands.check(moderationCommandCheck)
@commands.has_any_role(692952463501819984, 706952785362681906, 714584510523768903, 714676918175137814)
async def kick(ctx, member:discord.Member=None, reason="None", messageid=None, channel:discord.TextChannel=None):
    if not member:
        await ctx.send('Enter a member to kick.')
        return

    author = ctx.author

    #Grabbing next id
    guild = client.get_guild(692906379203313695)

    with open(f'auditcount.json') as json_file:
        auditcount = json.load(json_file)

    auditid = auditcount["count"]
    auditcount["count"] += 1

    with open(f'auditcount.json', 'w') as f:
        json.dump(auditcount, f, indent=2)


    #Building embed
    datetime = str(ctx.message.created_at.utcnow())
    embed = discord.Embed(color=0xf56451, title=f"User Kicked", description=f"Reason: {reason}")
    member_avatar = member.avatar_url_as(static_format='jpg',size=256)
    embed.set_author(name=f"{member.name}#{member.discriminator}", icon_url=member_avatar)
    author_avatar = author.avatar_url_as(static_format='jpg',size=256)
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
    rules = client.get_channel(704925578326966316)
    rule_invite = await rules.create_invite(max_uses=1, reason='Kicked, invited back.')
    rule_invite = str(rule_invite)
    await member.send(f'You were kicked by {author.mention} for: {reason}\n\nHere is a new invite link to join back: {rule_invite}')
    await member.kick(reason=reason)
    embed.add_field(name='Jump Url', value=ctx.message.jump_url)
    audit_log_channel = client.get_channel(723339632145596496)
    await audit_log_channel.send(embed=embed)


    #Saving kick data
    try:
        with open(f'member-audits\{member.id}.json') as json_file:
            audits = json.load(json_file)
        
        with open(f'member-audits\{member.id}.json','w') as f:

            if content == None:
                audits.append({'audit id':auditid, 'action':'kick', 'reason':reason, 'date':datetime, 'jump link':ctx.message.jump_url})
                json.dump(audits, f, indent=2)
            else:
                audits.append({'audit id':auditid, 'action':'kick', 'reason':reason, 'date':datetime, 'jump link':ctx.message.jump_url, 'message content':content})
                json.dump(audits, f, indent=2)
    except: 

        with open(f'member-audits\{member.id}.json','w') as f:
            if content == None:
                json.dump([{'audit id':auditid, 'action':'kick', 'reason':reason, 'date':datetime, 'jump link':ctx.message.jump_url}], f, indent=2)
            else:
                json.dump([{'audit id':auditid, 'action':'kick', 'reason':reason, 'date':datetime, 'jump link':ctx.message.jump_url, 'message content':content}], f, indent=2)

    #Adding to count
    kick_count = read_value('members', 'id', member.id, 'kicks')
    kick_count += 1
    write_value('members', 'id', member.id, 'kicks', kick_count)


@client.command()
@commands.check(moderationCommandCheck)
@commands.has_any_role(692952463501819984, 706952785362681906, 714584510523768903, 714676918175137814)
async def ban(ctx, member:discord.Member=None, reason="None", messageid=None, channel:discord.TextChannel=None):
    if not member:
        await ctx.send('Enter a member to ban.')
        return

    author = ctx.author

    #Grabbing next id
    guild = client.get_guild(692906379203313695)

    with open(f'auditcount.json') as json_file:
        auditcount = json.load(json_file)

    auditid = auditcount["count"]
    auditcount["count"] += 1

    with open(f'auditcount.json', 'w') as f:
        json.dump(auditcount, f, indent=2)


    #Building embed
    datetime = str(ctx.message.created_at.utcnow())
    embed = discord.Embed(color=0xf56451, title=f"User Banned", description=f"Reason: {reason}")
    member_avatar = member.avatar_url_as(static_format='jpg',size=256)
    embed.set_author(name=f"{member.name}#{member.discriminator}", icon_url=member_avatar)
    author_avatar = author.avatar_url_as(static_format='jpg',size=256)
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
    await member.send(f'You were banned by {author.mention} for: {reason}')
    await member.ban(reason=reason)
    embed.add_field(name='Jump Url', value=ctx.message.jump_url)
    audit_log_channel = client.get_channel(723339632145596496)
    await audit_log_channel.send(embed=embed)


    #Saving ban data
    try:
        with open(f'member-audits\{member.id}.json') as json_file:
            audits = json.load(json_file)
        
        with open(f'member-audits\{member.id}.json','w') as f:

            if content == None:
                audits.append({'audit id':auditid, 'action':'ban', 'reason':reason, 'date':datetime, 'jump link':ctx.message.jump_url})
                json.dump(audits, f, indent=2)
            else:
                audits.append({'audit id':auditid, 'action':'ban', 'reason':reason, 'date':datetime, 'jump link':ctx.message.jump_url, 'message content':content})
                json.dump(audits, f, indent=2)
    except: 

        with open(f'member-audits\{member.id}.json','w') as f:
            if content == None:
                json.dump([{'audit id':auditid, 'action':'ban', 'reason':reason, 'date':datetime, 'jump link':ctx.message.jump_url}], f, indent=2)
            else:
                json.dump([{'audit id':auditid, 'action':'ban', 'reason':reason, 'date':datetime, 'jump link':ctx.message.jump_url, 'message content':content}], f, indent=2)

    #Adding to count
    ban_count = read_value('members', 'id', member.id, 'bans')
    ban_count += 1
    write_value('members', 'id', member.id, 'bans', ban_count)

@client.command()
@commands.check(modChannel)
@commands.has_any_role(692952463501819984, 706952785362681906, 714584510523768903, 714676918175137814)
async def unban(ctx, member:int=None, reason="None"):
    if not member:
        await ctx.send('Enter a member to unban.')
        return


    try:
        member = await client.fetch_user(member)
    except:
        await ctx.send('Member not found.')
        return

    author = ctx.author

    #Grabbing next id
    guild = client.get_guild(692906379203313695)

    with open(f'auditcount.json') as json_file:
        auditcount = json.load(json_file)

    auditid = auditcount["count"]
    auditcount["count"] += 1

    with open(f'auditcount.json', 'w') as f:
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
    embed = discord.Embed(color=0xf56451, title=f"User unbanned", description=f"Reason: {reason}")
    member_avatar = member.avatar_url_as(static_format='jpg',size=256)
    embed.set_author(name=f"{member.name}#{member.discriminator}", icon_url=member_avatar)
    author_avatar = author.avatar_url_as(static_format='jpg',size=256)
    embed.set_footer(text=f'By {author.name}#{author.discriminator} • {datetime}', icon_url=author_avatar)
    embed.add_field(name='User ID:', value=member.id, inline=True)
    embed.add_field(name='Audit ID:', value=auditid, inline=True)

    await ctx.send(embed=embed)
    



    #Sending to audit log
    embed.add_field(name='Jump Url', value=ctx.message.jump_url)
    audit_log_channel = client.get_channel(723339632145596496)
    await audit_log_channel.send(embed=embed)


    #Saving unban data
    try:
        with open(f'member-audits\{member.id}.json') as json_file:
            audits = json.load(json_file)
        
        with open(f'member-audits\{member.id}.json','w') as f:
            audits.append({'audit id':auditid, 'action':'unban', 'reason':reason, 'date':datetime, 'jump link':ctx.message.jump_url})
            json.dump(audits, f, indent=2)
    except: 

        with open(f'member-audits\{member.id}.json','w') as f:
            json.dump([{'audit ID':auditid, 'action':'unban', 'reason':reason, 'date':datetime, 'jump link':ctx.message.jump_url}], f, indent=2)


@client.command()
@commands.check(modChannel)
@commands.has_any_role(692952463501819984, 706952785362681906, 714584510523768903, 714676918175137814)
async def history(ctx, member:int=None, page=1):

    if not member:
        await ctx.send('Enter a member id.')
        return

    try:
        member = await client.fetch_user(member)
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
        with open(f'member-audits\{member.id}.json') as json_file:
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
                memberavatar = member.avatar_url_as(static_format='jpg',size=256)
                embed.set_author(name=f'{member.name} (Page: {page}/{pages})', icon_url=memberavatar)
                for cur_audit in pairs:
                    embed.add_field(name=cur_audit, value=pairs[cur_audit])
                await ctx.send(embed=embed)
        except:
            await ctx.send('This member does not have that many pages.')

    except:
        await ctx.send('Member has no audit history.')


@client.command()
@commands.check(modChannel)
@commands.has_any_role(692952463501819984, 706952785362681906, 714584510523768903, 714676918175137814)
async def revoke(ctx, member=None, audit_id=None):
    
    if not member:
        await ctx.send('Enter a member to revoke an audit from.')
        return
    
    if not audit_id:
        await ctx.send('Enter the audit ID that you want to revoke.')
        return

    #Fetching member
    try:
        member = await commands.MemberConverter().convert(ctx, member)
    except:
        try:
            member = int(member)
            member = await client.fetch_user(member)
        except:
            await ctx.send('Member not found.')
            return

    #Verifying audit id
    try:
        audit_id = int(audit_id)
    except:
        await ctx.send('Enter a valid audit ID.')
        return

    revoked = False
    with open(f'member-audits\{member.id}.json') as json_file:
        audits = json.load(json_file)
    
    for audit in audits:
        if audit["audit id"] == audit_id:
            action = audit["action"]
            audits.remove(audit)
            revoked = True
            break
    
    if not revoked:
        await ctx.send('Audit not found.')
        return
    
    with open(f'member-audits\{member.id}.json','w') as f:
            json.dump(audits, f, indent=2)
    

    #Removing from count
    if action == 'warn':
        count = read_value('members', 'id', member.id, 'warns')
        count -= 1
        write_value('members', 'id', member.id, 'warns', count)

    elif action == 'kick':
        count = read_value('members', 'id', member.id, 'kicks')
        count -= 1
        write_value('members', 'id', member.id, 'kicks', count)

    elif action == 'ban':
        count = read_value('members', 'id', member.id, 'bans')
        count -= 1
        write_value('members', 'id', member.id, 'bans', count)

    await ctx.send(f'Audit {audit_id} successfully revoked from {member.name}#{member.discriminator}.')


@client.command()
@commands.check(modChannel)
@commands.has_any_role(692952463501819984, 706952785362681906, 714584510523768903, 714676918175137814)
async def offensecount(ctx, member=None):
    if not member:
        await ctx.send('Enter a member to revoke an audit from.')
        return
    
    #Fetching member
    try:
        member = await commands.MemberConverter().convert(ctx, member)
    except:
        try:
            member = int(member)
            member = await client.fetch_user(member)
        except:
            await ctx.send('Member not found.')
            return
    
    warns = read_value('members', 'id', member.id, 'warns')
    kicks = read_value('members', 'id', member.id, 'kicks')
    bans = read_value('members', 'id', member.id, 'bans')

    await ctx.send(f'{member.name}#{member.discriminator} offense count:\nWarns: {warns}\nKicks: {kicks}\nBans: {bans}')

@client.command()
@commands.check(moderationCommandCheck)
@commands.has_any_role(692952463501819984, 706952785362681906, 714584510523768903, 714676918175137814)
async def purge(ctx, amount=5, channel:discord.TextChannel=None):
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

@client.command()
@commands.check(inGuild)
async def report(ctx, member:discord.Member=None, *, reason="Not Specified"):
    if not member:
        await ctx.send('Enter a member to report')
        return
    author = ctx.author
    if member == author:
        await ctx.send("You can't report yourself.")
        return
    
    member_reportc = read_value('members', 'id', member.id, 'reportc')
    if time.time() < member_reportc:
        await ctx.send('That member has already been reported.')
        return
    
    reportc = int(time.time()) + 7200
    write_value('members', 'id', member.id, 'reportc', reportc)

    with open(f'auditcount.json') as json_file:
        auditcount = json.load(json_file)

    auditid = auditcount["count"]
    auditcount["count"] += 1

    with open(f'auditcount.json', 'w') as f:
        json.dump(auditcount, f, indent=2)

    #Building and sending embed
    embed = discord.Embed(color=0xf56451, title="User Reported", description=f"Reason: {reason}")
    datetime = str(ctx.message.created_at.utcnow())
    member_avatar = member.avatar_url_as(static_format='jpg',size=256)
    embed.set_author(name=f"{member.name}#{member.discriminator}", icon_url=member_avatar)
    author_avatar = author.avatar_url_as(static_format='jpg',size=256)
    embed.set_footer(text=f'By {author.name}#{author.discriminator} • {datetime}', icon_url=author_avatar)
    embed.add_field(name='User ID:', value=member.id, inline=True)
    embed.add_field(name='Audit ID:', value=auditid, inline=True)
    await ctx.send(embed=embed)
    
    embed.add_field(name='Jump Url', value=ctx.message.jump_url)
    report_channel = client.get_channel(723985222412140584)

    guild = client.get_guild(692906379203313695)
    admin = guild.get_role(706952785362681906)
    mod = guild.get_role(714584510523768903)
    trial_mod = guild.get_role(714676918175137814)
    await report_channel.send(content=f"{admin.mention} {mod.mention} {trial_mod.mention}",embed=embed)

@client.command()
@commands.check(reportChannel)
async def close(ctx, member=None):
    if not member:
        await ctx.send("Enter a member to close a report for.")
        return
    
    #Fetching member
    try:
        member = await commands.MemberConverter().convert(ctx, member)
    except:
        try:
            member = int(member)
            member = await client.fetch_user(member)
        except:
            await ctx.send('Member not found.')
            return


    read_reportc = read_value('members', 'id', member.id, 'reportc')
    if read_reportc == 0:
        await ctx.send(f"Report for {member.name}#{member.discriminator} is already closed.")
    elif time.time() < read_reportc:
        write_value('members', 'id', member.id, 'reportc', 0)
        await ctx.send(f"Closed report for {member.name}#{member.discriminator}.")
    elif time.time() > read_reportc:
        write_value('members', 'id', member.id, 'reportc', 0)
        await ctx.send(f"Closed report for {member.name}#{member.discriminator}. (Report was already auto-closed.)")

# Error handlers

@history.error
@unban.error
@revoke.error
@offensecount.error
async def member_not_found_error(ctx, error):
    if isinstance(error, commands.CheckAnyFailure) or isinstance(error, commands.CheckFailure):
        pass
    elif isinstance(error, commands.BadArgument):
        await ctx.send('Member not found.')
    else:
        print(error)

@purge.error
async def channel_not_found_error(ctx, error):
    if isinstance(error, commands.CheckAnyFailure) or isinstance(error, commands.CheckFailure):
        pass
    elif isinstance(error, commands.BadArgument):
        await ctx.send('Channel not found.')
    else:
        print(error)

@warn.error
@kick.error
@ban.error
async def member_or_channel_not_found_error(ctx, error):
    if isinstance(error, commands.CheckAnyFailure) or isinstance(error, commands.CheckFailure):
        pass
    elif isinstance(error, commands.BadArgument):
        await ctx.send('Member (or channel) not found.')
    else:
        print(error)

# Events

@client.event
async def on_message(message):
    if not message.author.bot and message.channel.id == 716720359818133534:
        submissions = client.get_channel(716724583767474317)
        to_file_attachments = []
        for attachment in message.attachments:
            to_file = await attachment.to_file()
            to_file_attachments.append(to_file)

        await submissions.send(f"By {message.author.mention}:")
        await submissions.send(f"{message.content}", files=to_file_attachments)
        await message.delete()
        await message.channel.send(f"{message.author.mention}, your application was successfully submitted.")

    else:
        await client.process_commands(message)
    

client.run("NzIzMjI0MDExMDE3OTQ1MjAy.XuuhLg.pAZTqcpkhZEWaFWZ8-NBSOW8H9g")
