# pylint: disable=import-error

import asyncio
import json
import random
import time
import datetime

import discord
from discord.ext import commands, tasks
from discord.ext.commands import BadArgument, CommandNotFound, MaxConcurrencyReached

from utils import bot_check, splittime, timestring, log_command


def adminCheck(ctx):
    return ctx.channel.id == 706953015415930941


class Members(commands.Cog):


    def __init__(self, client):
        self.client = client

        self.update_count.start() # noqa pylint: disable=no-member

    def cog_unload(self):

        self.update_count.cancel() # noqa pylint: disable=no-member
    

    @commands.command()
    @commands.check(adminCheck)
    async def memberupdate(self, ctx):
        guild = self.client.get_guild(692906379203313695)
        membercountchannel = self.client.membercountchannel
        membercount = len(list(filter(lambda x: not guild.get_member(x.id).bot ,guild.members)))
        await membercountchannel.edit(name=f"Members: {membercount}")
        await ctx.send('Successfully updated member count.')

    
    @commands.Cog.listener()
    async def on_member_update(self, before, after):

        if before.nick != after.nick:

            async with self.client.pool.acquire() as db:
                await db.set_member_val(after.id, 'nick', after.nick)

    
    @commands.Cog.listener()
    async def on_user_update(self, before, after):

        if before.name != after.name:

            async with self.client.pool.acquire() as db:
                await db.set_member_val(after.id, 'name', after.name)


    @commands.Cog.listener()
    async def on_member_join(self, member):

        guild = self.client.mainGuild
        
        if member.bot:
            botrole = guild.get_role(706026795413143553)
            await member.add_roles(botrole)
            return

        channel = self.client.welcomeChannel
        poor = guild.get_role(692952611141451787)
        alreadyin = False

        await channel.send(f"Hey {member.mention}, welcome to **The Hierarchy**! Please check <#692951648410140722> before you do anything else!")
        await member.add_roles(poor)
        
        generalchannel = self.client.get_channel(692906379203313698)
        joinEmbed = discord.Embed(color=0x2feb61)
        joinEmbed.set_author(name=f"{member.name} just joined!", icon_url=member.avatar_url_as(static_format='jpg'))
        await generalchannel.send(embed=joinEmbed)

        async with self.client.pool.acquire() as db:


            alreadyin = bool(await db.fetchval('SELECT id FROM members WHERE id = $1;', member.id))
            
            # mutes
            with open('./storage/jsons/mutes.json') as f:
                mutes = json.load(f)

            if str(member.id) in mutes:

                if mutes[str(member.id)] > time.time():
                    mute_role = guild.get_role(743255783055163392)
                    await member.add_roles(mute_role)

                    if self.client.get_cog('Admin'):
                        asyncio.create_task(self.client.get_cog('Admin').wait_until_unmute(str(member.id), mutes[str(member.id)]), name=f"unmute {member.id}")
                
                else:
                    del mutes[str(member.id)]
                    with open(f'./storage/jsons/mutes.json', 'w') as f:
                        json.dump(mutes, f, indent=2)

            
            # rank leaderboard
            if self.client.get_cog('Leveling'):
                asyncio.create_task(self.client.get_cog('Leveling').rank_leaderboard())
                            
            if alreadyin == False:

                await db.execute('INSERT INTO members (id) VALUES ($1);', member.id)
                
                try:
                    await member.send('*This is the only automated DM you will ever recieve*\n\nHey, you look new to the server! If you want, feel free to DM me `tutorial` and I\'ll walk you through the basics!')
                except:
                    pass

            await db.execute('UPDATE members SET name = $1, nick = NULL, in_guild = TRUE WHERE id = $2', member.name, member.id)
        
            await db.leaderboard()


    @commands.Cog.listener()
    async def on_member_remove(self, member):
        if member.bot:
            return

        guild = self.client.mainGuild

        channel = self.client.get_channel(692956542437425153)

        await channel.send(f"{member.mention} has left **The Hierarchy**. Too bad for them.")

        # heists
        if self.client.heist:

            if member.id in self.client.heist["participants"]:
                self.client.heist["participants"].remove(member.id)

                asyncio.create_task( self.client.heist["location"].send(f"**{member.name}** has left the server and the heist.") )

            elif member.id == self.client.heist["victim"]:
                self.client.heist_task.cancel()
                asyncio.create_task( self.client.heist["location"].send(f"**{member.name}** has left the server. Heist cancelled.") )
                self.client.heist = {}


        if self.client.get_cog('Leveling'):
            asyncio.create_task(self.client.get_cog('Leveling').rank_leaderboard())


        # mutes        
        for task in asyncio.all_tasks():
            if task.get_name() == f'unmute {member.id}':
                task.cancel()
                break

        # gangs
        async with self.client.pool.acquire() as db:

            await db.set_member_val(member.id, 'in_guild', False)


            gang = await db.fetchrow('SELECT name, owner, members, role_id FROM gangs WHERE owner = $1 OR $1 = ANY(members);', member.id)


            if gang:

                name, owner, members, role_id = gang


                if member.id == owner:
                    await db.execute('DELETE FROM gangs WHERE name = $1;', name)

                    if role_id:
                        role = guild.get_role(role_id)
                        await role.delete(reason="Gang role deleted")

                else:
                    
                    members.remove(member.id)
                    await db.execute('UPDATE gangs SET members = $1 WHERE name = $2;', members, name)


                    if len(members) <= 2:
                        
                        if role_id:
                            role = guild.get_role(role_id)

                            await role.delete(reason="Gang role deleted")
                            await db.execute('UPDATE gangs SET role_id = NULL WHERE name = $1;', name)

                
            await db.leaderboard()
                

    @tasks.loop(minutes=10)
    async def update_count(self):
        guild = self.client.mainGuild

        membercountchannel = self.client.membercountchannel

        membercount = len(list(filter(lambda x: not guild.get_member(x.id).bot ,guild.members)))
        asyncio.create_task( membercountchannel.edit(name=f"Members: {membercount}") )
                
def setup(client):
    client.add_cog(Members(client))
