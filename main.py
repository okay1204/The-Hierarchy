import discord
from discord.ext import commands, tasks
import random
import json
import time
import datetime
import asyncio
import sqlite3
import os
from sqlite3 import Error
from utils import *
import bottokens



client = commands.Bot(command_prefix = '.')
client.remove_command('help')


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
    heisttimer.start()
    await leaderboard(client)
    

@tasks.loop(seconds=1)
async def heisttimer():
    heist = open_json()
    if heist["heistt"] > 0:
        heist["heistt"] -= 1
        write_json(heist)
        if heist["heistt"] == 0:
            channel = client.get_channel(heist["heistl"])
            if len(heist["heistp"]) < 3:
                heist["heistl"] = 0
                heist["oheist"] = "False"
                heist["heistp"] = []
                heist["heistv"] = 0
                write_json(heist)
                await channel.send("Heist cancelled: Not enough people joined.")
            else:
                guild = client.get_guild(692906379203313695)
                total = 0
                for userid in heist["heistp"]:
                    heistamount = random.randint(40,50)
                    write_value('members', 'id', userid, 'heistamount', heistamount)
                    total += heistamount
                    
                while read_value('members', 'id', heist['heistv'], 'bank') < total:
                    total2 = 0
                    for userid2 in heist["heistp"]:
                        heistamount = read_value('members', 'id', userid2, 'heistamount')
                        heistamount -= 1
                        total2 += heistamount
                        write_value('members', 'id', userid2, 'heistamount', heistamount)
                        total = total2
                            
                embed = discord.Embed(color=0xed1f1f)
                embed.set_author(name="Heist results")
                for userid in heist["heistp"]:
                    if random.randint(1,4) == 1:
                        gotaway = False
                        for item in in_use(userid):
                            if item["name"] == "gun":
                                if random.randint(1,2) == 1:
                                    embed.add_field(name=f'{guild.get_member(userid).name}', value=f'Caught, got away with their gun.', inline=True)
                                    gotaway = True
                        if gotaway == False:
                            embed.add_field(name=f'{guild.get_member(userid).name}', value=f'Caught, jailed for 3h.', inline=True)
                            jailtime = int(time.time()) + 10800
                            write_value('members', 'id', userid, 'jailtime', jailtime)
                        await rolecheck(client, userid)
                    else:
                        heistamount = read_value("members", "id", userid, "heistamount")
                        embed.add_field(name=f'{guild.get_member(userid).name}', value=f'Got away with ${heistamount}.')
                        money = read_value("members", "id", userid, "money")
                        money += heistamount
                        write_value("members", "id", userid, "money", money)
                        update_total(userid)
                        bank = read_value("members", "id", heist["heistv"], "bank")
                        bank -= heistamount
                        write_value("members", "id", heist["heistv"], "bank", bank)
                        update_total(heist["heistv"])

                await rolecheck(client, heist["heistv"])

                channel = client.get_channel(heist["heistl"])
                await channel.send(embed=embed)
                heist["heistv"] = "None"
                heist["heistt"] = 0
                heist["heistp"] = []
                heist["heistl"] = "None"
                heist["oheist"] = "False"
                write_json(heist)
                conn = sqlite3.connect('hierarchy.db')
                c = conn.cursor()
                c.execute(f"UPDATE heist SET cooldown = {int(time.time())+9000}")
                conn.commit()
                conn.close()
                await leaderboard(client)


    
        
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
    try:
        if message.channel.category == client.get_channel(692949972764590160):
            if message.content.lower().startswith('pls'):
                helpchannel = client.get_channel(692950528417595453)
                await message.channel.send(f"Hey, this server isn't ran by Dank Memer, it's a custom bot! Check {helpchannel.mention} for a list of commands.")
    except:
        pass
    
    if message.channel.id == 723644542275813386: # private system
        boost_channel=client.get_channel(723645417253896234)
        await boost_channel.send(f'HUGE Thank you to {message.author.mention} for boosting the server, we greatly appreciate it! Enjoy the premium perks!')
        write_value('members', 'id', message.author.id, 'premium', '"True"')
        write_value('members', 'id', message.author.id, 'boosts', '3')
    
    if message.channel.id == 730584224305774602: #bot comms
        if message.content.startswith('main : '):
            command = message.content
            command = command.replace('main : ', '')
            command = command.split(' | ')

            green = discord.Color(0x42f57b)
            red = discord.Color(0xff5254)
            statuschannel = client.get_channel(698384786460246147)
            statusmessage = await statuschannel.fetch_message(698775210173923429)
            for x in statusmessage.embeds:
                if x.color == green:
                    await message.add_reaction('✅')
                elif x.color == red:
                    await message.add_reaction('❌')
                    return
            
            guild = client.get_guild(692906379203313695)
            if command[0] == 'tutorial':
                await asyncio.sleep(30)
                
                #checking if member is still in server
                try:
                    member = guild.get_member(int(command[1]))
                except:
                    return
                
                await member.send('*This is the only automated DM you will ever recieve*\n\nHey, you look new to the server! If you want, feel free to DM me `tutorial` and I\'ll walk you through the basics!')

    # DM check
    if not message.guild:
        if message.content.lower() == "tutorial":
            for task in asyncio.all_tasks():
                if str(task.get_name()) == f"tutorial {message.author.id}":
                    await message.channel.send('You already have a tutorial in progress.')
                    return
            asyncio.create_task(tutorial(message), name=f"tutorial {message.author.id}")

        
        if message.content.lower() == "cancel":
            for task in asyncio.all_tasks():
                if str(task.get_name()) == f"tutorial {message.author.id}":
                    await message.channel.send('Cancelled tutorial.')
                    task.cancel()
                    return
        

    await client.process_commands(message)

