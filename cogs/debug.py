# pylint: disable=import-error

import nextcord
from nextcord.ext import commands
import json
import asyncpg
import os
import asyncio
import random
import aiohttp

# To import from different path
import sys
sys.path.insert(1 , os.getcwd())

from utils import bot_check, splittime, timestring, log_command

class Debug(commands.Cog):

    def __init__(self, client):
        self.client = client

    async def cog_check(self, ctx):
        if ctx.channel.id == self.client.adminChannel:
            return True
        else:
            return False

    async def cog_after_invoke(self, ctx):
        await log_command(self.client, ctx)

    @commands.command()
    async def online(self, ctx):
        guild = self.client.mainGuild
        channel = self.client.get_channel(698384786460246147)
        message = await channel.fetch_message(698775210173923429)
        embed = nextcord.Embed(color=0x42f57b)
        botuser = guild.get_member(self.client.user.id)
        botuser = botuser.avatar.with_format('jpg').url
        embed.set_author(name="Bot ready to use.",icon_url=botuser)
        await message.edit(embed=embed)
        await ctx.send("Status updated to online.")
        await self.client.change_presence(status=nextcord.Status.online,activity=nextcord.Game(name='with money'))

    @commands.command()
    async def offline(self, ctx):
        guild = self.client.mainGuild
        channel = self.client.get_channel(698384786460246147)
        message = await channel.fetch_message(698775210173923429)
        embed = nextcord.Embed(color=0xff5254)
        botuser = guild.get_member(self.client.user.id)
        botuser = botuser.avatar.with_format('jpg').url
        embed.set_author(name="Bot under development.",icon_url=botuser)
        await message.edit(embed=embed)
        await ctx.send("Status updated to offline.")
        await self.client.change_presence(status=nextcord.Status.dnd, activity=nextcord.Game(name='UNDER DEVELOPMENT'))

    @commands.command()
    async def mode(self, ctx, mode=''):

        mode = mode.lower()
        allowed_modes = ['normal', 'event']

        if mode not in allowed_modes:
            await ctx.send(f"Incorrect command usage:\n`.mode {'/'.join(allowed_modes)}`")
            return

        with open('./storage/jsons/mode.json','w') as f: 
            json.dump(mode, f, indent=2)

        await ctx.send(f"Mode successfully set to `{mode}`.")
    
    @commands.command()
    async def db(self, ctx, *, command=None):

        if not command:
            return await ctx.send("Incorrect command usage:\n`.db dbcommand`.")
            

        try:

            async with self.client.pool.acquire() as db:
                output = await db.fetch(command)

        except Exception as error:

            await ctx.send(f"Error:\n```{error}```")
        
        else:

            if output:
                # 2000 including backticks
                output = str(output)[:1998]

                await ctx.send(f"`{output}`")

            else:
                await ctx.send("Command successfully executed.")

    @commands.command()
    async def json(self, ctx, *, filename=None):

        if not filename:
            await ctx.send("Incorrect command usage:\n`.json filename`.")
            return

        try:
            with open(f'./storage/jsons/{filename}.json') as f:
                output = json.load(f)

        except Exception as error:

            await ctx.send(f"Error:\n```{error}```")
        
        else:
            output = json.dumps(output, indent=2)

            if len(output) + 2 > 2000:
                await ctx.send("Output too long to display.")
            else:
                await ctx.send(f"```{output}```")

    @commands.command()
    async def shopupdate(self, ctx):


        async with self.client.pool.acquire() as db:
            shopitems = await db.fetch('SELECT name, price, description, emoji FROM shop;')

        embed = nextcord.Embed(color=0x30ff56, title='Shop')

        x = 1
        for name, price, desc, emoji in shopitems:

            embed.add_field(name=f'{x}. ${price} - {name.capitalize()} {emoji}', value=desc, inline=False)

            x += 1

        shopchannel = self.client.get_channel(702654620291563600)
        message = await shopchannel.fetch_message(740680266086875243)
        await message.edit(embed=embed)

        await ctx.send("Shop successfully updated.")

    @commands.command()
    async def money(self, ctx, member: nextcord.Member=None, add=None):

        if not member or not add:
            await ctx.send("Incorrect command usage:\n`.money member +amount` or `.money member -amount`")
            return

        if not add.startswith(('+', '-')):
            await ctx.send("Incorrect command usage:\n`.money member +amount` or `.money member -amount`")
            return

        try:
            add = int(add)
        except:
            await ctx.send("Incorrect command usage:\n`.money member +amount` or `.money member -amount`")
            return

        async with self.client.pool.acquire() as db:
            money = await db.get_member_val(member.id, 'money')
            money += add
            await db.set_member_val(member.id, 'money', money)


            if add >= 0:
                await ctx.send(f"Added ${add} to **{member.name}**'s balance.")
            else:
                await ctx.send(f"Subtracted ${add * -1} from **{member.name}**'s balance.")

            await db.rolecheck(member.id)
            await db.leaderboard()
    

    @commands.group(invoke_without_command=True)
    async def adminaward(self, ctx):

        await ctx.send("Incorrect command usage: \n`.adminaward list/about/create/edit/delete/member`")

    @adminaward.command(name="list")
    async def award_list(self, ctx, page=1):

        if isinstance(page, str):
            if page.isdigit():
                page = int(page)
            else:
                return await ctx.send("Enter a valid page number.")
        
        async with self.client.pool.acquire() as db:
            awards = await db.fetch("SELECT id, name, short_description FROM awards;")

        # splitting into pages of 5
        awards = [awards[x:x+5] for x in range(0, len(awards), 5)]

        if page > len(awards):
            return await ctx.send("There are not that many pages.")

        embed = nextcord.Embed(color=0x19a83f, title="All Awards")

        for award_id, name, short_description in awards[page-1]:
            embed.add_field(name=f"{award_id}. {name}", value=short_description, inline=False)


        embed.set_footer(text=f"Page {page}/{len(awards)}")
        
        await ctx.send(embed=embed)

    @adminaward.command()
    async def about(self, ctx, award_id=None):

        if not award_id:
            return await ctx.send("Incorrect command usage:\n`.adminaward about awardid`")
        
        if award_id.isdigit():
            award_id = int(award_id)
        else:
            return await ctx.send("Enter a valid award id.")

        async with self.client.pool.acquire() as db:
            award = await db.fetchrow("SELECT name, color, long_description, image_link FROM awards WHERE id = $1;", award_id)
            
        if not award:
            return await ctx.send("Award not found.")

        name, color, long_description, image_link = award
        
        embed = nextcord.Embed(color=color, title=f"{name}  Award ID: {award_id}", description=long_description)
        embed.set_image(url=image_link)

        await ctx.send(embed=embed)


    @adminaward.command(aliases=["add"])
    async def create(self, ctx):

        await ctx.send("Enter award name:")
        try:
            name = await self.client.wait_for('message', check=lambda m: m.channel == ctx.channel and m.author == ctx.author, timeout=30)
        except asyncio.TimeoutError:
            return await ctx.send("Award creation timed out.")

        await ctx.send("Enter award color:")
        while True:
            try:
                color = await self.client.wait_for('message', check=lambda m: m.channel == ctx.channel and m.author == ctx.author, timeout=30)
            except asyncio.TimeoutError:
                return await ctx.send("Award creation timed out.")

            color = color.content.replace('#', '')

            if len(color) != 6:
                await ctx.send("Enter a valid hex color.")
                continue

            try:
                color = int(color, 16)
            except:
                await ctx.send("Enter a valid hex color.")
                continue

            if color > 16777215 or color < 0: # equivalent to ffffff
                await ctx.send("Enter a valid hex color code.")
                continue

            break

        await ctx.send("Enter award short description:")
        try:
            short_description = await self.client.wait_for('message', check=lambda m: m.channel == ctx.channel and m.author == ctx.author, timeout=60)
        except asyncio.TimeoutError:
            return await ctx.send("Award creation timed out.")

        await ctx.send("Enter award long description:")
        try:
            long_description = await self.client.wait_for('message', check=lambda m: m.channel == ctx.channel and m.author == ctx.author, timeout=120)
        except asyncio.TimeoutError:
            return await ctx.send("Award creation timed out.")

        await ctx.send("Enter award image:")

        while True:
            try:
                image_message = await self.client.wait_for('message', check=lambda m: m.channel == ctx.channel and m.author == ctx.author, timeout=30)
            except asyncio.TimeoutError:
                return await ctx.send("Award creation timed out.")

            if image_message.attachments:
                image = image_message.attachments[0]

                if not image.filename.lower().endswith(('png', 'jpg', 'jpeg', 'gif')):
                    await ctx.send("Only files with `.png`, `.jpg`, `jpeg`, and `gif` file extensions are supported.")
                    continue

                image = image.url
            
            else:

                image = image_message.content

                try:
                    async with aiohttp.ClientSession() as session:

                        async with session.get(image) as resp:

                            allowed_formats = ['png', 'jpg', 'jpeg', 'gif']
                            allowed_formats = list(map(lambda extension: f"image/{extension}", allowed_formats))

                            if resp.content_type not in allowed_formats:
                                await ctx.send("Only files with `.png`, `.jpg`, `.jpeg`, and `.gif` file extensions are supported.")
                                continue
                                
                except aiohttp.client_exceptions.InvalidURL:
                    await ctx.send("Invalid image link.")
                    continue

            break

        
        await ctx.send("Should this award be listed? `yes/y` or `no/n`")
        while True:
            try:
                listed = await self.client.wait_for('message', check=lambda m: m.channel == ctx.channel and m.author == ctx.author, timeout=60)
            except asyncio.TimeoutError:
                return await ctx.send("Award creation timed out.")

            listed = listed.content.lower()

            if listed in ('y', 'yes'):
                listed = True
                break
            elif listed in ('n', 'no'):
                listed = False
                break
            else:
                await ctx.send("Enter a valid answer.")
                continue

        name, short_description, long_description = name.content, short_description.content, long_description.content

        if listed:
            channel = self.client.get_channel(765694242617032774)

            embed = nextcord.Embed(color=color, title=name, description=long_description)
            embed.set_image(url=image)

            message = await channel.send(embed=embed)
            message = message.id
        else:
            message = None


        async with self.client.pool.acquire() as db:
            await db.execute("""INSERT INTO awards
        (message_id, name, color, short_description, long_description, image_link)
        VALUES ($1, $2, $3, $4, $5, $6);""", message, name, color, short_description, long_description, image)


        await ctx.send("Award successfully created.")


    @adminaward.command()
    async def edit(self, ctx, award_id=None, param=None, *, new=None):
        
        if not award_id or not param or not new:
            return await ctx.send("Incorrect command usage:\n`.adminaward edit awardid name/color/short/long/image new`")


        if param not in ("name", "color", "short", "long", "image"):
            return await ctx.send("Incorrect command usage:\n`.adminaward edit awardid name/color/short/long/image new`")

        
        if param == "color":
            new = new.replace('#', '')

            if len(new) != 6:
                return await ctx.send("Invalid hex color code.")

            try:
                new = int(new, 16)
            except:
                return await ctx.send("Invalid hex color code.")

            if new > 16777215 or new < 0: # equivalent to ffffff
                return await ctx.send("Invalid hex color code.")

        
        elif param == "image":

            if ctx.message.attachments:
                image = ctx.message.attachments[0]

                if not image.filename.lower().endswith(('png', 'jpg', 'jpeg', 'gif')):
                    return await ctx.send("Only files with `.png`, `.jpg`, `jpeg`, and `gif` file extensions are supported.")

                new = image.url
            
            else:

                try:
                    async with aiohttp.ClientSession() as session:

                        async with session.get(new) as resp:

                            allowed_formats = ['png', 'jpg', 'jpeg', 'gif']
                            allowed_formats = list(map(lambda extension: f"image/{extension}", allowed_formats))

                            if resp.content_type not in allowed_formats:
                                return await ctx.send("Only files with `.png`, `.jpg`, `.jpeg`, and `.gif` file extensions are supported.")
                                
                                
                except aiohttp.client_exceptions.InvalidURL:
                    return await ctx.send("Invalid image link.")


        replacements = {
            "name": "name",
            "color": "color",
            "short": "short_description",
            "long": "long_description",
            "image": "image_link"
        }

        param = replacements[param]
        
        async with self.client.pool.acquire() as db:

            
            exists = await db.fetchval("SELECT id FROM awards WHERE id = $1;", award_id)

            if not exists:
                return await ctx.send("Award not found.")

            message_id, name, color, long_description, image_link = await db.fetchrow(
            f'''
            UPDATE awards SET {param} = $1 WHERE id = $2
            RETURNING message_id, name, color, long_description, image_link''',
            new, award_id)
        


        if param in ("name", "color", "long_description", "image_link") and message_id:

            embed = nextcord.Embed(color=color, title=name, description=long_description)
            embed.set_image(url=image_link)

            channel = self.client.get_channel(765694242617032774)
            message = await channel.fetch_message(message_id)

            await message.edit(embed=embed)

            



        await ctx.send("Award successfully updated.")

        


    @adminaward.command()
    async def delete(self, ctx, award_id):

        if not award_id:
            return await ctx.send("Incorrect command usage:\n`.adminaward delete awardid`")


        with open('./storage/text/englishwords.txt') as f:
            word = random.choice(f.read().splitlines())


        # for confirmation
        await ctx.send(f"Are you sure you want to delete this award? Type `{word}` to proceed.")

        try:
            response = await self.client.wait_for('message', check=lambda m: m.channel == ctx.channel and m.author == ctx.author, timeout=20)
        except:
            return await ctx.send("Save timed out.")

        if response.content.lower() != word.lower(): return await ctx.send("Save cancelled.")

        
        if award_id.isdigit():
            award_id = int(award_id)
        else:
            return await ctx.send("Enter a valid award id.")

        async with self.client.pool.acquire() as db:
            message_id = await db.fetchrow('SELECT message_id FROM awards WHERE id = $1', award_id)

        
            # detect if row even exists
            if not message_id:
                return await ctx.send("Award not found.")

            message_id = message_id[0]

            await db.execute('DELETE FROM awards WHERE id = $1', award_id)

            if message_id:
                channel = self.client.get_channel(765694242617032774)
                message = await channel.fetch_message(message_id)
                await message.delete()


            members = await db.execute('SELECT id, awards FROM members WHERE $1 = ANY(awards);', award_id)

            for userid, awards in members:
                awards.remove(award_id)   
            
                await db.execute('UPDATE members SET awards = $1 WHERE id = $2', awards, userid)


        await ctx.send("Award successfully deleted.")
        

    @adminaward.group(invoke_without_command=True)
    async def member(self, ctx):

        await ctx.send("Incorrect command usage:\n`.adminaward member give/remove`")

    @member.command()
    async def give(self, ctx, member: nextcord.Member=None, award_id=None):

        if not member or not award_id:
            return await ctx.send("Incorrect command usage:\n`.adminaward member give memberid awardid`")

        if award_id.isdigit():
            award_id = int(award_id)
        else:
            return await ctx.send("Enter a valid award id.")

        async with self.client.pool.acquire() as db:

            name = await db.fetchval('SELECT name FROM awards WHERE id = $1', award_id)
            
            # detect if row even exists
            if not name:
                return await ctx.send("Award not found.")


            awards = await db.get_member_val(member.id, 'awards')

            
            if award_id in awards:
                return await ctx.send(f"**{member.name}** already has **{name}**.")

            awards.append(award_id)


            await db.set_member_val(member.id, 'awards', awards)

        await ctx.send(f"The award **{name}** was granted to **{member.name}**.")

    @member.command()
    async def remove(self, ctx, member: nextcord.Member=None, award_number=None):

        if not member or not award_number:
            return await ctx.send("Incorrect command usage:\n`.adminaward member remove memberid awardnumber`")

        if award_number.isdigit():
            award_number = int(award_number)
        else:
            return await ctx.send("Enter a valid award id.")

        async with self.client.pool.acquire() as db:

            awards = await db.get_member_val(member.id, 'awards')

            try:
                award = awards[award_number-1]
            except IndexError:
                return await ctx.send("Award not found.")

            awards.remove(award)

            await db.set_member_val(member.id, "awards", awards)

        await ctx.send(f"The award was removed from **{member.name}**.")

    

def setup(client):
    client.add_cog(Debug(client))