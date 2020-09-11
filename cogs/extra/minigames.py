import random
import asyncio
import discord
import difflib
import inflect
import itertools
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
            await ctx.send(f"Time's up!\n{correct}/{total} tasks successful.")
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
            await ctx.send(f'Time\'s up! The answer was {answer}.\n{correct}/{total} tasks successful.')
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
            await ctx.send(f"Time's up! The answer was **{item_missing}**.\n{correct}/{total} tasks successful.")
            return False


        if response.content.lower() == item_missing.lower():
            await ctx.send(f"Correct.\n{correct+1}/{total} tasks successful.")
            return True

        else:
            await ctx.send(f"Incorrect. The answer was **{item_missing}**.\n{correct}/{total} tasks successful.")
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

        self.cook_tasks = []
        self.cook_tasks_states = []
        for index, stove in enumerate(self.stoves):
            self.cook_tasks.append(
                asyncio.create_task(self.cook(ctx.channel, message, stove['times'], index, ctx.author.id, correct, total), name=f"stoves cook {ctx.author.id} {index}")
            )
            self.cook_tasks_states.append("Completed")


        stoves_input_task = asyncio.create_task(self.stoves_input(ctx, correct, total, message))

        while True:
            await asyncio.wait([
                *self.cook_tasks, stoves_input_task
            ], return_when=asyncio.FIRST_COMPLETED)

            if not stoves_input_task.done():

                for index, task in enumerate(self.cook_tasks):
                    if task.done():
                        if self.cook_tasks_states[index] == "Completed":
                            stoves_input_task.cancel()
                            for task in self.cook_tasks:
                                task.cancel()
                            return False
                        else:
                            task.cancel()
                            continue


            else:
                for task in self.cook_tasks:
                    task.cancel()
                return await stoves_input_task
        
 

        

    async def stoves_input(self, ctx, correct, total, message):

        reactions = []
        for x in range(6):
            reactions.append(f'{x+1}\N{combining enclosing keycap}')

        successful = 0

        while successful < 6:
            reaction = await self.client.wait_for('reaction_add', check=lambda reaction, user: user == ctx.author and reaction.message.id == message.id and str(reaction.emoji) in reactions),

            reactions.remove(str(reaction[0][0].emoji))

            reaction = int(str(reaction[0][0].emoji)[0]) - 1

            state = self.stoves[reaction]['state']

            if state == 'raw':

                self.stoves[reaction]['emoji'] = '❌'

                # updating message
                text = "Here are your stoves, don't let the steak burn!\n"
                for x in range(0, 6, 3):
                    text += f"{x+1}\N{combining enclosing keycap}\t{x+2}\N{combining enclosing keycap}\t{x+3}\N{combining enclosing keycap}\n{self.stoves[x]['emoji']}\t{self.stoves[x+1]['emoji']}\t{self.stoves[x+2]['emoji']}\n\n"
                await message.edit(content=text)

                await ctx.send(f"The meat you removed was raw.\n{correct}/{total} tasks successful.")

                return False

            elif state == 'cooked':

                successful += 1

                self.stoves[reaction]['emoji'] = '✅'

                # updating message
                text = "Here are your stoves, don't let the steak burn!\n"
                for x in range(0, 6, 3):
                    text += f"{x+1}\N{combining enclosing keycap}\t{x+2}\N{combining enclosing keycap}\t{x+3}\N{combining enclosing keycap}\n{self.stoves[x]['emoji']}\t{self.stoves[x+1]['emoji']}\t{self.stoves[x+2]['emoji']}\n\n"
                
                asyncio.create_task(message.edit(content=text))
                
                for index, task in enumerate(self.cook_tasks):
                    if task.get_name() == f"stoves cook {ctx.author.id} {reaction}":
                        self.cook_tasks_states[index] = "Cancelled"
                        task.cancel()
                        break
    

        await ctx.send(f"You got all the meat!\n{correct+1}/{total} tasks successful.")
        return True

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

        await channel.send(f"One steak burned!\n{correct}/{total} tasks successful.")
        return False
        

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
            
            if difflib.get_close_matches(response.content.lower(), [current], cutoff=0.7): # doesnt have to be perfect
                await response.add_reaction('✅')
            else:
                order_text = "\n".join(order)
                await ctx.send(f"Incorrect. The order was:\n{order_text}\n\n{correct}/{total} tasks successful.")
                return False
        
        await ctx.send(f"You got all the steps right!\n{correct+1}/{total} tasks successful.")
        return True

    @sci_game
    async def word_scramble(self, ctx, correct, total):

        wordcount = 5
        
        with open('./storage/text/englishwords.txt') as f:
            all_words = f.read().splitlines()
            words = [all_words.pop(random.randint(0, len(all_words)-1)) for x in range(wordcount)]

        message = await ctx.send("Make a discovery and decode the scrambled words!")

        scramble_words_task = asyncio.create_task(self.scramble_words(ctx, words, message))
        scramble_timer_task = asyncio.create_task(self.scramble_timer(ctx, correct, total))
        word_scramble_input_task = asyncio.create_task(self.word_scramble_input(ctx, correct, total, wordcount, message))

        await asyncio.wait([
            scramble_timer_task, word_scramble_input_task
        ], return_when=asyncio.FIRST_COMPLETED)

        if not scramble_timer_task.done():
            scramble_timer_task.cancel()
            scramble_words_task.cancel()
            return await word_scramble_input_task
        
        elif not word_scramble_input_task.done():
            word_scramble_input_task.cancel()
            scramble_words_task.cancel()
            return await scramble_timer_task

        

    async def word_scramble_input(self, ctx, correct, total, wordcount, message):
        

        while wordcount > 0:

            try:
                answer = await self.client.wait_for('message', check=lambda m: m.author == ctx.author and m.channel == ctx.channel)
            except:
                pass
        
            
            word = answer.content.lower()

            for seq_word in self.sequences.keys():

                if seq_word.lower() == word.lower():

                    self.sequences[seq_word] = seq_word
                    wordcount -= 1
                    await answer.add_reaction("✅")

                    # update message
                    text = "Make a discovery and decode the scrambled words!\n\n"
                    for word, sequence in self.sequences.items():

                        if type(sequence) != str:
                            text += f"📘\t`{self.current[word]}`\n" 
                        else:
                            text += f"✅\t`{word}`\n"

                    asyncio.create_task(message.edit(content=text))
                        
                    break
            
            else:
                await ctx.send(f"Incorrect. The words were {', '.join(map(lambda word: f'`{word}`', self.sequences.keys()))}.\n{correct}/{total} tasks successful.")
                return False

        
        await ctx.send(f"You decoded all the words!\n{correct+1}/{total} tasks successful.")
        return True
        


    async def scramble_words(self, ctx, words, message):

        self.sequences = {}
        for word in words:

            sequence = []
            for x in range(3): # noqa pylint: disable=unused-variable
                shuffled = "".join(random.sample(list(word), len(word)))
                sequence.append(shuffled)

            sequence.insert(random.randint(0, len(sequence)), word)

            self.sequences[word] = itertools.cycle(sequence)

        self.current = {}
        while True:
            text = "Make a discovery and decode the scrambled words!\n\n"

            for word, sequence in self.sequences.items():

                if type(sequence) != str:
                    new_sequence = next(sequence)
                    text += f"📘\t`{new_sequence}`\n"
                    self.current[word] = new_sequence
                else:
                    text += f"✅\t`{sequence}`\n"

            await message.edit(content=text)

            await asyncio.sleep(random.uniform(1, 3))

    async def scramble_timer(self, ctx, correct, total):

        await asyncio.sleep(20)
        await ctx.send(content=f"Time's up! The words were {', '.join(map(lambda word: f'`{word}`', self.sequences.keys()))}.\n{correct}/{total} tasks successful.")
        return False


    @sci_game
    async def remove_threats(self, ctx, correct, total):

        with open('./storage/text/emojis.txt', 'r', encoding='utf-8') as f:
            emojis = f.read().splitlines()
        emojis.remove('💀')


        await ctx.send(f"Remove all 💀 reactions as fast as possible.")
        
        messages = [await ctx.send("_ _") for x in range(3)]

        remove_threats_random_reactions_tasks = []
        remove_threats_skulls_tasks = []
        remove_threats_input_task = asyncio.create_task( self.remove_threats_input(ctx.channel, ctx.author, messages, correct, total) )
        for message in messages:
            remove_threats_random_reactions_tasks.append( asyncio.create_task(self.remove_threats_random_reactions(message, emojis)) )
            remove_threats_skulls_tasks.append( asyncio.create_task(self.remove_threats_skulls(ctx.channel, message, ctx.author, correct, total)) )
        
        remove_threats_success_timer_task = asyncio.create_task(self.remove_threats_success_timer())

        await asyncio.wait([
            *remove_threats_skulls_tasks, remove_threats_success_timer_task, remove_threats_input_task
        ], return_when=asyncio.FIRST_COMPLETED)

        for task in remove_threats_random_reactions_tasks: task.cancel()
        for task in remove_threats_skulls_tasks: task.cancel()
        remove_threats_input_task.cancel()

        if remove_threats_success_timer_task.done():
            await ctx.send(f"You prevented the hazard!\n{correct+1}/{total} tasks successful.")
            return True

        else:
            return False


    async def remove_threats_input(self, channel, author, messages, correct, total):

        messages = [message.id for message in messages]

        while True:
            reaction = await self.client.wait_for('reaction_add', check=lambda reaction, user: user == author and reaction.message.id in messages)
            reaction = reaction[0]

            if str(reaction.emoji) != "💀":
                await channel.send(f"You removed the wrong threat!\n{correct}/{total} tasks successful.")
                return False


    async def remove_threats_random_reactions(self, message, emojis):

        await asyncio.sleep(random.uniform(2, 4))
        
        while True:
            try:
                await message.add_reaction(emojis.pop(random.randint(0, len(emojis)-1)))
            except:
                await asyncio.sleep(10000000000)
            await asyncio.sleep(random.uniform(1, 5))


    async def remove_threats_skulls(self, channel, message, author, correct, total):
        
        while True:
            await asyncio.sleep(random.uniform(3, 8))
            try:
                await message.add_reaction("💀")
            except:
                await asyncio.sleep(10000000000)

            try:
                reaction = await self.client.wait_for('reaction_add', check=lambda reaction, user: str(reaction.emoji) == "💀" and user == author and reaction.message.id == message.id, timeout=1.5)
            except asyncio.TimeoutError:
                await channel.send(f"The hazard spread!\n{correct}/{total} tasks successful.")
                return False

            reaction = reaction[0]

            message = await channel.fetch_message(message.id)

            for reaction in message.reactions:
                if str(reaction.emoji) == "💀":
                    await reaction.clear()
                    break

            

    async def remove_threats_success_timer(self):
        await asyncio.sleep(random.uniform(15, 30))
        return True


        
    
            
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



    async def reveal_house_order(self, order):
        for number in order:
            await number["message"].edit(content=f"{number['number']}\N{combining enclosing keycap} 🏠")

    @garb_game
    async def filter_messages(self, ctx, correct, total):
        
        self.good_ids = []
        self.bad_ids = []
        self.messages = {}


        filter_messages_input_task = asyncio.create_task(self.filter_messages_input(ctx, correct, total))
        throw_messages_task = asyncio.create_task(self.throw_messages(ctx, correct, total))

        await asyncio.wait([
            throw_messages_task, filter_messages_input_task
        ], return_when=asyncio.FIRST_COMPLETED)

        if not throw_messages_task.done():
            throw_messages_task.cancel()
            return await filter_messages_input_task

        elif not filter_messages_input_task.done():
            filter_messages_input_task.cancel()
            return await throw_messages_task
        
        


    
    async def filter_messages_input(self, ctx, correct, total):

        await ctx.send("Throw out any messages that has a 🗑️ in it!")

        while True:


            reaction = await self.client.wait_for('reaction_add', check=lambda reaction, user: (reaction.message.id in self.good_ids or reaction.message.id in self.bad_ids) and str(reaction.emoji) == "🗑️" and user == ctx.author)
            reaction = reaction[0]

            asyncio.create_task(self.messages[reaction.message.id].delete())

            if reaction.message.id in self.good_ids:
                await ctx.send(f"You threw out a clean message!\n{correct}/{total} tasks successful.")

                for task in asyncio.all_tasks():
                    if task.get_name() == f"throw messages {ctx.author.id}":
                        task.cancel()
                        break
                
                return False
            
            self.bad_ids.remove(reaction.message.id)

        

    
    async def throw_messages(self, ctx, correct, total):

        with open('./storage/text/emojis.txt', 'r', encoding='utf-8') as f:
            emojis = f.read().splitlines()
            # trashcan not included for some reason

        messages = ["trash" for x in range(random.randint(3, 5))]

        while len(messages) < 10:
            messages.append('clean')
        
        random.shuffle(messages)

        await asyncio.sleep(3)

        for message in messages:
            emojispam = []
            for x in range(random.randint(15, 20)): # noqa pylint: disable=unused-variable
                emojispam.append(random.choice(emojis))

            
            if message == "trash":
                emojispam[random.randint(0, len(emojispam)-1)] = "🗑️"

            emojispam = " ".join(emojispam)
            discord_message = await ctx.send(emojispam)
            
            if message == "trash":
                self.bad_ids.append(discord_message.id)
            else:
                self.good_ids.append(discord_message.id)
            
            self.messages[discord_message.id] = discord_message

            await discord_message.add_reaction("🗑️")

            await asyncio.sleep(1.5)

        await asyncio.sleep(3.5) # for total of 5 seconds

        if self.bad_ids:
            await ctx.send(content=f"Time's up!\n{correct}/{total} tasks successful.")
            return False
        else:
            await ctx.send(content=f"You successfully filtered all the trash!\n{correct+1}/{total} tasks successful.")
            return True



    @garb_game
    async def word_typing(self, ctx, correct, total):

        word_typing_input_task = asyncio.create_task(self.word_typing_input(ctx, correct, total))
        word_typing_timer_task = asyncio.create_task(self.word_typing_timer(ctx, correct, total))

        await asyncio.wait([
            word_typing_input_task, word_typing_timer_task
        ], return_when=asyncio.FIRST_COMPLETED)

        if not word_typing_timer_task.done():
            word_typing_timer_task.cancel()
            return word_typing_input_task

        elif not word_typing_input_task.done():
            word_typing_input_task.cancel()
            return word_typing_timer_task



    async def word_typing_input(self, ctx, correct, total):

        with open('./storage/text/englishwords.txt') as f:
            all_words = f.read().splitlines()

        words = [all_words.pop(random.randint(0, len(all_words)-1)) for x in range(10)]

        text = map(lambda word: f"🗑️\t`{word}`", words)
        text = "\n".join(text)

        message = await ctx.send(f"Type all these words quickly to collect the trash! (They do not have to be in order)\n\n{text}")

        while len(words) > 0:
            
            response = await self.client.wait_for('message', check=lambda m: m.channel == ctx.channel and m.author == ctx.author, timeout=30)

            
            if response.content.lower() in map(lambda word: word.lower(), words):
                asyncio.create_task(response.add_reaction("✅"))

                for word in words:
                    if response.content.lower() == word.lower():
                        words.remove(word)
                        break

                text = map(lambda word: f"🗑️\t`{word}`", words)
                text = "\n".join(text)

                asyncio.create_task(message.edit(content=f"Type all these words quickly to collect the trash! (They do not have to be in order)\n\n{text}"))
            else:
                asyncio.create_task(response.add_reaction("❌"))

        
        await ctx.send(f"Success.\n{correct+1}/{total} tasks successful.")
        return True


    
    async def word_typing_timer(self, ctx, correct, total):

        await asyncio.sleep(40)

        await ctx.send(f"Time's up!\n{correct}/{total} tasks successful.")
        return False

        



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

        delete_chat_input_task = asyncio.create_task(self.delete_chat_input(ctx, correct, total, number_emojis, discord_message, messages, bad_count))
        stream_message_timer_task = asyncio.create_task(self.stream_message_timer(ctx, correct, total))

        self.start_timer = False

        await asyncio.wait([
            delete_chat_input_task, stream_message_timer_task
        ], return_when=asyncio.FIRST_COMPLETED)

        if not stream_message_timer_task.done():
            stream_message_timer_task.cancel()
            await delete_chat_input_task
        
        elif not delete_chat_input_task.done():
            delete_chat_input_task.cancel()
            await stream_message_timer_task




    async def delete_chat_input(self, ctx, correct, total, number_emojis, discord_message, messages, bad_count):
        

        failed = False

        while bad_count > 0:
            
            reaction = await self.client.wait_for('reaction_add', check=lambda reaction, user: str(reaction.emoji) in number_emojis and reaction.message.id == discord_message.id and user == ctx.author),

            reaction = int(str(reaction[0][0].emoji)[0]) # extract number from emoji

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
                return False

        await ctx.send(f"You deleted all the bad messages!\n{correct+1}/{total} tasks successful.")
        return True




    async def stream_message_timer(self, ctx, correct, total):

        await asyncio.sleep(4.5)
        await ctx.send(f"Time's up!\n{correct}/{total} tasks successful.")
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
        

        # to remove any duplicate possible answers
        letter, placement = random.choice(fake[:5])

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
        await asyncio.wait([self.react_number_emojis(message), asyncio.sleep(5)], return_when=asyncio.ALL_COMPLETED)

        number_emojis = []
        for x in range(1, 7):
            number_emojis.append(f"{x}\N{combining enclosing keycap}")

        # add text accordingly
        text += f"\nQuickly mute the music where the name has a `{letter}` in the {inflect.number_to_words(inflect.ordinal(placement))} position."

        await message.edit(content=text)

        try:
            reaction = await self.client.wait_for('reaction_add', check=lambda reaction, user: str(reaction.emoji) in number_emojis and user == ctx.author and reaction.message.id == message.id, timeout=random.randint(5, 7))
        except asyncio.TimeoutError:
            await ctx.send(f"Time's up! The song name was \"{copyrighted}\".\n{correct}/{total} tasks successful.")
            return False

        # extacting number from reaction
        reaction = int(str(reaction[0].emoji)[0])

        if reaction == names.index(copyrighted) + 1:
            await ctx.send(f"You muted the right song.\n{correct+1}/{total} tasks successful.")
            return True
        else:
            await ctx.send(f"You muted the wrong song. The song name was \"{copyrighted}\".\n{correct}/{total} tasks successful.")
            return False 

    async def react_number_emojis(self, message):
        for x in range(1, 6):
            await message.add_reaction(f"{x}\N{combining enclosing keycap}")
        
    @stream_game
    async def ban_abuser(self, ctx, correct, total):

        username = generate_username(1)[0]

        index = random.randint(0, len(username)-2)

        prompt = [username[:index], username[index:]]
        prompt = "".join(map(lambda text: f"||{text}||", prompt))

        prefixes = ["-", "!", "?", "+", ">", ">>", ";", ":", "[", "{", "="]

        prefix = random.choice(prefixes)

        timeout = random.randint(7, 9)

        await ctx.send(f"(Click on the black boxes to reveal them)\n\n{prompt} is abusing your stream! Quickly type \"{prefix}ban {prompt}\" in {timeout} seconds.\n")

        try:
            response = await self.client.wait_for('message', check=lambda m: m.channel == ctx.channel and m.author == ctx.author, timeout=timeout)
        except asyncio.TimeoutError:
            await ctx.send(f"Time's up!\n{correct}/{total} tasks successful.")
            return False
        
        if response.content == f"{prefix}ban {username}":
            await ctx.send(f"Success!\n{correct+1}/{total} tasks successful.")
            return True
        
        else:
            await ctx.send(f"You made a typo.\n{correct}/{total} tasks successful.")
            return False


