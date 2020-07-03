import discord
from discord.ext import commands, tasks
import os
import bottokens

client = commands.Bot(command_prefix = '.')
client.remove_command('help')

@client.event
async def on_ready():
    print(f"Logged in as {client.user}.\nID: {client.user.id}")
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="for reactions"))

@client.event
async def on_raw_reaction_add(payload):
    guild = client.get_guild(692906379203313695)
    user = payload.user_id
    user = guild.get_member(user)
    if user == client.user:
        return


    if payload.message_id == 716819696346857524:
        if str(payload.emoji) == '🔔':
            announcements = guild.get_role(716818513708187668)
            await user.add_roles(announcements)
        elif str(payload.emoji) == '✅':
            newfeatures = guild.get_role(716818605110460418)
            await user.add_roles(newfeatures)
        elif str(payload.emoji) == '☑️':
            polls = guild.get_role(716818729987473408)
            await user.add_roles(polls)
        elif str(payload.emoji) == '🤝':
            partnerships = guild.get_role(716836063150342184)
            await user.add_roles(partnerships)
        elif str(payload.emoji) == '🏦':
            bank = guild.get_role(698322063206776972)
            await user.add_roles(bank)
        elif str(payload.emoji) == '💰':
            tax = guild.get_role(698321954742075504)
            await user.add_roles(tax)
        elif str(payload.emoji) == '🛒':
            shop = guild.get_role(716818790947618857)
            await user.add_roles(shop)
        elif str(payload.emoji) == '⏱️':
            boost = guild.get_role(727725637317427332)
            await user.add_roles(boost)
        return

    elif payload.channel_id == 725065871554510848:
        if str(payload.emoji) == '♂️':
            male = guild.get_role(725146445656883271)
            await user.add_roles(male)
        elif str(payload.emoji) == '♀️':
            female = guild.get_role(725146537201631272)
            await user.add_roles(female)
        elif str(payload.emoji) == '❓':
            other = guild.get_role(725146594365931581)
            await user.add_roles(other)
        elif str(payload.emoji) == '🇺🇸':
            us = guild.get_role(725153499683225702)
            await user.add_roles(us)
        elif str(payload.emoji) == '🇧🇷':
            br = guild.get_role(725154063582494791)
            await user.add_roles(br)
        elif str(payload.emoji) == '🇨🇳':
            ch = guild.get_role(725154438594953267)
            await user.add_roles(ch)
        elif str(payload.emoji) == '🇪🇺':
            eu = guild.get_role(725154767239774231)
            await user.add_roles(eu)
        elif str(payload.emoji) == '🇿🇦':
            af = guild.get_role(725155259491680266)
            await user.add_roles(af)
        elif str(payload.emoji) == '🇦🇺':
            au = guild.get_role(725155549938974761)
            await user.add_roles(au)
        elif str(payload.emoji) == '🇦🇶':
            an = guild.get_role(725155788699467857)
            await user.add_roles(an)
        elif str(payload.emoji) == '♈':
            aries = guild.get_role(725157028229808248)
            await user.add_roles(aries)
        elif str(payload.emoji) == '♉':
            taurus = guild.get_role(725157846488186910)
            await user.add_roles(taurus)
        elif str(payload.emoji) == '♊':
            gemini = guild.get_role(725158133235974294)
            await user.add_roles(gemini)
        elif str(payload.emoji) == '♋':
            cancer = guild.get_role(725158441831891034)
            await user.add_roles(cancer)
        elif str(payload.emoji) == '♌':
            leo = guild.get_role(725158644559118379)
            await user.add_roles(leo)
        elif str(payload.emoji) == '♍':
            virgo = guild.get_role(725158875463942175)
            await user.add_roles(virgo)
        elif str(payload.emoji) == '♎':
            libra = guild.get_role(725159100232630383)
            await user.add_roles(libra)
        elif str(payload.emoji) == '♏':
            scorpius = guild.get_role(725159358845157448)
            await user.add_roles(scorpius)
        elif str(payload.emoji) == '♐':
            sagittarius = guild.get_role(725159686164447295)
            await user.add_roles(sagittarius)
        elif str(payload.emoji) == '♑':
            capricorn = guild.get_role(725159927236001924)
            await user.add_roles(capricorn)
        elif str(payload.emoji) == '♒':
            aquarius = guild.get_role(725160136791818351)
            await user.add_roles(aquarius)
        elif str(payload.emoji) == '♓':
            pisces = guild.get_role(725160360797274132)
            await user.add_roles(pisces)




    if payload.channel_id == 698009727803719757:
        if payload.user_id != 717086649460326510:
            pollchannel = client.get_channel(698009727803719757)
            message = await pollchannel.fetch_message(payload.message_id)
            for reaction in message.reactions:
                if str(reaction.emoji) != str(payload.emoji):
                    await client.http.remove_reaction(payload.channel_id, payload.message_id, reaction.emoji, payload.user_id)

    elif payload.channel_id == 725065871554510848:
        selfrole = client.get_channel(725065871554510848)
        message = await selfrole.fetch_message(payload.message_id)
        for reaction in message.reactions:
            if str(reaction.emoji) != str(payload.emoji):
                await client.http.remove_reaction(payload.channel_id, payload.message_id, reaction.emoji, payload.user_id)

