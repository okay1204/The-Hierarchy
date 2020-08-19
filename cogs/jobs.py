# pylint: disable=import-error

import discord
from discord.ext import commands
import random
import time
import os
import inspect
import asyncio
import sqlite3

# To import from different path
import sys
sys.path.insert(1 , os.getcwd())

from utils import (read_value, write_value, update_total, leaderboard,
rolecheck, level_check, minisplittime)


def days_hours_minutes(minutes):
    
    hours = minutes // 60
    rminutes = minutes % 60
    days = hours // 24
    rhours = hours % 24

    return f"{days}d {rhours}h {rminutes}m"



class University:

    def __init__(self, name: str, major: str, days: int, low_increment: int, high_increment: int,cooldown_minutes: int, max_study: int, price: int):
        self.name = name
        self.major = major
        self.days = days
        self.low_increment = low_increment
        self.high_increment = high_increment
        self.cooldown_minutes = cooldown_minutes
        self.max_study = max_study
        self.price = price

universities = [
            University('Culinary Arts Academy', 'Culinary', 7, 4, 8, 180, 100, 90),
            University('Emory', 'Medical', 12, 9, 12, 360, 95, 80),
            University('East Bay', 'Science', 5, 10, 15, 60, 65, 70),
            University('Harvard', 'Science', 11, 2, 4, 15, 95, 85),
            University('Apicius', 'Culinary', 5, 7, 9, 120, 90, 110),
            University('Duke', 'Medical', 7, 5, 8, 120, 100, 100)
        ]

def find_university(name: str):
    
    global universities
    for university in universities:
        if name == university.name:
            return university
    
    return None

def find_next_day(university: University, study_start: int) -> int:

    
    finish = university.days * 86400 + study_start

    if int(time.time()) >= finish:
        return 0

    temp_day = study_start
    days = []
    while temp_day <= finish:
        days.append(temp_day)
        temp_day += 86400

    days.pop(0)
    
    for day in days:
        if int(time.time()) <= day:
            next_time = day
            break
    
    next_time -= int(time.time())
    return next_time
 