doctor_minigames = []
def doc_game(function):
    doctor_minigames.append(function)


class Doctor:

    def __init__(self, client):
        self.client = client

    async def random_game(self, ctx, correct, total) -> bool:
        return await random.choice(doctor_minigames)(self, ctx, correct, total)

    @doc_game
    async def get_items(self, ctx, correct, total):

        all_items = ["Syringe", "Stethoscope", "Ventilator", "Thermometer", "Blood Oximeter", "Gloves", "Mask", "Colposcope"]
        removed = []

        goal = []
        goal_names = []
        for x in range(3): # noqa pylint: disable=unused-variable
            item = all_items.pop(random.randint(0, len(all_items)-1))
            goal.append({"name": item, "count": random.randint(1,3)})
            goal_names.append(item)
            removed.append(item)

        for item in removed:
            all_items.append(item)

        text = ""
        for item in goal:
            text += f"{item['name']} x{item['count']}\n"

        message = await ctx.send(f"Memorize these items:\n\n{text}")

        await asyncio.sleep(7)
    
        await message.edit(content="Now gather all the items.\nType in the name of the item to recieve one of that item.")

        items = []

        while items != goal:
            try:
                response = await self.client.wait_for('message', check=lambda m: m.channel == ctx.channel and m.author == ctx.author, timeout=20)
            except asyncio.TimeoutError:
                await ctx.send(f"Timed out.\n{correct}/{total} tasks successful.")
                return False

            close = difflib.get_close_matches(response.content.lower(), all_items, cutoff=0.7)

            if not close:
                await ctx.send(f"You took the wrong item. The items were:\n\n{text}\n{correct}/{total} tasks successful.")
                return False
            
            answer = close[0]

            if answer not in goal_names:
                await ctx.send(f"You took the wrong item. The items were:\n\n{text}\n{correct}/{total} tasks successful.")
                return False


            for item in items:
                # add 1 to count, if exists
                if answer == item["name"]:
                    item["count"] += 1

                    # check if item count is greater than the goal
                    for goal_item in goal:
                        if answer == goal_item["name"] and item["count"] > goal_item["count"]:
                            await ctx.send(f"You took too much of `{answer}`. The items were:\n\n{text}\n{correct}/{total} tasks successful.")
                            return False

                    break
            else:
                items.append({"name": answer, "count": 1})
        
            await response.add_reaction('✅')
    

        await ctx.send(f"You got all the items!\n{correct+1}/{total} tasks successful.")
        return True


    @doc_game
    async def reaction_sequence(self, ctx, correct, total):

        emojis = ['💉', '💊', '🩺', '🩸', '❤️', '👨‍⚕️', '🛏️', '🌡️']

        order = [emojis.pop(random.randint(0, len(emojis)-1)) for x in range(4)]
        for emoji in order:
            emojis.append(emoji) # to return all emojis back
        
        prompt = await ctx.send("Pay attention to the order of reactions on this message...")

        await asyncio.sleep(3)

        for emoji in order:
            await prompt.add_reaction(emoji)
            await asyncio.sleep(2)
            await prompt.clear_reactions()
            await asyncio.sleep(2)

        message = await ctx.send("Give me a second... (Reacting too early WILL break it!)")

        random.shuffle(emojis)
        for emoji in emojis:
            await message.add_reaction(emoji)
        
        await message.edit(content="React to this message in the order you saw.")

        number = 0
        while number < len(order):

            try:
                reaction = await self.client.wait_for('reaction_add', check=lambda reaction, user: user == ctx.author and reaction.message.id == message.id and str(reaction.emoji) in emojis, timeout=20)
            except asyncio.TimeoutError:
                await ctx.send(f"Took too long. The order was:\n{'  '.join(order)}\n{correct}/{total} tasks successsful.")
                return False
            
            reaction = reaction[0]

            if str(reaction.emoji) == order[number]:
                number += 1
            else:
                await ctx.send(f"Incorrect. The order was:\n{'  '.join(order)}\n{correct}/{total} tasks successsful.")
                return False
        
        await ctx.send(f"Correct.\n{correct+1}/{total} tasks successsful.")
        return True

    @doc_game
    async def emoji_instruct(self, ctx, correct, total):

        all_choices = [-2, -1, 1, 2]
        key = {-2:"⏪", -1:"⬅️", 1:"➡️", 2:"⏩"}

        all_emojis = ['💉', '💊', '🩺', '🩸', '❤️', '👨‍⚕️', '🛏️', '🌡️']
        random.shuffle(all_emojis)
        emojis = {}

        for emoji in all_emojis:
            emojis[emoji] = False

        
        message = await ctx.send("Key:\n\n➡️ - Right\n⬅️ - Left\n⏩ - 2 Right\n⏪ - 2 Left\n⏭️ - As right as possible\n⏮️ - As left as possible")

        await asyncio.wait([
            self.emoji_instruct_message_react(message, emojis), asyncio.sleep(7)
        ], return_when=asyncio.ALL_COMPLETED)
    

        current = random.choice(list(emojis.keys()))
        await message.edit(content=f"React with {current}")

        while True:
            emojis[current] = True

            try:
                reaction = await self.client.wait_for('reaction_add', check=lambda reaction, user: str(reaction.emoji) in all_emojis and reaction.message.id == message.id and user == ctx.author, timeout=2)
            except asyncio.TimeoutError:
                await ctx.send(f"Too slow! You were meant to react with {current}\n{correct}/{total} tasks successful.")
                return False

            reaction = str(reaction[0].emoji)

            # checks if all emojis have been clicked
            if all(emojis.values()):
                break
            
            if reaction == current:
                
                # get new emoji to react with
                choices = ["left", "right"]
                emojikeys = list(emojis.keys())
                index = emojikeys.index(current)

                for choice in all_choices:
                    try:
                        changed = index + choice
                        if changed < 0:
                            continue

                        name = emojikeys[changed]
                        if not emojis[name]:
                            choices.append(choice)
                    except IndexError:
                        pass
                

                choice = random.choice(choices)

                if isinstance(choice, int):
                    current = emojikeys[index + choice]
                    asyncio.create_task(message.edit(content=key[choice]))
                else:
                    not_chosen = []
                    for emoji, value in emojis.items():
                        if not value:
                            not_chosen.append(emoji)


                    if choice == "right":
                        current = not_chosen[-1]
                        asyncio.create_task(message.edit(content="⏭️"))
                    else:
                        current = not_chosen[0]
                        asyncio.create_task(message.edit(content="⏮️"))

 


                

            else:
                await ctx.send(f"Wrong emoji! You were meant to react with {current}\n{correct}/{total} tasks successful.")
                return False


        await ctx.send(f"Success.\n{correct+1}/{total} tasks successful.")
        return True

        


    async def emoji_instruct_message_react(self, message, emojis):
        for emoji in emojis.keys():
            await message.add_reaction(emoji)

                    



jobs = {'Chef': Chef, 'Scientist': Scientist, 'Garbage Collector': Garbage_Collector, 'Streamer': Streamer, 'Doctor': Doctor}
async def work_game(client, job, ctx, correct, total) -> bool:
    return await jobs[job](client).random_game(ctx, correct, total)