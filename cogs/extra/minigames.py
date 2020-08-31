import random
import asyncio

class Studygames():

    
    minigames = []

    def __init__(self, client):
        self.client = client

    async def random_game(self, ctx, correct, total) -> bool:
        return await random.choice(self.minigames)(self, ctx, correct, total)

    @minigames.append
    async def react(self, ctx, correct, total) -> bool:

        with open('./storage/other/emojis.txt', encoding='utf-8') as f:
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
            reaction, user = await self.client.wait_for('reaction_add', check=lambda reaction, user: user == ctx.author and reaction.message.id == message.id, timeout=2)
        except asyncio.TimeoutError:
            await ctx.send(f"Times up!\n{correct}/{total} tasks successful.")
            return False
        
        if str(reaction.emoji) == chosen:
            await ctx.send(f"GG\n{correct + 1}/{total} tasks successful.")
            return True
        else:
            await ctx.send(f"Wrong reaction.\n{correct}/{total} tasks successful.")
            return False

        

    @minigames.append
    async def emoji_count(self, ctx, correct, total) -> bool:
        
        count = random.randint(30, 40)

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
        for x in range(count): # noqa pylint: disable=unused-variable
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

    @minigames.append
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


    @minigames.append
    async def memorize(self, ctx, correct, total) -> bool:

        with open('./storage/other/englishwords.txt') as f:
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