class jobs(commands.Cog):

    def __init__(self, client):
        self.client = client

        conn = sqlite3.connect('./storage/databases/hierarchy.db')
        c = conn.cursor()
        c.execute('SELECT id, university, study_start FROM members WHERE university IS NOT NULL')
        students = c.fetchall()
        conn.close()
        
        for student in students:
            university = find_university(student[1])
            next_time = find_next_day(university, student[2])

            asyncio.create_task(self.school_fee(next_time, student[0], university.price), name=f"school {student[0]}")

    
    def cog_unload(self):

        for task in asyncio.all_tasks():
            if task.get_name().startswith('school '):
                task.cancel()


    async def cog_check(self, ctx):
        if ctx.channel.category.id != self.client.rightCategory:
            return False
        else:
            return True

    async def school_fee(self, duration, userid, payment):

        await asyncio.sleep(duration)

        broke = False

        money = read_value(userid, 'money')
        original_money = money
        money -= payment

        if money < 0:
            bank = read_value(userid, 'bank')
            original_bank = bank
            bank += money # adding negative amount
            money = 0 

            if bank < 0:
                broke = True
                money = original_money
                bank = original_bank
                
                # set university values
                conn = sqlite3.connect('./storage/databases/hierarchy.db')
                c = conn.cursor()
                c.execute('UPDATE members SET university = null, study_prog = 0, study_start = 0 WHERE id = ?', (userid,))
                conn.commit()
                conn.close()
            
            write_value(userid, 'bank', bank)
        
        write_value(userid, 'money', money)
        update_total(userid)

        asyncio.create_task(rolecheck(self.client, userid))
        asyncio.create_task(leaderboard(self.client))

        school_announcements = self.client.get_channel(744988365082067034)

        if not broke:
            await school_announcements.send(f"${payment} taken from <@{userid}>'s account.")
        else:
            await school_announcements.send(f"@<{userid}> did not have enough money to pay, enrollment automatically cancelled.")
            return
        
        if duration == 0:

            if read_value(userid, 'final_announced') == "False":

                school_announcements = self.client.get_channel(744988365082067034)
                
                await school_announcements.send(f"<@{userid}> can take their finals.")
                write_value(userid, 'final_announced', 'True')


    @commands.command()
    async def universities(self, ctx):
        
        embed = discord.Embed(color=0x48157a, title="Universities", description="""__**Key**__:\n🎓 - Major
📅 - Days to complete
⏫ - Finals percentage gain on each study
🕑 - Study Cooldown
📚 - Maximum finals percentage
💸 - Cost""")

        for university in universities:

            text = f"""🎓 {university.major}
            📅 {university.days} days
            ⏫ {university.low_increment}% - {university.high_increment}%
            🕑 {minisplittime(university.cooldown_minutes)}
            📚 {university.max_study}%
            💸 ${university.price} per day
            """

            embed.add_field(name=university.name, value=text, inline=True)

        await ctx.send(embed=embed)

    @commands.command()
    async def studyinfo(self, ctx, member: discord.Member=None):

        if not member:
            member = ctx.author

        current = read_value(member.id, 'university')

        if not current:
            if member == ctx.author:
                await ctx.send("You are not enrolling at a university.")
            else:
                await ctx.send(f"**{member.name}** is not enrolling at a university.")
            return

        current = find_university(current)
        
        progress = read_value(member.id, 'study_prog')
        started = read_value(member.id, 'study_start')


        time_left = (( started + current.days * 86400 ) - int(time.time()) ) // 60

        embed = discord.Embed(color=0x48157a, description=f"""Enrolled at: **{current.name}**
Majoring in: {current.major}
Chance to pass final: {progress}%
Time left until final: {days_hours_minutes(time_left)}
Time left until next payment: {days_hours_minutes(find_next_day(current, started) // 60)}""")
        embed.set_author(name=member.name, icon_url=member.avatar_url_as(static_format='jpg'))
        
        await ctx.send(embed=embed)

    @commands.command()
    @commands.max_concurrency(1, per=commands.BucketType.member)
    async def enroll(self, ctx, *, name=None):

        #TODO cannot enroll if working at a job

        if not name:
            await ctx.send("Incorrect command usage:\n`.enroll universityname`")
            return

        university = find_university(name.capitalize())

        if not university:
            await ctx.send(f"There is no university called **{name}**.")
            return

        current = read_value(ctx.author.id, 'university')
        if current:
            await ctx.send(f"You are already enrolling at **{current}**.")
            return
        
        university = find_university(name.capitalize())


        if university.price > read_value(ctx.author.id, 'total'):
            await ctx.send("You do not have enough money to pay for the first day.")

        else:
            money = read_value(ctx.author.id, 'money')
            
            money -= university.price
            if money < 0:

                bank = read_value(ctx.author.id, 'bank')
                bank += money # adding negative amount
                money = 0
                write_value(ctx.author.id, 'bank')

            write_value(ctx.author.id, 'money', money)
            write_value(ctx.author.id, 'university', name.capitalize())
            write_value(ctx.author.id, 'study_prog', 0)
            write_value(ctx.author.id, 'study_start', int(time.time()))

            await ctx.send(f"""You payed ${university.price} and successfully enrolled in **{name.capitalize()}**.
If you do not have enough money to pay the cost every 24 hours, your enrollment will automatically end and no refund will be given.
Good luck on the finals!""")
            

            asyncio.create_task(self.school_fee( find_next_day(university, int(time.time())), ctx.author.id, university.price), name=f"school {ctx.author.id}")

            update_total(ctx.author.id)
            await leaderboard(self.client)
            await rolecheck(self.client, ctx.author.id)

    @commands.command()
    @commands.max_concurrency(1, per=commands.BucketType.member)
    async def unenroll(self, ctx):
        
        current = read_value(ctx.author.id, 'university')
        if not current:
            await ctx.send("You are not enrolling at a university.")
            return

        await ctx.send(f"Are you sure you want to unenroll from **{current}**? You will not be refunded any payments you made. Respond with `yes` or `y` to proceed.")

        try:
            response = await self.client.wait_for('message', check=lambda m: m.author == ctx.author and m.channel == ctx.channel, timeout=20)
        except asyncio.TimeoutError:
            await ctx.send("Unenrollment timed out.")
            return
        
        response = response.content.lower()

        if response == 'yes' or response == 'y':
            for task in asyncio.all_tasks():
                if task.get_name() == f'school {ctx.author.id}':
                    task.cancel()
                    break
            
            conn = sqlite3.connect('./storage/databases/hierarchy.db')
            c = conn.cursor()
            c.execute('UPDATE members SET university = null, study_prog = 0, study_start = 0 WHERE id = ?', (ctx.author.id,))
            conn.commit()
            conn.close()

            await ctx.send(f"**{ctx.author.name}** unenrolled from **{current.capitalize()}**.")
            
        
    


def setup(client):
    client.add_cog(jobs(client))