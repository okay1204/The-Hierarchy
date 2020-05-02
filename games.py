import discord
from discord.ext import commands
import json
import random
from utils import *

class games(commands.Cog):

    def __init__(self, client):
        self.client = client

    
    @commands.command()
    @commands.check(rightCategory)
    async def rps(self, ctx, entry=None):
        author = ctx.author
        hierarchy = open_json()
        for person in hierarchy:
            if str(author.id) == person["user"]:
                if person["jailtime"] > 0:
                    await ctx.send(f'You are still in jail for {splittime(person["jailtime"])}.')
                    return
                if person["rpsc"] > 0:
                    await ctx.send(f'You must wait {splittime(person["rpsc"])} before you can play again.')
                    return
        hierarchystats = open_json2()
        if hierarchystats["heistv"] == str(author.id):
            await ctx.send(f"You are currently being targeted for a heist.")
            return
        if author.id in hierarchystats["heistp"]:
            await ctx.send(f"You are participating in a heist right now.")
            return
        if not entry:
            await ctx.send("Enter rock, paper, or scissors.")
            return    
        if entry.lower() != "rock" and entry.lower() != "paper" and entry.lower() != "scissors" and entry.lower() != "r" and entry.lower() != "p" and entry.lower() != "s":
            await ctx.send("Enter rock, paper, or scissors.")
            return
        if entry.lower() == 'r':
            entry = 'rock'
        if entry.lower() == 'p':
            entry = 'paper'
        if entry.lower() == 's':
            entry = 'scissors'
        
        choices = ['Rock','Paper','Scissors']
        pc = random.choice(choices)
        rmoney = random.randint(2,5)
        await ctx.send(pc)
        if entry.lower() == 'rock' and pc =='Rock':
            await ctx.send("Tie.")
        if entry.lower() == 'rock' and pc =='Paper':
            await ctx.send("You lose.")
        if entry.lower() == 'rock' and pc =='Scissors':
            await ctx.send(f'You win. ${rmoney} was added to your account.')
            for person in hierarchy:
                if person["user"] == str(author.id):
                    person["money"] += rmoney
                    person["total"] = person["money"] + person["bank"]
                    write_json(hierarchy)
        if entry.lower() == 'paper' and pc =='Rock':
            await ctx.send(f'You win. ${rmoney} was added to your account.')
            for person in hierarchy:
                if person["user"] == str(author.id):
                    person["money"] += rmoney
                    person["total"] = person["money"] + person["bank"]
                    write_json(hierarchy)
        if entry.lower() == 'paper' and pc =='Paper':
            await ctx.send("Tie.")
        if entry.lower() == 'paper' and pc =='Scissors':
            await ctx.send("You lose.")  
        if entry.lower() == 'scissors' and pc =='Rock':
            await ctx.send("You lose.")
        if entry.lower() == 'scissors' and pc =='Paper':
            await ctx.send(f'You win. ${rmoney} was added to your account.')
            for person in hierarchy:
                if person["user"] == str(author.id):
                    person["money"] += rmoney
                    person["total"] = person["money"] + person["bank"]
                    write_json(hierarchy)
        if entry.lower() == 'scissors' and pc =='Scissors':
            await ctx.send("Tie.")
        for person in hierarchy:
                if person["user"] == str(author.id):
                    person["rpsc"] = 10
                    write_json(hierarchy)
        await leaderboard(self.client)
        await rolecheck(self.client, author.id)

        
    @commands.command()
    @commands.check(rightCategory)
    async def roll(self, ctx):
        author = ctx.author
        hierarchy = open_json()
        for person in hierarchy:
            if str(author.id) == person["user"]:
                if person["jailtime"] > 0:
                    await ctx.send(f'You are still in jail for {splittime(person["jailtime"])}.')
                    return
                if person["rpsc"] > 0:
                    await ctx.send(f'You must wait {splittime(person["rpsc"])} before you can play again.')
                    return
        hierarchystats = open_json2()
        if hierarchystats["heistv"] == str(author.id):
            await ctx.send(f"You are currently being targeted for a heist.")
            return
        if author.id in hierarchystats["heistp"]:
            await ctx.send(f"You are participating in a heist right now.")
            return
        for person in hierarchy:
            if str(author.id) == person["user"]:
                rollp = random.randint(1,6)
                rollb = random.randint(1,6)
                await ctx.send(f'**{author.name}** rolled {rollp}.\n**The Hierarchy** rolled {rollb}.')
                if rollp > rollb:
                    await ctx.send(f'You won. $2 was added to your account.')
                    person['money'] += 2
                elif rollp < rollb:
                    await ctx.send(f'You lost.')
                elif rollp == rollb:
                    await ctx.send(f'Tie. $1 was added to your account.')
                    person['money'] += 1
                person["rpsc"] = 10
                person["total"] = person["money"] + person["bank"]
                write_json(hierarchy)

        await leaderboard(self.client)
        await rolecheck(self.client, author.id)


    @commands.command()
    @commands.check(rightCategory)
    async def guess(self, ctx, entry=None):
        author = ctx.author
        hierarchy = open_json()
        for person in hierarchy:
            if str(author.id) == person["user"]:
                if person["jailtime"] > 0:
                    await ctx.send(f'You are still in jail for {splittime(person["jailtime"])}.')
                    return
                if person["rpsc"] > 0:
                    await ctx.send(f'You must wait {splittime(person["rpsc"])} before you can play again.')
                    return
        hierarchystats = open_json2()
        if hierarchystats["heistv"] == str(author.id):
            await ctx.send(f"You are currently being targeted for a heist.")
            return
        if author.id in hierarchystats["heistp"]:
            await ctx.send(f"You are participating in a heist right now.")
            return
        if not entry:
            await ctx.send("Enter a number from 1-10.")
            return
        try:
            entry = int(entry)
            if entry < 1 or entry > 10:
                await ctx.send("Enter a number from 1-10.")
                return
        except:
            await ctx.send("Enter a valid number from 1-10.")
            return

        number = random.randint(1,10)
        rmoney = random.randint(10,15)
        if entry == number:
            await ctx.send(f"You won. ${rmoney} was added to your account.")
            for person in hierarchy:
                if person["user"] == str(author.id):
                    person["money"] += rmoney
                    person["rpsc"] = 10
                    person["total"] = person["money"] + person["bank"]
        elif entry != number:
            await ctx.send(f"You lost. The number was {number}.")
            for person in hierarchy:
                if person["user"] == str(author.id):
                    person["rpsc"] = 10
        write_json(hierarchy)

        await leaderboard(self.client)
        await rolecheck(self.client, author.id)



def setup(client):
    client.add_cog(games(client))










        
