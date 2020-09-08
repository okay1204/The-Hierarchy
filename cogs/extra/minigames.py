import random
import asyncio
import discord
import difflib
import inflect
from random_username.generate import generate_username
inflect = inflect.engine()

study_minigames = []

def study_minigame(function):
    study_minigames.append(function)

class Studygames:


    def __init__(self, client):
        self.client = client

    async def random_game(self, ctx, correct, total) -> bool:
        return await random.choice(study_minigames)(self, ctx, correct, total)

    @study_minigame
    async def react(self, ctx, correct, total) -> bool:

        with open('./storage/text/emojis.txt', encoding='utf-8') as f:
            emojis = f.read().splitlines()
        
        message = await ctx.send("Give me a second...")

        added = []
        for x in range(10): # noqa pylint: disable=unused-variable
            current = emojis.pop(random.randint(0, len(emojis)))
            added.append(current)
            await message.add_reaction(current)

        chosen = random.choice(added)

        await message.edit(content=f"React with  {chosen}  quick!")

        try:
            reaction, user = await self.client.wait_for('reaction_add', check=lambda reaction, user: user == ctx.author and reaction.message.id == message.id, timeout=2) #noqa pylint: disable=unused-variable
        except asyncio.TimeoutError:
            await ctx.send(f"Times up!\n{correct}/{total} tasks successful.")
            return False
        
        if str(reaction.emoji) == chosen:
            await ctx.send(f"GG\n{correct + 1}/{total} tasks successful.")
            return True
        else:
            await ctx.send(f"Wrong reaction.\n{correct}/{total} tasks successful.")
            return False

        

    @study_minigame
    async def emoji_count(self, ctx, correct, total) -> bool:
    

        emojis = [
            {'emoji':'🍎', 'name':'red apples', 'helping verb': 'many'},
            {'emoji':'🍏', 'name':'green apples', 'helping verb': 'many'},
            {'emoji':'🍌', 'name':'bananas', 'helping verb': 'many'},
            {'emoji':'🍊', 'name':'oranges', 'helping verb': 'many'},
            {'emoji':'🍑', 'name':'peaches', 'helping verb': 'many'},
            {'emoji':'🍆', 'name':'eggplants', 'helping verb': 'many'},
            {'emoji':'🍅', 'name':'tomatoes', 'helping verb': 'many'},
            {'emoji':'🥔', 'name':'potatoes', 'helping verb': 'many'},
            {'emoji':'🥬', 'name':'lettuce', 'helping verb': 'much'}
        ]

        text = ''
        for x in range(random.randint(30,50)): # noqa pylint: disable=unused-variable
            text += random.choice(emojis)['emoji']

        ask = random.choice(emojis)
        answer = text.count(ask['emoji'])

        await ctx.send(f"How {ask['helping verb']} {ask['name']} are there?\n\n{text}")

        try:
            response = await self.client.wait_for('message', check=lambda m: m.author == ctx.author and m.channel == ctx.channel, timeout=7)
        except asyncio.TimeoutError:
            await ctx.send(f"Out of time: The answer was {answer}.\n{correct}/{total} tasks successful.")
            return False
        
        response = response.content.lower()

        if response == str(answer):
            await ctx.send(f"Correct.\n{correct + 1}/{total} tasks successful.")
            return True
        else:
            await ctx.send(f"Incorrect. The answer was {answer}.\n{correct}/{total} tasks successful.")
            return False

    @study_minigame
    async def math(self, ctx, correct, total) -> bool:

        timer = random.randint(5, 10)
        text = f"Solve this in {timer} seconds:\n"

        mod = random.randint(1,2) # multiply or divide
        aos = random.randint(1,2) # add or subtract

        # constructing problem
        if mod == 1:

            n1 = random.randint(2,9)
            n2 = random.randint(2,9)

            if aos == 1:
                n3 = random.randint(1,10)
                answer = (n1 * n2) + n3
                order = random.randint(1,2)
                if order == 1:
                    text += f"{n1} x {n2} + {n3}"
                elif order == 2:
                    text += f"{n3} + {n2} x {n1}"
            
            else:
                n3 = random.randint(1,10)
                answer = (n1 * n2) - n3
                order = random.randint(1,2)
                if order == 1:
                    text += f"{n1} x {n2} - {n3}"
                elif order == 2:
                    text += f"-{n3} + {n2} x {n1}"

        else:

            t1 = random.randint(2,9)
            t2 = random.randint(2,9)
            t3 = t1 * t2
            n1 = t3
            n2 = t1

            if aos == 1:

                n3 = random.randint(1,10)
                answer = t2 + n3
                order = random.randint(1,2)

                if order == 1:
                    text += f"{n1} / {n2} + {n3}"
                else:
                    text += f"{n3} + {n1} / {n2}"

            else:

                n3 = random.randint(1,10)
                answer = t2 - n3
                order = random.randint(1,2)

                if order == 1:
                    text += f"{n1} / {n2} - {n3}"
                elif order == 2:
                    text += f"-{n3} + {n1} / {n2}"

        await ctx.send(text)

        try:
            submission = await self.client.wait_for('message', check=lambda m: m.channel == ctx.channel and m.author == ctx.author, timeout=timer)

        except asyncio.TimeoutError:
            await ctx.send(f'Times up! The answer was {answer}.\n{correct}/{total} tasks successful.')
            return False

        answer = str(answer)
        submission = submission.content

        if submission == answer:
            await ctx.send(f'Correct.\n{correct + 1}/{total} tasks successful.')
            return True
            
        else:
            await ctx.send(f'Incorrect. The answer was {answer}.\n{correct}/{total} tasks successful.')
            return False


    @study_minigame
    async def memorize(self, ctx, correct, total) -> bool:

        with open('./storage/text/englishwords.txt', 'r') as f:
            words = f.read().splitlines()


        colors = [
                {'unicode':'\U0001f534', 'name':'red'},
                {'unicode':'\U000026aa', 'name':'white'},
                {'unicode':'\U0001f7e3', 'name':'purple'},
                {'unicode':'\U0001f7e0', 'name':'orange'},
                {'unicode':'\U0001f535', 'name':'blue'},
                {'unicode':'\U0001f7e4', 'name':'brown'},
                {'unicode':'\U0001f7e2', 'name':'green'}
        ]

        pairs = []
        messagecontent = '**Memorize this!**\n'

        for x in range(3): # noqa pylint: disable=unused-variable

            rcolor = colors.pop(random.randint(0, len(colors) - 1))
            rword = words.pop(random.randint(0, len(words) - 1))

            pairs.append({'color': rcolor['name'], 'word':rword})

            messagecontent += f'{rcolor["unicode"]}  {rword}\n'

        message = await ctx.send(messagecontent)

        await asyncio.sleep(5)

        ask = random.randint(1,2) # ask for either color or word
        pair = random.choice(pairs) # ask for which pair

        def check(m):
            return m.channel == ctx.channel and m.author == ctx.author

        if ask == 1:
            await message.edit(content=f"What color was next to {pair['word']}?") # asking for color
        else:
            await message.edit(content=f"What word was next to {pair['color']}?") # asking for word

        try:
            answer = await self.client.wait_for('message', check=check, timeout=20)
        except asyncio.TimeoutError:

            if ask == 1:
                await ctx.send(f"Took too long. The answer was {pair['color']}.\n{correct}/{total} tasks successful.")
            else:
                await ctx.send(f"Took too long. The answer was {pair['word']}.\n{correct}/{total} tasks successful.")

            return False


        answer = answer.content.lower()

        if ask == 1:
            if answer != pair['color']:
                await ctx.send(f"Incorrect. The answer was {pair['color']}.\n{correct}/{total} tasks successful.")
                return False
            else:
                await ctx.send(f"Correct.\n{correct + 1}/{total} tasks successful.")
                return True


        else:

            if answer != pair['word']:
                await ctx.send(f"Incorrect. The answer was {pair['word']}.\n{correct}/{total} tasks successful.")
                return False
            else:
                await ctx.send(f"Correct.\n{correct + 1}/{total} tasks successful.")
                return True


