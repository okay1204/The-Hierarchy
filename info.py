import discord
from discord.ext import commands
import json
import time
from utils import *



class info(commands.Cog):

    def __init__(self, client):
        self.client = client

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
                await ctx.send(f'**{author.name}** has {splittime(jailtime)} left in jail.')
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
                await ctx.send(f'**{member.name}** has {splittime(jailtime)} left in jail.')
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
        elif member.bot == True:
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
                await ctx.send(f'**{author.name}** has {splittime(bankc)} left until they can steal.')
            else:
                await ctx.send(f'**{author.name}** can steal.')
        elif member.id==698771271353237575:
            await ctx.send("Why me?")
            return
        elif member.bot == True:
            await ctx.send("Bots don't play!")
            return
        elif member!=None:
            bankc = read_value('members', 'id', member.id, 'bankc')
            if bankc > time.time():
                await ctx.send(f'**{member.name}** has {splittime(bankc)} left until they can steal.')
            else:
                await ctx.send(f'**{member.name}** can steal.')


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
    async def bailprice(self, ctx, member:discord.Member=None):
        author = ctx.author
        if member==None:
            jailtime = read_value('members', 'id', author.id, 'jailtime')
            if jailtime < time.time:
                await ctx.send(f"**{author.name}** is not in jail.")
                write_value('members', 'id', author.id, 'jailtime', 0)
            else:
                bailprice = int(int(jailtime-time.time)/3600*40)
                await ctx.send(f"**{author.name}**'s bail price right now is ${bailprice}.")
        elif member.id==698771271353237575:
            await ctx.send("Why me?")
            return
        elif member.bot == True:
            await ctx.send("Bots don't play!")
            return
        elif member!=None:
            jailtime = read_value('members', 'id', member.id, 'jailtime')
            if jailtime < time.time:
                await ctx.send(f"**{member.name}** is not in jail.")
                write_value('members', 'id', member.id, 'jailtime', 0)
            else:
                bailprice = int(int(jailtime-time.time)/3600*40)
                await ctx.send(f"**{member.name}**'s bail price right now is ${bailprice}.")



                
        

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
        for x in sorted_list:
            if guild.get_member(x[0]) is None:
                sorted_list.remove(x)
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
            inuse = []
            for x in read_value('members', 'id', author.id, 'inuse').split():
                try:
                    x = int(x)
                    citem["timer"] = x
                    inuse.append(citem)
                except:
                    citem = {'name':x}
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
            inuse = []
            for x in read_value('members', 'id', member.id, 'inuse').split():
                try:
                    x = int(x)
                    citem["timer"] = x
                    inuse.append(citem)
                except:
                    citem = {'name':x}
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
    async def tokens(self, ctx, member:discord.Member=None):
        author = ctx.author
        if not member:
            tokens = read_value('members', 'id', author.id, 'tokens')
            await ctx.send(f"**{author.name}** has {tokens} tokens.")
        elif member.id==698771271353237575:
            await ctx.send("Why me?")
            return
        elif member.bot == True:
            await ctx.send("Bots don't play!")
            return
        elif member != None:
            tokens = read_value('members', 'id', member.id, 'tokens')
            await ctx.send(f"**{member.name}** has {tokens} tokens.")

    
                        
    @bal.error
    async def bal_error(self,ctx,error):
        if isinstance(error, commands.BadArgument):
            await ctx.send("Member not found.")

    @place.error
    async def place_error(self,ctx,error):
        if isinstance(error, commands.BadArgument):
            await ctx.send("Member not found.")

    @jailtime.error
    async def jailtime_error(self,ctx,error):
        if isinstance(error, commands.BadArgument):
            await ctx.send("Member not found.")

    @worktime.error
    async def worktime_error(self,ctx,error):
        if isinstance(error, commands.BadArgument):
            await ctx.send("Member not found.")

    @stealtime.error
    async def stealtime_error(self,ctx,error):
        if isinstance(error, commands.BadArgument):
            await ctx.send("Member not found.")

    @bailprice.error
    async def bailprice_error(self,ctx,error):
        if isinstance(error, commands.BadArgument):
            await ctx.send("Member not found.")

    @banktime.error
    async def banktime_error(self,ctx,error):
        if isinstance(error, commands.BadArgument):
            await ctx.send("Member not found.")

    @items.error
    async def items_error(self,ctx,error):
        if isinstance(error, commands.BadArgument):
            await ctx.send("Member not found.")

    @tokens.error
    async def tokens_error(self,ctx,error):
        if isinstance(error, commands.BadArgument):
            await ctx.send("Member not found.")



        

def setup(client):
    client.add_cog(info(client))



