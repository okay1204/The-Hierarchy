import time
import json
import discord
import asyncpg
from utils import splittime

# pylint: disable=no-member

class DBUtils(asyncpg.Connection):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    # common functions

    async def get_member_val(self, id, column):
        return await self.fetchval(f'SELECT {column} FROM hierarchy.members WHERE id = $1;', id)

    async def set_member_val(self, id, column, overwrite):
        await self.execute(f'UPDATE hierarchy.members SET {column} = $1 WHERE id = $2;', overwrite, id)


    # check functions

    async def jail_heist_check(self, ctx, member):

        jailtime = await self.fetchval(f'SELECT jailtime FROM hierarchy.members WHERE id = $1;', member.id)
        
        if jailtime > time.time():
            await ctx.send(f'You are still in jail for {splittime(jailtime)}.')
            return False

        if self.client.heist:
            if self.client.heist["victim"] == member.id:
                await ctx.send(f"You are being targeted by heist.")
                return False
            
            elif member.id in self.client.heist["participants"]:
                await ctx.send(f"You are participating in a heist.")
                return False
        
        return True


    
    async def level_check(self, ctx, id, required_level, use_what):

        level = await self.get_member_val(id, 'level')
        
        if level < required_level:
            await ctx.send(f"You must be at least level {required_level} in order to {use_what}.")
            return False
        else:
            return True


    async def event_disabled(self, ctx):

        if ctx.bot.get_cog('Christmas'):

            with open('./storage/jsons/christmas meter.json') as f:
                meter_state = json.load(f)

            if meter_state == "on":
                await ctx.send("This command is disabled during the Christmas event.")
                return False

        with open('./storage/jsons/mode.json') as f:
            mode = json.load(f)

        if mode == "event":
            in_event = await self.get_member_val(ctx.author.id, 'in_event')

            if in_event:
                await ctx.send("This command is disabled during events.\nUse `.eventleave` to leave the event, **however you may not join back once you leave**.")
                return False

        
        return True


    async def member_event_check(self, ctx, id):

        with open('./storage/jsons/mode.json') as f:
            mode = json.load(f)

        if mode == "event":

            in_event = self.get_member_val(ctx.author.id, 'in_event')

            if in_event:
                await ctx.send("This user is participating in the event.")
                return False

        
        return True


    # item functions

    async def in_use(self, id):

        items = json.loads(await self.fetchval('SELECT in_use FROM hierarchy.members WHERE id = $1;', id))
        removed = []

        for name, timer in items.items():

            if timer <= time.time():
                removed.append(name)

        for name in removed:
            del items[name]

        if removed:
            await self.execute("UPDATE hierarchy.members SET in_use = $1 WHERE id = $2;", json.dumps(items), id)

        return items

    
    async def add_use(self, id, name, timer):

        items = json.loads(await self.fetchval('SELECT in_use FROM hierarchy.members WHERE id = $1;', id))
        items[name] = timer
        await self.execute('UPDATE hierarchy.members SET in_use = $1 WHERE id = $2;', json.dumps(items), id)

    async def remove_use(self, id, name):

        items = json.loads(await self.fetchval('SELECT in_use FROM hierarchy.members WHERE id = $1;', id))
        del items[name]
        await self.execute('UPDATE hierarchy.members SET in_use = $1 WHERE id = $2;', json.dumps(items), id)


    async def add_item(self, id, name):

        await self.execute('UPDATE hierarchy.members SET items = ARRAY_APPEND(items, $1) WHERE id = $2;', name, id)

    async def remove_item(self, id, name):

        items = await self.fetchval('SELECT items FROM hierarchy.members WHERE id = $1;', id)
        items.remove(name)
        await self.execute('UPDATE hierarchy.members SET items = $1 WHERE id = $2;', items, id)


    # misc

    async def steal_log(self, id, channel, text):

        message = await channel.send(text)

        steal_logs = json.loads(await self.get_member_val(id, 'steal_logs'))

        steal_logs.insert(0, {'text': text, 'created_at': str(message.created_at), 'jump_url': message.jump_url})
        steal_logs = steal_logs[:5]

        await self.set_member_val(id, 'steal_logs', json.dumps(steal_logs))



    async def around(self, id, find):

        hierarchy = await self.fetch('SELECT id, money + bank FROM members WHERE money + bank > 0 ORDER BY money + bank DESC;')

        guild = self.client.mainGuild

        hierarchy = list(filter(lambda x: guild.get_member(x[0]), hierarchy))
        ids=[]


        for x in hierarchy:
            ids.append(x[0])
        try:
            index = ids.index(id)
        except ValueError:
            hierarchy.append((id, 0))
            ids.append(id)
            index = ids.index(id)
        lower_index = index-find

        if lower_index < 0:
            lower_index = 0

        higher_index = index+find+1
        length = len(hierarchy)

        if higher_index > length:
            higher_index = length

        result = ids[lower_index:higher_index]
        return result



    async def leaderboard(self):
        guild = self.client.get_guild(692906379203313695)

        embed = discord.Embed(color = 0xffd24a, title='\U0001f3c6 Leaderboard \U0001f3c6')

        hierarchy = await self.fetch('SELECT id, money + bank AS total FROM hierarchy.members ORDER BY total DESC;')
        hierarchy = list(filter(lambda x: guild.get_member(x[0]), hierarchy))

        for x in range(10):

            medal = ''
            if x == 0:
                medal = ' 🥇'
            elif x == 1:
                medal = ' 🥈'
            elif x == 2:
                medal = ' 🥉'

            embed.add_field(name=discord.utils.escape_markdown('_______'),value=f'{x+1}. <@{hierarchy[x][0]}>{medal} - ${hierarchy[x][1]}',inline=False)


        await self.client.leaderboardMessage.edit(embed=embed)

    
    async def rolecheck(self, id):

        guild = self.client.mainGuild

        poor = guild.get_role(692952611141451787)
        middle = guild.get_role(692952792016355369)
        rich = guild.get_role(692952919947083788)

        hierarchy = await self.fetch('SELECT id, money + bank FROM hierarchy.members WHERE money + bank != 0')

        hierarchy = list(filter(lambda member: guild.get_member(member[0]), hierarchy))

        members = len(list(filter(lambda member: member.id in map(lambda user: user[0], hierarchy) and not member.bot, guild.members)))

        totalmoney = sum(map(lambda member: member[1], hierarchy))

        average = int(totalmoney/members)

        haverage = average + average/2
        laverage = average - average/2

        total = await self.get_member_val(id, 'money + bank')

        member = guild.get_member(id)

        member_roles = map(lambda role: role.id, member.roles)

        if total < laverage:
            if poor.id not in member_roles:
                await member.add_roles(poor)
                await member.remove_roles(middle, rich)

        elif total < haverage:
            if middle.id not in member_roles:
                await member.add_roles(middle)
                await member.remove_roles(poor, rich)

        elif total >= haverage: 
            if rich.id not in member_roles:
                await member.add_roles(rich)
                await member.remove_roles(poor, middle)