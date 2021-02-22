# pylint: disable=unused-wildcard-import

import discord
from discord.ext import commands, tasks
from discord.ext.commands import BadArgument, CommandNotFound, MaxConcurrencyReached, CheckFailure, ExpectedClosingQuoteError, UnexpectedQuoteError
import random
import json
import time
import datetime
import asyncio
import asyncpg
import os
import difflib
import traceback
import asyncio
import string
from captcha.image import ImageCaptcha
import asyncpraw


from utils import *
import authinfo

import dbutils



async def do_captcha(ctx):

                   
    if ctx.author.id not in client.making_captchas:

        client.making_captchas.append(ctx.author.id)


        # generate random word
        word = ""
        for x in range(3): word += random.choice(string.ascii_lowercase) # noqa pylint: disable=unused-variable


        # generate captcha image
        image = ImageCaptcha()
        image.generate(word)
        image.write(word, f"./storage/images/captchas/{word}.png")

        # making embed
        embed = discord.Embed(title="Captcha Required", description="Please answer this captcha to prove this is you.\n(There are only lowercase letters)", color=0x15a7c2)
        embed.set_image(url="attachment://captcha.png")

        # prompt user
        captcha = await ctx.send(embed=embed, file=discord.File(f'./storage/images/captchas/{word}.png', filename="captcha.png"))

        os.remove(f"./storage/images/captchas/{word}.png")

        try:
            response = await client.wait_for('message', check = lambda message: message.author == ctx.author and message.channel == ctx.channel, timeout=30)
        except asyncio.TimeoutError:
            embed = discord.Embed(color=0xed373a, title="❌ Captcha Timed Out", description="No response was given in the last 30 seconds.")
            embed.set_image(url="attachment://captcha.png")
            await captcha.edit(embed=embed)

            client.making_captchas.remove(ctx.author.id)
            return False
        

        # decide fate
        response = response.content.lower().replace(' ', '')

        if response == word:
            embed = discord.Embed(color=0x4fed4a, title="✅ Captcha Complete", description="Your command will be run in a moment.")
            embed.set_image(url="attachment://captcha.png")
            await captcha.edit(embed=embed)
            await asyncio.sleep(1.5)

            client.making_captchas.remove(ctx.author.id)
            return True
        else:
            embed = discord.Embed(color=0xed373a, title="❌ Captcha Failed", description="Run another command to try again.")
            embed.set_image(url="attachment://captcha.png")
            await captcha.edit(embed=embed)

            client.making_captchas.remove(ctx.author.id)
            return False


    else:
        return False

    


async def macro_check(ctx):

    userid = str(ctx.author.id)
    
    if str(userid) not in client.history:
        
        client.history[userid] = {"last": [ctx.command.name], "time": int(time.time()+random.randint(1800, 3600)), "useCount": 1, "useMax": random.randint(10,15), "diffMax": random.randint(2,3), "captcha": False}
    
    else:
        if client.history[userid]["captcha"]:

            if await do_captcha(ctx):
                client.history[userid] = {"last": [ctx.command.name], "time": int(time.time()+random.randint(1800, 3600)), "useCount": 1, "useMax": random.randint(10,15),"diffMax": random.randint(2,3), "captcha": False}
            else:
                return False

        elif client.history[userid]["time"] <= time.time():
            client.history[userid] = {"last": [ctx.command.name], "time": int(time.time()+random.randint(1800, 3600)), "useCount": 1, "useMax": random.randint(10,15),"diffMax": random.randint(2,3), "captcha": False}


        elif ctx.command.name in client.history[userid]["last"]:
            client.history[userid]["useCount"] += 1

            if client.history[userid]["useCount"] >= client.history[userid]["useMax"]:
                client.history[userid]["captcha"] = True
                
                if await do_captcha(ctx):
                    client.history[userid] = {"last": [ctx.command.name], "time": int(time.time()+random.randint(1800, 3600)), "useCount": 1, "useMax": random.randint(10,15),"diffMax": random.randint(2,3), "captcha": False}
                else:
                    return False
        
        else:
            client.history[userid]["last"].append(ctx.command.name)

            if len(client.history[userid]["last"]) - 1 >= client.history[userid]["diffMax"]:
                client.history[userid] = {"last": [ctx.command.name], "time": int(time.time()+random.randint(1800, 3600)), "useCount": 1, "useMax": random.randint(10,15),"diffMax": random.randint(2,3), "captcha": False}
        


    return True



client = commands.Bot(command_prefix = '.', intents=discord.Intents.all())
client.remove_command('help')

client.add_check(lambda ctx: not ctx.author.bot)
client.add_check(macro_check)
client.add_check(lambda ctx: ctx.guild)

