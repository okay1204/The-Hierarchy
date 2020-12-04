# pylint: disable=import-error

import discord
from discord.ext import commands
import sqlite3
import random
import time
import asyncio

import os
# To import from different path
import sys
sys.path.insert(1 , os.getcwd())

from utils import (log_command, splittime, bot_check)


def get_halloween_value(userid, value):

    conn = sqlite3.connect('./storage/databases/hierarchy.db')
    c = conn.cursor()

    c.execute(f"SELECT {value} FROM halloween WHERE id = ?", (userid,))
    result = c.fetchone()

    if not result:
        c.execute("INSERT INTO halloween (id) VALUES (?)", (userid,))
        conn.commit()

        if value == "pumpkins":
            result = 100
        elif value == "cooldown":
            result = 0

    else:
        result = result[0]
    
    conn.close()
    return result

def write_halloween_value(userid, value, overwrite):

    conn = sqlite3.connect('./storage/databases/hierarchy.db')
    c = conn.cursor()

    c.execute("SELECT id FROM halloween WHERE id = ?", (userid,))
    exists = c.fetchone()

    if not exists:
        c.execute("INSERT INTO halloween (id) VALUES (?)", (userid))

    c.execute(f"UPDATE halloween SET {value} = ? WHERE id = ?", (overwrite, userid))

    conn.commit()
    conn.close()



