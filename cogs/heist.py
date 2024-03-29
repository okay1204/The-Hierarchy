# pylint: disable=import-error

import asyncio
import json
import random
import sqlite3
import time
import os
import datetime
from sqlite3 import Error

import nextcord
from nextcord.ext import commands, tasks
from nextcord.ext.commands import BadArgument, CommandNotFound, MaxConcurrencyReached

# To import from different path
import sys
sys.path.insert(1 , os.getcwd())

from utils import bot_check, splittime, timestring, log_command

class Heist(commands.Cog):

    def __init__(self, client):
        self.client = client

    async def cog_check(self, ctx):
        if ctx.channel.category.id != self.client.rightCategory:
            return False
        else:
            return True

    async def heist(self):

        await asyncio.sleep(self.client.heist["start"]-int(time.time()))

        heist = self.client.heist

        channel = heist["location"]

        if len(heist["participants"]) < 3:
            self.client.heist = {}
            return await channel.send("Heist cancelled: Not enough people joined.")


        guild = self.client.mainGuild

        stolen = 0
        
        amounts = {}

        rolecheck_tasks = []

        async with self.client.pool.acquire() as db:

            if self.client.heist["victim"] == "bank":

                for userid in heist["participants"]:
                    heistamount = random.randint(60,70) # bank gives more money

                    amounts[userid] = heistamount
                    stolen += heistamount

            else:

                for userid in heist["participants"]:
                    heistamount = random.randint(40,50)

                    amounts[userid] = heistamount
                    stolen += heistamount

                victim_bank = await db.get_member_val(heist["victim"], 'bank')

                # in case does not have enough money
                while victim_bank < stolen:

                    temp_total = 0

                    for userid in heist["participants"]:

                        amounts[userid] -= 1
                        temp_total += amounts[userid]

                    stolen = temp_total

                        
            embed = nextcord.Embed(color=0xed1f1f, title="Heist Results")

            done_stolen = 0

        

            for userid in heist["participants"]:

                if random.randint(1,4) == 1:

                    gotaway = False
                    if 'lawyer' in await db.in_use(userid):

                        if random.getrandbits(1):
                            embed.add_field(name=f'{guild.get_member(userid).name}', value=f'Caught, avoided jail with their lawyer.', inline=True)
                            gotaway = True

                    if not gotaway:

                        embed.add_field(name=f'{guild.get_member(userid).name}', value=f'Caught, jailed for 3h.', inline=True)

                        jailtime = int(time.time()) + 10800
                        await db.set_member_val(userid, 'jailtime', jailtime)

                    rolecheck_tasks.append( db.rolecheck(userid) )

                else:
                    
                    embed.add_field(name=f'{guild.get_member(userid).name}', value=f'Got away with ${amounts[userid]}.')

                    money = await db.get_member_val(userid, "money")
                    money += amounts[userid]

                    done_stolen += amounts[userid]

                    await db.set_member_val(userid, "money", money)

            embed.set_footer(text=f"Total stolen: ${done_stolen}")


            if self.client.heist["victim"] != "bank":
                victim_bank -= done_stolen
            
                await db.set_member_val(heist["victim"], "bank", victim_bank)

                rolecheck_tasks.append( db.rolecheck(heist["victim"]) )


            await channel.send(embed=embed)

            self.client.heist = {}

            with open(f'./storage/jsons/heist cooldown.json', 'w') as f:
                json.dump(int(time.time())+9000, f) # 3 hours

            await db.leaderboard()

            # doing all rolechecks at the end
            for task in rolecheck_tasks:
                await task


    @commands.group(name="heist", invoke_without_command=True)
    async def heist_group(self, ctx):
        await ctx.send(f'Incorrect command usage:\n`.heist start/join/list/time/leave/cancel`')

    @heist_group.command()
    async def start(self, ctx, *, target=None):

        with open("./storage/jsons/heist cooldown.json") as f:
            heistc = json.load(f)


        async with self.client.pool.acquire() as db:
            jailtime = await db.get_member_val(ctx.author.id, 'jailtime')        
            if jailtime > time.time():
                return await ctx.send(f'You are still in jail for {splittime(jailtime)}.')


            if heistc > time.time():
                return await ctx.send(f'Everyone must wait {splittime(heistc)} before another heist be made.')
                

            elif self.client.heist:
                return await ctx.send(f"There is an ongoing heist right now.")

            elif not target:
                return await ctx.send(f'Incorrect command usage:\n`.heist start member` or `.heist start bank`')

            if self.client.get_cog('Gambling'):
                if self.client.get_cog('Gambling').roulette_members:
                    return await ctx.send('You cannot start a heist during a roulette.')

            if target.lower() == "bank":
                
                self.client.heist = {"victim": "bank", "participants": [ctx.author.id], "location": ctx.channel, "start": int(time.time())+120}

            else:
                try:
                    member = await commands.MemberConverter().convert(ctx, target)
                except:
                    return await ctx.send("Member not found.")

                if ctx.author == member:
                    return await ctx.send(f"You can't heist yourself.")
                    
                elif not await bot_check(self.client, ctx, member): return

                elif await db.get_member_val(member.id, 'bank') < 100:
                    return await ctx.send(f'The victim must have at least $100 in their bank in order to be heisted from.')

                self.client.heist = {"victim": member.id, "participants": [ctx.author.id], "location": ctx.channel, "start": int(time.time())+120}
                    

            await ctx.send(f'Heist started. You have two minutes to gather at least two more people to join the heist. <@&761786482771099678>') # end part is mention for heist role

            self.client.heist_task = asyncio.create_task( self.heist() )

    @heist_group.command()
    async def join(self, ctx):

        async with self.client.pool.acquire() as db:
            jailtime = await db.get_member_val(ctx.author.id, 'jailtime')        
            if jailtime > time.time():
                return await ctx.send(f'You are still in jail for {splittime(jailtime)}.')

        if not self.client.heist: return await ctx.send(f"There is no ongoing heist right now.")

        elif self.client.heist["victim"] == ctx.author.id: return await ctx.send(f"You are the target of this heist.")
                  
        if ctx.author.id in self.client.heist["participants"]: return await ctx.send(f"You are already in this heist.")

        self.client.heist["participants"].append(ctx.author.id)
        guild = self.client.mainGuild

        if self.client.heist["victim"] == "bank":
            await ctx.send(f'**{ctx.author.name}** has joined the heist on the bank.')
        else:
            await ctx.send(f'**{ctx.author.name}** has joined the heist on **{guild.get_member(self.client.heist["victim"]).name}**.')

    @heist_group.command()
    async def leave(self, ctx):

        if not self.client.heist: return await ctx.send(f"There is no ongoing heist right now.")

        elif ctx.author.id not in self.client.heist["participants"]: return await ctx.send("You aren't participating in a heist.")
            
        elif self.client.heist["participants"][0] == ctx.author.id: return await ctx.send("You are leading this heist.")

            
        self.client.heist["participants"].remove(ctx.author.id)
        guild = self.client.mainGuild

        if self.client.heist["victim"] == "bank":
            await ctx.send(f'**{ctx.author.name}** has left the heist on the bank.')
        else:
            await ctx.send(f'**{ctx.author.name}** has left the heist on **{guild.get_member(self.client.heist["victim"]).name}**.')

    @heist_group.command()
    async def cancel(self, ctx):

        if not self.client.heist: return await ctx.send(f"There is no ongoing heist right now.")

        elif ctx.author.id not in self.client.heist["participants"]: return await ctx.send("You aren't participating in the heist.")
            
        elif self.client.heist["participants"][0] != ctx.author.id: return await ctx.send("You are not leading this heist.")
            
        
        self.client.heist_task.cancel()
        self.client.heist = {}
        await ctx.send("Heist cancelled: Heist cancelled by leader.")

    @heist_group.command(name="list")
    async def heist_list(self, ctx):

        if not self.client.heist: return await ctx.send(f"There is no ongoing heist right now.")

        guild = self.client.mainGuild

        if self.client.heist["victim"] == "bank":
            embed = nextcord.Embed(color=0xff1414, title=f'Heist on the bank')
        else:
            embed = nextcord.Embed(color=0xff1414, title=f'Heist on {guild.get_member(self.client.heist["victim"]).name}')

        for person in self.client.heist["participants"]:
            name = nextcord.utils.escape_markdown(guild.get_member(person).name)
            embed.add_field(value=name, name=nextcord.utils.escape_markdown('___'), inline=True)

        await ctx.send(embed=embed)

    @heist_group.command(name="time")
    async def heist_time(self, ctx):

        if not self.client.heist: return await ctx.send(f"There is no ongoing heist right now.")

        guild = self.client.mainGuild

        if self.client.heist["victim"] == "bank":
            await ctx.send(f'The heist on the bank will start in {self.client.heist["start"]-int(time.time())} seconds.') 
        else:
            await ctx.send(f'The heist on **{guild.get_member(self.client.heist["victim"]).name}** will start in {self.client.heist["start"]-int(time.time())} seconds.') 

def setup(client):
    client.add_cog(Heist(client))