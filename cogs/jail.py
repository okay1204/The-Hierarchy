from discord.ext import commands
import discord

class Jail(commands.Cog):
    
    def __init__(self, client):
        self.client = client

    


def setup(client):
    client.add_cog(Jail(client))