# pylint: disable=unused-wildcard-import

import discord
from discord.ext import commands, tasks
from discord.ext.commands import BadArgument, CommandNotFound, MaxConcurrencyReached, CheckFailure
import random
import json
import time
import datetime
import asyncio
import sqlite3
import os
import difflib
import traceback
from sqlite3 import Error


from utils import *
import bottoken



client = commands.Bot(command_prefix = '.')
client.remove_command('help')

@client.event
async def on_command_error(ctx, error):

    error = getattr(error, 'original', error)


    if isinstance(error, CommandNotFound):

        allowed_cogs = ['actions', 'fun', 'gambling', 'games', 'info', 'premium']

        command_string = ctx.message.content.split()[0]
        command_string = command_string.replace('.', '')
        if command_string in client.every_command:
            return

        enabled_commands = client.commands
        enabled_commands = list(filter(lambda command: command.cog and command.cog_name in allowed_cogs, enabled_commands))
        command_names = list(map(lambda command: command.name, enabled_commands))
        
        command_aliases = list(map(lambda command: command.aliases, enabled_commands))
        all_aliases = []
        for command_alias in command_aliases:
            all_aliases.extend(command_alias)


        command_names.extend(all_aliases)

        content = ctx.message.content.split()[0]
        content = content.replace('.', '')
        close = difflib.get_close_matches(content, command_names)


        if len(close) == 0:
            await ctx.send(f"Command not found.\nSee {client.commandsChannel.mention} for a list of commands.")
        else:

            close = list(map(lambda command: f"`{command}`", close))

            text = '\n'.join(close)
            await ctx.send(f"Command not found. Did you mean:\n{text}")

    
    elif isinstance(error, BadArgument):
        if ctx.command.cog_name == "admin":
            
            if len(ctx.args) == 2:
                await ctx.send("Member not found.")

            else:
                await ctx.send("Channel not found.")
            
        else:
            await ctx.send("Member not found.")
    
    elif isinstance(error, MaxConcurrencyReached):
        return

    elif isinstance(error, CheckFailure):
        return

    else:
        message = await ctx.send("An error occured while performing this command. This has been automatically reported.")

        error_channel = client.get_channel(740055762956451870)

        error_message = traceback.format_exception(type(error), error, error.__traceback__)
        error_message = "".join(error_message) 
        new_message = await error_channel.send(client.myself.mention)
        await new_message.edit(content=f"In {ctx.channel.mention} by {ctx.author.mention}:\n{message.jump_url}\n```{error_message}```")


        raise error


@client.event
async def on_ready():
    print(f"Logged in as {client.user}.\nID: {client.user.id}")


    statuschannel = client.get_channel(698384786460246147)
    statusmessage = await statuschannel.fetch_message(698775210173923429)


    green = discord.Color(0x42f57b)
    red = discord.Color(0xff5254)

    for x in statusmessage.embeds:
        if x.color == green:
            await client.change_presence(status=discord.Status.online, activity=discord.Game(name='with money'))
        elif x.color == red:
            await client.change_presence(status=discord.Status.dnd, activity=discord.Game(name='UNDER DEVELOPMENT'))


    client.bailprice = lambda number: int(int(number-time.time())/3600*40)
    client.leaderboardChannel = client.get_channel(692955859109806180)
    client.leaderboardMessage = await client.leaderboardChannel.fetch_message(698775209024552975)
    client.commandsChannel = client.get_channel(692950528417595453)
    client.gameInfoChannel = client.get_channel(706643007646203975)
    client.membercountchannel = client.get_channel(719716526101364778)
    client.mainGuild = client.get_guild(692906379203313695)
    client.welcomeChannel = client.get_channel(692956542437425153)

    client.myself = client.mainGuild.get_member(322896727071784960)


    cogs = ['debug', 'info', 'games', 'actions', 'gambling', 'misc', 'premium', 'tutorial', 'heist', 'members', 'fun', 'polls', 'admin', 'reactions', 'timers', 'events']
    for cog in cogs:
        client.load_extension(f'cogs.{cog}')

    commands = set(client.walk_commands())
    aliases = []
    for command in commands:
        aliases.extend(command.aliases)
    
    
    commands = list(map(lambda command: command.name, commands))
    commands.extend(aliases)
    client.every_command = commands
    

    cogs_to_unload = ['debug', 'info', 'games', 'actions', 'gambling', 'misc', 'premium', 'tutorial', 'heist', 'members', 'polls', 'admin', 'reactions', 'timers', 'events']
    for cog in cogs_to_unload:
        client.unload_extension(f'cogs.{cog}')


    # TODO: add all the cogs back afterward
    
    await leaderboard(client)

client.adminChannel = 706953015415930941
client.partnershipChannel = 723945572708384768
client.rightCategory = 692949972764590160
    
        
@client.event
async def on_member_join(member):
    await asyncio.sleep(0.1)
    await leaderboard(client)

@client.event
async def on_member_remove(member):
    await asyncio.sleep(0.1)
    await leaderboard(client)

@client.event
async def on_message(message):    
    
    if type(message.channel) != discord.channel.DMChannel:
        if message.channel.category.id == client.rightCategory:
            if message.content.lower().startswith('pls '):
                await message.channel.send(f"Hey, this server isn't ran by Dank Memer, it's a custom bot! Check {client.commandsChannel.mention} for a list of commands.")
    

    await client.process_commands(message)


def adminCheck(ctx):
    return ctx.channel.id == client.adminChannel


