# pylint: disable=import-error, anomalous-backslash-in-string
import discord
from discord.ext import commands, tasks
import json
import time
import os
import asyncio

# To import from different path
import sys
sys.path.insert(1 , os.getcwd())

from utils import (splittime, timestring)

class alerts(commands.Cog):
    
    def __init__(self, client):
        self.client = client


        with open('./storage/jsons/alerts.json') as f:
            all_alerts = json.load(f)

        self.alert_tasks = {}

        for member, alerts in all_alerts.items():
            self.alert_tasks[int(member)] = []

            for alert in alerts:
                self.alert_tasks[int(member)].append( asyncio.create_task( self.make_alert(int(member), alert[0] - int(time.time()), alert[1]), name=alert[1] ))

    async def cog_check(self, ctx):
        if ctx.channel.category.id != self.client.rightCategory:
            return False
        else:
            return True

    def cog_unload(self):
        
        for alert_tasks in self.alert_tasks.items():
            alert_tasks = alert_tasks[1]
            for alert in alert_tasks:
                alert.cancel()



    async def make_alert(self, member, wait, name):
        
        try:
            if wait < 0:
                wait = 0
            
            await asyncio.sleep(wait)

            member = self.client.mainGuild.get_member(member)

            try:
                await member.send(f"🔔 Alert 🔔: {name}")
            except discord.Forbidden:
                pass

            with open('./storage/jsons/alerts.json') as f:
                all_alerts = json.load(f)
            
            for when, alert_name in all_alerts[str(member.id)]:
                
                if alert_name == name:
                    all_alerts[str(member.id)].remove([when, alert_name])

                    if not all_alerts[str(member.id)]:
                        del all_alerts[str(member.id)]

                    break

            with open('./storage/jsons/alerts.json', 'w') as f:
                json.dump(all_alerts, f, indent=2)

        except Exception as e:
            print(e)


    @commands.group(invoke_without_command=True)
    async def alert(self, ctx):
        await ctx.send("Incorrect command usage:\n`.alert list/add/delete`")


    @alert.command(name="list")
    async def alert_list(self, ctx, *, member:discord.Member=None):
        
        if not member:
            member = ctx.author

        with open('./storage/jsons/alerts.json') as f:
            all_alerts = json.load(f)

        if str(member.id) not in all_alerts:
            text = "None"
        else:
            text = "\n".join(map(lambda info: f"{all_alerts[str(member.id)].index([info[0], info[1]]) + 1}. {splittime(info[0])}: {info[1]}", all_alerts[str(member.id)]))
        
        
        embed = discord.Embed(color=0xff931f, description=text)
        embed.set_author(name=f"{member.name}'s alerts", icon_url=member.avatar_url_as(static_format='jpg'))

        await ctx.send(embed=embed)

    @alert.command(aliases=["make", "create"])
    async def add(self, ctx):

        await ctx.send("After how long do you want to be alerted? Use `0h 0m 0s` format, or type `cancel` to cancel.")

        while True:
            try:
                when = await self.client.wait_for('message', check=lambda m: m.author == ctx.author and m.channel == ctx.channel, timeout=20)
            except asyncio.TimeoutError:
                return await ctx.send("Alert make timed out.")

            when = when.content.lower()
            if when == "cancel":
                return await ctx.send("Alert make cancelled.")

            when = timestring(when)
            if when == None:
                await ctx.send("Incorrect time format. Use the `0h 0m 0s` format.")
            else:
                break

        
        if when < 1 or when > 86400: return await ctx.send("Choose a time between 1 second and a day.")


        await ctx.send("What do you want the alert to be called?")

        while True:
            try:
                name = await self.client.wait_for('message', check=lambda m: m.author == ctx.author and m.channel == ctx.channel, timeout=20)
            except asyncio.TimeoutError:
                return await ctx.send("Alert make timed out.")
        
            name = name.content
            if len(name) > 20:
                await ctx.send("Alert names can only be a maximum of 20 characters long.")

            else:
                break

        with open('./storage/jsons/alerts.json') as f:
            all_alerts = json.load(f)

        if str(ctx.author.id) in all_alerts:

            if len(all_alerts[str(ctx.author.id)]) >= 5:
                return await ctx.send("You may only have a maximum of 5 pending alerts at a time.")


            all_alerts[str(ctx.author.id)].append([int(time.time()) + when, name])
        else:
            all_alerts[str(ctx.author.id)] = [[int(time.time()) + when, name]]

        with open('./storage/jsons/alerts.json', 'w') as f:
            json.dump(all_alerts, f, indent=2)

        await ctx.send("🔔 Alert successfully created. 🔔")

        if str(ctx.author.id) in self.alert_tasks:
            self.alert_tasks[str(ctx.author.id)].append( asyncio.create_task( self.make_alert(ctx.author.id, when, name), name=name ) )
        else:
            self.alert_tasks[str(ctx.author.id)] = [asyncio.create_task( self.make_alert(ctx.author.id, when, name), name=name )]


    @alert.command(aliases=["remove", "cancel", "stop"])
    async def delete(self, ctx, number=None):
        if not number:
            return await ctx.send("Incorrect command usage:\n`.alert delete number`")

        try:
            number = int(number)
        except:
            return await ctx.send("Incorrect command usage:\n`.alert delete number`")

        with open('./storage/jsons/alerts.json') as f:
            all_alerts = json.load(f)

        if str(ctx.author.id) in all_alerts:
            
            # delete from json
            try:
                name = all_alerts[str(ctx.author.id)].pop(number - 1)[1]
            except IndexError:
                return await ctx.send(f"Alert {number} does not exist.")

            if not all_alerts[str(ctx.author.id)]:
                del all_alerts[str(ctx.author.id)]

            # cancel  alerttask
            for task in self.alert_tasks[str(ctx.author.id)]:
                if task.get_name() == name:
                    task.cancel()


                    if not self.alert_tasks[str(ctx.author.id)]:
                        del self.alert_tasks[str(ctx.author.id)]
                    break

        else:
            return await ctx.send("You do not have any pending alerts.")

        with open('./storage/jsons/alerts.json', 'w') as f:
            json.dump(all_alerts, f, indent=2)

        await ctx.send("🔔 Alert successfully deleted. 🔔")




# NOTE add in cogs to remove in main when done




def setup(client):
    client.add_cog(alerts(client))