import discord
from discord.ext import commands
import json
import asyncio
import random
import sqlite3
from sqlite3 import Error
from utils import *

class gambling(commands.Cog):

    def __init__(self, client):
        self.client = client


    @commands.command()
    @commands.check(rightCategory)
    async def fight(self, ctx, action=None, member:discord.Member=None, bet=None):
        author = ctx.author
        jailtime = read_value('members', 'id', author.id, 'jailtime')
        if not action:
            await ctx.send('Enter a fight action.')
            return

        if action.lower() == 'start':
            jailtime = read_value('members', 'id', author.id, 'jailtime')
            if jailtime > time.time():
                await ctx.send(f'You are still in jail for {splittime(jailtime)}.')
                return
            if read_value('members', 'id', author.id, 'isfighting') == 'True':
                await ctx.send('You already have a fight request pending, or are fighting someone already.')
                return
            if not member:
                await ctx.send('Enter a user to send a fight request to.')
                return
            if author == member:
                await ctx.send("You can't fight yourself.")
                return
            jailtime = read_value('members', 'id', member.id, 'jailtime')
            if jailtime > time.time():
                await ctx.send(f'**{member.name}** is still in jail for {splittime(jailtime)}.')
                return
            if not bet:
                await ctx.send('Enter your bet.')
                return
            try:
                bet = int(bet)
            except:
                await ctx.send('Enter a valid amount of money for your bet.')
                return
            if bet < 1:
                await ctx.send('Enter a valid amount of money for your bet.')
                return
            money = read_value('members', 'id', author.id, 'money')
            if bet > money:
                await ctx.send("You don't have enough money for that.")
                return

            write_value('members', 'id', author.id, "isfighting", "'True'")
            write_value('members', 'id', member.id, "isfighting", "'True'")
                
            embed = discord.Embed(color = 0xffa60d)
            embed.set_author(name='Fight Request')
            embed.add_field(name=f'Bet: ${bet}', value=f'{author.name} vs {member.name}')
            request = await ctx.send(embed=embed)
            await request.add_reaction('✅')
            await request.add_reaction('❌')
            def check(reaction, user):
                return user == member and (str(reaction.emoji) == '✅' or str(reaction.emoji) == '❌') and reaction.message.id == request.id
            try:
                rreaction, ruser = await self.client.wait_for('reaction_add', timeout=60.0, check=check)

            except asyncio.TimeoutError:
                await ctx.send(f'Took too long: fight request auto rejected.')
                write_value('members', 'id', author.id, "isfighting", "'False'")
                write_value('members', 'id', member.id, "isfighting", "'False'")
                return

            if str(rreaction.emoji) == '✅':

                money = read_value('members', 'id', member.id, 'money')
                if bet > money:
                    await ctx.send(f"**{member.name}** does not have enough money for the bet.")
                    write_value('members', 'id', author.id, "isfighting", "'False'")
                    write_value('members', 'id', member.id, "isfighting", "'False'")
                    return



                await ctx.send(f'**{member.name}** has accepted the fight against **{author.name}**.\nGo to your DMs.')
                health1 = 3
                health2 = 3

                while health1 > 0 and health2 > 0:
                    attacking = discord.Embed(color= 0xff0000)
                    attacking.set_author(name=f"{author.name} ({health1}/3) vs {member.name} ({health2}/3)")
                    attacking.add_field(name='Status:',value='Attacking',inline=False)
                    defending = discord.Embed(color= 0x0015ff)
                    defending.set_author(name=f"{member.name} ({health2}/3) vs {author.name} ({health1}/3)")
                    defending.add_field(name=f"Status:",value='Defending',inline=False)
                    
                    am = await author.send(embed=attacking)
                    dm = await member.send(embed=defending)
                    await am.add_reaction('✊')
                    await am.add_reaction('🦵')
                    await dm.add_reaction('✊')
                    await dm.add_reaction('🦵')
                    def check(reaction, user):
                        return (reaction.message.id == am.id or reaction.message.id == dm.id) and (str(reaction.emoji) == '✊' or str(reaction.emoji) == '🦵' and user.id != 698771271353237575)
                    try:
                        reaction, user = await self.client.wait_for('reaction_add', timeout=30.0, check=check)

                    except asyncio.TimeoutError:
                        await author.send(f'Both users took too long: Fight cancelled.')
                        await member.send(f'Both users took too long: Fight cancelled.')
                        await ctx.send(f'Both users took too long: Fight cancelled.')
                        write_value('members', 'id', author.id, "isfighting", "'False'")
                        write_value('members', 'id', member.id, "isfighting", "'False'")
                        return
                    
                    if user == author:
                        if str(reaction.emoji) == '✊':
                            aa = 'punch'
                        elif str(reaction.emoji) == '🦵':
                            aa = 'kick'
                        awaiting = await author.send('Waiting for opponent...')
                        def check(reaction, user):
                            return reaction.message.id == dm.id and (str(reaction.emoji) == '✊' or str(reaction.emoji) == '🦵' and user.id != 698771271353237575)
                        try:
                            reaction, user = await self.client.wait_for('reaction_add', timeout=15.0, check=check)
                            if str(reaction.emoji) == '✊':
                                da = 'punch'
                            elif str(reaction.emoji) == '🦵':
                                da = 'kick'
                        
                        except asyncio.TimeoutError:
                            da = 'none'
                        await awaiting.delete()
                    
                    elif user == member:
                        if str(reaction.emoji) == '✊':
                            da = 'punch'
                        elif str(reaction.emoji) == '🦵':
                            da = 'kick'
                        dwaiting = await member.send('Waiting for oppenent...')
                        def check(reaction, user):
                            return reaction.message.id == am.id and (str(reaction.emoji) == '✊' or str(reaction.emoji) == '🦵' and user.id != 698771271353237575)
                        try:
                            reaction, user = await self.client.wait_for('reaction_add', timeout=15.0, check=check)
                            if str(reaction.emoji) == '✊':
                                aa = 'punch'
                            elif str(reaction.emoji) == '🦵':
                                aa = 'kick'
                        except asyncio.TimeoutError:
                            aa = 'none'
                        await dwaiting.delete()

                    if (aa is 'punch' and (da is 'kick' or da is 'none')) or (aa is 'kick' and (da is 'punch' or da is 'none')):
                        await ctx.send(f'**{author.name}** {aa}ed **{member.name}**.')
                        await author.send(f'You successfully {aa}ed your opponent.')
                        await member.send(f'You were {aa}ed by your opponent.')
                        health2 -= 1
                    

                    elif (aa is 'punch' and da is 'punch') or (aa is 'kick' and da is 'kick'):
                        rword = random.choice(['dodged', 'blocked'])
                        await ctx.send(f"**{member.name}** {rword} **{author.name}**'s {aa}.")
                        await author.send(f'Your opponent {rword} your {aa}.')
                        await member.send(f"You {rword} your opponent's {aa}.")
                    
                    elif aa is 'none':
                        await ctx.send(f'**{author.name}** just stood there and did nothing.')
                        await member.send(f'Your opponent just stood there and did nothing.')
                        await author.send(f'You just stood there and did nothing.')



                    

                    attacking = discord.Embed(color= 0xff0000)
                    attacking.set_author(name=f"{member.name} ({health2}/3) vs {author.name} ({health1}/3)")
                    attacking.add_field(name='Status:',value='Attacking',inline=False)
                    defending = discord.Embed(color= 0x0015ff)
                    defending.set_author(name=f"{author.name} ({health1}/3) vs {member.name} ({health2}/3)")
                    defending.add_field(name=f"Status:",value='Defending',inline=False)
                    
                    am = await member.send(embed=attacking)
                    dm = await author.send(embed=defending)
                    await am.add_reaction('✊')
                    await am.add_reaction('🦵')
                    await dm.add_reaction('✊')
                    await dm.add_reaction('🦵')
                    def check(reaction, user):
                        return (reaction.message.id == am.id or reaction.message.id == dm.id) and (str(reaction.emoji) == '✊' or str(reaction.emoji) == '🦵' and user.id != 698771271353237575)
                    try:
                        reaction, user = await self.client.wait_for('reaction_add', timeout=30.0, check=check)

                    except asyncio.TimeoutError:
                        await author.send(f'Both users took too long: Fight cancelled.')
                        await member.send(f'Both users took too long: Fight cancelled.')
                        await ctx.send(f'Both users took too long: Fight cancelled.')
                        write_value('members', 'id', author.id, "isfighting", "'False'")
                        write_value('members', 'id', member.id, "isfighting", "'False'")
                        return
                    
                    if user == member:
                        if str(reaction.emoji) == '✊':
                            aa = 'punch'
                        elif str(reaction.emoji) == '🦵':
                            aa = 'kick'
                        awaiting = await member.send('Waiting for oppenent...')
                        def check(reaction, user):
                            return reaction.message.id == dm.id and (str(reaction.emoji) == '✊' or str(reaction.emoji) == '🦵' and user.id != 698771271353237575)
                        try:
                            reaction, user = await self.client.wait_for('reaction_add', timeout=15.0, check=check)
                            if str(reaction.emoji) == '✊':
                                da = 'punch'
                            elif str(reaction.emoji) == '🦵':
                                da = 'kick'
                        
                        except asyncio.TimeoutError:
                            da = 'none'
                        await awaiting.delete()
                    
                    elif user == author:
                        if str(reaction.emoji) == '✊':
                            da = 'punch'
                        elif str(reaction.emoji) == '🦵':
                            da = 'kick'
                        dwaiting = await author.send('Waiting for opponent...')
                        def check(reaction, user):
                            return reaction.message.id == am.id and (str(reaction.emoji) == '✊' or str(reaction.emoji) == '🦵' and user.id != 698771271353237575)
                        try:
                            reaction, user = await self.client.wait_for('reaction_add', timeout=15.0, check=check)
                            if str(reaction.emoji) == '✊':
                                aa = 'punch'
                            elif str(reaction.emoji) == '🦵':
                                aa = 'kick'
                        except asyncio.TimeoutError:
                            aa = 'none'
                        await dwaiting.delete()

                    if (aa is 'punch' and (da is 'kick' or da is 'none')) or (aa is 'kick' and (da is 'punch' or da is 'none')):
                        await ctx.send(f'**{member.name}** {aa}ed **{author.name}**.')
                        await member.send(f'You successfully {aa}ed your opponent.')
                        await author.send(f'You were {aa}ed by your opponent.')
                        health1 -= 1
                    

                    elif (aa is 'punch' and da is 'punch') or (aa is 'kick' and da is 'kick'):
                        rword = random.choice(['dodged', 'blocked'])
                        await ctx.send(f"**{author.name}** {rword} **{member.name}**'s {aa}.")
                        await member.send(f'Your opponent {rword} your {aa}.')
                        await author.send(f"You {rword} your opponent's {aa}.")
                    
                    elif aa is 'none':
                        await ctx.send(f'**{member.name}** just stood there and did nothing.')
                        await author.send(f'Your opponent just stood there and did nothing.')
                        await member.send(f'You just stood there and did nothing.')


                if health1 == 0 and health2 == 0:
                    await author.send(f'There was a tie and no one earned any money.')
                    await member.send(f'There was a tie and no one earned any money.')
                    await ctx.send(f'There was a tie between **{author.name}** and **{member.name}**, and no one earned any money.')

                elif health1 == 0:
                    await member.send(f'You have won the fight against **{author.name}** and earned ${bet}.')
                    await author.send(f'You have lost the fight against **{member.name}** and lost ${bet}.')
                    await ctx.send(f'**{member.name}** has won the fight against **{author.name}**, earning ${bet}.')
                    money1 = read_value('members', 'id', author.id, 'money')
                    money2 = read_value('members', 'id', member.id, 'money')
                    money1 -= bet
                    money2 += bet
                    write_value('members', 'id', author.id, 'money', money1)
                    write_value('members', 'id', member.id, 'money', money2)

                elif health2 == 0:
                    await author.send(f'You have won the fight against **{member.name}** and earned ${bet}.')
                    await member.send(f'You have lost the fight against **{author.name}** and lost ${bet}.')
                    await ctx.send(f'**{author.name}** has won the fight against **{member.name}**, earning ${bet}.')              
                    money1 = read_value('members', 'id', author.id, 'money')
                    money2 = read_value('members', 'id', member.id, 'money')
                    money1 += bet
                    money2 -= bet
                    write_value('members', 'id', author.id, 'money', money1)

                write_value('members', 'id', author.id, "isfighting", "'False'")
                write_value('members', 'id', member.id, "isfighting", "'False'")
                update_total(author.id)
                update_total(member.id)
                await rolecheck(self.client, author.id)
                await rolecheck(self.client, member.id)
                await leaderboard(self.client)
                    

                
            elif str(rreaction.emoji) == '❌':
                await ctx.send(f'**{member.name}** has rejected the fight against **{author.name}**.')
                write_value('members', 'id', author.id, "isfighting", "'False'")
                write_value('members', 'id', member.id, "isfighting", "'False'")
                return
        

        elif action == 'help':
            await ctx.send("Once you start a fight, a message will be sent to both participant's DMs. In your Dms, react to the message with the corresponding punch or kick reaction. If both the attacker and defender choose the same action, the action will be blocked or dodged. However, if they are different, the attacker will successfully hit the defender, causing them to lose one health. First one to get to zero health loses, and also loses their bet. **Note that whoever went second will still have one more chance to attack even if their health is at zero, to make it fair.**")


        else:
            await ctx.send('Enter a valid fight action.')


    
    @fight.error
    async def member_not_found_error(self, ctx,error):
        if isinstance(error, commands.BadArgument):
            await ctx.send("Member not found.")
        
    

def setup(client):
    client.add_cog(gambling(client))