@client.command()
@commands.check(adminCheck)
async def refresh(ctx):

    files = [f for f in os.listdir('./cogs') if os.path.isfile(os.path.join('./cogs', f))]
    files = list(map(lambda filename: filename.replace('.py', ''), files))

    current_cogs = list(client.extensions)
    current_cogs = list(map(lambda cog: cog.replace('cogs.', ''), current_cogs))

    disabled_cogs = []

    for cog in current_cogs:
        if cog not in files:
            disabled_cogs.append(cog)
            client.load_extension(f'cogs.{cog}')

        commands = set(client.walk_commands())
        aliases = []
        for command in commands:
            aliases.extend(command.aliases)
        
        
        commands = list(map(lambda command: command.name, commands))
        commands.extend(aliases)
        client.every_command = commands

    for cog in disabled_cogs:
        client.unload_extension(f'cogs.{cog}')
    
    await ctx.send("Refreshed and added all existing commands to cache.")

@client.command()
@commands.check(adminCheck)
async def cache(ctx, name=None):

    if not name:
        await ctx.send("Incorrect command usage:\n`.cache commandname`")
        return

    client.every_command.append(name)
    await ctx.send("Successfully added command to cache.")


@client.command()
@commands.check(adminCheck)
async def cogs(ctx):

    files = [f for f in os.listdir('./cogs') if os.path.isfile(os.path.join('./cogs', f))]

    current_cogs = list(client.extensions)
    current_cogs = list(map(lambda cog: cog.replace('cogs.', ''), current_cogs))

    cogs = []
    for filename in files:
        filename = filename.replace('.py', '')
        if filename in current_cogs:
            state = ': Enabled'
        else:
            state = ': Disabled'
        
        filename += state
        cogs.append(filename)


    cogs = "\n".join(cogs)
    await ctx.send(f"```{cogs}```")


@client.command()
@commands.check(adminCheck)
async def enable(ctx, name=None):

    if not name:
        await ctx.send("Incorrect command usage:\n`.enable cogname`")
        return

    name = name.lower()

    current_cogs = list(client.extensions)
    current_cogs = list(map(lambda cog: cog.replace('cogs.', ''), current_cogs))

    if name != "all":

        if name in current_cogs:
            await ctx.send("This cog is already enabled.")
            return
        
        files = [f for f in os.listdir('./cogs') if os.path.isfile(os.path.join('./cogs', f))]
        files = list(map(lambda filename: filename.replace('.py', ''), files))

        if name not in files:
            await ctx.send("This cog does not exist.")
            return
        
        else:
            client.load_extension(f'cogs.{name}')
            await ctx.send(f"Cog `{name}` successfully enabled.")

    else:

        files = [f for f in os.listdir('./cogs') if os.path.isfile(os.path.join('./cogs', f))]
        files = list(map(lambda filename: filename.replace('.py', ''), files))

        for filename in files:
            if filename not in current_cogs:
                client.load_extension(f'cogs.{filename}')

        await ctx.send("All cogs successfully enabled.")

    
@client.command()
@commands.check(adminCheck)
async def disable(ctx, name=None):

    if not name:
        await ctx.send("Incorrect command usage:\n`.disable cogname`")
        return

    name = name.lower()

    if name != "all":

        files = [f for f in os.listdir('./cogs') if os.path.isfile(os.path.join('./cogs', f))]
        files = list(map(lambda filename: filename.replace('.py', ''), files))

        if name not in files:
            await ctx.send("This cog does not exist.")
            return

        current_cogs = list(client.extensions)
        current_cogs = list(map(lambda cog: cog.replace('cogs.', ''), current_cogs))

        if name not in current_cogs:
            await ctx.send("This cog is already disabled.")
            return
        
        else:
            client.unload_extension(f'cogs.{name}')
            await ctx.send(f"Cog `{name}` successfully disabled.")

    
    else:

        files = [f for f in os.listdir('./cogs') if os.path.isfile(os.path.join('./cogs', f))]
        files = list(map(lambda filename: filename.replace('.py', ''), files))

        current_cogs = list(client.extensions)
        current_cogs = list(map(lambda cog: cog.replace('cogs.', ''), current_cogs))

        for filename in files:
            if filename in current_cogs:
                client.unload_extension(f'cogs.{filename}')

        await ctx.send("All cogs successfully disabled.")


@client.command()
@commands.check(adminCheck)
async def reload(ctx, name=None):

    if not name:
        await ctx.send("Incorrect command usage:\n`.reload cogname`")
        return

    name = name.lower()

    files = [f for f in os.listdir('./cogs') if os.path.isfile(os.path.join('./cogs', f))]
    files = list(map(lambda filename: filename.replace('.py', ''), files))

    if name != "all":

        if name not in files:
            await ctx.send("This cog does not exist.")
            return

        current_cogs = list(client.extensions)
        current_cogs = list(map(lambda cog: cog.replace('cogs.', ''), current_cogs))

        if name in current_cogs:
            client.unload_extension(f'cogs.{name}')

        
        client.load_extension(f'cogs.{name}')
        await ctx.send(f"Cog `{name}` successfully reloaded.")

    else:

        current_cogs = list(client.extensions)
        current_cogs = list(map(lambda cog: cog.replace('cogs.', ''), current_cogs))

        for filename in files:
            if filename in current_cogs:
                client.unload_extension(f'cogs.{filename}')
                client.load_extension(f'cogs.{filename}')

        await ctx.send("All cogs succesfully reloaded.")





client.run(os.environ.get("main"))
