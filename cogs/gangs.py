# pylint: disable=import-error
import discord
from discord.ext import commands

import datetime
import re
import difflib
import asyncio
import aiohttp

import os
# To import from different path
import sys
sys.path.insert(1 , os.getcwd())

from utils import bot_check

class Gangs(commands.Cog):

    def __init__(self, client):
        self.client = client


    @commands.group(invoke_without_command=True)
    async def gang(self, ctx):
        await ctx.send("Incorrect command usage:\n`.gang list/which/about/balance/members/membersm/create/invite/uninvite/settings/leave/promote/kick/disband`")


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
        
        async with self.client.pool.acquire() as db:

            gangs = await db.fetch('SELECT name, created_at FROM gangs')

        if not gangs:
            await ctx.send("There are no existing gangs.")
            return

        regex = re.compile(r"\..*")

        gangs = sorted(gangs, key=lambda gang: int(datetime.datetime.strptime(regex.sub('', gang[1][2:]), '%y-%m-%d %H:%M:%S').timestamp()))
        
        gangs = list(map(lambda gang: gang[0], gangs))
        
        gangs = [gangs[x:x+6] for x in range(0, len(gangs), 6)]
        
        if page > len(gangs):
            await ctx.send("Page not found.")
            return
        
        embed = discord.Embed(color=0xffe6a1, title="Gangs")

        for gang in gangs[page-1]:
            embed.add_field(name=discord.utils.escape_markdown("________"), value=gang, inline=True)
        
        embed.set_footer(text=f"Page {page}/{len(gangs)}")

        await ctx.send(embed=embed)

    @gang.command()
    @commands.max_concurrency(1, per=commands.BucketType.member)
    async def which(self, ctx, *, member:discord.Member=None):

        if not member:
            member = ctx.author


        async with self.client.pool.acquire() as db:
            gang = await db.fetchrow('SELECT name, owner FROM gangs WHERE $1 = ANY(members) OR $1 = owner;', member.id)


        if not gang:
            await ctx.send(f"**{member.name}** is not in a gang.")
        elif member.id == gang[1]:
            await ctx.send(f"**{member.name}** owns the gang **{gang[0]}**.")
        else:
            await ctx.send(f"**{member.name}** is in the gang **{gang[0]}**.")

        

    @gang.command()
    @commands.max_concurrency(1, per=commands.BucketType.member)
    async def about(self, ctx, *, name=None):


        async with self.client.pool.acquire() as db:
        
            if not name:

                name = await db.fetchval('SELECT name FROM gangs WHERE $1 = ANY(members) OR $1 = owner;', ctx.author.id)

                if not name:
                    return await ctx.send("You are not in a gang.")



            try:
                gangid, owner, description, created_at, role_id, color, img_link = await db.fetchrow('SELECT id, owner, description, created_at, role_id, color, img_link FROM gangs WHERE name = $1;', name)

            except TypeError:
                gangs = await db.fetch('SELECT name FROM gangs;')
                gangs = [gang[0] for gang in gangs]

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
        
        description += f"\n\nGang Id: {gangid}"

        # Convert string to datetime
        created_at = datetime.datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S.%f')

        embed = discord.Embed(color=color, title=name, description=description, timestamp=created_at)

        owner = guild.get_member(owner)
        embed.set_author(name=f"Owner: {owner.name}", icon_url=owner.avatar_url_as(static_format='jpg'))

        embed.set_footer(text="Created at")

        if img_link:
            embed.set_image(url=img_link)
        
        await ctx.send(embed=embed)

    @gang.command()
    async def balance(self, ctx, *, name=None):

        async with self.client.pool.acquire() as db:
        
            if not name:

                name = await db.fetchval('SELECT name FROM gangs WHERE $1 = ANY(members) OR $1 = owner;', ctx.author.id)

                if not name:
                    return await ctx.send("You are not in a gang.")



            try:
                owner, members, color, img_link = await db.fetchrow('SELECT owner, members, color, img_link FROM gangs WHERE name = $1;', name)
            except TypeError:

                gangs = await db.fetch('SELECT name FROM gangs;')
                gangs = [gang[0] for gang in gangs]


                close = difflib.get_close_matches(name, gangs, n=3, cutoff=0.5)
                

                if len(close) > 0:
                    
                    close = list(map(lambda word: f"`{word}`", close))

                    text = "\n".join(close)

                    text = f"There is no gang called **{name}**. Did you mean:\n{text}"

                else:
                    
                    text = f"There is no gang called **{name}**."
                
                await ctx.send(text) 
                return


            guild = self.client.mainGuild
            
            # Converts into hexadecimal
            color = int(color, 16)

            members.append(owner)

            total = await db.fetchval("SELECT SUM(money + bank) FROM members WHERE id = ANY($1)", members)

            owner = guild.get_member(owner)

            embed = discord.Embed(color=color, title=f"{name}'s balance", description=f"${total}")
            embed.set_author(name=f"Owner: {owner.name}", icon_url=owner.avatar_url_as(static_format='jpg'))

            if img_link:
                embed.set_image(url=img_link)
            
            await ctx.send(embed=embed)


    @gang.command()
    async def members(self, ctx, *, name=None):
        
        async with self.client.pool.acquire() as db:
        
            if not name:

                name = await db.fetchval('SELECT name FROM gangs WHERE $1 = ANY(members) OR $1 = owner;', ctx.author.id)

                if not name:
                    return await ctx.send("You are not in a gang.")



            try:
                owner, members, color, img_link = await db.fetchrow('SELECT owner, members, color, img_link FROM gangs WHERE name = $1;', name)
            except:
                gangs = await db.fetch('SELECT name FROM gangs;')
                gangs = [gang[0] for gang in gangs]


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
            members = list(map(lambda id: f"<@{id}>", members))
            members = "\n".join(members)

        else:
            members = "No members."

        embed = discord.Embed(color=color, title=name, description=members)

        owner = guild.get_member(owner)
        embed.set_author(name=f"Owner: {owner.name}", icon_url=owner.avatar_url_as(static_format='jpg'))

        if img_link:
            embed.set_image(url=img_link)
        
        await ctx.send(embed=embed)
        


    @gang.command()
    async def membersm(self, ctx, *, name=None):
        
        async with self.client.pool.acquire() as db:
        
            if not name:

                name = await db.fetchval('SELECT name FROM gangs WHERE $1 = ANY(members) OR $1 = owner;', ctx.author.id)

                if not name:
                    return await ctx.send("You are not in a gang.")



            try:
                owner, members, color, img_link = await db.fetchrow('SELECT owner, members, color, img_link FROM gangs WHERE name = $1;', name)
            except:
                gangs = await db.fetch('SELECT name FROM gangs;')
                gangs = [gang[0] for gang in gangs]


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
            members = list(map(lambda userid: discord.utils.escape_markdown(guild.get_member(int(userid)).name), members))
            members = "\n".join(members)
        else:
            members = "No members."

        embed = discord.Embed(color=color, title=name, description=members)

        owner = guild.get_member(owner)
        embed.set_author(name=f"Owner: {owner.name}", icon_url=owner.avatar_url_as(static_format='jpg'))

        if img_link:
            embed.set_image(url=img_link)
        
        await ctx.send(embed=embed)
        


    @gang.command()
    async def create(self, ctx, *, name=None):

        async with self.client.pool.acquire() as db:

            if not await db.level_check(ctx, ctx.author.id, 3, "be in a gang"):
                return
            

            if not name:
                return await ctx.send("Incorrect command usage:\n`.gang create gangname`")
            

            gang = await db.fetchrow('SELECT name, owner FROM gangs WHERE $1 = ANY(members) OR owner = $1 OR name = $2;', ctx.author.id, name)

            if not gang:
                await db.execute('INSERT INTO gangs (name, owner, created_at) VALUES ($1, $2, $3);', name, ctx.author.id, str(datetime.datetime.utcnow()))
                await ctx.send(f"Successfully created gang: **{name}**")

            elif name == gang[0]:
                return await ctx.send("A gang with that name already exists.")

            elif ctx.author.id == gang[1]:
                return await ctx.send("You already own a gang.")
                
            else:
                return await ctx.send("You are already in another gang.")
            
    
    @gang.command()
    async def invite(self, ctx, member:discord.Member=None):


        if not member:
            return await ctx.send("Incorrect command usage:\n`.gang invite member`")

        elif member.id == ctx.author.id:
            return await ctx.send("You can't invite yourself.")

        if not await bot_check(self.client, ctx, member):
            return

        async with self.client.pool.acquire() as db:

            if await db.get_member_val(member.id, 'level') < 3:
                return await ctx.send(f"**{member.name}** must be at least level 3 in order to be in a gang.")

            # making sure member is not already in another gang
            gang = await db.fetchrow('SELECT name, owner FROM gangs WHERE owner = $1 OR $1 = ANY(members);', member.id)

            if gang:

                if ctx.author.id == gang[1]:
                    await ctx.send(f"**{member.name}** is the owner of the gang **{gang[0]}**.")
                else:
                    await ctx.send(f"**{member.name}** is already in the gang **{gang[0]}**.")

                return

            gang = await db.fetchrow('SELECT name, members, all_invite, owner, img_link, color FROM gangs WHERE owner = $1 OR $1 = ANY(members);', ctx.author.id)

    
        if not gang: 
            return await ctx.send("You are not in a gang.")

        elif member.id in gang[1]:
            return await ctx.send(f"**{member.name}** is already in your gang.")
            
        elif member.id == gang[3]:
            return await ctx.send(f"**{member.name}** is the owner of your gang.")
        
        
        if gang[2] or gang[3] == ctx.author.id:
            name, img_link, color = gang[0], gang[4], int(gang[5], 16)

        else:
            return await ctx.send("All invite is disabled for your gang.")
        

        for task in asyncio.all_tasks():
            if task.get_name() == f'gang invite {ctx.author.id} {member.id}':
                return await ctx.send("You already sent an invite to this user.")
    
        
        asyncio.create_task(self.invite_req_task(ctx, member, name, img_link, color), name=f"gang invite {ctx.author.id} {member.id}")




    async def invite_req_task(self, ctx, member, gangname, img_link, color):

        embed = discord.Embed(color=color, title="Gang invite", description=f"To: {member.mention}\nFrom {ctx.author.mention}\nGang: {gangname}")


        if img_link:
            embed.set_image(url=img_link)
        
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

            async with self.client.pool.acquire() as db:
                
                # checking if already in another gang

                gang = await db.fetchrow('SELECT name, owner FROM gangs WHERE owner = $1 OR $1 = ANY(members);', member.id)

                if gang:

                    if ctx.author.id == gang[1]:
                        await ctx.send(f"**{member.name}** is the owner of the gang **{gang[0]}**.")
                    else:
                        await ctx.send(f"**{member.name}** is already in the gang **{gang[0]}**.")

                    return


                members, role_id = await db.fetchrow('SELECT members, role_id FROM gangs WHERE name = $1;', gangname)
                members.append(member.id)

                await db.execute('UPDATE gangs SET members = $1 WHERE name = $2;', members, gangname)

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
            return await ctx.send("Incorrect command usage:\n`.gang uninvite member`")
            

        for task in asyncio.all_tasks():

            if task.get_name() == f'gang invite {ctx.author.id} {member.id}':
                task.cancel()
                await ctx.send(f"Invite to **{member.name}** cancelled.")
                break

        else:   
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
        

        async with self.client.pool.acquire() as db:

            # making sure no other gang with the same name exists
            exists = bool(await db.fetchval('SELECT name FROM gangs WHERE name = $1', name))

            if exists:
                return await ctx.send(f"A gang called {name} already exists.")


            gang = await db.fetchrow('SELECT name, owner, role_id FROM gangs WHERE owner = $1 OR $1 = ANY(members);', ctx.author.id)

        
            if not gang:
                return await ctx.send("You are not in a gang.")

            gangname, owner, role_id = gang
        
            if ctx.author.id != owner:
                return await ctx.send(f"You do not own the gang **{gangname}**.")
                
            else:
                if role_id:
                    guild = self.client.mainGuild
                    role = guild.get_role(gang[3])

                    await role.edit(name=name)

                await db.execute('UPDATE gangs SET name = $1 WHERE name = $2', name, gangname)


        await ctx.send(f"Gang name updated from **{gangname}** to **{name}**.")

                
            


    @settings.command()
    @commands.max_concurrency(1, per=commands.BucketType.member)
    async def description(self, ctx, *, description=None):

        if not description:
            await ctx.send("Incorrect command usage:\n`.gang settings description newdescription`")
            return
        
        async with self.client.pool.acquire() as db:
            gang = await db.fetchrow('SELECT name, owner FROM gangs WHERE owner = $1 OR $1 = ANY(members);', ctx.author.id)

            if not gang:
                return await ctx.send("You are not in a gang.")
                
            elif ctx.author.id != gang[1]:
                return await ctx.send(f"You do not own the gang **{gang[0]}**.")
                

            else:

                await db.execute('UPDATE gangs SET description = $1 WHERE name = $2;', description, gang[0])

        
        await ctx.send("Gang description successfully updated.")

    
    @settings.command()
    @commands.max_concurrency(1, per=commands.BucketType.member)
    async def icon(self, ctx, *, image_link=None):

        if not image_link and not ctx.message.attachments:
            await ctx.send("Incorrect command usage:\n`.gang settings icon imagelink` or `.gang settings icon` *with the image attached.*\n`.gang settings icon delete` to delete icon.")
            return
        

        async with self.client.pool.acquire() as db:

            gang = await db.fetchrow('SELECT name, owner FROM gangs WHERE owner = $1 OR $1 = ANY(members);', ctx.author.id)

            if not gang:
                return await ctx.send("You are not in a gang.")
                
            elif ctx.author.id != gang[1]:
                return await ctx.send(f"You do not own the gang **{gang[0]}**.")

            name = gang[0]


            if image_link and image_link.lower() == 'delete':

                img_link = await db.fetchval('SELECT img_link FROM gangs WHERE name = $1;', name)

                if not img_link:
                    return await ctx.send("Your gang does not have an icon saved.")
                
                await db.execute('UPDATE gangs SET img_link = NULL WHERE name = $1;', name)
                await ctx.send("Successfully deleted gang icon.")


            elif image_link:

                try:
                    async with aiohttp.ClientSession() as session:

                        async with session.get(image_link) as resp:

                            allowed_formats = ['png', 'jpg', 'jpeg', 'gif']
                            allowed_formats = list(map(lambda extension: f"image/{extension}", allowed_formats))

                            if resp.content_type not in allowed_formats:
                                return await ctx.send("Only files with `.png`, `.jpg`, `.jpeg`, and `.gif` file extensions are supported.")
                                
                except aiohttp.client_exceptions.InvalidURL:
                    return await ctx.send("Invalid image link.")
                    

            # to get a image link
            elif ctx.message.attachments:

                image = ctx.message.attachments[0]

                if not image.filename.lower().endswith(('png', 'jpg', 'jpeg', 'gif')):
                    return await ctx.send("Only files with `.png`, `.jpg`, `jpeg`, and `gif` file extensions are supported.")
                
                image_link = image.url

            
            await db.execute('UPDATE gangs SET img_link = $1 WHERE name = $2;', image_link, name)
            await ctx.send(f"Gang icon successfully updated.")
        


    @settings.command()
    @commands.max_concurrency(1, per=commands.BucketType.member)
    async def role(self, ctx, action = ''):
        
        action = action.lower()

        if action not in ('create', 'delete'):
            return await ctx.send("Incorrect command usage:\n`.gang settings role create/delete`")
            

        async with self.client.pool.acquire() as db:

            gang = await db.fetchrow('SELECT name, owner, members, role_id, color FROM gangs WHERE owner = $1 OR $1 = ANY(members);', ctx.author.id)

            if not gang:
                return await ctx.send("You are not in a gang.")
                
            elif ctx.author.id != gang[1]:
                return await ctx.send(f"You do not own the gang **{gang[0]}**.")

            name, owner, members, role_id, color = gang

            guild = self.client.mainGuild

            if action == 'create':

                # owner counts as one also
                if len(members) < 2:
                    return await ctx.send("You must have at least three members in your gang to create a role.")

                if role_id:
                    return await ctx.send("You already has a gang role.")
                    

                color = discord.Color(int(color, 16))
                role = await guild.create_role(reason="Gang role created", name=name, color=color, mentionable=True)

                await db.execute('UPDATE gangs SET role_id = $1 WHERE name = $2;', role.id, name)

                members.append(owner)


                members = list(map(lambda member: guild.get_member(member), members))

                members = list(filter(lambda member: member, members))
                

                await ctx.send(f"Your gang role, {role.mention}, was successfully created.")

                for member in members:
                    await member.add_roles(role)
            
            else:

                if not role_id:
                    return await ctx.send("Your gang does not have a role.")

                role = guild.get_role(role_id)
                await role.delete()

                await db.execute('UPDATE gangs SET role_id = null WHERE name = $1;', name)
                await ctx.send("Your gang role has been deleted.")



    @settings.command()
    async def color(self, ctx, color=None):
        

        if not color:
            await ctx.send("Incorrect command usage:\n`.gang settings color #ffffff`\nWhere `#ffffff` is the hex color code.")
            return

        async with self.client.pool.acquire() as db:

            gang = await db.fetchrow('SELECT name, owner, role_id FROM gangs WHERE owner = $1 OR $1 = ANY(members);', ctx.author.id)

            if not gang:
                return await ctx.send("You are not in a gang.")
                
            elif ctx.author.id != gang[1]:
                return await ctx.send(f"You do not own the gang **{gang[0]}**.")

            name, role_id = gang[0], gang[2]


            color = color.replace('#', '')

            if len(color) != 6:
                return await ctx.send("Enter a valid hex color code.")

            try:
                color_code = int(color, 16)

                if color_code > 16777215 or color_code < 0: # equivalent to ffffff
                    return await ctx.send("Enter a valid hex color code.")
                    

            except:
                return await ctx.send("Enter a valid hex color code.")

            
            await db.execute('UPDATE gangs SET color = $1 WHERE name = $2', color, name)
            
            await ctx.send(f"Gang color set to #{color}.")

            if role_id:
                guild = self.client.mainGuild
                role = guild.get_role(role_id)
                
                await role.edit(color=discord.Color(color_code))


    @settings.command()
    async def allinvite(self, ctx, state=''):

        state = state.lower()

        if state != 'on' and state != 'off':
            await ctx.send("Incorrect command usage:\n`.gang settings allinvite on/off`")
            return

        if state == 'on':
            state = True
        else:
            state = False

        async with self.client.pool.acquire() as db:

            gang = await db.fetchrow('SELECT name, owner FROM gangs WHERE owner = $1 OR $1 = ANY(members);', ctx.author.id)

            if not gang:
                return await ctx.send("You are not in a gang.")
                
            elif ctx.author.id != gang[1]:
                return await ctx.send(f"You do not own the gang **{gang[0]}**.")

            name = gang[0]


            await db.execute('UPDATE gangs SET all_invite = $1 WHERE name = $2;', state, name)

            if state:
                state = 'enabled'
            else:
                state = 'disabled'

            await ctx.send(f"All invite {state}.")

        
        


    @gang.command()
    @commands.max_concurrency(1, per=commands.BucketType.member)
    async def leave(self, ctx):


        async with self.client.pool.acquire() as db:

            gang = await db.fetchrow('SELECT name, owner FROM gangs WHERE owner = $1 OR $1 = ANY(members);', ctx.author.id)

            if not gang:
                return await ctx.send("You are not in a gang.")
                
            elif ctx.author.id == gang[1]:
                return await ctx.send(f"You own the gang **{gang[0]}**.")

            name = gang[0]

            await ctx.send(f"Are you sure you want to leave **{name}**? Respond with `yes` or `y` to proceed.")

            try:
                response = await self.client.wait_for('message', check=lambda message: message.channel == ctx.channel and message.author == ctx.author, timeout=20)
            except:
                await ctx.send("Leave cancelled due to inactivity.")
                return
            
            response = response.content.lower()

            if response in ('y', 'yes'):

                members, role_id = await db.fetchrow('UPDATE gangs SET members = ARRAY_REMOVE(members, $1) WHERE name = $2 RETURNING members, role_id;', ctx.author.id, name)

                await ctx.send(f"**{ctx.author.name}** has left **{gang[0]}**.")

                if role_id:
                    guild = self.client.mainGuild
                    role = guild.get_role(role_id)

                    await ctx.author.remove_roles(role)

                    if len(members) < 2:
                        await role.delete(reason="Gang role deleted")

                        await db.execute('UPDATE gangs SET role_id = NULL WHERE name = $1;', name)

            else:
                await ctx.send("Leave cancelled.")


    @gang.command()
    @commands.max_concurrency(1, per=commands.BucketType.member)
    async def promote(self, ctx, member:discord.Member=None):

        if not member:
            await ctx.send("Incorrect command usage:\n`.gang promote member`")
            return


        async with self.client.pool.acquire() as db:

            gang = await db.fetchrow('SELECT name, owner FROM gangs WHERE owner = $1 OR $1 = ANY(members);', ctx.author.id)

            if not gang:
                return await ctx.send("You are not in a gang.")
                
            elif ctx.author.id != gang[1]:
                return await ctx.send(f"You do not own the gang **{gang[0]}**.")

            name = gang[0]

            await ctx.send(f"Are you sure you want to promote **{member.name}** to the gang owner? Respond with `yes` or `y` to proceed.")

            try:
                response = await self.client.wait_for('message', check=lambda message: message.channel == ctx.channel and message.author == ctx.author, timeout=20)
            except:
                return await ctx.send("Promotion cancelled due to inactivity.")
            
            response = response.content.lower()

            if response in ('yes', 'y'):

                await db.execute('UPDATE gangs SET members = ARRAY_APPEND(ARRAY_REMOVE(members, $1), $2) WHERE name = $3;', member.id, ctx.author.id, name)
                await db.execute('UPDATE gangs SET owner = $1 WHERE name = $2', member.id, name)

                await ctx.send(f"**{member.name}** was promoted to the gang owner by **{ctx.author.name}**.")

            else:
                await ctx.send("Promotion cancelled.")


    @gang.command()
    @commands.max_concurrency(1, per=commands.BucketType.member)
    async def kick(self, ctx, member:discord.Member=None):

        if not member:
            await ctx.send("Incorrect command usage:\n`.gang kick member`")
            return


        async with self.client.pool.acquire() as db:
            gang = await db.fetchrow('SELECT name, owner, members, role_id FROM gangs WHERE owner = $1 OR $1 = ANY(members);', ctx.author.id)

            if not gang:
                return await ctx.send("You are not in a gang.")
                
            elif ctx.author.id != gang[1]:
                return await ctx.send(f"You do not own the gang **{gang[0]}**.")

            name, owner, members, role_id = gang # noqa pylint: disable=unused-variable


            if member.id not in members:
                return await ctx.send("This user is not in your gang.")

            await ctx.send(f"Are you sure you want to kick **{member.name}** from the gang? Respond with `yes` or `y` to proceed.")

            try:
                response = await self.client.wait_for('message', check=lambda message: message.channel == ctx.channel and message.author == ctx.author, timeout=20)
            except:
                return await ctx.send("Kick cancelled due to inactivity.")
                
            response = response.content.lower()

            if response in ('yes', 'y'):

                guild = self.client.mainGuild

                members.remove(member.id)

                if role_id:

                    role = guild.get_role(role_id)

                    await member.remove_roles(role)

                    if len(members) < 2:
                
                        await role.delete(reason="Gang role deleted")
                        
                        await db.execute('UPDATE gangs SET role_id = NULL WHERE name = $1;', name)
                        

                await db.execute('UPDATE gangs SET members = $1 WHERE name = $2;', members, name)

                await ctx.send(f"**{member.name}** was kicked from **{gang[0]}**.")

            else:
                await ctx.send("Kick cancelled.")


    @gang.command()
    @commands.max_concurrency(1, per=commands.BucketType.member)
    async def disband(self, ctx):


        async with self.client.pool.acquire() as db:
            gang = await db.fetchrow('SELECT name, owner, role_id FROM gangs WHERE owner = $1 OR $1 = ANY(members);', ctx.author.id)

            if not gang:
                return await ctx.send("You are not in a gang.")
                
            elif ctx.author.id != gang[1]:
                return await ctx.send(f"You do not own the gang **{gang[0]}**.")

            name, owner, role_id = gang # noqa pylint: disable=unused-variable


            await ctx.send(f"Are you sure you want to disband **{name}**? Respond with the gang name to proceed.")

            try:
                response = await self.client.wait_for('message', check=lambda message: message.channel == ctx.channel and message.author == ctx.author, timeout=20)
            except:
                await ctx.send("Disband cancelled due to inactivity.")
                return
            
            response = response.content.lower()

            if response == name.lower():

                if role_id:
                    guild = self.client.mainGuild
                    role = guild.get_role(role_id)

                    await role.delete(reason="Gang role deleted")

                await db.execute('DELETE FROM gangs WHERE name = $1;', name)

                await ctx.send(f"The gang **{name}** has been disbanded.")

            else:
                await ctx.send("Disband cancelled.")
    



def setup(client):
    client.add_cog(Gangs(client))