async def tutorial(message):

    dmchannel = message.channel
    category = client.get_channel(692949972764590160)
    channels = category.text_channels

    async def channel_check(channel):
        special_channels = [706953015415930941, 714585657808257095, 723945572708384768]
        if channel.id in special_channels:
            return False
        else:
            async for msg in channel.history(limit=1):
                secondspast = int(datetime.datetime.utcnow().timestamp()-msg.created_at.timestamp())
            if secondspast <= 60:
                return False
            else:
                return True
                
    acceptedChannels = []
    for channel in channels:
        check = await channel_check(channel)
        if check:
            acceptedChannels.append(channel)

    if len(acceptedChannels) == 0:
        await dmchannel.send('All bot command channels are busy right now, sorry! Try again later.')
        return
    
    channel = random.choice(acceptedChannels)
    await dmchannel.send(f"Tutorial started! You may cancel it by DMing me `cancel` at any time. Please head on over to {channel.mention}.")
    
    guild = client.get_guild(692906379203313695)
    author = guild.get_member(message.author.id)

    async with channel.typing():
        await asyncio.sleep(5)
    
    await channel.send(f"Welcome to The Hierarchy, {author.mention}! This is a game of collecting as much money as you can.")

    async with channel.typing():
        await asyncio.sleep(5)
    


    for role in author.roles:
        if role.id == 692952611141451787:
            guild_role = guild.get_role(692952611141451787) # Poor
            break
        elif role.id == 692952792016355369:
            guild_role = guild.get_role(692952792016355369) # Middle
            break
        elif role.id == 692952919947083788:
            guild_role = guild.get_role(692952919947083788) # Rich
            break

    rolemessage = await channel.send('_ _')
    await rolemessage.edit(content=f"First off, let's talk about your role. You currently have the {guild_role.mention} role. This role signifies how rich you are compared to the average amount of money in the server.")

    async with channel.typing():
        await asyncio.sleep(10)

    await channel.send("Let's get you started with the basics.")

    client_member = guild.get_member(client.user.id)

    async with channel.typing():
        await asyncio.sleep(3)

    if read_value('members', 'id', author.id, 'workc') < time.time() and read_value('members', 'id', author.id, 'jailtime') < time.time():        
        canWork = True

    elif read_value('members', 'id', author.id, 'workc') >= time.time():
        await channel.send("Hm.. you already seem to have used the `.work` command. Since you already know about it, let's move on then.")
        canWork = False
    else:
        await channel.send("Well, it looks like you're in jail. It looks like we will have to skip majority of the tutorial.")
        canWork = False

    
    if canWork: 

        await channel.send("Start off by typing `.work`. Be ready though, there will be some minigames coming your way.")

        while True:
            try:
                message = await client.wait_for('message', check=lambda x: x.author == author and x.guild == guild, timeout=60)
            except asyncio.TimeoutError:
                await channel.send("Tutorial cancelled due to inactivity.")
                return
            if message.content == '.work' or message.content.startswith('.work '):
                channel = message.channel
                break

        while True:
            try:
                message = await client.wait_for('message', check=lambda x: x.author == client_member and x.channel == channel, timeout=60)
            except asyncio.TimeoutError:
                await channel.send("Hmm... something went wrong. Please start the tutorial again.")
                return
            if 'worked and' in message.content:
                break

    async with channel.typing():
        await asyncio.sleep(5)
    
    await channel.send("You can check your balance with `.balance`. Try that now.")

    while True:
        try:
            message = await client.wait_for('message', check=lambda x: x.author == author and x.guild == guild, timeout=60)
        except asyncio.TimeoutError:
            await channel.send("Tutorial cancelled due to inactivity.")
            return
        if message.content == '.bal' or message.content == '.balance':
            channel = message.channel
            break

    async with channel.typing():
        await asyncio.sleep(3)

    await channel.send("Next, let's steal from someone!")

    async with channel.typing():
        await asyncio.sleep(3)

    if read_value('members', 'id', author.id, 'stealc') < time.time() and read_value('members', 'id', author.id, 'jailtime') < time.time():        
        canSteal = True

    elif read_value('members', 'id', author.id, 'stealc') >= time.time():
        await channel.send("Hm.. you already seem to have used the `.steal` command. Since you already know about it, let's move on then.")
        canSteal = False
    else:
        await channel.send("Well, it looks like you're in jail. Perhaps you already tried to steal from someone and got jailed already?")
        canSteal = False

    if canSteal:
        await channel.send("First, we will have to see who is in your place range. To do this, use `.around`.")
        while True:
            try:
                message = await client.wait_for('message', check=lambda x: x.author == author and x.guild == guild, timeout=60)
            except asyncio.TimeoutError:
                await channel.send("Tutorial cancelled due to inactivity.")
                return
            if message.content == '.around' or message.content.startswith('.around '):
                channel = message.channel
                break
        
        async with channel.typing():
            await asyncio.sleep(8)

        image = discord.File('stealinfo.png')
        await channel.send("When stealing, you can only steal from those that are up to 3 places above you or up to 3 places below you. Refer to this diagram:", file=image)
        
        async with channel.typing():
            await asyncio.sleep(15)


        aroundbug = discord.File('aroundbug.png')
        await channel.send("**If this is what you saw when you did `.around`, it is a common mobile bug. Try using `.aroundm` instead.**", file=aroundbug)

        async with channel.typing():
            await asyncio.sleep(12)

        await channel.send("Now, let's try it out!")

        async with channel.typing():
            await asyncio.sleep(3)

        #Quick checks to make sure they didn't spoof the system
        spoofed = False
        if read_value('members', 'id', author.id, 'stealc') >= time.time():
            await channel.send("You already used `.steal`... what a shame.")
            spoofed = True
        elif read_value('members', 'id', author.id, 'jailtime') >= time.time():
            await channel.send("Well, it looks like you're in jail. Perhaps you already tried to steal from someone and got jailed already?")
            spoofed = True
        
        if not spoofed:
            await channel.send(f"Use `.steal @mention amount` to steal from someone. Make sure you replace `@mention` with the member you want to steal from, and `amount` with the amount you want to steal.\n\n***Wait!*** When you choose an amount to steal, you may choose a number from 1-200 (as long as the person you are stealing from has enough cash). However, the more you try to steal, the higher chance you have of being jailed.\n\nAn example of this command is:\n.steal {client_member.mention} 100\n\nTry out this command now.")
            breakOut = False
            while True:
                try:
                    message = await client.wait_for('message', check=lambda x: x.author == author and x.guild == guild, timeout=120)
                except asyncio.TimeoutError:
                    await channel.send("Tutorial cancelled due to inactivity.")
                    return
                if message.content.startswith('.steal '):
                    channel = message.channel
                    while True:
                        try:
                            message = await client.wait_for('message', check=lambda x: x.author == client_member and x.channel == channel, timeout=60)
                        except asyncio.TimeoutError:
                            await channel.send("Hmm... something went wrong. Please start the tutorial again.")
                            return
                        if author.name in message.content:
                            breakOut = True
                        break

                if breakOut:
                    break
        
    async with channel.typing():
        await asyncio.sleep(5)

    commands = client.get_channel(692950528417595453)
    game_info = client.get_channel(706643007646203975)
    await channel.send(f"And that's about it! Of course, these are only the basics to get you started. However, there is a shop, fee collection, banking system, and so much more! Feel free to explore these on your own. Looking through {commands.mention} and {game_info.mention} will help you a lot.\n\n*Please consider boosting the server, it will also grant you some premium features such as boosting time!*")

    async with channel.typing():
        await asyncio.sleep(15)

    await channel.send("Have fun, and good luck!")
        

        


client.load_extension('debug')        
client.load_extension('info')
client.load_extension('games')
client.load_extension('actions')
client.load_extension('gambling')
client.load_extension('misc')


client.run(os.environ.get("main"))
