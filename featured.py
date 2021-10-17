import nextcord
from nextcord.ext import commands
import asyncpg
import asyncio
from datetime import datetime
import os
import time
import authinfo
import dbutils
import traceback

client = commands.Bot(command_prefix = '.', intents=nextcord.Intents.all())
client.remove_command('help')

async def is_owner(ctx):

    if ctx.author.id == 322896727071784960: # my own id
        return True
    else:
        await ctx.send("Only the bot owner may use my commands.")
        return False

client.add_check(is_owner)


@client.event
async def on_command_error(ctx, error):

    error = getattr(error, 'original', error)

    if isinstance(error, commands.CommandNotFound) or isinstance(error, commands.CheckFailure):
        return

    elif isinstance(error, commands.InvalidEndOfQuotedStringError) or isinstance(error, commands.UnexpectedQuoteError):
        await ctx.send("Incorrect quote usage.")

    else:
        message = await ctx.send("An error occured while performing this command. This has been automatically reported.")

        error_channel = client.get_channel(740055762956451870)

        error_message = traceback.format_exception(type(error), error, error.__traceback__)
        error_message = "".join(error_message) 
        print(error_message)
        new_message = await error_channel.send(client.myself.mention)
        await new_message.edit(content=f"In {ctx.channel.mention} by {ctx.author.mention}:\n{message.jump_url}\n```{error_message}```")


#TODO commands to veiw guilds and leave guilds

@client.group(invoke_without_command=True)
async def featured(ctx):
    await ctx.send("Incorrect command usage:\n`.featured list/about/remove/invite`")

@featured.command(name="list")
async def featured_list(ctx):
    
    embed = nextcord.Embed(color=0x7ef7ab, title="Featured Servers")

    for guild in client.guilds:
        if guild.id != 692906379203313695: # hierarchy guild id
            embed.add_field(name="\_\_\_\_\_\_\_\_\_\_", value=guild.name, inline=True) # noqa pylint: disable=anomalous-backslash-in-string

    if len(embed.fields) == 0:
        embed = nextcord.Embed(color=0x7ef7ab, title="Featured Servers", description="None")
    
    await ctx.send(embed=embed)


@featured.command()
async def about(ctx, *, name=None):

    if not name:
        await ctx.send("Incorrect command usage:\n`featured about guildname`")
        return
    
    for guild in client.guilds:


        if guild.name == name:


            joined_at = int(guild.me.joined_at.timestamp())

            time_passed = int(datetime.utcnow().timestamp()) - joined_at

            minutes = time_passed // 60


            hours = minutes // 60
            rhours = minutes % 60

            days = hours // 24
            rdays = hours % 24

            weeks = days // 7

            time_passed = f"{weeks}w {rdays}d {rhours}h"

            
            
            embed = nextcord.Embed(color=0x7ef7ab, title=name, description=f"Member Count: {len(guild.members)}\nFeatured For: {time_passed}")
            embed.set_author(name=f"{guild.owner.name}#{guild.owner.discriminator}", icon_url=guild.owner.avatar.with_format('jpg').url)
            embed.set_thumbnail(url=guild.icon_url_as(static_format='jpg'))
            await ctx.send(embed=embed)
            return

    
    await ctx.send("Guild not found.")

@featured.command()
@commands.max_concurrency(1, per=commands.BucketType.channel)
async def remove(ctx, *, name=None):

    if not name:
        await ctx.send("Incorrect command usage:\n`featured about guildname`")
        return

    for guild in client.guilds:

        if guild.name == name:
            
            await ctx.send(f"Are you sure you want to remove **{guild.name}** from the featured server list? Respond with `y` or `yes` to proceed.")

            try:
                response = await client.wait_for('message', check=lambda m: m.author == ctx.author and m.channel == ctx.channel, timeout=20)
            except asyncio.TimeoutError:
                await ctx.send("Remove timed out.")

            response = response.content.lower()

            if response == 'yes' or response == 'y':
                await guild.leave()
                await ctx.send(f"Successfully left **{guild.name}**")

                
            else:
                await ctx.send("Remove cancelled.")

            return
            
            
    
    await ctx.send("Guild not found.")

@featured.command()
async def invite(ctx):

    await ctx.send("https://discord.com/api/oauth2/authorize?client_id=745412179536379915&permissions=0&scope=bot")


@client.event
async def on_ready():
    print(f"Logged in as {client.user}.\nID: {client.user.id}")
    await client.change_presence(status=nextcord.Status.online, activity=nextcord.Game(name='with money'))

    guild = client.get_guild(692906379203313695)
    client.myself = guild.get_member(322896727071784960)

@client.event
async def on_member_join(member):

    if member.guild.id == 692906379203313695: # hierarchy guild id
        return
    
    async with client.pool.acquire() as db:

        userids = await db.fetch(f'SELECT userid FROM featured.g_{member.guild.id};')

        userids = list(map(lambda user: user[0], userids))

        if member.id not in userids:

            for task in asyncio.all_tasks():
                if task.get_name() == f'timer {member.id}':
                    return
            
            asyncio.create_task(timer_money(member), name=f'timer {member.guild.id} {member.id}')

@client.event
async def on_member_remove(member):

    if member.guild.id == 692906379203313695: # hierarchy guild id
        return

    for task in asyncio.all_tasks():
        if task.get_name() == f'timer {member.guild.id} {member.id}':
            task.cancel()
            break

async def timer_money(member):

        await asyncio.sleep(300) # five minutes
        
        member = member.guild.get_member(member.id) # check if they are still in server
        if not member:
            return

        else:
            
            async with client.pool.acquire() as db:

                money = await db.get_member_val(member.id, 'money')
                
                if not money: return

                money += 100
                await db.set_member_val(member.id, 'money', money)

                try:
                    await member.send(f'You have been in **{member.guild.name}** for five minutes and have recieved your prize of $100!')
                except:
                    pass
                
                await db.execute(f'INSERT INTO featured.g_{member.guild.id} (userid) VALUES ($1);', member.id)

@client.event
async def on_guild_join(guild):
    
    async with client.pool.acquire() as db:
        await db.execute(f'CREATE TABLE IF NOT EXISTS featured.g_{guild.id} (userid BIGINT PRIMARY KEY);')


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


client.run(os.environ.get('featured'))