# pylint: disable=import-error

import discord
from discord.ext import commands
import json
import random
import sqlite3
from sqlite3 import Error
import time
import os

# To import from different path
import sys
sys.path.insert(1 , os.getcwd())

from utils import bot_check, splittime, timestring, log_command
class Games(commands.Cog):

    def __init__(self, client):
        self.client = client

    async def cog_check(self, ctx):
        if ctx.channel.category.id != self.client.rightCategory:
            return False
        else:
            return True
    
    @commands.command()
    async def rps(self, ctx, entry=None):
        author = ctx.author

        if not await jail_heist_check(self.client, ctx, author):
            return

        rpsc = read_value(author.id, 'rpsc')
        
        if rpsc > int(time.time()):
            await ctx.send(f'You must wait {splittime(rpsc)} before you can play again.')
            return

        if not entry:
            await ctx.send("Incorrect command usage:\n`.rps rock/paper/scissors`")
            return
            
        entry = entry.capitalize()

        allowed = ["Rock", "Paper", "Scissors", "R", "P", "S"]

        if entry not in allowed:
            await ctx.send("Incorrect command usage:\n`.rps rock/paper/scissors`")
            return

        if entry == 'R':
            entry = 'Rock'
        elif entry == 'P':
            entry = 'Paper'
        elif entry == 'S':
            entry = 'Scissors'
    
        pc = random.choice(['Rock','Paper','Scissors'])
        rmoney = random.randint(2,5)

        key = {"Rock":["Scissors","Paper"], "Paper":["Rock", "Scissors"], "Scissors":["Paper", "Rock"]}

        if entry.capitalize() == pc:
            await ctx.send(f"{pc}\nTie.")

        elif key[entry][0] == pc:
            await ctx.send(f"{pc}\nYou win. ${rmoney} was added to your account.")
            money = read_value(author.id, 'money')
            money += rmoney
            write_value(author.id, 'money', money)

        elif key[entry][1] == pc:
            await ctx.send(f"{pc}\nYou lose. L")

        rpsc = int(time.time()) + 8
        write_value(author.id, 'rpsc', rpsc)
        await leaderboard(self.client)
        await rolecheck(self.client, author.id)

        
    @commands.command()
    async def roll(self, ctx):
        author = ctx.author


        if not await jail_heist_check(self.client, ctx, author):
            return

        rpsc = read_value(author.id, 'rpsc')

        if rpsc > int(time.time()):
            await ctx.send(f'You must wait {splittime(rpsc)} before you can play again.')
            return


        rollp = random.randint(1,6)
        rollb = random.randint(1,6)
        text = f'🎲 **{author.name}** rolled {rollp}. 🎲\n🎲 **The Hierarchy** rolled {rollb}. 🎲\n'
        if rollp > rollb:
            text += f'You won. $2 was added to your account.'
            money = read_value(author.id, 'money')
            money += 2
            write_value(author.id, 'money', money)
        elif rollp < rollb:
            text += f'You lost.'
        elif rollp == rollb:
            text += f'Tie. $1 was added to your account.'
            money = read_value(author.id, 'money')
            money += 1
            write_value(author.id, 'money', money)

        await ctx.send(text)
        rpsc = int(time.time()) + 8
        write_value(author.id, 'rpsc', rpsc)
        await leaderboard(self.client)
        await rolecheck(self.client, author.id)


    @commands.command()
    async def guess(self, ctx, entry=None):
        author = ctx.author

        if not await jail_heist_check(self.client, ctx, author):
            return

        rpsc = read_value(author.id, 'rpsc')
        
        if rpsc > int(time.time()):
            await ctx.send(f'You must wait {splittime(rpsc)} before you can play again.')
            return

        if not entry:
            await ctx.send("Incorrect command usage:\n`.guess number`")
            return
            
        entry = entry.lower()
        try:
            entry = int(entry)
            if entry < 1 or entry > 10:
                await ctx.send("Enter a number from 1-10.")
                return
        except:
            await ctx.send("Incorrect command usage:\n`.guess number`")
            return

        number = random.randint(1,10)
        rmoney = random.randint(10,15)
        if entry == number:
            await ctx.send(f"You won. ${rmoney} was added to your account.")
            money = read_value(author.id, 'money')
            money += rmoney
            write_value(author.id, 'money', money)
            
        elif entry != number:
            await ctx.send(f"You lost. The number was {number}.")


        rpsc = int(time.time()) + 8
        write_value(author.id, 'rpsc', rpsc)

        await leaderboard(self.client)
        await rolecheck(self.client, author.id)



def setup(client):
    client.add_cog(Games(client))










        