chef_minigames = []
def chef_game(function):
    chef_minigames.append(function)

raw_beef = "<:raw_beef:751215506786353193>"
rotten_beef = "<:rotten_beef:751604021218902046>"
steak = "<:steak:751215515321761792>"
burnt_steak = "<:burnt_steak:751215527556415549>"

class Chef:

    def __init__(self, client):
        self.client = client

    async def random_game(self, ctx, correct, total) -> bool:
        return await random.choice(chef_minigames)(self, ctx, correct, total)

    @chef_game
    async def missing_ingredient(self, ctx, correct, total) -> bool:

        all_ingredients = ['Beef', 'Chicken', 'Lettuce', 'Tomato', 'Cheese', 'Pickle', 'Jalapeno', 'Onion']
        random.shuffle(all_ingredients)
        picked = []

        items = {}

        for ingredient in all_ingredients:
            if random.randint(0, 1):
                items[ingredient] = random.randint(1, 3)
                picked.append(ingredient)

        for ingredient in picked:
            all_ingredients.remove(ingredient)

        # making sure there are enough items
        while len(items) < 2:
            new_ingredient = random.choice(all_ingredients)
            items[new_ingredient] = random.randint(1, 3)

        order = ""

        for key, value in items.items():
            order += f"\t{key} x{value}\n"
        
        
        await ctx.send(f"Here is your order:\n\n{order}")

        await asyncio.sleep(5)

        item_missing = random.choice(list(items.keys()))

        items[item_missing] -= 1

        items = list(items.items())
        
        random.shuffle(items)

        new_items = {}
        for item in items: new_items[item[0]] = item[1]
        

        find = ""

        for key, value in new_items.items():
            
            if value != 0:
                find += f"\t{key} x{value}\n"
            else:
                pass
        
        await ctx.send(f"Quickly find the missing ingredient:\n\n{find}")

        try:
            response = await self.client.wait_for('message', check=lambda m: m.channel == ctx.channel and m.author == ctx.author, timeout=random.randint(5, 8))
        except asyncio.TimeoutError:
            await ctx.send(f"Times up!\n{correct}/{total} tasks successful.")
            return False


        if response.content.lower() == item_missing.lower():
            await ctx.send(f"Correct.\n{correct+1}/{total} tasks successful.")
            return True

        else:
            await ctx.send(f"Incorrect.\n{correct}/{total} tasks successful.")
            return False
        

    @chef_game
    async def stoves(self, ctx, correct, total) -> bool:

        message = await ctx.send("Give me a second...") 
        for x in range(1, 7):
            await message.add_reaction(f'{x}\N{combining enclosing keycap}')

        self.stoves = []
        for x in range(6):
            self.stoves.append({'state':'raw', 'emoji': raw_beef,'times':(random.uniform(3, 20), random.uniform(2, 4))})

        text = "Here are your stoves, don't let the steak burn!\n"
        for x in range(1, 7, 3):
            text += f"{x}\N{combining enclosing keycap}\t{x+1}\N{combining enclosing keycap}\t{x+2}\N{combining enclosing keycap}\n{raw_beef}\t{raw_beef}\t{raw_beef}\n\n"

        await message.edit(content=text)

        for stove in self.stoves:
            asyncio.create_task(self.cook(ctx.channel, message, stove['times'], self.stoves.index(stove), ctx.author.id, correct, total), name=f"stove {ctx.author.id} {self.stoves.index(stove)}")

        reactions = []
        for x in range(6):
            reactions.append(f'{x+1}\N{combining enclosing keycap}')

        successful = 0

        while successful < 6:
            done, pending = await asyncio.wait([
                self.client.wait_for('reaction_add', check=lambda reaction, user: user == ctx.author and reaction.message.id == message.id and str(reaction.emoji) in reactions),
                self.client.wait_for('message', check=lambda m: m.author == self.client.user and m.channel == ctx.channel and m.content == f"One steak burned!\n{correct}/{total} tasks successful.\n|| {ctx.author.id} ||")
            ], return_when=asyncio.FIRST_COMPLETED)

            try:
                result = done.pop().result()
            except Exception as e:
                raise e

            for future in done:
                future.exception()

            for future in pending:
                future.cancel()

            if type(result) == discord.Message:
                await result.edit(content=f"One steak burned!\n{correct}/{total} tasks successful.")
                return False
            else:
                reaction = result



            reactions.remove(str(reaction[0].emoji))

            reaction = int(str(reaction[0].emoji)[0]) - 1

            state = self.stoves[reaction]['state']

            if state == 'raw':

                self.stoves[reaction]['emoji'] = '❌'

                # updating message
                text = "Here are your stoves, don't let the steak burn!\n"
                for x in range(0, 6, 3):
                    text += f"{x+1}\N{combining enclosing keycap}\t{x+2}\N{combining enclosing keycap}\t{x+3}\N{combining enclosing keycap}\n{self.stoves[x]['emoji']}\t{self.stoves[x+1]['emoji']}\t{self.stoves[x+2]['emoji']}\n\n"
                await message.edit(content=text)

                await ctx.send(f"The meat you removed was raw.\n{correct}/{total} tasks successful.")

                for task in asyncio.all_tasks():
                    if task.get_name().startswith(f'stove {ctx.author.id}'):
                        task.cancel()

                return False

            elif state == 'cooked':

                successful += 1

                self.stoves[reaction]['emoji'] = '✅'


                # updating message
                text = "Here are your stoves, don't let the steak burn!\n"
                for x in range(0, 6, 3):
                    text += f"{x+1}\N{combining enclosing keycap}\t{x+2}\N{combining enclosing keycap}\t{x+3}\N{combining enclosing keycap}\n{self.stoves[x]['emoji']}\t{self.stoves[x+1]['emoji']}\t{self.stoves[x+2]['emoji']}\n\n"
                
                asyncio.create_task(message.edit(content=text))

                asyncio.create_task(self.cancel_task(f'stove {ctx.author.id} {reaction}'))
        


        await ctx.send(f"You got all the meat!\n{correct+1}/{total} tasks successful.")
        return True

    async def cancel_task(self, name):
        for task in asyncio.all_tasks():
            if task.get_name() == name:
                task.cancel()
                break


    async def cook(self, channel, message, duration, index, authorid, correct, total):
        
        await asyncio.sleep(duration[0])

        self.stoves[index]['state'] = 'cooked'
        self.stoves[index]['emoji'] = steak

        text = "Here are your stoves, don't let the steak burn!\n"

        for x in range(0, 6, 3):
            text += f"{x+1}\N{combining enclosing keycap}\t{x+2}\N{combining enclosing keycap}\t{x+3}\N{combining enclosing keycap}\n{self.stoves[x]['emoji']}\t{self.stoves[x+1]['emoji']}\t{self.stoves[x+2]['emoji']}\n\n"

        await message.edit(content=text)

        await asyncio.sleep(duration[1])

        self.stoves[index]['state'] = 'burnt'
        self.stoves[index]['emoji'] = burnt_steak

        text = "Here are your stoves, don't let the steak burn!\n"

        for x in range(0, 6, 3):
            text += f"{x+1}\N{combining enclosing keycap}\t{x+2}\N{combining enclosing keycap}\t{x+3}\N{combining enclosing keycap}\n{self.stoves[x]['emoji']}\t{self.stoves[x+1]['emoji']}\t{self.stoves[x+2]['emoji']}\n\n"

        await message.edit(content=text)

        for task in asyncio.all_tasks():
            if task.get_name().startswith(f'stove {authorid}'):
                task.cancel()

        await channel.send(f"One steak burned!\n{correct}/{total} tasks successful.\n|| {authorid} ||") # content linked to stoves, change stoves if this is changed
        

    @chef_game
    async def rotten_meat(self, ctx, correct, total):
        
        meat = []
        for x in range(9):
            meat.append({'number': x, 'current':'clean', 'state':random.choice(['clean', 'rotten'])})

        rotten = list(filter(lambda meat: meat['state'] == 'rotten', meat))
        random.shuffle(rotten)
        
        text = "Keep an eye on all the meat, you will remove all the rotten ones at the end.\n"
        for x in range(0, 9, 3):
            text += f"{x+1}\N{combining enclosing keycap}\t{x+2}\N{combining enclosing keycap}\t{x+3}\N{combining enclosing keycap}\n{raw_beef}\t{raw_beef}\t{raw_beef}\n\n"

        message = await ctx.send(text)

        await asyncio.sleep(3)

        for rotten_meat in rotten:
            
            meat[rotten_meat['number']]['current'] = 'rotten'

            text = "Keep an eye on all the meat, you will remove all the rotten ones at the end.\n"
            for x in range(0, 9, 3):
                text += f"{x+1}\N{combining enclosing keycap}\t{x+2}\N{combining enclosing keycap}\t{x+3}\N{combining enclosing keycap}\n{self.get_emoji(meat[x]['current'])}\t{self.get_emoji(meat[x+1]['current'])}\t{self.get_emoji(meat[x+2]['current'])}\n\n"
            
            await message.edit(content=text)

            await asyncio.sleep(random.uniform(1.5, 2))

            meat[rotten_meat['number']]['current'] = 'clean'

            text = "Keep an eye on all the meat, you will remove all the rotten ones at the end.\n"
            for x in range(0, 9, 3):
                text += f"{x+1}\N{combining enclosing keycap}\t{x+2}\N{combining enclosing keycap}\t{x+3}\N{combining enclosing keycap}\n{self.get_emoji(meat[x]['current'])}\t{self.get_emoji(meat[x+1]['current'])}\t{self.get_emoji(meat[x+2]['current'])}\n\n"
            
            await message.edit(content=text)

            await asyncio.sleep(random.uniform(1,4))


        await ctx.send("React with which ones you think are rotten, and react with the ✅ to submit. (There could be no rotten meat!)")


        number_emojis = []
        for x in range(1, 10):
            await message.add_reaction(f"{x}\N{combining enclosing keycap}")
            number_emojis.append(f"{x}\N{combining enclosing keycap}")
        await message.add_reaction('✅')

        try:
            reaction = await self.client.wait_for('reaction_add', check=lambda reaction, user: str(reaction.emoji) == '✅' and user == ctx.author and reaction.message.id == message.id, timeout=30)
        except asyncio.TimeoutError:
            await ctx.send(f"Took too long.\n{correct}/{total} tasks successful.")
            return False
        

        reaction = reaction[0]

        answers = []

        await ctx.send("Processing answer...")
        message = await ctx.channel.fetch_message(message.id)

        for reaction in message.reactions:
            if str(reaction.emoji) in number_emojis and ctx.author in await reaction.users().flatten():
                answers.append(reaction)
        
        rotten = list(map(lambda rotten: rotten['number'] + 1, rotten))
        rotten.sort()

        answers = list(map(lambda answer: int(str(answer.emoji)[0]), answers))
        answers.sort()
        
        if answers == rotten:
            await ctx.send(f"Correct.\n{correct+1}/{total} tasks successful.")
            return True
        else:
            rotten = list(map(lambda rotten: str(rotten), rotten))
            if len(rotten) > 1:
                await ctx.send(f"Incorrect. The answers were {', '.join(rotten)}.\n{correct}/{total} tasks successful.")
            elif len(rotten) == 1:
                await ctx.send(f"Incorrect. The answers was {rotten[0]}.\n{correct}/{total} tasks successful.")
            else:
                await ctx.send(f"Incorrect. The answer was none.\n{correct}/{total} tasks successful.")
            return False



    def get_emoji(self, name):

        if name == 'clean':
            return raw_beef
        else:
            return rotten_beef