@client.event
async def on_command_error(ctx, error):

    error = getattr(error, 'original', error)


    if isinstance(error, CommandNotFound):

        if ctx.message.content.startswith('..') or not ctx.guild:
            return
        
        try:
            if ctx.channel.category.id != client.rightCategory:
                return
        except:
            pass

        allowed_cogs = ['actions', 'fun', 'gangs', 'gambling', 'games', 'info', 'premium', 'jobs', 'leveling']

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

    elif isinstance(error, ExpectedClosingQuoteError) or isinstance(error, UnexpectedQuoteError):
        await ctx.send("Invalid quote usage.")
    
    elif isinstance(error, MaxConcurrencyReached):
        return

    elif isinstance(error, CheckFailure):
        return

    else:
        message = await ctx.send("An error occured while performing this command. This has been automatically reported.")

        error_channel = client.get_channel(740055762956451870)

        error_message = traceback.format_exception(type(error), error, error.__traceback__)
        error_message = "".join(error_message) 
        print(error_message)
        new_message = await error_channel.send(client.myself.mention)
        await new_message.edit(content=f"In {ctx.channel.mention} by {ctx.author.mention}:\n{message.jump_url}\n```{error_message}```")

@client.event
async def on_ready():

    print(f"Logged in as {client.user}.\nID: {client.user.id}")

    client.history = {}
    client.making_captchas = []
    
    client.last_messages = {}


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

    cogs = list(map(lambda filename: filename.replace('.py', ''), [f for f in os.listdir('./cogs') if os.path.isfile(os.path.join('./cogs', f))]))

    for cog in cogs:
        client.load_extension(f'cogs.{cog}')

    commands = set(client.walk_commands())
    aliases = []
    for command in commands:
        aliases.extend(command.aliases)
    
    
    commands = list(map(lambda command: command.name, commands))
    commands.extend(aliases)
    client.every_command = commands
    client.every_command.append('featured')

    # for production
    
    cogs_to_unload = ['events', 'invites', 'halloween', 'christmas', 'birthday']

    # cogs to ungload for development
    
    cogs_to_unload = [
    'debug', 'actions', 'games', 'gambling', 
    'misc', 'premium', 'tutorial', 'heist', 
    'members', 'info', 'polls', 'admin', 
    'reactions', 'timers', 'events', 'invites', 'leveling', 
    'jobs', 'voice_channels', 'alerts', 'halloween',
    'christmas', 'gangs']

    
    # all cogs

    # cogs_to_unload = [
    # 'debug', 'actions', 'games', 'gambling', 
    # 'misc', 'premium', 'tutorial', 'heist', 
    # 'members', 'fun', 'info', 'polls', 'admin', 
    # 'reactions', 'timers', 'events', 'invites', 'leveling', 
    # 'jobs', 'voice_channels', 'alerts', 'halloween',
    # 'christmas', 'gangs', 'birthday']


    for cog in cogs_to_unload:
        client.unload_extension(f'cogs.{cog}')

    async with client.pool.acquire() as db:
        await db.leaderboard()

    
    # waiting for reddit connection to finish
    client.reddit = asyncpraw.Reddit(
        client_id = os.environ.get("reddit_client_id"),
        client_secret = os.environ.get("reddit_client_secret"),
        password = os.environ.get("reddit_password"),
        username = os.environ.get("reddit_username"),
        user_agent = os.environ.get("reddit_user_agent")
    )
    print("Reddit Connection Successful")
    

client.adminChannel = 706953015415930941
client.partnershipChannel = 723945572708384768
client.rightCategory = 692949972764590160
client.heist = {}


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
async def uncache(ctx, name=None):

    if not name:
        await ctx.send("Incorrect command usage:\n`.uncache commandname`")
        return

    try:
        client.every_command.append(name)
    except:
        return await ctx.send("This command is not cached.")

    await ctx.send("Successfully removed command from cache.")


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
                client.reload_extension(f'cogs.{filename}')

        await ctx.send("All cogs succesfully reloaded.")


loop = asyncio.get_event_loop()

async def connection_init(conn):
    await conn.execute("SET CLIENT_ENCODING to 'utf-8';")
    conn.client = client

try:
    client.pool = loop.run_until_complete(asyncpg.create_pool(
        host=os.environ.get("postgres_host"),
        database=os.environ.get("postgres_database"),
        user=os.environ.get("postgres_user"),
        password=os.environ.get("postgres_password"),
        connection_class=dbutils.DBUtils,
        init=connection_init
    ))

    print('PostgreSQL connection successful')
except Exception as e:
    print(e)

    # the bot basically cannot function without database
    print('PostgreSQL connection failed- aborting')
    exit()

client.run(os.environ.get("main"))