class Halloween(commands.Cog):

    def __init__(self, client):
        self.client = client

        self.pumpkinchannel = client.get_channel(765994365393829948)

        self.pumpkin_search_task = asyncio.create_task(self.pumpkin_search())

    
    def cog_unload(self):

        self.pumpkin_search_task.cancel()


    async def cog_check(self, ctx):
        if ctx.channel.category.id != self.client.rightCategory:
            return False
        else:
            return True

    
    async def pumpkin_search(self):

        async with self.pumpkinchannel.typing():

            while True:
                
                nothing = random.randint(30, 60)

                while nothing > 0:

                    while True:
                        try:
                            await self.pumpkinchannel.send("_ _\n\nNothing...\n\n_ _")
                            break
                        except:
                            pass
                    
                    nothing -= 1
                    await asyncio.sleep(random.randint(2, 5))

                while True:
                    try:
                        message = await self.pumpkinchannel.send("🎃")
                        await message.add_reaction("🎃")
                        break
                    except:
                        pass
                await asyncio.sleep(random.randint(2, 5))



    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):

        if payload.channel_id == self.pumpkinchannel.id:

            if payload.user_id == self.client.user.id: return

            message = await self.pumpkinchannel.fetch_message(payload.message_id)

            if message.content == "🎃" and str(payload.emoji) == "🎃":

                member = self.client.mainGuild.get_member(payload.user_id)

                gained = random.randint(1, 5)
                await message.edit(content=f"_ _\n{gained} 🎃 claimed by {member.mention}.\n_ _")
                await message.clear_reactions()


                pumpkins = get_halloween_value(payload.user_id, "pumpkins")
                pumpkins += gained
                write_halloween_value(payload.user_id, "pumpkins", pumpkins)


    @commands.command()
    async def writehalloween(self, ctx):

        if ctx.channel.id != self.client.adminChannel: return

        with open('./storage/text/englishwords.txt') as f:
            word = random.choice(f.read().splitlines())
        # for confirmation
        await ctx.send(f"Are you sure you want to save all pumpkins? Type `{word}` to proceed.")

        try:
            response = await self.client.wait_for('message', check=lambda m: m.channel == ctx.channel and m.author == ctx.author, timeout=20)
        except:
            return await ctx.send("Save timed out.")

        if response.content.lower() != word.lower(): return await ctx.send("Save cancelled.")
        
        conn = sqlite3.connect('./storage/databases/hierarchy.db')
        c = conn.cursor()
        c.execute("DROP TABLE IF EXISTS halloween;")
        c.execute("CREATE TABLE halloween (id INTEGER PRIMARY KEY, pumpkins INTEGER DEFAULT 100, cooldown INTEGER DEFAULT 0);")
        c.execute("""
        INSERT INTO halloween
        (id, pumpkins)
        SELECT id, 
        CASE
            WHEN members.money + members.bank > 0 THEN 100
            ELSE 0
        END
        FROM members;""")
        conn.commit()
        conn.close()

        await ctx.send("Reset all pumpkins.")
        await log_command(self.client, ctx)


    @commands.command()
    async def converthalloween(self, ctx):

        if ctx.channel.id != self.client.adminChannel: return

        with open('./storage/text/englishwords.txt') as f:
            word = random.choice(f.read().splitlines())
        # for confirmation
        await ctx.send(f"Are you sure you want to convert all pumpkins? Type `{word}` to proceed.")

        try:
            response = await self.client.wait_for('message', check=lambda m: m.channel == ctx.channel and m.author == ctx.author, timeout=20)
        except:
            return await ctx.send("Conversion timed out.")

        if response.content.lower() != word.lower(): return await ctx.send("Conversion cancelled.")
        
        conn = sqlite3.connect('./storage/databases/hierarchy.db')
        c = conn.cursor()
        c.execute("SELECT id, pumpkins FROM halloween WHERE pumpkins > 0;")
        pumpkins = c.fetchall()
        c.execute("SELECT id, money FROM members")
        moneys = c.fetchall()

        for userid1, pumpkins in pumpkins:

            for userid2, money in moneys:
                if userid1 == userid2:
                    c.execute(f"UPDATE members SET money = {money + pumpkins*2} WHERE id = ?", (userid1,))
                    break

        conn.commit()
        conn.close()

        await ctx.send("Converted all pumpkins.")
        await log_command(self.client, ctx)



    @commands.command()
    async def pumpkins(self, ctx, *, member:discord.Member=None):

        if not member:
            member = ctx.author

        pumpkins = get_halloween_value(member.id, "pumpkins")

        embed = discord.Embed(color=0xff8519, description=f"🎃  {pumpkins} Pumpkins  🎃")
        embed.set_author(name=f"{member.name}'s pumpkins", icon_url=member.avatar_url_as(static_format='jpg'))
        
        await ctx.send(embed=embed)

    
    @commands.command(aliases=["plead", "pumpkinlead", "hlead"])
    async def halloweenlead(self, ctx):

        guild = self.client.mainGuild


        embed = discord.Embed(color = 0xff8519)
        embed.set_author(name='🎃 Halloween Leaderboard 🎃')


        conn = sqlite3.connect('./storage/databases/hierarchy.db')
        c = conn.cursor()
        c.execute("""
        SELECT members.id,
        CASE 
            WHEN halloween.pumpkins IS NULL THEN 100
            ELSE halloween.pumpkins
        END
        FROM members
        LEFT JOIN halloween
        ON members.id = halloween.id;""")
        hierarchy = c.fetchall()
        conn.close()

        hierarchy = list(filter(lambda x: guild.get_member(x[0]), hierarchy))
        hierarchy.sort(key=lambda member: member[1], reverse=True)

        for x in range(5):

            if x == 0:
                embed.add_field(name='__________',value=f'1. <@{hierarchy[x][0]}> 🥇 - {hierarchy[x][1]} 🎃',inline=False)
            elif x == 1:
                embed.add_field(name='__________',value=f'2. <@{hierarchy[x][0]}> 🥈 - {hierarchy[x][1]} 🎃',inline=False)
            elif x == 2:
                embed.add_field(name='__________',value=f'3. <@{hierarchy[x][0]}> 🥉 - {hierarchy[x][1]} 🎃',inline=False)
            else:
                embed.add_field(name='__________',value=f'{x+1}. <@{hierarchy[x][0]}> - {hierarchy[x][1]} 🎃',inline=False)


        await ctx.send(embed=embed)


    @commands.command(aliases=["pleadm", "pumpkinleadm", "hleadm"])
    async def halloweenleadm(self, ctx):

        guild = self.client.mainGuild


        embed = discord.Embed(color = 0xff8519)
        embed.set_author(name='🎃 Halloween Leaderboard 🎃')


        conn = sqlite3.connect('./storage/databases/hierarchy.db')
        c = conn.cursor()
        c.execute("""
        SELECT members.id,
        CASE 
            WHEN halloween.pumpkins IS NULL THEN 100
            ELSE halloween.pumpkins
        END
        FROM members
        LEFT JOIN halloween
        ON members.id = halloween.id;""")
        hierarchy = c.fetchall()
        conn.close()

        hierarchy = list(filter(lambda x: guild.get_member(x[0]), hierarchy))
        hierarchy.sort(key=lambda member: member[1], reverse=True)

        for x in range(5):
            member = guild.get_member(hierarchy[x][0])

            if x == 0:
                embed.add_field(name='__________',value=f'1. {member.name} 🥇 - {hierarchy[x][1]} 🎃',inline=False)
            elif x == 1:
                embed.add_field(name='__________',value=f'2. {member.name} 🥈 - {hierarchy[x][1]} 🎃',inline=False)
            elif x == 2:
                embed.add_field(name='__________',value=f'3. {member.name} 🥉 - {hierarchy[x][1]} 🎃',inline=False)
            else:
                embed.add_field(name='__________',value=f'{x+1}. {member.name} - {hierarchy[x][1]} 🎃',inline=False)


        await ctx.send(embed=embed)


    @commands.command(aliases=["paround", "haround", "pumpkinaround"])
    async def halloweenaround(self, ctx, find=None, *, member:discord.Member=None):


        if not member: 
            member = ctx.author
        
        if not await bot_check(self.client, ctx, member):
            return

        if not find:
            find = 3
        try:
            find = int(find)

        except:
            await ctx.send('Incorrect command usage:\n`.halloweenaround (range) (member)`')
            return

        if find < 1 or find > 12:
            await ctx.send('Enter a number from 1-12 for `range`.')
            return

        userid = member.id
        guild = self.client.mainGuild


        conn = sqlite3.connect('./storage/databases/hierarchy.db')
        c = conn.cursor()
        c.execute("""
        SELECT members.id,
        CASE 
            WHEN halloween.pumpkins IS NULL THEN 100
            ELSE halloween.pumpkins
        END
        FROM members
        LEFT JOIN halloween
        ON members.id = halloween.id;""")
        hierarchy = c.fetchall()
        conn.close()

        hierarchy = list(filter(lambda x: guild.get_member(x[0]), hierarchy))
        hierarchy.sort(key=lambda member: member[1], reverse=True)

        ids = list(map(lambda x: x[0], hierarchy))

        try:
            index = ids.index(userid)
        except ValueError:
            hierarchy.append((userid, 0))
            ids.append(userid)
            index = ids.index(userid)


        lower_index = index-find

        if lower_index < 0:
            lower_index = 0

        higher_index = index+find+1
        length = len(hierarchy)

        if higher_index > length:
            higher_index = length

        result = hierarchy[lower_index:higher_index]

        avatar = member.avatar_url_as(static_format='jpg')
        embed = discord.Embed(color=0xff8519)
        embed.set_author(name=f"🎃 Around {member.name} 🎃",icon_url=avatar)

        place = ids.index(result[0][0])+1
        for person in result:

            medal = ''
            mk = ''
            if place == 1:
                medal = '🥇 '
            elif place == 2:
                medal = '🥈 '
            elif place == 3:
                medal = '🥉 '
            if member.id == person[0]:
                mk = '**'
            embed.add_field(name='__________', value=f'{mk}{place}. <@{person[0]}> {medal}- {person[1]}{mk} 🎃', inline=False)
            place += 1


        if find > 5:
            await ctx.send('Embed too large, check your DMs.')
            await ctx.author.send(embed=embed)

        else:
            await ctx.send(embed=embed)


    @commands.command(aliases=["paroundm", "haroundm", "pumpkinaroundm"])
    async def halloweenaroundm(self, ctx, find=None, *, member:discord.Member=None):


        if not member: 
            member = ctx.author
        
        if not await bot_check(self.client, ctx, member):
            return

        if not find:
            find = 3
        try:
            find = int(find)

        except:
            await ctx.send('Incorrect command usage:\n`.halloweenaroundm (range) (member)`')
            return

        if find < 1 or find > 12:
            await ctx.send('Enter a number from 1-12 for `range`.')
            return

        userid = member.id
        guild = self.client.mainGuild


        conn = sqlite3.connect('./storage/databases/hierarchy.db')
        c = conn.cursor()
        c.execute("""
        SELECT members.id,
        CASE 
            WHEN halloween.pumpkins IS NULL THEN 100
            ELSE halloween.pumpkins
        END
        FROM members
        LEFT JOIN halloween
        ON members.id = halloween.id;""")
        hierarchy = c.fetchall()
        conn.close()

        hierarchy = list(filter(lambda x: guild.get_member(x[0]), hierarchy))
        hierarchy.sort(key=lambda member: member[1], reverse=True)

        ids = list(map(lambda x: x[0], hierarchy))

        try:
            index = ids.index(userid)
        except ValueError:
            hierarchy.append((userid, 0))
            ids.append(userid)
            index = ids.index(userid)


        lower_index = index-find

        if lower_index < 0:
            lower_index = 0

        higher_index = index+find+1
        length = len(hierarchy)

        if higher_index > length:
            higher_index = length

        result = hierarchy[lower_index:higher_index]

        avatar = member.avatar_url_as(static_format='jpg')
        embed = discord.Embed(color=0xff8519)
        embed.set_author(name=f"🎃 Around {member.name} 🎃",icon_url=avatar)

        place = ids.index(result[0][0])+1
        for person in result:

            current_member = guild.get_member(person[0])

            medal = ''
            mk = ''
            if place == 1:
                medal = '🥇 '
            elif place == 2:
                medal = '🥈 '
            elif place == 3:
                medal = '🥉 '
            if member.id == person[0]:
                mk = '**'


            embed.add_field(name='__________', value=f'{mk}{place}. {current_member.name} {medal}- {person[1]}{mk} 🎃', inline=False)
            place += 1


        if find > 5:
            await ctx.send('Embed too large, check your DMs.')
            await ctx.author.send(embed=embed)

        else:
            await ctx.send(embed=embed)

    @commands.command(aliases=["ptime", "htime", "pumpkintime"])
    async def halloweentime(self, ctx, *, member:discord.Member=None):

        if not member:
            member = ctx.author

        
        cooldown = get_halloween_value(member.id, 'cooldown')

        if cooldown > int(time.time()):
            await ctx.send(f"🎃  **{member.name}** has {splittime(cooldown)} left until they can steal pumpkins.  🎃")
        else:
            await ctx.send(f"🎃  **{member.name}** can steal pumpkins.  🎃")


    @commands.command(aliases=["psteal", "hsteal", "pumpkinsteal"])
    async def halloweensteal(self, ctx, member:discord.Member=None, amount=None):

        if not member or not amount:
            return await ctx.send("Incorrect command usage:\n`.halloweensteal member amount`")


        if amount.isdigit():
            amount = int(amount)
        else:
            return await ctx.send("Enter an amount from 1 to 100.")

        if not 0 < amount <= 100:
            return await ctx.send("Enter an amount from 1 to 100.")

        if (hstealc := get_halloween_value(ctx.author.id, 'cooldown')) > time.time():
            return await ctx.send(f"You must wait {splittime(hstealc)} before you can steal pumpkins again.")
        
        member_pumpkins = get_halloween_value(member.id, 'pumpkins')

        if amount > member_pumpkins:
            return await ctx.send("This member does not have that many pumpkins.")
        
        member_pumpkins -= amount
        write_halloween_value(member.id, 'pumpkins', member_pumpkins)

        author_pumpkins = get_halloween_value(ctx.author.id, 'pumpkins')
        author_pumpkins += amount
        write_halloween_value(ctx.author.id, 'pumpkins', author_pumpkins)

        cooldown = ((amount**2)//20 + amount)*60 + int(time.time())

        write_halloween_value(ctx.author.id, 'cooldown', cooldown)

        await ctx.send(f"**{ctx.author.name}** stole {amount} 🎃 from **{member.name}** and has to wait {splittime(cooldown)} before they can steal again.")


    @commands.command(aliases=["htest", "ptest", "pumpkintest"])
    async def halloweentest(self, ctx, amount=None):

        if not amount:
            return await ctx.send("Incorrect command usage:\n`.halloweentest amount`")

        if amount.isdigit():
            amount = int(amount)
        else:
            return await ctx.send("Enter an amount from 1 to 100.")

        if not 0 < amount <= 100:
            return await ctx.send("Enter an amount from 1 to 100.")

        
        cooldown = ((amount**2)//20 + amount)*60 + int(time.time())
        await ctx.send(f"You would have to wait {splittime(cooldown)} if you stole {amount} 🎃.")


    @commands.Cog.listener() # halloween submission
    async def on_message(self, message):
        if not message.author.bot and message.channel.id == 771787118158413865:
            submissions = self.client.get_channel(771787494764183572)
            to_file_attachments = []
            for attachment in message.attachments:
                to_file = await attachment.to_file()
                to_file_attachments.append(to_file)

            await submissions.send(f"By {message.author.mention}:")
            await submissions.send(f"{message.content}", files=to_file_attachments)
            await message.delete()
            await message.channel.send(f"{message.author.mention}, your submission was made.")





def setup(client):
    client.add_cog(Halloween(client))