scientist_minigames = []
def sci_game(function):
    scientist_minigames.append(function)


class Scientist:

    def __init__(self, client):
        self.client = client

    async def random_game(self, ctx, correct, total) -> bool:
        return await random.choice(scientist_minigames)(self, ctx, correct, total)

    @sci_game
    async def chemical_instructions(self, ctx, correct, total):

        colors = ["orange", "red", "blue", "green", "pink", "lime", "white", "gray", "black"]

        instructions_chemicals = list(map(lambda color: f"pour {color}", colors))

        instructions = ["POUR CHEMICAL", "stir slowly", "stir quickly", "wait", "cool down", "heat up", "blow air", "extract"] # POUR CHEMICAL is special
        
        message = await ctx.send("Remember these instructions in the right order:\n_ _")

        order = []

        previous = ""
        for x in range(random.randint(4, 5)):

            if x == 0: # first step should always be pour chemical
                chosen = "POUR CHEMICAL"
            else:
                chosen = random.choice(instructions)
                instructions.append(previous)

            if chosen == "POUR CHEMICAL":
                text = random.choice(instructions_chemicals)
            else:
                text = chosen
            
            order.append(text)
            
            await message.edit(content="Remember these instructions in the right order:\n" + text)
            
            previous = chosen
            instructions.remove(chosen)

            await asyncio.sleep(3)

        await message.edit(content="Now repeat the steps back, in the correct order.")

        for current in order:

            try:
                response = await self.client.wait_for('message', check=lambda m: m.author == ctx.author and m.channel == ctx.channel, timeout=30)
            except asyncio.TimeoutError:
                await ctx.send(f"Took too long.\n{correct}/{total} tasks successful.")
                return False
            
            if difflib.get_close_matches(response.content.lower(), [current], cutoff=0.4): # doesnt have to be perfect
                await response.add_reaction('✅')
            else:
                order_text = "\n".join(order)
                await ctx.send(f"Incorrect. The order was:\n{order_text}\n\n{correct}/{total} tasks successful.")
                return False
        
        await ctx.send(f"You got all the steps right!\n{correct+1}/{total} tasks successful.")
        return True

        #TODO 2 more minigames

        
            
