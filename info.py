import discord
from discord.ext import commands
import json
import time
import sqlite3
from sqlite3 import Error
from utils import *



class info(commands.Cog):

    def __init__(self, client):
        self.client = client


    @commands.command()
    @commands.check(rightCategory)
    async def help(self, ctx):
        helpchannel = self.client.get_channel(692950528417595453)
        await ctx.send(f'{helpchannel.mention}')

    @commands.command(aliases=['balance'])
    @commands.check(rightCategory)
    async def bal(self, ctx, member:discord.Member=None):
        author = ctx.author
        hierarchy = open_json()
        if member==None:
            money = read_value('members', 'id', author.id, 'money')
            bank = read_value('members', 'id', author.id, 'bank')
            total = read_value('members', 'id', author.id, 'total')
            avatar = author.avatar_url_as(static_format='jpg',size=256)
            embed = discord.Embed(color=0x57d9d0)
            embed.set_author(name=f"{author.name}'s balance",icon_url=avatar)
            embed.add_field(name="Cash",value=f'${money}', inline=True)
            embed.add_field(name="Bank", value=f'${bank}', inline=True)
            embed.add_field(name="Total", value=f'${total}', inline=True)
            await ctx.send(embed=embed)
        elif member.id==698771271353237575:
            await ctx.send("Why me?")
            return
        elif member.bot == True:
            await ctx.send("Bots don't play!")
            return
        elif member!=None:
            money = read_value('members', 'id', member.id, 'money')
            bank = read_value('members', 'id', member.id, 'bank')
            total = read_value('members', 'id', member.id, 'total')
            avatar = member.avatar_url_as(static_format='jpg',size=256)
            embed = discord.Embed(color=0x57d9d0)
            embed.set_author(name=f"{member.name}'s balance",icon_url=avatar)
            embed.add_field(name="Cash",value=f'${money}', inline=True)
            embed.add_field(name="Bank", value=f'${bank}', inline=True)
            embed.add_field(name="Total", value=f'${total}', inline=True)
            await ctx.send(embed=embed)

                    
    @commands.command()
    @commands.check(rightCategory)
    async def jailtime(self, ctx, member:discord.Member=None):
        author = ctx.author
        if member==None:
            jailtime = read_value('members', 'id', author.id, 'jailtime')
            if jailtime > time.time():
                bailprice = int(int(jailtime-time.time())/3600*40)
                await ctx.send(f'**{author.name}** has {splittime(jailtime)} left in jail with a bail price of ${bailprice}.')
            else:
                await ctx.send(f'**{author.name}** is not in jail.')
        elif member.id==698771271353237575:
            await ctx.send("Why me?")
            return
        elif member.bot == True:
            await ctx.send("Bots don't play!")
            return
        elif member!=None:
            jailtime = read_value('members', 'id', member.id, 'jailtime')
            if jailtime > time.time():
                bailprice = int(int(jailtime-time.time())/3600*40)
                await ctx.send(f'**{member.name}** has {splittime(jailtime)} left in jail with a bail price of ${bailprice}.')
            else:
                await ctx.send(f'**{member.name}** is not in jail.')

    @commands.command()
    @commands.check(rightCategory)
    async def worktime(self, ctx, member:discord.Member=None):
        author = ctx.author
        if member==None:
            workc = read_value('members', 'id', author.id, 'workc')
            if workc > time.time():
                await ctx.send(f'**{author.name}** has {splittime(workc)} left until they can work.')
            else:
                await ctx.send(f'**{author.name}** can work.')
        elif member.id==698771271353237575:
            await ctx.send("Why me?")
            return
        elif member.bot:
            await ctx.send("Bots don't play!")
            return
        elif member!=None:
            workc = read_value('members', 'id', member.id, 'workc')
            if workc > time.time():
                await ctx.send(f'**{member.name}** has {splittime(workc)} left until they can work.')
            else:
                await ctx.send(f'**{member.name}** can work.')

    @commands.command()
    @commands.check(rightCategory)
    async def stealtime(self, ctx, member:discord.Member=None):
        author = ctx.author
        hierarchy = open_json()
        if member==None:
            stealc = read_value('members', 'id', author.id, 'stealc')
            if stealc > time.time():
                await ctx.send(f'**{author.name}** has {splittime(stealc)} left until they can steal.')
            else:
                await ctx.send(f'**{author.name}** can steal.')
        elif member.id==698771271353237575:
            await ctx.send("Why me?")
            return
        elif member.bot == True:
            await ctx.send("Bots don't play!")
            return
        elif member!=None:
            stealc = read_value('members', 'id', member.id, 'stealc')
            if stealc > time.time():
                await ctx.send(f'**{member.name}** has {splittime(stealc)} left until they can steal.')
            else:
                await ctx.send(f'**{member.name}** can steal.')

    @commands.command()
    @commands.check(rightCategory)
    async def banktime(self, ctx, member:discord.Member=None):
        author = ctx.author
        hierarchy = open_json()
        if member==None:
            bankc = read_value('members', 'id', author.id, 'bankc')
            if bankc > time.time():
                await ctx.send(f'**{author.name}** has {splittime(bankc)} left until they can access their bank.')
            else:
                await ctx.send(f'**{author.name}** can access their bank.')
        elif member.id==698771271353237575:
            await ctx.send("Why me?")
            return
        elif member.bot == True:
            await ctx.send("Bots don't play!")
            return
        elif member!=None:
            bankc = read_value('members', 'id', member.id, 'bankc')
            if bankc > time.time():
                await ctx.send(f'**{member.name}** has {splittime(bankc)} left until they can access their bank.')
            else:
                await ctx.send(f'**{member.name}** can access their bank.')


    @commands.command()
    @commands.check(rightCategory)
    async def heisttime(self, ctx):
        guild = self.client.get_guild(692906379203313695)
        author = ctx.author
        heist = open_json()
        conn = sqlite3.connect('hierarchy.db')
        c = conn.cursor()
        c.execute('SELECT cooldown FROM heist')
        heistc = c.fetchone()
        conn.close()
        heistc = int(heistc[0])
        if heistc > time.time():
            await ctx.send(f'Everyone must wait {splittime(heistc)} before another heist can be made.')
        elif heist["heistt"] > 0:
            await ctx.send(f'The heist on **{guild.get_member(heist["heistv"]).name}** will start in {heist["heistt"]} seconds.')
        else:
            await ctx.send(f'A heist can be made.')             
        

    @commands.command()
    @commands.check(rightCategory)
    async def place(self, ctx, member:discord.Member=None):
        author = ctx.author
        guild = self.client.get_guild(692906379203313695)
        conn = sqlite3.connect('hierarchy.db')
        c = conn.cursor()
        c.execute('SELECT id, total FROM members')
        hierarchy = c.fetchall()
        conn.close()
        sorted_list = sorted(hierarchy, key=lambda k: k[1], reverse=True)
        sorted_list = tuple(filter(lambda x: guild.get_member(x[0]) is not None, sorted_list))
        if member==None:
            for x in sorted_list:
                if author.id == x[0]:
                    place = sorted_list.index(x)
            place += 1
            await ctx.send(f"**{author.name}** is **#{place}** in The Hierarchy.")   

        elif member.id==698771271353237575:
            await ctx.send("Why me?")
            return

        elif member.bot == True:
            await ctx.send("Bots don't play!")
            return

        elif member!=None:
            for x in sorted_list:
                if member.id == x[0]:
                    place = sorted_list.index(x)
            place += 1
            await ctx.send(f"**{member.name}** is **#{place}** in The Hierarchy.")

    @commands.command()
    @commands.check(rightCategory)
    async def items(self, ctx, member:discord.Member=None):
        author = ctx.author
        guild = self.client.get_guild(692906379203313695)
        if not member:
            items = read_value('members', 'id', author.id, 'items').split()
            count = []
            tempcount = []
            for x in items:
                if x not in tempcount:
                    count.append({"name":x,"count":1})
                    tempcount.append(x)
                elif x in tempcount:
                    for y in count:
                        if x==y["name"]:
                            y["count"]+=1
            avatar = guild.get_member(author.id)
            avatar = avatar.avatar_url_as(static_format='jpg',size=256)
            embed = discord.Embed(color=0x4785ff)
            embed.set_author(name=f"{author.name}'s items ({len(items)}/{read_value('members', 'id', author.id, 'storage')})",icon_url=avatar)

            embed2 = discord.Embed(color=0xff8000)
            embed2.set_author(name=f"{author.name}'s items in use",icon_url=avatar)
            inuse = in_use(author.id)
            for x in inuse:
                embed2.add_field(name='__________', value=f'{x["name"].capitalize()}: {splittime(x["timer"])}', inline=False)

            if len(embed2.fields) == 0:
                embed2.add_field(name='__________', value="None", inline=False)
                        
        elif member.id==698771271353237575:
            await ctx.send("Why me?")
            return
        elif member.bot == True:
            await ctx.send("Bots don't play!")
            return

        elif member != None:
            items = read_value('members', 'id', member.id, 'items').split()
            count = []
            tempcount = []
            for x in items:
                if x not in tempcount:
                    count.append({"name":x,"count":1})
                    tempcount.append(x)
                elif x in tempcount:
                    for y in count:
                        if x==y["name"]:
                            y["count"]+=1
            avatar = guild.get_member(member.id)
            avatar = avatar.avatar_url_as(static_format='jpg',size=256)
            embed = discord.Embed(color=0x4785ff)
            embed.set_author(name=f"{member.name}'s items ({len(items)}/{read_value('members', 'id', member.id, 'storage')})",icon_url=avatar)

            embed2 = discord.Embed(color=0xff8000)
            embed2.set_author(name=f"{member.name}'s items in use",icon_url=avatar)
            inuse = in_use(member.id)
            for x in inuse:
                embed2.add_field(name='__________', value=f'{x["name"].capitalize()}: {splittime(x["timer"])}', inline=False)

            if len(embed2.fields) == 0:
                embed2.add_field(name='__________', value="None", inline=False)

        for x in count:
            name = x["name"].capitalize()
            embed.add_field(name="__________", value=f"{name} x{x['count']}", inline=True)


        if len(embed.fields) == 0:
            embed.add_field(name='__________', value="None", inline=True)
        
        await ctx.send(embed=embed)
        await ctx.send(embed=embed2)

    @commands.command()
    @commands.check(rightCategory)
    async def around(self, ctx, find=None, member:discord.Member=None):
        if find == None:
            find = 3
        try:
            find = int(find)
        except:
            await ctx.send('Enter a valid number from 1-25')
            return
        if find < 1 or find > 25:
            await ctx.send('Enter a number from 1-25.')
            return
        if not member:
            author = ctx.author
        elif member.id==self.client.user.id:
            await ctx.send("Why me?")
            return
        elif member.bot:
            await ctx.send("Bots don't play!")
            return
        else:
            author = member
        author2 = ctx.author
        userid = author.id
        guild = self.client.get_guild(692906379203313695)
        conn = sqlite3.connect('hierarchy.db')
        c = conn.cursor()
        c.execute('SELECT id, total FROM members WHERE total > 0 ORDER BY total DESC')
        hierarchy = c.fetchall()
        conn.close()
        hierarchy = list(filter(lambda x: guild.get_member(x[0]) is not None, hierarchy))
        ids=[]
        for x in hierarchy:
            ids.append(x[0])
        try:
            index = ids.index(userid)
        except ValueError:
            hierarchy.append((userid, 0))
            ids.append(userid)
            index = ids.index(userid)


        lower_index = index-find

        if lower_index < 0:
            lower_index = 0

        higher_index = index+find+1
        length = len(hierarchy)

        if higher_index > length:
            higher_index = length

        result = hierarchy[lower_index:higher_index]

        avatar = author.avatar_url_as(static_format='jpg',size=256)
        embed = discord.Embed(color=0xffd24a)
        embed.set_author(name=f"Around {author.name}",icon_url=avatar)

        place = ids.index(result[0][0])+1
        for person in result:
            member2 = guild.get_member(person[0])
            medal = ''
            mk = ''
            if place == 1:
                medal = '🥇 '
            elif place == 2:
                medal = '🥈 '
            elif place == 3:
                medal = '🥉 '
            if author.id == person[0]:
                mk = '**'
            embed.add_field(name='__________', value=f'{mk}{place}. {member2.mention} {medal}- ${person[1]}{mk}', inline=False)
            place += 1
        if find > 5:
            await ctx.send('Embed too large, check your DMs.')
            await author2.send(embed=embed)
        else:
            await ctx.send(embed=embed)

    @commands.command()
    @commands.check(rightCategory)
    async def aroundm(self, ctx, find=None, member:discord.Member=None):
        if find == None:
            find = 3
        try:
            find = int(find)
        except:
            await ctx.send('Enter a valid number from 1-25')
            return
        if find < 1 or find > 25:
            await ctx.send('Enter a number from 1-25.')
            return
        if not member:
            author = ctx.author
        elif member.id==self.client.user.id:
            await ctx.send("Why me?")
            return
        elif member.bot:
            await ctx.send("Bots don't play!")
            return
        else:
            author = member
        author2 = ctx.author
        userid = author.id
        guild = self.client.get_guild(692906379203313695)
        conn = sqlite3.connect('hierarchy.db')
        c = conn.cursor()
        c.execute('SELECT id, total FROM members WHERE total > 0 ORDER BY total DESC')
        hierarchy = c.fetchall()
        conn.close()
        hierarchy = list(filter(lambda x: guild.get_member(x[0]) is not None, hierarchy))
        ids=[]
        for x in hierarchy:
            ids.append(x[0])
        try:
            index = ids.index(userid)
        except ValueError:
            hierarchy.append((userid, 0))
            ids.append(userid)
            index = ids.index(userid)


        lower_index = index-find

        if lower_index < 0:
            lower_index = 0

        higher_index = index+find+1
        length = len(hierarchy)

        if higher_index > length:
            higher_index = length

        result = hierarchy[lower_index:higher_index]

        avatar = author.avatar_url_as(static_format='jpg',size=256)
        embed = discord.Embed(color=0xffd24a)
        embed.set_author(name=f"Around {author.name}",icon_url=avatar)

        place = ids.index(result[0][0])+1
        for person in result:
            member2 = guild.get_member(person[0])
            medal = ''
            mk = ''
            if place == 1:
                medal = '🥇 '
            elif place == 2:
                medal = '🥈 '
            elif place == 3:
                medal = '🥉 '
            if author.id == person[0]:
                mk = '**'
            embed.add_field(name='__________', value=f'{mk}{place}. {member2.name} {medal}- ${person[1]}{mk}', inline=False)
            place += 1
        if find > 5:
            await ctx.send('Embed too large, check your DMs.')
            await author2.send(embed=embed)
        else:
            await ctx.send(embed=embed)

    @commands.command()
    @commands.check(rightCategory)
    async def dailyinfo(self, ctx, member:discord.Member=None):
        rewards = [40, 50, 60, 70, 80, 90, 100]
        if not member:
            streak = read_value('members', 'id', ctx.author.id, 'dailystreak')

            await ctx.send(f"**Day 1**: ${rewards[0]}\n**Day 2**: ${rewards[1]}\n**Day 3**: ${rewards[2]}\n**Day 4**: ${rewards[3]}\n**Day 5**: ${rewards[4]}\n**Day 6**: ${rewards[5]}\n**Day 7**: ${rewards[6]} + Random shop item\n\n*Your current streak: {streak}*")
        elif member.id==self.client.user.id:
            await ctx.send("Why me?")
            return
        elif member.bot:
            await ctx.send("Bots don't play!")
            return
        else:
            streak = read_value('members', 'id', member.id, 'dailystreak')

            await ctx.send(f"**{member.name}**'s streak: {streak}")

    @commands.command()
    @commands.check(rightCategory)
    async def boostcount(self, ctx, member:discord.Member=None):
        if not member:
            author = ctx.author
            premium = read_value('members', 'id', author.id, 'premium')
            if premium == 'False':
                await ctx.send("You don't have __premium__. Get __premium__ by boosting the server!")
                return
            boosts = read_value('members', 'id', author.id, 'boosts')
            await ctx.send(f"⏱️ **{author.name}**'s boosts: {boosts}")
        elif member.id==self.client.user.id:
            await ctx.send("Why me?")
            return
        elif member.bot:
            await ctx.send("Bots don't play!")
            return
        else:
            premium = read_value('members', 'id', member.id, 'premium')
            if premium == 'False':
                await ctx.send(f"**{member.name}** does not have __premium__.")
                return
            boosts = read_value('members', 'id', member.id, 'boosts')
            await ctx.send(f"⏱️ **{member.name}**'s boosts: {boosts}")


    @bal.error
    @place.error
    @jailtime.error
    @worktime.error
    @stealtime.error
    @banktime.error
    @items.error
    @around.error
    @aroundm.error
    @dailyinfo.error
    @boostcount.error
    async def member_not_found_error(self,ctx,error):
        if isinstance(error, commands.BadArgument):
            await ctx.send("Member not found.")
        else:
            print(error)


        

def setup(client):
    client.add_cog(info(client))



