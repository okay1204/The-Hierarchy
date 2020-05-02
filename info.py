import discord
from discord.ext import commands
import json
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
            for person in hierarchy:
                if str(author.id) == person["user"]:
                    name = author.name
                    avatar = author.avatar_url_as(static_format='jpg',size=256)
                    embed = discord.Embed(color=0x57d9d0)
                    embed.set_author(name=f"{name}'s balance",icon_url=avatar)
                    embed.add_field(name="Cash",value=f'${person["money"]}', inline=True)
                    embed.add_field(name="Bank", value=f'${person["bank"]}', inline=True)
                    embed.add_field(name="Total", value=f'${person["total"]}', inline=True)
                    await ctx.send(embed=embed)
        elif member.id==698771271353237575:
            await ctx.send("Why me?")
            return
        elif member.bot == True:
            await ctx.send("Bots don't play!")
            return
        elif member!=None:
            for person in hierarchy:
                if str(member.id) == person["user"]:
                    name = member.name
                    avatar = member.avatar_url_as(static_format='jpg',size=256)
                    embed = discord.Embed(color=0x57d9d0)
                    embed.set_author(name=f"{name}'s balance",icon_url=avatar)
                    embed.add_field(name="Cash",value=f'${person["money"]}', inline=True)
                    embed.add_field(name="Bank", value=f'${person["bank"]}', inline=True)
                    embed.add_field(name="Total", value=f'${person["total"]}', inline=True)
                    await ctx.send(embed=embed)

                    
    @commands.command()
    @commands.check(rightCategory)
    async def jailtime(self, ctx, member:discord.Member=None):
        author = ctx.author
        hierarchy = open_json()
        if member==None:
            for person in hierarchy:
                if str(author.id) == person["user"]:
                    if person["jailtime"] != 0:
                        await ctx.send(f'**{author.name}** has {splittime(person["jailtime"])} left in jail.')
                    else:
                        await ctx.send(f'**{author.name}** is not in jail.')
        elif member.id==698771271353237575:
            await ctx.send("Why me?")
            return
        elif member.bot == True:
            await ctx.send("Bots don't play!")
            return
        elif member!=None:
            for person in hierarchy:
                if str(member.id) == person["user"]:
                    if person["jailtime"] != 0:
                        await ctx.send(f'**{member.name}** has {splittime(person["jailtime"])} left in jail.')
                    else:
                        await ctx.send(f'**{member.name}** is not in jail.')

    @commands.command()
    @commands.check(rightCategory)
    async def worktime(self, ctx, member:discord.Member=None):
        author = ctx.author
        hierarchy = open_json()
        if member==None:
            for person in hierarchy:
                if str(author.id) == person["user"]:
                    if person["workc"] != 0:
                        await ctx.send(f'**{author.name}** has {splittime(person["workc"])} left until they can work.')
                    else:
                        await ctx.send(f'**{author.name}** can work.')
        elif member.id==698771271353237575:
            await ctx.send("Why me?")
            return
        elif member.bot == True:
            await ctx.send("Bots don't play!")
            return
        elif member!=None:
            for person in hierarchy:
                if str(member.id) == person["user"]:
                    if person["workc"] != 0:
                        await ctx.send(f'**{member.name}** has {splittime(person["workc"])} left until they can work.')
                    else:
                        await ctx.send(f'**{member.name}** can work.')

    @commands.command()
    @commands.check(rightCategory)
    async def stealtime(self, ctx, member:discord.Member=None):
        author = ctx.author
        hierarchy = open_json()
        if member==None:
            for person in hierarchy:
                if str(author.id) == person["user"]:
                    if person["stealc"] != 0:
                        await ctx.send(f'**{author.name}** has {splittime(person["stealc"])} left until they can steal.')
                    else:
                        await ctx.send(f'**{author.name}** can steal.')
        elif member.id==698771271353237575:
            await ctx.send("Why me?")
            return
        elif member.bot == True:
            await ctx.send("Bots don't play!")
            return
        elif member!=None:
            for person in hierarchy:
                if str(member.id) == person["user"]:
                    if person["stealc"] != 0:
                        await ctx.send(f'**{member.name}** has {splittime(person["stealc"])} left until they can steal.')
                    else:
                        await ctx.send(f'**{member.name}** can steal.')

    @commands.command()
    @commands.check(rightCategory)
    async def banktime(self, ctx, member:discord.Member=None):
        author = ctx.author
        hierarchy = open_json()
        if member==None:
            for person in hierarchy:
                if str(author.id) == person["user"]:
                    if person["bankc"] != 0:
                        await ctx.send(f'**{author.name}** has {splittime(person["bankc"])} left until they can access their bank.')
                    else:
                        await ctx.send(f'**{author.name}** can access their bank.')
        elif member.id==698771271353237575:
            await ctx.send("Why me?")
            return
        elif member.bot == True:
            await ctx.send("Bots don't play!")
            return
        elif member!=None:
            for person in hierarchy:
                if str(member.id) == person["user"]:
                    if person["stealc"] != 0:
                        await ctx.send(f'**{member.name}** has {splittime(person["bankc"])} left until they can access their bank.')
                    else:
                        await ctx.send(f'**{member.name}** can access their bank.')



    @commands.command()
    @commands.check(rightCategory)
    async def heisttime(self, ctx):
        guild = self.client.get_guild(692906379203313695)
        author = ctx.author
        hierarchystats = open_json2()
        if hierarchystats["heistc"] > 0:
            await ctx.send(f'Everyone must wait {splittime(hierarchystats["heistc"])} before another heist can be made.')
        elif hierarchystats["heistt"] > 0:
            await ctx.send(f'The heist on **{guild.get_member(int(hierarchystats["heistv"])).name}** will start in {hierarchystats["heistt"]} seconds.')
        else:
            await ctx.send(f'A heist can be made.')


    @commands.command()
    @commands.check(rightCategory)
    async def bailprice(self, ctx, member:discord.Member=None):
        author = ctx.author
        hierarchy = open_json()
        if member==None:
            for person in hierarchy:
                if str(author.id) == person["user"]:
                    if person["jailtime"] == 0:
                        await ctx.send(f"**{author.name}** is not in jail.")
                    else:
                        bailprice = int(person["jailtime"]/3600*40)
                        await ctx.send(f"**{author.name}**'s bail price right now is ${bailprice}.")
        elif member.id==698771271353237575:
            await ctx.send("Why me?")
            return
        elif member.bot == True:
            await ctx.send("Bots don't play!")
            return
        elif member!=None:
            for person in hierarchy:
                if str(member.id) == person["user"]:
                    if person["jailtime"] == 0:
                        await ctx.send(f"**{member.name}** is not in jail.")
                    else:
                        bailprice = int(person["jailtime"]/3600*40)
                        await ctx.send(f"**{member.name}**'s bail price right now is ${bailprice}.")



                
        

    @commands.command()
    @commands.check(rightCategory)
    async def place(self, ctx, member:discord.Member=None):
        author = ctx.author
        guild = self.client.get_guild(692906379203313695)
        hierarchy = open_json()
        if member==None:
            sorted_list = sorted(hierarchy, key=lambda k: k["total"], reverse=True)
            for x in sorted_list:
                if guild.get_member(int(x["user"])) is None:
                    sorted_list.remove(x)
            for x in sorted_list:
                if str(author.id) == x["user"]:
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
            sorted_list = sorted(hierarchy, key=lambda k: k["total"], reverse=True)
            for x in sorted_list:
                if guild.get_member(int(x["user"])) is None:
                    sorted_list.remove(x)
            for x in sorted_list:
                if str(member.id) == x["user"]:
                    place = sorted_list.index(x)
            place += 1
            await ctx.send(f"**{member.name}** is **#{place}** in The Hierarchy.")

    @commands.command()
    @commands.check(rightCategory)
    async def items(self, ctx, member:discord.Member=None):
        author = ctx.author
        guild = self.client.get_guild(692906379203313695)
        hierarchy = open_json()
        if not member:
            for person in hierarchy:
                if int(person["user"]) == author.id:
                    count = []
                    tempcount = []
                    for x in person["items"]:
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
                    embed.set_author(name=f"{author.name}'s items ({len(person['items'])}/{person['storage']})",icon_url=avatar)

                    embed2 = discord.Embed(color=0xff8000)
                    embed2.set_author(name=f"{author.name}'s items in use",icon_url=avatar)
                    for x in person["inuse"]:
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
            for person in hierarchy:
                if int(person["user"]) == member.id:
                    count = []
                    tempcount = []
                    for x in person["items"]:
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
                    embed.set_author(name=f"{author.name}'s items ({len(person['items'])}/{person['storage']})",icon_url=avatar)
                    embed2 = discord.Embed(color=0xff8000)
                    embed2.set_author(name=f"{member.name}'s items in use",icon_url=avatar)
                    for x in person["inuse"]:
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



        

def setup(client):
    client.add_cog(info(client))