garbage_minigames = []
def garb_game(function):
    garbage_minigames.append(function)


class Garbage_Collector:

    def __init__(self, client):
        self.client = client

    async def random_game(self, ctx, correct, total) -> bool:
        return await random.choice(garbage_minigames)(self, ctx, correct, total)

    @garb_game
    async def house_order(self, ctx, correct, total) -> bool:
        
        order = []
        for x in range(1, 6):
            order.append(x)

        random.shuffle(order)

        await ctx.send("Remember this order:\n")

        for number in order:
            order[order.index(number)] = {"number": number, "message": await ctx.send(f"{number}\N{combining enclosing keycap} 🏠")}

        await asyncio.sleep(2)

        for number in order:
            await number["message"].edit(content="🏠")
            await number["message"].add_reaction("🗑️")

        order.sort(key=lambda number: number["number"])

        messageids = list(map(lambda number: number["message"].id, order))

        await ctx.send("Collect the trash in the right order!")

        for number in order:

            try:
                reaction = await self.client.wait_for('reaction_add', check=lambda reaction, user: str(reaction.emoji == "🗑️") and user == ctx.author and reaction.message.id in messageids, timeout=20)
            except asyncio.TimeoutError:
                await ctx.send(f"Took too long.\n{correct}/{total} tasks successful.")
                return False
            reaction = reaction[0]

            if reaction.message.id == number["message"].id:
                await reaction.message.add_reaction("✅")
            else:
                await ctx.send(f"Incorrect.\n{correct}/{total} tasks successful.")
                asyncio.create_task(self.reveal_house_order(order))
                return False



        await ctx.send(f"You got the right order!\n{correct+1}/{total} tasks successful.")
        return True

        #TODO 2 more minigames


    async def reveal_house_order(self, order):
        for number in order:
            await number["message"].edit(content=f"{number['number']}\N{combining enclosing keycap} 🏠")
        



