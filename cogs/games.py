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

from utils import (read_value, write_value, update_total, leaderboard,
rolecheck, splittime, open_heist, bot_check, in_use, jail_heist_check, around,
remove_item, remove_use, add_item, write_heist, add_use)
class games(commands.Cog):

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

        if not await jail_heist_check(ctx, author):
            return

        rpsc = read_value(author.id, 'rpsc')
        
        if rpsc > int(time.time()):
            await ctx.send(f'You must wait {splittime(rpsc)} before you can play again.')
            return

        if not entry:
            await ctx.send("Incorrect command usage:\n`.rps rock/paper/scissors`")
            return
            
        entry = entry.lower()

        if entry != "rock" and entry != "paper" and entry != "scissors" and entry != "r" and entry != "p" and entry != "s":
            await ctx.send("Incorrect command usage:\n`.rps rock/paper/scissors`")
            return

        if entry == 'r':
            entry = 'rock'
        elif entry == 'p':
            entry = 'paper'
        elif entry == 's':
            entry = 'scissors'
        
        choices = ['Rock','Paper','Scissors']
        pc = random.choice(choices)
        rmoney = random.randint(2,5)
        await ctx.send(pc)
        if entry == 'rock' and pc =='Rock':
            await ctx.send("Tie.")
        if entry == 'rock' and pc =='Paper':
            await ctx.send("You lose.")
        if entry == 'rock' and pc =='Scissors':
            await ctx.send(f'You win. ${rmoney} was added to your account.')
            money = read_value(author.id, 'money')
            money += rmoney
            write_value(author.id, 'money', money)
            update_total(author.id)
        if entry == 'paper' and pc =='Rock':
            await ctx.send(f'You win. ${rmoney} was added to your account.')
            money = read_value(author.id, 'money')
            money += rmoney
            write_value(author.id, 'money', money)
            update_total(author.id)
        if entry == 'paper' and pc =='Paper':
            await ctx.send("Tie.")
        if entry == 'paper' and pc =='Scissors':
            await ctx.send("You lose.")  
        if entry == 'scissors' and pc =='Rock':
            await ctx.send("You lose.")
        if entry == 'scissors' and pc =='Paper':
            await ctx.send(f'You win. ${rmoney} was added to your account.')
            money = read_value(author.id, 'money')
            money += rmoney
            write_value(author.id, 'money', money)
            update_total(author.id)
        if entry == 'scissors' and pc =='Scissors':
            await ctx.send("Tie.")
        rpsc = int(time.time()) + 10
        write_value(author.id, 'rpsc', rpsc)
        await leaderboard(self.client)
        await rolecheck(self.client, author.id)

        
    @commands.command()
    async def roll(self, ctx):
        author = ctx.author


        if not await jail_heist_check(ctx, author):
            return

        rpsc = read_value(author.id, 'rpsc')

        if rpsc > int(time.time()):
            await ctx.send(f'You must wait {splittime(rpsc)} before you can play again.')
            return


        rollp = random.randint(1,6)
        rollb = random.randint(1,6)
        await ctx.send(f'🎲 **{author.name}** rolled {rollp}. 🎲\n🎲 **The Hierarchy** rolled {rollb}. 🎲')
        if rollp > rollb:
            await ctx.send(f'You won. $2 was added to your account.')
            money = read_value(author.id, 'money')
            money += 2
            write_value(author.id, 'money', money)
            update_total(author.id)
        elif rollp < rollb:
            await ctx.send(f'You lost.')
        elif rollp == rollb:
            await ctx.send(f'Tie. $1 was added to your account.')
            money = read_value(author.id, 'money')
            money += 1
            write_value(author.id, 'money', money)
            update_total(author.id)
        rpsc = int(time.time()) + 10
        write_value(author.id, 'rpsc', rpsc)
        await leaderboard(self.client)
        await rolecheck(self.client, author.id)


    @commands.command()
    async def guess(self, ctx, entry=None):
        author = ctx.author

        if not await jail_heist_check(ctx, author):
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
            update_total(author.id)
            rpsc = int(time.time()) + 10
            write_value(author.id, 'rpsc', rpsc)
        elif entry != number:
            await ctx.send(f"You lost. The number was {number}.")
            rpsc = int(time.time()) + 10
            write_value(author.id, 'rpsc', rpsc)

        await leaderboard(self.client)
        await rolecheck(self.client, author.id)



def setup(client):
    client.add_cog(games(client))










        
