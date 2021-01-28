import discord
from discord.ext import commands
import authinfo
import os

client = commands.Bot(command_prefix = '.', intents=discord.Intents.all())


@client.event
async def on_ready():
    print("bot ready")

@client.event
async def on_member_join(member):
    print("memer join", member.name, member.id)

@client.event
async def on_member_remove(member):
    print("memer remove", member.name, member.id)

client.run(os.environ.get("main"))