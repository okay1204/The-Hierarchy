import discord
from discord.ext import commands, tasks

client = commands.Bot(command_prefix = '.')
client.remove_command('help')


class reactions(commands.Cog):

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

            if str(payload.emoji) == '🔔':
                role = guild.get_role(716818513708187668) # announcements

            elif str(payload.emoji) == '✅':
                role = guild.get_role(716818605110460418) # new features

            elif str(payload.emoji) == '☑️':
                role = guild.get_role(716818729987473408) # polls


            elif str(payload.emoji) == '🤝':
                role = guild.get_role(716836063150342184) # partnerships

            elif str(payload.emoji) == '🏦':
                role = guild.get_role(698322063206776972) # bank

            elif str(payload.emoji) == '💰':
                role = guild.get_role(698321954742075504) # tax

            elif str(payload.emoji) == '🛒':
                role = guild.get_role(716818790947618857) # shop

            elif str(payload.emoji) == '⏱️':
                role = guild.get_role(727725637317427332) # boost

            await user.add_roles(role)

        elif payload.channel_id == 725065871554510848: # Self roles

            if str(payload.emoji) == '♂️':
                role = guild.get_role(725146445656883271) # male

            elif str(payload.emoji) == '♀️':
                role = guild.get_role(725146537201631272) # female

            elif str(payload.emoji) == '❓':
                role = guild.get_role(725146594365931581) # other

            elif str(payload.emoji) == '🇺🇸':
                role = guild.get_role(725153499683225702) # us

            elif str(payload.emoji) == '🇧🇷':
                role = guild.get_role(725154063582494791) # br

            elif str(payload.emoji) == '🇨🇳':
                role = guild.get_role(725154438594953267) # ch

            elif str(payload.emoji) == '🇪🇺':
                role = guild.get_role(725154767239774231) # eu

            elif str(payload.emoji) == '🇿🇦':
                role = guild.get_role(725155259491680266) # af

            elif str(payload.emoji) == '🇦🇺':
                role = guild.get_role(725155549938974761) # au

            elif str(payload.emoji) == '🇦🇶':
                role = guild.get_role(725155788699467857) #aq

            elif str(payload.emoji) == '♈':
                role = guild.get_role(725157028229808248) # aries

            elif str(payload.emoji) == '♉':
                role = guild.get_role(725157846488186910) # taurus

            elif str(payload.emoji) == '♊':
                role = guild.get_role(725158133235974294) #gemini

            elif str(payload.emoji) == '♋':
                role = guild.get_role(725158441831891034) # cancer

            elif str(payload.emoji) == '♌':
                role = guild.get_role(725158644559118379) # leo

            elif str(payload.emoji) == '♍':
                role = guild.get_role(725158875463942175) # virgo

            elif str(payload.emoji) == '♎':
                role = guild.get_role(725159100232630383) # libra

            elif str(payload.emoji) == '♏':
                role = guild.get_role(725159358845157448) # scorpius

            elif str(payload.emoji) == '♐':
                role = guild.get_role(725159686164447295) # sagittarius

            elif str(payload.emoji) == '♑':
                role = guild.get_role(725159927236001924) # capricorn

            elif str(payload.emoji) == '♒':
                role = guild.get_role(725160136791818351) # aquarius

            elif str(payload.emoji) == '♓':
                role = guild.get_role(725160360797274132) # pisces
            
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
        
        if payload.message_id == 716819696346857524: # Ping roles

            if str(payload.emoji) == '🔔':
                role = guild.get_role(716818513708187668) # announcements

            elif str(payload.emoji) == '✅':
                role = guild.get_role(716818605110460418) # new features

            elif str(payload.emoji) == '☑️':
                role = guild.get_role(716818729987473408) # polls


            elif str(payload.emoji) == '🤝':
                role = guild.get_role(716836063150342184) # partnerships

            elif str(payload.emoji) == '🏦':
                role = guild.get_role(698322063206776972) # bank

            elif str(payload.emoji) == '💰':
                role = guild.get_role(698321954742075504) # tax

            elif str(payload.emoji) == '🛒':
                role = guild.get_role(716818790947618857) # shop

            elif str(payload.emoji) == '⏱️':
                role = guild.get_role(727725637317427332) # boost

            await user.remove_roles(role)

        elif payload.channel_id == 725065871554510848: # Self roles

            if str(payload.emoji) == '♂️':
                role = guild.get_role(725146445656883271) # male

            elif str(payload.emoji) == '♀️':
                role = guild.get_role(725146537201631272) # female

            elif str(payload.emoji) == '❓':
                role = guild.get_role(725146594365931581) # other

            elif str(payload.emoji) == '🇺🇸':
                role = guild.get_role(725153499683225702) # us

            elif str(payload.emoji) == '🇧🇷':
                role = guild.get_role(725154063582494791) # br

            elif str(payload.emoji) == '🇨🇳':
                role = guild.get_role(725154438594953267) # ch

            elif str(payload.emoji) == '🇪🇺':
                role = guild.get_role(725154767239774231) # eu

            elif str(payload.emoji) == '🇿🇦':
                role = guild.get_role(725155259491680266) # af

            elif str(payload.emoji) == '🇦🇺':
                role = guild.get_role(725155549938974761) # au

            elif str(payload.emoji) == '🇦🇶':
                role = guild.get_role(725155788699467857) #aq

            elif str(payload.emoji) == '♈':
                role = guild.get_role(725157028229808248) # aries

            elif str(payload.emoji) == '♉':
                role = guild.get_role(725157846488186910) # taurus

            elif str(payload.emoji) == '♊':
                role = guild.get_role(725158133235974294) #gemini

            elif str(payload.emoji) == '♋':
                role = guild.get_role(725158441831891034) # cancer

            elif str(payload.emoji) == '♌':
                role = guild.get_role(725158644559118379) # leo

            elif str(payload.emoji) == '♍':
                role = guild.get_role(725158875463942175) # virgo

            elif str(payload.emoji) == '♎':
                role = guild.get_role(725159100232630383) # libra

            elif str(payload.emoji) == '♏':
                role = guild.get_role(725159358845157448) # scorpius

            elif str(payload.emoji) == '♐':
                role = guild.get_role(725159686164447295) # sagittarius

            elif str(payload.emoji) == '♑':
                role = guild.get_role(725159927236001924) # capricorn

            elif str(payload.emoji) == '♒':
                role = guild.get_role(725160136791818351) # aquarius

            elif str(payload.emoji) == '♓':
                role = guild.get_role(725160360797274132) # pisces
            
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
    client.add_cog(reactions(client))
