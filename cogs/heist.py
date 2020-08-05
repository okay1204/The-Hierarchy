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

# To import from different path
import sys
sys.path.insert(1 , os.getcwd())

from utils import (read_value, write_value, update_total, leaderboard,
rolecheck, splittime, open_heist, bot_check, in_use, jail_heist_check, around,
remove_item, remove_use, add_item, write_heist, add_use)

class heist(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.heisttimer.start() # noqa pylint: disable=no-member

    def cog_unload(self):
        self.heisttimer.cancel() # noqa pylint: disable=no-member

    @tasks.loop(seconds=1)
    async def heisttimer(self):
        heist = open_heist()
        if heist["heistt"] > 0:
            heist["heistt"] -= 1
            write_heist(heist)
            if heist["heistt"] == 0:
                channel = self.client.get_channel(heist["heistl"])
                if len(heist["heistp"]) < 3:
                    heist["heistl"] = 0
                    heist["oheist"] = "False"
                    heist["heistp"] = []
                    heist["heistv"] = 0
                    write_heist(heist)
                    await channel.send("Heist cancelled: Not enough people joined.")
                else:
                    guild = self.client.get_guild(692906379203313695)
                    total = 0
                    for userid in heist["heistp"]:
                        heistamount = random.randint(40,50)
                        write_value(userid, 'heistamount', heistamount)
                        total += heistamount
                        
                    while read_value(heist['heistv'], 'bank') < total:
                        total2 = 0
                        for userid2 in heist["heistp"]:
                            heistamount = read_value(userid2, 'heistamount')
                            heistamount -= 1
                            total2 += heistamount
                            write_value(userid2, 'heistamount', heistamount)
                            total = total2
                                
                    embed = discord.Embed(color=0xed1f1f)
                    embed.set_author(name="Heist results")
                    for userid in heist["heistp"]:
                        if random.randint(1,4) == 1:
                            gotaway = False
                            if 'gun' in in_use(userid):
                                if random.randint(1,2) == 1:
                                    embed.add_field(name=f'{guild.get_member(userid).name}', value=f'Caught, got away with their gun.', inline=True)
                                    gotaway = True
                            if gotaway == False:
                                embed.add_field(name=f'{guild.get_member(userid).name}', value=f'Caught, jailed for 3h.', inline=True)
                                jailtime = int(time.time()) + 10800
                                write_value(userid, 'jailtime', jailtime)
                            await rolecheck(self.client, userid)
                        else:
                            heistamount = read_value(userid, "heistamount")
                            embed.add_field(name=f'{guild.get_member(userid).name}', value=f'Got away with ${heistamount}.')
                            money = read_value(userid, "money")
                            money += heistamount
                            write_value(userid, "money", money)
                            update_total(userid)
                            bank = read_value(heist["heistv"], "bank")
                            bank -= heistamount
                            write_value(heist["heistv"], "bank", bank)
                            update_total(heist["heistv"])

                    await rolecheck(self.client, heist["heistv"])

                    channel = self.client.get_channel(heist["heistl"])
                    await channel.send(embed=embed)
                    heist["heistv"] = "None"
                    heist["heistt"] = 0
                    heist["heistp"] = []
                    heist["heistl"] = "None"
                    heist["oheist"] = "False"
                    write_heist(heist)
                    conn = sqlite3.connect('../storage/databases/hierarchy.db')
                    c = conn.cursor()
                    c.execute(f"UPDATE heist SET cooldown = {int(time.time())+9000}")
                    conn.commit()
                    conn.close()
                    await leaderboard(self.client)

def setup(client):
    client.add_cog(heist(client))