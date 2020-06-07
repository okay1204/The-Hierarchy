import discord
from discord.ext import commands, tasks

client = commands.Bot(command_prefix = '.')
client.remove_command('help')

@client.event
async def on_ready():
    print(f"Logged in as {client.user}.\nID: {client.user.id}")
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="for reactions"))



@client.event
async def on_raw_reaction_add(payload):
    guild = client.get_guild(692906379203313695)
    pollchannel = client.get_channel(698009727803719757)
    if payload.message_id == 716819696346857524:
        if str(payload.emoji) == '🔔':
            announcements = guild.get_role(716818513708187668)
            user = payload.user_id
            user = guild.get_member(user)
            await user.add_roles(announcements)
        elif str(payload.emoji) == '✅':
            newfeatures = guild.get_role(716818605110460418)
            user = payload.user_id
            user = guild.get_member(user)
            await user.add_roles(newfeatures)
        elif str(payload.emoji) == '☑️':
            polls = guild.get_role(716818729987473408)
            user = payload.user_id
            user = guild.get_member(user)
            await user.add_roles(polls)
        elif str(payload.emoji) == '🤝':
            partnerships = guild.get_role(716836063150342184)
            user = payload.user_id
            user = guild.get_member(user)
            await user.add_roles(partnerships)
        elif str(payload.emoji) == '🏦':
            bank = guild.get_role(698322063206776972)
            user = payload.user_id
            user = guild.get_member(user)
            await user.add_roles(bank)
        elif str(payload.emoji) == '💰':
            tax = guild.get_role(698321954742075504)
            user = payload.user_id
            user = guild.get_member(user)
            await user.add_roles(tax)
        elif str(payload.emoji) == '🛒':
            shop = guild.get_role(716818790947618857)
            user = payload.user_id
            user = guild.get_member(user)
            await user.add_roles(shop)




    if payload.channel_id == 698009727803719757:
        if payload.user_id != 717086649460326510:
            message = await pollchannel.fetch_message(payload.message_id)
            for reaction in message.reactions:
                if str(reaction.emoji) != str(payload.emoji):
                    await client.http.remove_reaction(payload.channel_id, payload.message_id, reaction.emoji, payload.user_id)

@client.event
async def on_raw_reaction_remove(payload):
    guild = client.get_guild(692906379203313695)
    if payload.message_id == 716819696346857524:
        if str(payload.emoji) == '🔔':
            announcements = guild.get_role(716818513708187668)
            user = payload.user_id
            user = guild.get_member(user)
            await user.remove_roles(announcements)
        elif str(payload.emoji) == '✅':
            newfeatures = guild.get_role(716818605110460418)
            user = payload.user_id
            user = guild.get_member(user)
            await user.remove_roles(newfeatures)
        elif str(payload.emoji) == '☑️':
            polls = guild.get_role(716818729987473408)
            user = payload.user_id
            user = guild.get_member(user)
            await user.remove_roles(polls)
        elif str(payload.emoji) == '🤝':
            partnerships = guild.get_role(716836063150342184)
            user = payload.user_id
            user = guild.get_member(user)
            await user.remove_roles(partnerships)
        elif str(payload.emoji) == '🏦':
            bank = guild.get_role(698322063206776972)
            user = payload.user_id
            user = guild.get_member(user)
            await user.remove_roles(bank)
        elif str(payload.emoji) == '💰':
            tax = guild.get_role(698321954742075504)
            user = payload.user_id
            user = guild.get_member(user)
            await user.remove_roles(tax)
        elif str(payload.emoji) == '🛒':
            shop = guild.get_role(716818790947618857)
            user = payload.user_id
            user = guild.get_member(user)
            await user.remove_roles(shop)


client.run("NzE2ODM3NzU5NTE5NTU1NjI0.XtRlPg.xHLUA9U_IyVOcUBcfJa_vRW-zuw")
