# pylint: disable=import-error

import asyncio
import json
import random
import sqlite3
import time
import os
import datetime
from sqlite3 import Error

import discord
from discord.ext import commands, tasks
from discord.ext.commands import BadArgument, CommandNotFound, MaxConcurrencyReached


def adminCheck(ctx):
    return ctx.channel.id == 706953015415930941


class members(commands.Cog):


    def __init__(self, client):
        self.client = client


    

    @commands.command()
    @commands.check(adminCheck)
    async def memberupdate(self, ctx):
        guild = self.client.get_guild(692906379203313695)
        membercountchannel = self.client.membercountchannel
        membercount = len(list(filter(lambda x: not guild.get_member(x.id).bot ,guild.members)))
        await membercountchannel.edit(name=f"Members: {membercount}")
        await ctx.send('Successfully updated member count.')

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

        conn = sqlite3.connect('./storage/databases/hierarchy.db')
        c = conn.cursor()
        c.execute('SELECT id FROM members')
        users = c.fetchall()
        for person in users:
            if member.id == person[0]:
                alreadyin = True
                break

    

        membercountchannel = self.client.membercountchannel
        membercount = len(list(filter(lambda x: not guild.get_member(x.id).bot ,guild.members)))
        await membercountchannel.edit(name=f"Members: {membercount}")
            
                        
        if alreadyin == False:
            c.execute(f'INSERT INTO members (id) VALUES ({member.id})')
            conn.commit()
            conn.close()
            await asyncio.sleep(30)
                
            #checking if member is still in server
            member = guild.get_member(member.id)
            if not member:
                return
            
            try:
                await member.send('*This is the only automated DM you will ever recieve*\n\nHey, you look new to the server! If you want, feel free to DM me `tutorial` and I\'ll walk you through the basics!')
            except:
                pass

        else:
            conn.close()


    @commands.Cog.listener()
    async def on_member_remove(self, member):
        if member.bot:
            return

        guild = self.client.mainGuild

        channel = self.client.get_channel(692956542437425153)

        await channel.send(f"{member.mention} has left **The Hierarchy**. Too bad for them.")

        membercountchannel = self.client.membercountchannel
        membercount = len(list(filter(lambda x: not guild.get_member(x.id).bot ,guild.members)))
        await membercountchannel.edit(name=f"Members: {membercount}")


        conn = sqlite3.connect('./storage/databases/gangs.db')
        c = conn.cursor()
        c.execute('SELECT name, owner, members, role_id, img_location FROM gangs')
        gangs = c.fetchall()
        conn.close()

        for gang in gangs:

            if str(member.id) in gang[2].split():
                
                members = gang[2].split()
                members.remove(str(member.id))

                if len(members) < 2:
                    
                    if gang[3]:
                        role = guild.get_role(gang[3])

                        await role.delete(reason="Gang role deleted")

                        conn = sqlite3.connect('./storage/databases/gangs.db')
                        c = conn.cursor()
                        c.execute('UPDATE gangs SET role_id = null WHERE name = ?', (gang[0],))
                        conn.commit()
                        conn.close()
                        

                members = " ".join(members)

                conn = sqlite3.connect('./storage/databases/gangs.db')
                c = conn.cursor()
                c.execute('UPDATE gangs SET members = ? WHERE name = ?', (members, gang[0]))
                conn.commit()
                conn.close()
                return
                


            elif member.id == gang[1]:
                

                if gang[3]:
                    role = guild.get_role(gang[3])

                    await role.delete(reason="Gang role deleted")

                    conn = sqlite3.connect('./storage/databases/gangs.db')
                    c = conn.cursor()
                    c.execute('UPDATE gangs SET role_id = null WHERE name = ?', (gang[0],))
                    conn.commit()
                    conn.close()
                
                
                if gang[4]:
                    os.remove(gang[4])

                conn = sqlite3.connect('./storage/databases/gangs.db')
                c = conn.cursor()
                c.execute('DELETE FROM gangs WHERE name = ?', (gang[0],))
                conn.commit()
                conn.close()
                
                
def setup(client):
    client.add_cog(members(client))
