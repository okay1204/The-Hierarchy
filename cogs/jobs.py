# pylint: disable=import-error

import discord
from discord.ext import commands
import random
import time
import os
import asyncio
import sqlite3
import json
from cogs.extra.minigames import Studygames

# To import from different path
import sys
sys.path.insert(1 , os.getcwd())

from utils import (read_value, write_value, update_total, leaderboard,
rolecheck, level_check, minisplittime, jail_heist_check, splittime)


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
            University('Emory', 'Medical', 12, 8, 12, 360, 95, 80),
            University('East Bay', 'Science', 5, 10, 15, 60, 65, 70),
            University('Harvard', 'Science', 11, 3, 7, 15, 95, 85),
            University('Apicius', 'Culinary', 4, 9, 9, 120, 90, 110),
            University('Duke', 'Medical', 7, 4, 8, 120, 100, 100)
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

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):

        error = getattr(error, 'original', error)

        if isinstance(error, commands.MaxConcurrencyReached):
            if ctx.command.name == 'final':
                await ctx.send("Someone is already taking their finals in this channel.")
            elif ctx.command.name == 'study':
                await ctx.send("Someone is already studying in this channel.")


    async def cog_check(self, ctx):
        if ctx.channel.category.id != self.client.rightCategory:
            return False
        else:
            return True


    async def school_fee(self, duration, userid, payment):

        if duration != 0:
            can_pay = True
        else:
            if read_value(userid, 'final_announced') == "True":
                can_pay = False
            else:
                can_pay = True

        if not can_pay:
            return

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

            school_announcements = self.client.get_channel(744988365082067034)
            
            await school_announcements.send(f"<@{userid}> can take their finals. Use `.final` to take it!")
            write_value(userid, 'final_announced', 'True')
        
        else:
            asyncio.create_task(self.school_fee(int(time.time()) + 86400, userid, payment), name=f"school {userid}")


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


        time_left = ( started + current.days * 86400 ) - int(time.time())

        if time_left <= 0:
            time_left = "Ready to take finals"
        else:
            time_left //= 60
            time_left = days_hours_minutes(time_left)
            

        next_payment = find_next_day(current, started)
        if next_payment <= 0:
            next_payment = "No more payments"
        else:
            next_payment //= 60
            next_payment = days_hours_minutes(next_payment)


        embed = discord.Embed(color=0x48157a, description=f"""Enrolled at: **{current.name}**
Majoring in: {current.major}
Chance to pass final: {progress}%
Time left until final: {time_left}
Time left until next payment: {next_payment}""")
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

        majors = read_value(ctx.author.id, 'majors').split('|')
        
        if university.major in majors:
            await ctx.send(f"You already have a **{university.major}** major.")
            return

        if not await jail_heist_check(ctx, ctx.author):
            return

        if university.price > read_value(ctx.author.id, 'total'):
            await ctx.send("You do not have enough money to pay for the first day.")

        else:
            money = read_value(ctx.author.id, 'money')
            
            money -= university.price
            if money < 0:

                bank = read_value(ctx.author.id, 'bank')
                bank += money # adding negative amount
                money = 0
                write_value(ctx.author.id, 'bank', bank)

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

        if not await jail_heist_check(ctx, ctx.author):
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
            c.execute('UPDATE members SET university = null, study_prog = 0, study_start = 0, final_annouced = "False" WHERE id = ?', (ctx.author.id,))
            conn.commit()
            conn.close()

            await ctx.send(f"**{ctx.author.name}** unenrolled from **{current.capitalize()}**.")

    @commands.command()
    @commands.max_concurrency(1, per=commands.BucketType.channel)
    async def final(self, ctx):
        
        current = read_value(ctx.author.id, 'university')
        if not current:
            await ctx.send("You are not enrolling at a university.")
            return

        university = find_university(current)
        
        if find_next_day(university, read_value(ctx.author.id, 'study_start')) != 0:
            await ctx.send("You cannot take your finals yet.")
            return

        if not await jail_heist_check(ctx, ctx.author):
            return

        # confirmation
        await ctx.send("Are you sure you want to take your finals? Respond with `yes` or `y` to proceed.")
        try:
            response = await self.client.wait_for('message', check=lambda m: m.author == ctx.author and m.channel == ctx.channel, timeout=20)
        except asyncio.TimeoutError:
            await ctx.send("Finals timed out.")
            return
        
        response = response.content.lower()
        if response != 'y' and response != 'yes':
            await ctx.send("Finals cancelled.")
            return

        await ctx.send("You have began taking your finals...")

        test = 0
        while test < 100:
            
            await asyncio.sleep(random.randint(1,3))
            test += random.randint(8, 14)
            if test > 100:
                test = 100

            await ctx.send(f"Test progress: {test}%")

            if test == 100:
                await asyncio.sleep(2)
                await ctx.send("Test done!")
    
        await asyncio.sleep(2)
        await ctx.send("Waiting for test results...")

        async with ctx.channel.typing():
            await asyncio.sleep(10)
        
        
        prog = read_value(ctx.author.id, 'study_prog')
        prog = 100

        if prog >= random.randint(1, 100):
            await ctx.send(f"✅ You passed the finals from **{university.name}** and got your major in **{university.major}**! ✅")

            majors = read_value(ctx.author.id, 'majors').split("|")
            majors.append(university.major)
            majors = "|".join(majors)
            write_value(ctx.author.id, 'majors', majors)
        else:
            await ctx.send(f"❌ You failed the final.. well looks like you have to try again. ❌")

        conn = sqlite3.connect('./storage/databases/hierarchy.db')
        c = conn.cursor()
        c.execute('UPDATE members SET university = null, study_prog = 0, study_start, final_announced = "False" WHERE id = ?', (ctx.author.id,))
        conn.commit()
        conn.close()

    @commands.command()
    @commands.max_concurrency(1, per=commands.BucketType.member)
    async def majors(self, ctx, member:discord.Member=None):

        if not member:
            member = ctx.author

        majors = read_value(member.id, 'majors').split('|')
        

        if not majors:
            embed = discord.Embed(color=0x48157a, title="Majors", description="None")
        else:
            embed = discord.Embed(color=0x48157a, title="Majors")

            for major in majors:
                embed.add_field(name="\_\_\_\_\_\_\_\_\_\_", value=major, inline=True) # noqa pylint: disable=anomalous-backslash-in-string
        embed.set_author(name=member.name, icon_url=member.avatar_url_as(static_format='jpg'))

        await ctx.send(embed=embed)

    
    @commands.command()
    @commands.max_concurrency(1, per=commands.BucketType.channel)
    async def study(self, ctx):

        university = read_value(ctx.author.id, 'university')

        if not university:
            await ctx.send('You are not enrolling at a university.')
            return

        if not await jail_heist_check(ctx, ctx.author):
            return

        studyc = read_value(ctx.author.id, 'studyc')
        if studyc > time.time():
            await ctx.send(f'You must wait {splittime(studyc)} before you can study again.')
            return

        correct = 0

        with open('./storage/jsons/mode.json') as f:
            mode = json.load(f)

        if ctx.author.premium_since and mode == 'event':

            await ctx.send("*Premium perks are disabled during events*")
            premium = False
            await asyncio.sleep(2)

        elif ctx.author.premium_since:
            premium = True
        else:
            premium = False

        studygames = Studygames(self.client)
        for x in range(4):

            if x == 3:
                if premium:
                    await ctx.send(f"**{ctx.author.name}** has __premium__ and gets one extra task!")
                    await asyncio.sleep(2)
                else:
                    break

            await ctx.send("Get ready...")
            await asyncio.sleep(3)

            if await studygames.random_game(ctx, correct, x + 1):
                correct += 1
            
            await asyncio.sleep(2)

        extra = False

        if x > 3:
            x = 3
            extra = True
        
        university = find_university(university)
        
        end_range = university.low_increment
        start_range = university.high_increment

        # SECTION getting point value 
        output_start_range = 0
        output_end_range = 0
        r = (end_range - start_range)//3 
        if x == 0:
            output_start_range = start_range
            output_end_range +=  output_start_range + r

        else:
            if x == 1:
                output_start_range += start_range + r 
                output_end_range += output_start_range + r
            elif x == 2:
                output_start_range += start_range + 2*r
                output_end_range += output_start_range + r - (end_range - start_range)//9
            elif x == 3:
                output_start_range += start_range + 3*r - (end_range - start_range)//9
                output_end_range = end_range
            
        points = random.randint(output_start_range, output_end_range)
        if extra:
            points += random.randint(1, 3)

        # !SECTION
        

        study_prog = read_value(ctx.author.id, 'study_prog')
        study_prog += points

        text = f"**{ctx.author.name}** studied and got a {points}% higher chance of passing the finals.\n"

        if study_prog > university.max_study:
            study_prog = university.max_study
            text += f"They have hit their maximum study limit of {university.max_study}%."
        else:
            text += f"They now have a total of {study_prog}% to pass the finals."

        write_value(ctx.author.id, 'study_prog', study_prog)

        write_value(ctx.author.id, 'studyc', int(time.time()) + university.cooldown_minutes * 60)

        await ctx.send(text)
        

        

            

# NOTE when deploying make sure to update premium as well
        
    


def setup(client):
    client.add_cog(jobs(client))