streamer_minigames = []
def stream_game(function):
    streamer_minigames.append(function)


class Streamer:

    def __init__(self, client):
        self.client = client

    async def random_game(self, ctx, correct, total) -> bool:
        return await random.choice(streamer_minigames)(self, ctx, correct, total)


    @stream_game
    async def delete_chat(self, ctx, correct, total):
        
        with open('./storage/text/good twitch messages.txt') as f:
            good_messages = f.read().splitlines()
        
        with open('./storage/text/bad twitch messages.txt') as f:
            bad_messages = f.read().splitlines()

        # to get upper and lower case messages
        good_messages = list(map(lambda message: message.lower(), good_messages))
        good_messages.extend(list(map(lambda message: message.upper(), good_messages)))
        bad_messages = list(map(lambda message: message.lower(), bad_messages))
        bad_messages.extend(list(map(lambda message: message.upper(), bad_messages)))


        messages = []

        for x in range(random.randint(4, 5)): # noqa pylint: disable=unused-variable
            messages.append({'type':'good', 'content':"✅\t\t" + random.choice(good_messages)})
        
        bad_count = random.randint(2, 4)

        for x in range(bad_count): # noqa pylint: disable=unused-variable
            messages.append({'type':'bad', 'content':"❌\t\t" + random.choice(bad_messages)})

        random.shuffle(messages)

        for message in messages:
            number = messages.index(message) + 1
            messages[messages.index(message)]["number"] = number
            messages[messages.index(message)]["content"] = f"{number}\N{combining enclosing keycap}" + message["content"]

        
        text = "Quickly delete all the bad messages!\n" + "\n".join(map(lambda message: message["content"], messages))

        discord_message = await ctx.send("Give me a second...")
        number_emojis = []
        for message in messages:
            await discord_message.add_reaction(f"{message['number']}\N{combining enclosing keycap}")
            number_emojis.append(f"{message['number']}\N{combining enclosing keycap}")

        await discord_message.edit(content=text)

        failed = False

        asyncio.create_task(self.stream_message_timer(ctx, correct, total), name=f"stream message timer {ctx.author.id}")
        while bad_count > 0:
            
            done, pending = await asyncio.wait([
                self.client.wait_for('reaction_add', check=lambda reaction, user: str(reaction.emoji) in number_emojis and reaction.message.id == discord_message.id and user == ctx.author),
                self.client.wait_for('message', check=lambda m: m.author == self.client.user and m.content == f"Times up!\n{correct}/{total} tasks successful.\n|| {ctx.author.id} ||")
            ], return_when=asyncio.FIRST_COMPLETED)

            try:
                result = done.pop().result()
            except Exception as e:
                raise e

            for future in done:
                future.exception()

            for future in pending:
                future.cancel()

            if type(result) == discord.Message:
                await result.edit(content=f"Times up!\n{correct}/{total} tasks successful.")
                return False
            else:
                reaction = result

            reaction = int(str(reaction[0].emoji)[0]) # extract number from emoji

            for message in messages:
                if message["number"] == reaction:
                    if message["type"] == "good":
                        failed = True
                    number_emojis.remove(f"{message['number']}\N{combining enclosing keycap}")
                    messages.remove(message)
                    break

            text = "Quickly delete all the bad messages!\n" + "\n".join(map(lambda message: message["content"], messages))
            asyncio.create_task(discord_message.edit(content=text))
            bad_count -= 1

            if failed:
                await ctx.send(f"You deleted an innocent text!\n{correct}/{total} tasks successful.")
                for task in asyncio.all_tasks():
                    if task.get_name() == f"stream message timer {ctx.author.id}":
                        task.cancel()
                        break
                return False

        await ctx.send(f"You deleted all the bad messages!\n{correct+1}/{total} tasks successful.")

        for task in asyncio.all_tasks():
            if task.get_name() == f"stream message timer {ctx.author.id}":
                task.cancel()
                break

        return True




    async def stream_message_timer(self, ctx, correct, total):
        await asyncio.sleep(4.5)
        await ctx.send(f"Times up!\n{correct}/{total} tasks successful.\n|| {ctx.author.id} ||") # message linked to delete_chat, change there if this is changed
        return False


    @stream_game
    async def remove_copyright(self, ctx, correct, total):
        
        with open('./storage/text/meme song names.txt', 'r') as f:
            all_names = f.read().splitlines()
        
        names = []
        for x in range(5): # noqa pylint: disable=unused-variable
            names.append(all_names.pop(random.randint(0, len(all_names)-1)))

        copyrighted = random.choice(names)
        fake = copyrighted

        # to get a letter that isnt a space
        fake = fake.lower()
        fake = list(fake)
        for letter in fake:
            index = fake.index(letter)
            fake[index] = (letter, index+1)
        
        fake = list(filter(lambda fake: fake[0] != " ", fake))
        
        letter, placement = random.choice(fake)

        # to remove any duplicate possible answers
        for name in names:
            if name != copyrighted :
                while True:
                    
                    if placement <= len(name):

                        if name.lower()[placement-1] == letter:
                            try:
                                all_names.remove(name)
                            except:
                                pass
                            names[names.index(name)] = random.choice(all_names)
                        
                        else: break
                    else: break

        text = "Examine these:\n\n"
        for x in range(len(names)):
            text += f"{x+1}\N{combining enclosing keycap}\t{names[x]}\n"

        message = await ctx.send(text)

        # waits for all reactions to be sent OR 5 seconds to be over
        await asyncio.wait([self.react_number_emojis(message), self.five_seconds()], return_when=asyncio.ALL_COMPLETED)

        number_emojis = []
        for x in range(1, 7):
            number_emojis.append(f"{x}\N{combining enclosing keycap}")

        # add text accordingly
        if bool(random.getrandbits(1)):
            if placement == len(copyrighted):
                text += f"\nQuickly mute the music where the name has a `{letter}` in the last position."
            else:
                text += f"\nQuickly mute the music where the name has a `{letter}` in the {inflect.number_to_words(inflect.ordinal(placement))} position."
        else:
            # count from last
            reverse_placement = abs(placement - len(copyrighted) - 1)

            if reverse_placement == 1:
                text += f"\nQuickly mute the music where the name has a `{letter}` in the last position."
            else:
                text += f"\nQuickly mute the music where the name has a `{letter}` in the {inflect.number_to_words(inflect.ordinal(reverse_placement))} to last position."

        await message.edit(content=text)

        try:
            reaction = await self.client.wait_for('reaction_add', check=lambda reaction, user: str(reaction.emoji) in number_emojis and user == ctx.author and reaction.message.id == message.id, timeout=random.randint(5, 7))
        except asyncio.TimeoutError:
            await ctx.send(f"Times up! The song name was \"{copyrighted}\".\n{correct}/{total} tasks successful.")
            return False

        # extacting number from reaction
        reaction = int(str(reaction[0].emoji)[0])

        if reaction == names.index(copyrighted) + 1:
            await ctx.send(f"You muted the right song.\n{correct+1}/{total} tasks successful.")
            return True
        else:
            await ctx.send(f"You muted the wrong song. The song name was \"{copyrighted}\".\n{correct}/{total} tasks successful.")
            return False

        
    @stream_game
    async def ban_abuser(self, ctx, correct, total):

        username = generate_username(1)[0]

        index = random.randint(0, len(username)-2)

        prompt = [username[:index], username[index:]]
        prompt = "".join(map(lambda text: f"||{text}||", prompt))

        prefixes = ["-", "!", "?", "+", ">", ">>", ";", ":", "[", "{", "="]

        prefix = random.choice(prefixes)

        timeout = random.randint(6, 8)

        await ctx.send(f"(Click on the black boxes to reveal them)\n\n{prompt} is abusing your stream! Quickly type \"{prefix}ban {prompt}\" in {timeout} seconds.\n")

        try:
            response = await self.client.wait_for('message', check=lambda m: m.channel == ctx.channel and m.author == ctx.author, timeout=timeout)
        except asyncio.TimeoutError:
            await ctx.send(f"Times up!\n{correct}/{total} tasks successful.")
            return False
        
        if response.content == f"{prefix}ban {username}":
            await ctx.send(f"Success!\n{correct+1}/{total} tasks successful.")
            return True
        
        else:
            await ctx.send(f"You made a typo.\n{correct}/{total} tasks successful.")
            return False

        


        

    async def react_number_emojis(self, message):
        for x in range(1, 6):
            await message.add_reaction(f"{x}\N{combining enclosing keycap}")

    async def five_seconds(self):
        await asyncio.sleep(5)



jobs = {'Chef': Chef, 'Scientist': Scientist, 'Garbage Collector': Garbage_Collector}
async def work_game(client, job, ctx, correct, total) -> bool:
    # return await jobs[job](client).random_game(ctx, correct, total)
    return await Streamer(client).random_game(ctx, correct, total)