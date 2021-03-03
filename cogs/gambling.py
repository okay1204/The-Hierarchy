# pylint: disable=import-error, function-redefined

import discord
from discord.ext import commands
from discord.ext.commands import BadArgument, CommandNotFound, MaxConcurrencyReached
import json
import math
import asyncio
import random
import time
import os
from sqlite3 import Error

# To import from different path
import sys
sys.path.insert(1 , os.getcwd())

from utils import bot_check, splittime, timestring, log_command

def evaluateCards(cards):
    aceCount = 0
    reducedAces = 0
    for card in cards:
        if card[2] == 'A':
            aceCount += 1

    total = 0
    for card in cards:
        
        value = card.split()[1]

        try:
            value = int(value)
        except:
            if value == 'A':
                value = 11
            else:
                value = 10
        total += value
    
    while total > 21:
        if aceCount > reducedAces:
            total -= 10
            reducedAces += 1
        else:
            break
    
    return total

class Gambling(commands.Cog):

    def __init__(self, client):
        self.client = client

        self.roulette_members = []
        self.roulette_timer_task = None
        self.roulette_bet = None

    async def cog_check(self, ctx):
        if ctx.channel.category.id != self.client.rightCategory:
            return False
        else:
            return True


    async def lead_and_rolecheck(self, id):

        async with self.client.pool.acquire() as db:

            await db.leaderboard()
            await db.rolecheck(id)


    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):

        error = getattr(error, 'original', error)

        if isinstance(error, MaxConcurrencyReached):
            if ctx.command.name == 'blackjack':
                await ctx.send("Someone is already playing blackjack in this channel.")




    @commands.command()
    async def fight(self, ctx, action=None, member:discord.Member=None, bet=None):
        
        if not action:
            await ctx.send("Incorrect command usage:\n`.fight start/cancel/help`")
            return

        if not await bot_check(self.client, ctx, member):
            return

        async with self.client.pool.acquire() as db:

            if member and not await db.member_event_check(ctx, member.id): return

        action = action.lower()

        if action == 'start':
            for task in asyncio.all_tasks():
                name = str(task.get_name())
                if name == f'fightreq {ctx.author.id}':
                    await ctx.send("You already have a fight request pending for someone else.")
                    return
                elif 'fighting' in name and str(ctx.author.id) in name:
                    await ctx.send("You are already fighting someone else.")
                    return
            asyncio.create_task(self.fightreq(ctx, member, bet), name=f"fightreq {ctx.author.id}")
        
        elif action == 'cancel':
            for task in asyncio.all_tasks():
                name = str(task.get_name())
                if name == f'fightreq {ctx.author.id}':
                    task.cancel()
                    await ctx.send("Fight request cancelled.")
                    return

            await ctx.send("You do not have a fight request pending.")

        elif action == 'help':
            await ctx.send("Once you start a fight, a message will be sent to both participant's DMs. In your Dms, react to the message with the corresponding punch or kick reaction. If both the attacker and defender choose the same action, the action will be blocked or dodged. However, if they are different, the attacker will successfully hit the defender, causing them to lose one health. First one to get to zero health loses, and also loses their bet. **Note that whoever went second will still have one more chance to attack even if their health is at zero, to make it fair.**")


        else:
            await ctx.send('Enter a valid fight action.')

    async def fightreq(self, ctx, member:discord.Member=None, bet=None):
        ctx.author = ctx.author

        async with self.client.pool.acquire() as db:
        
            if not await db.jail_heist_check(ctx, ctx.author):
                return

            if not member or not bet:
                await ctx.send("Incorrect command usage:\n`.fight start member bet`")
                return
            if ctx.author == member:
                await ctx.send("You can't fight yourself.")
                return

            jailtime = await db.get_member_val(member.id, 'jailtime')
            if jailtime > time.time():
                return await ctx.send(f'**{member.name}** is still in jail for {splittime(jailtime)}.')
                

            try:
                bet = int(bet)
            except:
                await ctx.send("Incorrect command usage:\n`.fight start member bet`")
                return
            if bet <= 0:
                await ctx.send('Enter an bet greater than 0.')
                return

            money = await db.get_member_val(ctx.author.id, 'money')

            if bet > money:
                await ctx.send("You don't have enough money for that.")
                return


            embed = discord.Embed(color = 0xffa60d)
            embed.set_author(name='Fight Request')
            embed.add_field(name=f'Bet: ${bet}', value=f'{ctx.author.name} vs {member.name}')
            request = await ctx.send(embed=embed)
            await request.add_reaction('✅')
            await request.add_reaction('❌')
            def check(reaction, user):
                return user == member and (str(reaction.emoji) == '✅' or str(reaction.emoji) == '❌') and reaction.message.id == request.id
            try:
                rreaction, ruser = await self.client.wait_for('reaction_add', timeout=60.0, check=check) # noqa pylint: disable=unused-variable

            except asyncio.TimeoutError:
                await ctx.send(f'Took too long: fight request auto rejected.')
                return

            if str(rreaction.emoji) == '✅':

                money = await db.get_member_val(member.id, 'money')
                if bet > money:
                    await ctx.send(f"**{member.name}** does not have enough money for the bet.")
                    return

                for task in asyncio.all_tasks():
                    name = str(task.get_name())
                    if 'fighting' in name and str(member.id) in name:
                        await ctx.send(f"**{member.name}** is already fighting.")
                        return
            
                asyncio.create_task(self.fighting(ctx, member, bet), name=f"fighting {ctx.author.id} {member.id}")

            elif str(rreaction.emoji) == '❌':
                await ctx.send(f'**{member.name}** has rejected the fight against **{ctx.author.name}**.')
                return
        

    async def fighting(self, ctx, member, bet):
        ctx.author = ctx.author

        await ctx.send(f'**{member.name}** has accepted the fight against **{ctx.author.name}**.\nGo to your DMs.')
        health1 = 3
        health2 = 3

        while health1 > 0 and health2 > 0:
            attacking = discord.Embed(color= 0xff0000)
            attacking.set_author(name=f"{ctx.author.name} ({health1}/3) vs {member.name} ({health2}/3)")
            attacking.add_field(name='Status:',value='Attacking',inline=False)
            defending = discord.Embed(color= 0x0015ff)
            defending.set_author(name=f"{member.name} ({health2}/3) vs {ctx.author.name} ({health1}/3)")
            defending.add_field(name=f"Status:",value='Defending',inline=False)
            
            am = await ctx.author.send(embed=attacking)
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
                await ctx.author.send(f'Both users took too long: Fight cancelled.')
                await member.send(f'Both users took too long: Fight cancelled.')
                await ctx.send(f'Both users took too long: Fight cancelled.')
                return
            
            if user == ctx.author:
                if str(reaction.emoji) == '✊':
                    aa = 'punch'
                elif str(reaction.emoji) == '🦵':
                    aa = 'kick'
                awaiting = await ctx.author.send('Waiting for opponent...')
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

            if (aa == 'punch' and (da == 'kick' or da == 'none')) or (aa == 'kick' and (da == 'punch' or da == 'none')):
                await ctx.send(f'**{ctx.author.name}** {aa}ed **{member.name}**.')
                await ctx.author.send(f'You successfully {aa}ed your opponent.')
                await member.send(f'You were {aa}ed by your opponent.')
                health2 -= 1
            

            elif (aa == 'punch' and da == 'punch') or (aa == 'kick' and da == 'kick'):
                rword = random.choice(['dodged', 'blocked'])
                await ctx.send(f"**{member.name}** {rword} **{ctx.author.name}**'s {aa}.")
                await ctx.author.send(f'Your opponent {rword} your {aa}.')
                await member.send(f"You {rword} your opponent's {aa}.")
            
            elif aa == 'none':
                await ctx.send(f'**{ctx.author.name}** just stood there and did nothing.')
                await member.send(f'Your opponent just stood there and did nothing.')
                await ctx.author.send(f'You just stood there and did nothing.')



            

            attacking = discord.Embed(color= 0xff0000)
            attacking.set_author(name=f"{member.name} ({health2}/3) vs {ctx.author.name} ({health1}/3)")
            attacking.add_field(name='Status:',value='Attacking',inline=False)
            defending = discord.Embed(color= 0x0015ff)
            defending.set_author(name=f"{ctx.author.name} ({health1}/3) vs {member.name} ({health2}/3)")
            defending.add_field(name=f"Status:",value='Defending',inline=False)
            
            am = await member.send(embed=attacking)
            dm = await ctx.author.send(embed=defending)
            await am.add_reaction('✊')
            await am.add_reaction('🦵')
            await dm.add_reaction('✊')
            await dm.add_reaction('🦵')
            def check(reaction, user):
                return (reaction.message.id == am.id or reaction.message.id == dm.id) and (str(reaction.emoji) == '✊' or str(reaction.emoji) == '🦵' and user.id != 698771271353237575)
            try:
                reaction, user = await self.client.wait_for('reaction_add', timeout=30.0, check=check)

            except asyncio.TimeoutError:
                await ctx.author.send(f'Both users took too long: Fight cancelled.')
                await member.send(f'Both users took too long: Fight cancelled.')
                await ctx.send(f'Both users took too long: Fight cancelled.')
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
            
            elif user == ctx.author:
                if str(reaction.emoji) == '✊':
                    da = 'punch'
                elif str(reaction.emoji) == '🦵':
                    da = 'kick'
                dwaiting = await ctx.author.send('Waiting for opponent...')
                def check(reaction, user):
                    return reaction.message.id == am.id and (str(reaction.emoji) == '✊' or str(reaction.emoji) == '🦵' and user.id != 698771271353237575)
                    # Make user.id of bot a global variable
                try:
                    reaction, user = await self.client.wait_for('reaction_add', timeout=15.0, check=check)
                    if str(reaction.emoji) == '✊':
                        aa = 'punch'
                    elif str(reaction.emoji) == '🦵':
                        aa = 'kick'
                except asyncio.TimeoutError:
                    aa = 'none'
                await dwaiting.delete()
            # You can define a new function here to determine if aa/da is the same or not
            # Include comments so  I can tell whats going on in each code chunk
            # Define better variable names (shorthand) so you have some idea of what they represent from the name instead of mysterious acronyms
            if (aa == 'punch' and (da == 'kick' or da == 'none')) or (aa == 'kick' and (da == 'punch' or da == 'none')):
                await ctx.send(f'**{member.name}** {aa}ed **{ctx.author.name}**.')
                await member.send(f'You successfully {aa}ed your opponent.')
                await ctx.author.send(f'You were {aa}ed by your opponent.')
                health1 -= 1
            

            elif (aa == 'punch' and da == 'punch') or (aa == 'kick' and da == 'kick'):
                rword = random.choice(['dodged', 'blocked'])
                await ctx.send(f"**{ctx.author.name}** {rword} **{member.name}**'s {aa}.")
                await member.send(f'Your opponent {rword} your {aa}.')
                await ctx.author.send(f"You {rword} your opponent's {aa}.")
            
            elif aa == 'none':
                await ctx.send(f'**{member.name}** just stood there and did nothing.')
                await ctx.author.send(f'Your opponent just stood there and did nothing.')
                await member.send(f'You just stood there and did nothing.')

        async with self.client.pool.acquire() as db:

            if health1 == 0 and health2 == 0:
                await ctx.author.send(f'There was a tie and no one earned any money.')
                await member.send(f'There was a tie and no one earned any money.')
                await ctx.send(f'There was a tie between **{ctx.author.name}** and **{member.name}**, and no one earned any money.')
                return

            elif health1 == 0:
                await member.send(f'You have won the fight against **{ctx.author.name}** and earned ${bet}.')
                await ctx.author.send(f'You have lost the fight against **{member.name}** and lost ${bet}.')
                await ctx.send(f'**{member.name}** has won the fight against **{ctx.author.name}**, earning ${bet}.')
                money1 = await db.get_member_val(ctx.author.id, 'money')
                money2 = await db.get_member_val(member.id, 'money')
                money1 -= bet
                money2 += bet

            elif health2 == 0:
                await ctx.author.send(f'You have won the fight against **{member.name}** and earned ${bet}.')
                await member.send(f'You have lost the fight against **{ctx.author.name}** and lost ${bet}.')
                await ctx.send(f'**{ctx.author.name}** has won the fight against **{member.name}**, earning ${bet}.')              
                money1 = await db.get_member_val(ctx.author.id, 'money')
                money2 = await db.get_member_val(member.id, 'money')
                money1 += bet
                money2 -= bet

            await db.set_member_val(ctx.author.id, 'money', money1)
            await db.set_member_val(member.id, 'money', money2)

            
            
            await db.rolecheck(ctx.author.id)
            await db.rolecheck(member.id)
            await db.leaderboard()
                




    @commands.command()
    @commands.max_concurrency(1, per=commands.BucketType.channel)
    async def blackjack(self, ctx, bet=None):


        async with self.client.pool.acquire() as db:

            if not bet:
                return await ctx.send("Incorrect command usage:\n`.blackjack bet`")

            if not await db.event_disabled(ctx):
                return

            if not await db.jail_heist_check(ctx, ctx.author):
                return

            if bet.lower() == "all":
                bet = await db.get_member_val(ctx.author.id, 'money')

                if bet <= 0:
                    return await ctx.send("You don't have any money to blackjack")

            else:
                try:
                    bet = int(bet)
                except:
                    await ctx.send("Incorrect command usage:\n`.blackjack bet`")
                    return

                if bet <= 0:
                    await ctx.send('Enter a bet greater than 0.')
                    return

                money = await db.get_member_val(ctx.author.id, 'money')
                if bet > money:
                    await ctx.send("You don't have enough money for that.")
                    return

            # making all cards

            # spade, club, heart, diamond
            symbols = ['♤', '♧', '♡', '♢']
            values = ['A', '2', '3', '4', '5', '6', '7',
            '8', '9', '10', 'J', 'Q', 'K']

            cards = []
            for symbol in symbols:
                for value in values:
                    cards.append(f"{symbol} {value}")

            # "dealing" cards out

            dealer = []
            card = random.choice(cards)
            cards.remove(card)
            dealer.append(card)

            card = random.choice(cards)
            cards.remove(card)
            hidden = card

            player = [[]]
            bet = [bet]
            for x in range(2): # noqa pylint: disable=unused-variable
                card = random.choice(cards)
                cards.remove(card)
                player[0].append(card)

            await ctx.send(f"Actions: `hit`, `pass`, `double down`, `split`, `surrender`. Use `help <action name>` to get info on the action. Starting a message with `#` will ignore it.\n_ _")
            await asyncio.sleep(3)
            
            currentHand = 0

            money = await db.get_member_val(ctx.author.id, 'money')
            money -= bet[0]
            await db.set_member_val(ctx.author.id, 'money', money)

        while True:
            #Make hand info
            text = f"Dealer's hand: {', '.join(dealer)}, unknown\n"
            if len(player) == 1:
                text += f"Your hand: {', '.join(player[0])} | Value: {evaluateCards(player[0])} | Bet: ${bet[0]}\n"
            else:
                for hand in player:
                    index = player.index(hand)
                    if index != currentHand:
                        text += f"Hand {index+1}: {', '.join(player[index])} | Value: {evaluateCards(player[index])} | Bet: ${bet[index]}\n"
                    else:
                        text += f"**Hand {index+1}**: {', '.join(player[index])} | Value: {evaluateCards(player[index])} | Bet: ${bet[index]}\n"
            
                text = f"`You are on hand {currentHand+1}.`\n{text}"
            
            text += f"\n**Total bet: ${sum(bet)}**"

            await ctx.send(text)
            
            # Checking for insta win
            if len(player[currentHand]) == 2 and evaluateCards(player[currentHand]) == 21:
                winnings = bet[currentHand] * 2
                await ctx.send(f"You won your bet for an insta win! ${winnings} was added to your account.\n_ _")
                
                async with self.client.pool.acquire() as db:
                    money = await db.get_member_val(ctx.author.id, 'money')
                    money += winnings
                    await db.set_member_val(ctx.author.id, 'money', money)

                if len(player) == 1:
                    return

                player.remove(player[currentHand])
                bet.remove(bet[currentHand])
                
                if currentHand == len(player):
                    asyncio.create_task( self.lead_and_rolecheck(ctx.author.id) )
                    break

                await asyncio.sleep(5)
                continue

            # Check for bust here
            if evaluateCards(player[currentHand]) > 21:
                if len(player) == 1:
                    await ctx.send(f"You busted and lost ${bet[0]}!")
                    return

                else:
                    await ctx.send(f"You busted hand {currentHand+1} and lost ${bet[currentHand]} for that hand!\n_ _")
                    await asyncio.sleep(5)
                    bet.remove(bet[currentHand])
                    player.remove(player[currentHand])
                
                if currentHand == len(player):
                    asyncio.create_task( self.lead_and_rolecheck(ctx.author.id) )
                    break
                
                else:
                    continue

            try:
                message = await self.client.wait_for('message', check=lambda m: m.author == ctx.author and m.channel == ctx.channel and not m.content.startswith('#'), timeout=120)
            except asyncio.TimeoutError:
                await ctx.send("Blackjack automatically lost due to inactivity.")
                return
            
            action = message.content.lower()
            
            #Evaluate action
            if action == "hit":
                if len(cards) > 0:
                    card = random.choice(cards)
                    cards.remove(card)
                    player[currentHand].append(card)
                else:
                    await ctx.send('There are no more cards left in the deck.')

            
            elif action == "pass":
                currentHand += 1
                if currentHand + 1 > len(player):
                    break

            elif action == "double down" or action == "double":

                async with self.client.pool.acquire() as db:
                    money = await db.get_member_val(ctx.author.id, 'money')

                if bet[currentHand] > money:
                    await ctx.send("You don't have enough money to double down.")
                else:
                    if len(cards) > 1:

                        #removing money

                        async with self.client.pool.acquire() as db:
                            money = await db.get_member_val(ctx.author.id, 'money')
                            money -= bet[currentHand]
                            await db.set_member_val(ctx.author.id, 'money', money)
                        
                        asyncio.create_task( self.lead_and_rolecheck(ctx.author.id) )

                        card = random.choice(cards)
                        cards.remove(card)
                        dealer.append(card)
                        card = random.choice(cards)
                        cards.remove(card)
                        player[currentHand].append(card)
                        bet[currentHand] *= 2


                    else:
                        await ctx.send("There aren't enough cards left in the deck to double down.")

            elif action == "split":
                if len(player[currentHand]) == 2:

                    async with self.client.pool.acquire() as db:
                        money = await db.get_member_val(ctx.author.id, 'money')

                        if bet[currentHand] > money:

                            await ctx.send("You don't have enough money to split.")

                        else:

                            if player[currentHand][0].split()[1] == player[currentHand][1].split()[1]:
                                player.append([])
                                player[-1].append(player[currentHand][1])
                                player[currentHand].remove(player[currentHand][1])

                                card = random.choice(cards)
                                cards.remove(card)
                                player[currentHand].append(card)

                                card = random.choice(cards)
                                cards.remove(card)
                                player[-1].append(card)

                                #removing money
                                async with self.client.pool.acquire() as db:
                                    money = await db.get_member_val(ctx.author.id, 'money')
                                    money -= bet[currentHand]
                                    await db.set_member_val(ctx.author.id, 'money', money)
                                    
                                asyncio.create_task( self.lead_and_rolecheck(ctx.author.id) )
                                bet.append(bet[currentHand])

                            else:
                                await ctx.send("Your two cards do not match.")

                else:
                    await ctx.send("You may only split your initial two cards.")

            elif action == "surrender":
                if len(player) == 1:
                    bet = bet[0]
                    bet /= 2
                    loss = math.floor(bet)
                    bet = math.ceil(bet)
                    await ctx.send(f"You surrendered from the game and lost ${bet}.")
                    
                    async with self.client.pool.acquire() as db:
                        money = await db.get_member_val(ctx.author.id, 'money')
                        money += loss
                        await db.set_member_val(ctx.author.id, 'money', money)
                        
                    asyncio.create_task( self.lead_and_rolecheck(ctx.author.id) )
                    return
                    
                else:
                    bet[currentHand] /= 2
                    bet[currentHand] = math.ceil(bet[currentHand])
                    await ctx.send(f"You surrendered hand {currentHand+1} and lost ${bet[currentHand]}.")
                    
                    async with self.client.pool.acquire() as db:
                        money = await db.get_member_val(ctx.author.id, 'money')
                        money += bet[currentHand]
                        await db.set_member_val(ctx.author.id, 'money', money)
                    
                    asyncio.create_task( self.lead_and_rolecheck(ctx.author.id) )

                    bet.remove(bet[currentHand])
                    player.remove(player[currentHand])

                    if currentHand == len(player):
                        break

            
            elif action.startswith('help'):
                helpContinue = True
                try:
                    helpAction = action.split()[1].lower()
                except:
                    helpContinue = False

                if helpContinue:
                    
                    if helpAction == 'hit':
                        await ctx.send("Draws a card and add it to your hand.")
                    
                    elif helpAction == 'pass':
                        await ctx.send("Ends your turn *or* switches to your next hand.")
                        
                    elif helpAction == 'double down' or helpAction == 'double':
                        await ctx.send("Both you and the dealer draws a card, and the bet doubles.")
                        
                    elif helpAction == 'split':
                        await ctx.send("Splits your hand into two different hands, if the cards are your first two cards *and* they are matching.")
                        
                    elif helpAction == 'surrender':
                        await ctx.send("Quit the game *or* discard a deck, and only lose 50% of your bet.")
                    
                    else:
                        await ctx.send('Enter a valid blackjack action.\nActions: `hit`, `pass`, `double down`, `split`, `surrender`. Use `help <action name>` to get info on the action.\n_ _')
                    
                    await asyncio.sleep(3)

            
                



            else:
                await ctx.send('Enter a valid blackjack action.\nActions: `hit`, `pass`, `double down`, `split`, `surrender`. Use `help <action name>` to get info on the action. Starting a message with `#` will ignore it.\n_ _')
                await asyncio.sleep(3)

        await ctx.send("Your turn is over. The dealer will now flip their card.")

        await asyncio.sleep(3)

        # Final text

        dealer.append(hidden)
        dealerValue = evaluateCards(dealer)
        text = f"Dealer's hand: {', '.join(dealer)} | Value: {dealerValue}\n"
        if len(player) == 1:
            text += f"Your hand: {', '.join(player[0])} | Value: {evaluateCards(player[0])} | Bet: ${bet[0]}\n"
        else:
            for hand in player:
                index = player.index(hand)
                text += f"Hand {index+1}: {', '.join(player[index])} | Value: {evaluateCards(player[index])} | Bet: ${bet[player.index(hand)]}\n"
            
        text += f"\n**Total bet: ${sum(bet)}**"

        await ctx.send(text)

        await asyncio.sleep(2)

        # Check if value is higher or lower than 16
        if dealerValue <= 16:
            await ctx.send("The dealer had less than 17 points, drawing another card...")
            await asyncio.sleep(2)

            if len(cards) <= 0:
                await ctx.send("The deck is empty. Reshuffled the deck.")
                await asyncio.sleep(2)
                # resetting deck
                cards = []
                for symbol in symbols:
                    for value in values:
                        cards.append(f"{symbol} {value}")

            card = random.choice(cards)
            cards.remove(card)
            dealer.append(card)

            dealerValue = evaluateCards(dealer)
            text = f"Dealer's hand: {', '.join(dealer)} | Value: {dealerValue}\n"
            if len(player) == 1:
                text += f"Your hand: {', '.join(player[0])} | Value: {evaluateCards(player[0])} | Bet: ${bet[0]}\n"
            else:
                for hand in player:
                    index = player.index(hand)
                    text += f"Hand {index+1}: {', '.join(player[index])} | Value: {evaluateCards(player[index])} | Bet: ${bet[player.index(hand)]}\n"
                
            text += f"\n**Total bet: ${sum(bet)}**"

            await ctx.send(text)
        else:
            await ctx.send('The dealer had more than 16 points. No card is drawn.') 

        await asyncio.sleep(2)

        async with self.client.pool.acquire() as db:

            dealerValue = evaluateCards(dealer)
            if dealerValue > 21:
                winnings = 0
                displaybet = []
                for b in bet:
                    winnings += math.ceil(b * 1.5)
                    displaybet.append(math.ceil(b / 2))

                await ctx.send(f"The dealer busted! You won your 1.5x your bet. ${sum(displaybet)} was added to your account.")
                
                money = await db.get_member_val(ctx.author.id, 'money')
                money += winnings
                await db.set_member_val(ctx.author.id, 'money', money)
                
                asyncio.create_task( self.lead_and_rolecheck(ctx.author.id) )
                return

            
            await asyncio.sleep(2)


            money = await db.get_member_val(ctx.author.id, 'money')
            if len(player) > 1:
                text = "**Results**:\n"
                for hand in player:
                    index = player.index(hand)
                    if evaluateCards(hand) > dealerValue:
                        text += f"Hand {index+1}: + ${math.ceil(bet[index//2])}\n"
                        money += math.ceil(bet[index] * 1.5)
                    elif evaluateCards(hand) == dealerValue:
                        text += f"Hand {index+1}: Tie\n"
                        money += bet[index]
                    else:
                        text += f"Hand {index+1}: - ${bet[index]}\n"

                
        
            else:
                text = "**Result**: "
                if evaluateCards(player[0]) > dealerValue:
                    text += f"+ ${math.ceil(bet[0]/2)}"
                    money += math.ceil(bet[0] * 1.5)
                elif evaluateCards(player[0]) == dealerValue:
                    text += f"Tie"
                    money += bet[0]
                else:
                    text += f"- ${bet[0]}"

            await db.set_member_val(ctx.author.id, 'money', money)
            await ctx.send(text)
            
            asyncio.create_task( self.lead_and_rolecheck(ctx.author.id) )

    
    async def roulette_timer(self, ctx):
        await asyncio.sleep(120)
        self.roulette_timer_task = None
        await self.do_roulette_spin(ctx)

    async def do_roulette_spin(self, ctx):

        winner = random.choice(self.roulette_members)

        earnings = self.roulette_bet * len(self.roulette_members)

        if len(self.roulette_members) > 1:
            await ctx.send(f'<@{winner}> has won the roulette and won ${earnings-self.roulette_bet}!')
        else:
            await ctx.send(f'<@{winner}> has won the roulette *because they\'re the only damn possible winner.* ')

        self.roulette_members.clear()

        async with self.client.pool.acquire() as db:

            money = await db.get_member_val(winner, 'money')
            money += earnings

            await db.set_member_val(winner, 'money', money)

            await db.rolecheck(winner)


    @commands.group(invoke_without_command=True)
    async def roulette(self, ctx):

        await ctx.send('Incorrect command usage: `.roulette start/spin/join/leave/list`')
    
    @roulette.command(name='start')
    async def roulette_start(self, ctx, bet=''):

        async with self.client.pool.acquire() as db:

            if not bet.isdigit():
                return await ctx.send('Invalid bet amount.')
            
            bet = int(bet)

            if bet <= 0:
                return await ctx.send('Invalid bet amount.')

            if not await db.event_disabled(ctx):
                return

            money = await db.get_member_val(ctx.author.id, 'money')

            if bet > money:
                return await ctx.send('You don\'t have enough money for that.')

            if self.client.heist:
                return await ctx.send('You cannot start a roulette during a heist.')

            if self.roulette_members:
                return await ctx.send(f'There is already an ongoing roulette.')

            self.roulette_members.append(ctx.author.id)
            self.roulette_timer_task = asyncio.create_task(self.roulette_timer(ctx))
            self.roulette_bet = bet

            await ctx.send(f'roulette started for **${bet}**! Use `.roulette join` to join it. The wheel will spin automatically in 2 minutes.')
            
            await db.set_member_val(ctx.author.id, 'money', money-bet)

            await db.rolecheck(ctx.author.id)

    @roulette.command(name='spin')
    async def spin(self, ctx):

        if not self.roulette_members:
            return await ctx.send('There is no ongoing roulette.')

        if ctx.author.id != self.roulette_members[0]:
            return await ctx.send('You must be the first in the roulette list in order to spin the wheel.')

        self.roulette_timer_task.cancel()
        self.roulette_timer_task = None

        await self.do_roulette_spin(ctx)

    
    @roulette.command(name='join')
    async def roulette_join(self, ctx):

        if not self.roulette_members:
            return await ctx.send('There is no ongoing roulette.')

        if ctx.author.id in self.roulette_members:
            return await ctx.send('You are already participating in this roulette.')
        
        async with self.client.pool.acquire() as db:
            money = await db.get_member_val(ctx.author.id, 'money')

            if self.roulette_bet > money:
                return await ctx.send('You do not have enough for that.')

            await db.set_member_val(ctx.author.id, 'money', money-self.roulette_bet)

            await db.rolecheck(ctx.author.id)


        await ctx.send(f'**{ctx.author.name}** has joined the roulette for **${self.roulette_bet}**')
        self.roulette_members.append(ctx.author.id)

    @roulette.command(name='leave')
    async def roulette_leave(self, ctx):

        if not self.roulette_members:
            return await ctx.send('There is no ongoing roulette.')

        if ctx.author.id not in self.roulette_members:
            return await ctx.send('You are not participating in this roulette.')
        
        async with self.client.pool.acquire() as db:
            money = await db.get_member_val(ctx.author.id, 'money')

            await db.set_member_val(ctx.author.id, 'money', money+self.roulette_bet)

            await db.rolecheck(ctx.author.id)


        await ctx.send(f'**{ctx.author.name}** has left the roulette.')
        self.roulette_members.remove(ctx.author.id)

        if not self.roulette_members:
            self.roulette_timer_task.cancel()
            self.roulette_timer_task = None
            
            self.roulette_bet = None

            await ctx.send('roulette cancelled since everyone left.')


    @roulette.command(name='list', aliases=['members'])
    async def roulette_list(self, ctx):
        
        if not self.roulette_members: return await ctx.send(f"There is no ongoing roulette right now.")

        guild = self.client.mainGuild

        embed = discord.Embed(color=0x42f5b0, title=f'roulette for ${self.roulette_bet}')

        for person in self.roulette_members:
            embed.add_field(value=f'{guild.get_member(person).name}', name=discord.utils.escape_markdown('___'), inline=True)

        await ctx.send(embed=embed)
    

def setup(client):
    client.add_cog(Gambling(client))