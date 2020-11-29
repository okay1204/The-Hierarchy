# pylint: disable=import-error, anomalous-backslash-in-string
import discord
from discord.ext import commands, tasks
import json
import time
import os
import asyncio

# To import from different path
import sys
sys.path.insert(1 , os.getcwd())

from utils import (splittime, timestring)

class Christmas(commands.Cog):
    
    def __init__(self, client):
        self.client = client

        
    async def cog_check(self, ctx):
        if ctx.channel.category.id != self.client.rightCategory:
            return False
        else:
            return True


def setup(client):
    client.add_cog(Christmas(client))