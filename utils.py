# pylint: disable=anomalous-backslash-in-string

import discord
import json
import time
from collections import Counter
from datetime import datetime


async def bot_check(client, ctx, member):

    if member.id == client.user.id:
        await ctx.send("Why me?")
        return False

    elif member.bot:
        await ctx.send("Bots don't play!")
        return False
    
    else:
        return True


# time functions

def splittime(seconds):
    seconds -= int(time.time())

    minutes = seconds // 60
    rseconds = seconds % 60

    hours = minutes // 60
    rminutes = minutes % 60

    return f"{hours}h {rminutes}m {rseconds}s"

def minisplittime(minutes):

    hours = minutes // 60
    rminutes = minutes % 60
    
    return f"{hours}h {rminutes}m"

def timestring(string):
    string = string.lower().split()
    total = 0
    keys = {'d': 86400, 'h': 3600, 'm': 60, 's': 1}

    try:
        for combo in string:

            if not combo.endswith(tuple(keys)):
                raise ValueError()
            
            for key in keys:
                if combo.endswith(key):
                    total += int(combo[:-1]) * keys[key]
                    break

    except:
        total = None
    
    return total



async def log_command(client, ctx):

    command_logs = client.get_channel(755851445303115856)

    embed = discord.Embed(color=0xf56451, title="Command Used", timestamp=datetime.now())
    embed.set_author(name=f"{ctx.author.name}#{ctx.author.discriminator}", icon_url=ctx.author.avatar_url_as(static_format='jpg'))

    embed.add_field(name="Command", value=f"`{ctx.message.content}`")

    embed.add_field(name="Channel", value=ctx.channel.mention)

    embed.add_field(name="Jump", value=f"[Click Here]({ctx.message.jump_url})")

    await command_logs.send(embed=embed)