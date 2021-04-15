# pylint: disable=import-error

import asyncio
import json
import random
import time
import os
import datetime

import discord
from discord.ext import commands
from discord.ext.commands import BadArgument, CommandNotFound, MaxConcurrencyReached

# To import from different path
import sys
sys.path.insert(1 , os.getcwd())

from utils import bot_check, splittime, timestring, log_command

class Jail(commands.Cog):

    def __init__(self, client):
        self.client = client

    
    


def setup(client):
    client.add_cog(Jail(client))