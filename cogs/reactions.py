import discord
from discord.ext import commands, tasks


ping_roles = {
    '🔔': 716818513708187668, # announcements
    '✅': 716818605110460418, # new features
    '☑️': 716818729987473408, # polls
    '🤝': 716836063150342184, # partnerships
    '🏦': 698322063206776972, # bank
    '💰': 698321954742075504, # bank
    '🛒': 716818790947618857, # shop
    '⏱️': 727725637317427332, # boost
    '💸': 761786482771099678, # heists
    '👋': 848423749907775488 # welcomers
}

self_roles = {
    '♂️': 725146445656883271, # male
    '♀️': 725146537201631272, # female
    '❓': 725146594365931581, # other
    '🇺🇸': 725153499683225702, # us
    '🇧🇷': 725154063582494791, # br
    '🇨🇳': 725154438594953267, # ch
    '🇪🇺': 725154767239774231, # eu
    '🇿🇦': 725155259491680266, # af
    '🇦🇺': 725155549938974761, # au
    '🇦🇶': 725155788699467857, # aq
    '♈': 725157028229808248, # aries
    '♉': 725157846488186910, # taurus
    '♊': 725158133235974294, # gemini
    '♋': 725158441831891034, # cancer
    '♌': 725158644559118379, # leo
    '♍': 725158875463942175, # virgo
    '♎': 725159100232630383, # libra
    '♏': 725159358845157448, # scorpius
    '♐': 725159686164447295, # sagittarius
    '♑': 725159927236001924, # capricorn
    '♒': 725160136791818351, # aquaruius
    '♓': 725160360797274132 # pisces
}

class Reactions(commands.Cog):

    def __init__(self, client):
        self.client = client


    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        guild = self.client.mainGuild
        user = payload.user_id
        user = guild.get_member(user)

        if user.id == self.client.user.id:
            return


        if payload.message_id == 716819696346857524: # Ping roles

            role = guild.get_role(ping_roles[str(payload.emoji)])
            await user.add_roles(role)

        elif payload.channel_id == 725065871554510848: # Self roles

            role = guild.get_role(self_roles[str(payload.emoji)])
            await user.add_roles(role)


            # Prevent 2 reactions on one message
            selfrole = self.client.get_channel(725065871554510848)
            message = await selfrole.fetch_message(payload.message_id)
            for reaction in message.reactions:
                if str(reaction.emoji) != str(payload.emoji):
                    await self.client.http.remove_reaction(payload.channel_id, payload.message_id, reaction.emoji, payload.user_id)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):


        guild = self.client.mainGuild
        user = payload.user_id
        user = guild.get_member(user)

        if user:
            if user.id == self.client.user.id:
                return
        else:
            return
        
        if payload.message_id == 716819696346857524: # Ping roles

            role = guild.get_role(ping_roles[str(payload.emoji)])
            await user.remove_roles(role)

        elif payload.channel_id == 725065871554510848: # Self roles

            role = guild.get_role(self_roles[str(payload.emoji)])
            await user.remove_roles(role)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        ping_roles = self.client.get_channel(698318226613993553)
        message = await ping_roles.fetch_message(716819696346857524)
        for reaction in message.reactions:
            await message.remove_reaction(reaction.emoji, member)

        selfrole = self.client.get_channel(725065871554510848)
        async for message in selfrole.history():
            for reaction in message.reactions:
                await message.remove_reaction(reaction.emoji, member)

def setup(client):
    client.add_cog(Reactions(client))