@client.event
async def on_raw_reaction_remove(payload):
    guild = client.get_guild(692906379203313695)
    user = payload.user_id
    user = guild.get_member(user)
    if user == client.user:
        return
    
    if payload.message_id == 716819696346857524:
        if str(payload.emoji) == '🔔':
            announcements = guild.get_role(716818513708187668)
            await user.remove_roles(announcements)
        elif str(payload.emoji) == '✅':
            newfeatures = guild.get_role(716818605110460418)
            await user.remove_roles(newfeatures)
        elif str(payload.emoji) == '☑️':
            polls = guild.get_role(716818729987473408)
            await user.remove_roles(polls)
        elif str(payload.emoji) == '🤝':
            partnerships = guild.get_role(716836063150342184)
            await user.remove_roles(partnerships)
        elif str(payload.emoji) == '🏦':
            bank = guild.get_role(698322063206776972)
            await user.remove_roles(bank)
        elif str(payload.emoji) == '💰':
            tax = guild.get_role(698321954742075504)
            await user.remove_roles(tax)
        elif str(payload.emoji) == '🛒':
            shop = guild.get_role(716818790947618857)
            await user.remove_roles(shop)
        elif str(payload.emoji) == '⏱️':
            boost = guild.get_role(727725637317427332)
            await user.remove_roles(boost)

    elif payload.channel_id == 725065871554510848:
        if str(payload.emoji) == '♂️':
            male = guild.get_role(725146445656883271)
            await user.remove_roles(male)
        elif str(payload.emoji) == '♀️':
            female = guild.get_role(725146537201631272)
            await user.remove_roles(female)
        elif str(payload.emoji) == '❓':
            other = guild.get_role(725146594365931581)
            await user.remove_roles(other)
        elif str(payload.emoji) == '🇺🇸':
            us = guild.get_role(725153499683225702)
            await user.remove_roles(us)
        elif str(payload.emoji) == '🇧🇷':
            br = guild.get_role(725154063582494791)
            await user.remove_roles(br)
        elif str(payload.emoji) == '🇨🇳':
            ch = guild.get_role(725154438594953267)
            await user.remove_roles(ch)
        elif str(payload.emoji) == '🇪🇺':
            eu = guild.get_role(725154767239774231)
            await user.remove_roles(eu)
        elif str(payload.emoji) == '🇿🇦':
            af = guild.get_role(725155259491680266)
            await user.remove_roles(af)
        elif str(payload.emoji) == '🇦🇺':
            au = guild.get_role(725155549938974761)
            await user.remove_roles(au)
        elif str(payload.emoji) == '🇦🇶':
            an = guild.get_role(725155788699467857)
            await user.remove_roles(an)
        elif str(payload.emoji) == '♈':
            aries = guild.get_role(725157028229808248)
            await user.remove_roles(aries)
        elif str(payload.emoji) == '♉':
            taurus = guild.get_role(725157846488186910)
            await user.remove_roles(taurus)
        elif str(payload.emoji) == '♊':
            gemini = guild.get_role(725158133235974294)
            await user.remove_roles(gemini)
        elif str(payload.emoji) == '♋':
            cancer = guild.get_role(725158441831891034)
            await user.remove_roles(cancer)
        elif str(payload.emoji) == '♌':
            leo = guild.get_role(725158644559118379)
            await user.remove_roles(leo)
        elif str(payload.emoji) == '♍':
            virgo = guild.get_role(725158875463942175)
            await user.remove_roles(virgo)
        elif str(payload.emoji) == '♎':
            libra = guild.get_role(725159100232630383)
            await user.remove_roles(libra)
        elif str(payload.emoji) == '♏':
            scorpius = guild.get_role(725159358845157448)
            await user.remove_roles(scorpius)
        elif str(payload.emoji) == '♐':
            sagittarius = guild.get_role(725159686164447295)
            await user.remove_roles(sagittarius)
        elif str(payload.emoji) == '♑':
            capricorn = guild.get_role(725159927236001924)
            await user.remove_roles(capricorn)
        elif str(payload.emoji) == '♒':
            aquarius = guild.get_role(725160136791818351)
            await user.remove_roles(aquarius)
        elif str(payload.emoji) == '♓':
            pisces = guild.get_role(725160360797274132)
            await user.remove_roles(pisces)

@client.event
async def on_member_remove(member):
    ping_roles = client.get_channel(698318226613993553)
    message = await ping_roles.fetch_message(716819696346857524)
    for reaction in message.reactions:
        await message.remove_reaction(reaction.emoji, member)

    selfrole = client.get_channel(725065871554510848)
    async for message in selfrole.history():
        for reaction in message.reactions:
            await message.remove_reaction(reaction.emoji, member)

client.run(os.environ.get("reactionmanager"))
