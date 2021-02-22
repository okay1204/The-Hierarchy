# pylint: disable=import-error, anomalous-backslash-in-string
import asyncio
import json
import random

import discord

from discord.ext import commands, tasks
from discord.ext.commands import BadArgument, CommandNotFound, MaxConcurrencyReached

import os

# To import from different path
import sys
sys.path.insert(1 , os.getcwd())

from utils import bot_check, splittime, timestring, log_command


class Birthday(commands.Cog):

    def __init__(self, client):
        self.client = client

        self.event_category = client.get_channel(811469006404976692)

        self.button_presses = {}

        self.puzzle_channels = [811470424918982716, 811470458427277352, 811470494405623858, 811470515852148757]
        self.puzzle_roles = [811470801491722260, 811470827127308318, 811470848649068544, 811470866756010024]

        self.the_end = 811470546045763594

        self.client.add_check(self.disable)

    def cog_unload(self):
        self.client.remove_check(self.disable)


    def disable(self, ctx):
        
        if not ctx.command.cog or ctx.command.cog_name in ('Birthday', 'Debug'):
            return True
        
        return False


    async def cog_check(self, ctx):

        if ctx.channel.id == self.client.adminChannel or ctx.command.name in ('say', 'edit'): return True
        else: return False



    async def button_reset(self, member_id):

        member = self.client.mainGuild.get_member(member_id)

        channel = self.client.get_channel(self.puzzle_channels[3])
        message = await channel.fetch_message(811746360180998195)

        for reaction in message.reactions:
            await reaction.remove(member)


    async def button_timeout(self, member_id):

        await asyncio.sleep(10)

        del self.button_presses[member_id]

        channel = self.client.get_channel(self.puzzle_channels[3])
        
        await channel.send(f'<@{member_id}> You took too long and the buttons reset themselves.', delete_after=3)
        await self.button_reset(member_id)



    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):

        guild = self.client.mainGuild

        # original lore channel
        if payload.message_id == 811714156960940053:
            
            user = guild.get_member(payload.user_id)
            puzzle_1_role = guild.get_role(self.puzzle_roles[0])

            if not puzzle_1_role in user.roles:
                await user.add_roles(puzzle_1_role)
                channel = self.client.get_channel(payload.channel_id)
                await channel.send(f'{user.mention} <#{self.puzzle_channels[0]}>', delete_after=3)


        # final puzzle
        if payload.channel_id == self.puzzle_channels[3]:
            
            if payload.user_id not in self.button_presses:
                self.button_presses[payload.user_id] = {
                    'buttons': [str(payload.emoji)],
                    'timer': asyncio.create_task(self.button_timeout(payload.user_id))
                }
            
            else:

                self.button_presses[payload.user_id]['buttons'].append(str(payload.emoji))
                
                self.button_presses[payload.user_id]['timer'].cancel()


                if len(self.button_presses[payload.user_id]['buttons']) == 8:

                    channel = self.client.get_channel(self.puzzle_channels[3])
                    answer = ['🔴', '🔵', '🟣', '🟢', '🟡', '🟤', '🟠', '⚪']

                    if self.button_presses[payload.user_id]['buttons'] == answer:
                        
                        member = guild.get_member(payload.user_id)

                        # the end
                        the_end_channel = self.client.get_channel(self.the_end)

                        if len(the_end_channel.overwrites) >= 2:
                            await channel.send(f'{member.mention} Good job but someone has already won...', delete_after=3)
                        else:
                            await the_end_channel.edit(
                                overwrites= {
                                    guild.default_role: discord.PermissionOverwrite(read_messages=True, read_message_history=True, send_messages=False),
                                    member: discord.PermissionOverwrite(send_messages=True)
                                }
                            )

                            await channel.send(f'{member.mention} {the_end_channel.mention} Well done...', delete_after=3)

                            
                            await the_end_channel.send(f'The wall behind the desk splits open revealing the shining light. **{member.name}** hears a voice telling them to ***make the decision.***')

                            await the_end_channel.send(f'**{member.name}** decides to walk into the shining light and everything goes white...')

                            await the_end_channel.send(f'In front of them lays two buttons. A red and blue one. On the wall there is a sign that reads "Everyone will...". Above the red button there is a label saying "lose 50%", and above the blue button another label reads "gain 50%." {member.mention}**, what do you choose.**\n*(Just type your answer here)*')




                    else:
                        await channel.send(f'<@{payload.user_id}> A red light blinks indicating that you put the incorrect order.', delete_after=3)
                    
                    del self.button_presses[payload.user_id]
                    await self.button_reset(payload.user_id)
                
                else:
                    self.button_presses[payload.user_id]['timer'] = asyncio.create_task(self.button_timeout(payload.user_id))


    @commands.Cog.listener()
    async def on_message(self, message):

        if message.author.bot:
            return

        guild = self.client.mainGuild

        if message.channel.id == self.puzzle_channels[0]:

            puzzle_2_role = guild.get_role(self.puzzle_roles[1])

            await message.delete()

            if not puzzle_2_role in message.author.roles:
                if message.content.lower() == 'there will only be one':
                    await message.author.add_roles(puzzle_2_role)
                    await message.channel.send(f'{message.author.mention} <#{self.puzzle_channels[1]}>', delete_after=3)
                else:
                    await message.channel.send(f'{message.author.mention} *The board flips over and erases what you wrote.*', delete_after=3)
            

        elif message.channel.id == self.puzzle_channels[1]:

            puzzle_3_role = guild.get_role(self.puzzle_roles[2])
    
            await message.delete()

            if not puzzle_3_role in message.author.roles:
                if message.content == '432549':
                    await message.author.add_roles(puzzle_3_role)
                    await message.channel.send(f'{message.author.mention} <#{self.puzzle_channels[2]}>', delete_after=3)
                else:
                    await message.channel.send(f'{message.author.mention} *The lock does not open.*', delete_after=3)


        elif message.channel.id == self.puzzle_channels[2]:

            puzzle_4_role = guild.get_role(self.puzzle_roles[3])

            await message.delete()

            if not puzzle_4_role in message.author.roles:
                if message.content == 'the decision':
                    await message.author.add_roles(puzzle_4_role)
                    await message.channel.send(f'{message.author.mention} <#{self.puzzle_channels[3]}>', delete_after=3)
                else:
                    await message.channel.send(f'{message.author.mention} *The book closes and opens again, and what you have written has disappeared.*', delete_after=3)


    @commands.group(invoke_without_command=True)
    async def birthday(self, ctx):
        await ctx.send(f'Incorrect command usage:\n`.birthday save/start/restore`')

    @birthday.command()
    async def save(self, ctx):

        with open('./storage/text/englishwords.txt') as f:
            word = random.choice(f.read().splitlines())
        # for confirmation
        await ctx.send(f"Are you sure you want to save all channel overwrites? Type `{word}` to proceed.")

        try:
            response = await self.client.wait_for('message', check=lambda m: m.channel == ctx.channel and m.author == ctx.author, timeout=20)
        except:
            return await ctx.send("Save timed out.")

        if response.content.lower() != word.lower(): return await ctx.send("Save cancelled.")


        all_overwrites = {}

        guild = self.client.mainGuild

        async with ctx.channel.typing():
            for channel in guild.channels:

                if type(channel) in (discord.TextChannel, discord.VoiceChannel) and channel.category_id != self.event_category.id:

                    channel_overwrites = {}
                    
                    for role, overwrite in channel.overwrites.items():
                    
                        pair = overwrite.pair()
                        channel_overwrites[role.id] = {'allow': pair[0].value, 'deny': pair[1].value}


                    all_overwrites[channel.id] = channel_overwrites


            with open('./storage/jsons/overwrites.json', 'w') as f:
                json.dump(all_overwrites, f, indent=2)
        
        await ctx.send("Saved all channel overwrites.")
        await log_command(self.client, ctx)


    @birthday.command()
    async def start(self, ctx):

        guild = self.client.mainGuild

        async with ctx.channel.typing():

            # hiding all channels
            for channel in guild.channels:

                if channel.category_id != self.event_category.id:
                    await channel.edit(overwrites={guild.default_role: discord.PermissionOverwrite(read_messages=False)})


            # making specific channels visible
            for channel in self.event_category.channels:

                try:
                    index = self.puzzle_channels.index(channel.id)
                except ValueError:

                    if channel.id != self.the_end:
                        overwrites = {guild.default_role: discord.PermissionOverwrite(read_messages=True, read_message_history=True, send_messages=False, add_reactions=False)}
                    else:
                        overwrites = {guild.default_role: discord.PermissionOverwrite(read_messages=False)}

                    await channel.edit(overwrites=overwrites)

                else:
                    role = guild.get_role(self.puzzle_roles[index])
                    
                    overwrites = {
                        guild.default_role: discord.PermissionOverwrite(read_messages=False),
                        role: discord.PermissionOverwrite(read_messages=True, read_message_history=True, add_reactions=False)
                    }

                    # the last puzzle doesn't require sending messages
                    if 0 <= index <= 2:
                        overwrites[role].update(send_messages=True)
                    else:
                        overwrites[role].update(send_messages=False)

                    await channel.edit(overwrites=overwrites)


        await ctx.send('Birthday event started.')
        await log_command(self.client, ctx)

        
    @birthday.command()
    async def restore(self, ctx):

        guild = self.client.mainGuild

        with open('./storage/jsons/overwrites.json') as f:
            overwrites = json.load(f)

        async with ctx.channel.typing():

            for channel_id, all_overwrites in overwrites.items():

                channel = guild.get_channel(int(channel_id))

                if channel.category_id != self.event_category.id:

                    overwrites = {}

                    for role_id, overwrite in all_overwrites.items():

                        overwrites[guild.get_role(int(role_id))] = discord.PermissionOverwrite.from_pair(
                            discord.Permissions(permissions=overwrite['allow']),
                            discord.Permissions(permissions=overwrite['deny'])
                        )

                    await channel.edit(overwrites=overwrites)

        for channel in self.event_category.channels:

            overwrites = {guild.default_role: discord.PermissionOverwrite(read_messages=False)}
            await channel.edit(overwrites=overwrites)

        await ctx.send('Channel overwrites restored.')
        await log_command(self.client, ctx)


    @commands.command()
    async def say(self, ctx, *, message=None):

        if message:
            await ctx.send(message)

        await ctx.message.delete()

    @commands.command()
    async def edit(self, ctx, message_id=None, *, text=None):

        await ctx.message.delete()

        if message_id and text:
            
            try:
                message = await ctx.channel.fetch_message(message_id)
            except:
                return

            await message.edit(content=text)





def setup(client):
    client.add_cog(Birthday(client))