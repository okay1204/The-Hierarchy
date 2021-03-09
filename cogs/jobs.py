# pylint: disable=import-error

import discord
from discord.ext import commands
import random
import time
import os
import asyncio
import json
from cogs.extra import minigames

# To import from different path
import sys
sys.path.insert(1 , os.getcwd())

from utils import bot_check, splittime, minisplittime, timestring, log_command


def get_range_value(start_range, end_range, x):

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
    
    return random.randint(output_start_range, output_end_range)



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
            University('Apicius', 'Culinary', 4, 9, 12, 120, 90, 110),
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
        if int(time.time()) < day:
            next_time = day
            break
    
    next_time -= int(time.time())
    return next_time



class Job:

    def __init__(self, name, emoji, salary, cooldown, requirements):

        self.name = name
        self.emoji = emoji
        self.salary = salary
        self.cooldown = cooldown
        self.requirements = requirements


work_jobs = [

    Job('Garbage Collector', '🗑️', [
        (40, 45),
        (45, 55),
        (60, 70),
        (70, 80)
    ], 60, []),

    Job('Streamer', '⌨️', [
        (5, 15),
        (15, 25),
        (25, 32),
        (32, 40)
    ], 15, []), # Change tutorial if more non-major requirement jobs are added

    Job('Chef', '🔪', [
        (30, 40),
        (40, 55),
        (55, 65),
        (65, 70)
    ], 30, ['Culinary']),

    Job('Scientist', '🧪', [
        (30, 45),
        (45, 60),
        (60, 80),
        (80, 90)
    ], 45, ['Science']),

    Job('Doctor', '💉', [
        (50, 65),
        (65, 82),
        (82, 90),
        (110, 120)
    ], 120, ['Medical'])
]

def find_job(name: str):

    for work_job in work_jobs:
        if work_job.name == name:
            return work_job
    
    return None


 
class Jobs(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.studying = []
        self.working = []
        self.finals = []


        asyncio.create_task(self.start_school_tasks())

    

    async def start_school_tasks(self):

        async with self.client.pool.acquire() as db:
            students = await db.fetch('SELECT id, university, study_start FROM members WHERE university IS NOT NULL;')

        
        for student in students:
            university = find_university(student[1])
            next_time = find_next_day(university, student[2])

            asyncio.create_task(self.school_fee(next_time, student[0], university), name=f"school {student[0]}")

    
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
            elif ctx.command.name == 'work':
                await ctx.send("Someone is already working in this channel.")
            elif ctx.command.name == 'practice':
                await ctx.send("Someone is already practicing in this channel.")


    async def cog_check(self, ctx):
        if ctx.channel.category.id != self.client.rightCategory:
            return False
        else:
            return True


    async def school_fee(self, duration, userid, university):

        try:

            if duration == 0:
                can_pay = False
            else:
                can_pay = True

            school_announcements = self.client.get_channel(744988365082067034)

            async with self.client.pool.acquire() as db:

                if can_pay:

                    await asyncio.sleep(duration)

                    broke = False

                    money = await db.get_member_val(userid, 'money')
                    original_money = money
                    money -= university.price

                    if money < 0:
                        bank = await db.get_member_val(userid, 'bank')
                        original_bank = bank
                        bank += money # adding negative amount
                        money = 0 

                        if bank < 0:
                            broke = True
                            money = original_money
                            bank = original_bank
                            
                            # set university values
                            await db.execute('UPDATE members SET university = NULL, study_prog = 0, study_start = 0 WHERE id = $1;', userid)
                        
                        await db.set_member_val(userid, 'bank', bank)
                    
                    await db.set_member_val(userid, 'money', money)


                    await db.rolecheck(userid)

                    if not broke:
                        await school_announcements.send(f"${university.price} taken from <@{userid}>'s account.")

                        with open('./storage/jsons/mode.json') as f:
                            mode = json.load(f)

                        if mode == "event":

                            if await db.get_member_val(userid, 'in_event'):

                                event_total = await db.fetchval('SELECT total FROM events WHERE id = $1;', userid)

                                event_total -= university.price
                                await db.execute('UPDATE events SET total = $1 WHERE id = $2;', event_total, userid)

                    else:
                        await school_announcements.send(f"<@{userid}> did not have enough money to pay, enrollment automatically cancelled.")
                        return
                
                if duration == 0:
                    
                    if not await db.get_member_val(userid, 'final_announced'):
                        await school_announcements.send(f"<@{userid}> can take their finals. Use `.final` to take it!")
                        await db.set_member_val(userid, 'final_announced', True)
                
                else:
                    study_start = await db.get_member_val(userid, 'study_start')

                    asyncio.create_task(self.school_fee(find_next_day(university, study_start), userid, university), name=f"school {userid}")
        except Exception as e:
            print(e)

    @commands.command()
    async def universities(self, ctx):
        
        embed = discord.Embed(color=0x48157a, title="Universities", description="""__**Key**__:\n🎓 - Major
📅 - Days to complete
⏫ - Finals percentage gain on each study
🕑 - Study cooldown
📚 - Maximum finals percentage
💸 - Cost

_ _""")

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
    async def studyinfo(self, ctx, *, member: discord.Member=None):

        if not member:
            member = ctx.author

        async with self.client.pool.acquire() as db:

            current = await db.get_member_val(member.id, 'university')

            if not current:
                if member == ctx.author:
                    await ctx.send("You are not enrolling at a university.")
                else:
                    await ctx.send(f"**{member.name}** is not enrolling at a university.")
                return

            current = find_university(current)
            
            progress = await db.get_member_val(member.id, 'study_prog')
            started = await db.get_member_val(member.id, 'study_start')


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
                
                hours = next_payment // 60
                minutes = next_payment % 60

                next_payment = f"{hours}h {minutes}m"

            studyc = await db.get_member_val(member.id, 'studyc')

            if studyc > time.time():
                studyc = splittime(studyc)
            else:
                studyc = "Study Available"

            embed = discord.Embed(color=0x48157a, description=f"""Enrolled at: **{current.name}**
    Majoring in: {current.major}
    Chance to pass final: {progress}%
    Time left until final: {time_left}
    Time left until next payment: {next_payment}
    Study cooldown: {studyc}""")
            embed.set_author(name=member.name, icon_url=member.avatar_url_as(static_format='jpg'))
            
            await ctx.send(embed=embed)


    @commands.command()
    @commands.max_concurrency(1, per=commands.BucketType.member)
    async def enroll(self, ctx, *, name=None):


        if not name:
            await ctx.send("Incorrect command usage:\n`.enroll university`")
            return

        async with self.client.pool.acquire() as db:

            if not await db.level_check(ctx, ctx.author.id, 7, "study at a university"):
                return

            university = find_university(name.title())

            if not university:
                await ctx.send(f"There is no university called \"{name}\".")
                return

            current = await db.get_member_val(ctx.author.id, 'university')
            if current:
                await ctx.send(f"You are already enrolling at **{current}**.")
                return

            majors = await db.get_member_val(ctx.author.id, 'majors').split('|')
            
            if university.major in majors:
                await ctx.send(f"You already have a **{university.major}** major.")
                return

            if not await db.jail_heist_check(ctx, ctx.author):
                return

            if university.price > await db.get_member_val(ctx.author.id, 'money + bank'):
                await ctx.send("You do not have enough money to pay for the first day.")

            else:
                money = await db.get_member_val(ctx.author.id, 'money')
                
                money -= university.price
                if money < 0:

                    bank = await db.get_member_val(ctx.author.id, 'bank')
                    bank += money # adding negative amount
                    money = 0
                    await db.set_member_val(ctx.author.id, 'bank', bank)

                await db.set_member_val(ctx.author.id, 'money', money)
                await db.set_member_val(ctx.author.id, 'university', name.title())
                await db.set_member_val(ctx.author.id, 'study_prog', 0)
                await db.set_member_val(ctx.author.id, 'study_start', int(time.time()))
                await db.set_member_val(ctx.author.id, 'final_announced', False)

                with open('./storage/jsons/mode.json') as f:
                    mode = json.load(f)


                if mode == "event" and await db.get_member_val(ctx.author.id, 'in_event'):
                    
                    event_total = await db.fetchval("SELECT total FROM events WHERE id = $1;", ctx.author.id)

                    if event_total:
                        event_total += university.price
                        await db.execute("UPDATE events SET total = $1 WHERE id = $2;", event_total, ctx.author.id)
                    else:
                        await db.execute("INSERT INTO events (id, total) VALUES ($1, $2)", ctx.author.id, university.price)


                await ctx.send(f"""You payed ${university.price} and successfully enrolled in **{name.capitalize()}**.
    If you do not have enough money to pay the cost every 24 hours, your enrollment will automatically end and no refund will be given.
    Good luck on the finals!""")
                
                asyncio.create_task(self.school_fee( find_next_day(university, int(time.time())), ctx.author.id, university.price), name=f"school {ctx.author.id}")

                await db.leaderboard()
                await db.rolecheck(ctx.author.id)

    @commands.command()
    @commands.max_concurrency(1, per=commands.BucketType.member)
    async def unenroll(self, ctx):

        async with self.client.pool.acquire() as db:
        
            current = await db.get_member_val(ctx.author.id, 'university')

            if not current:
                return await ctx.send("You are not enrolling at a university.")
                

            if not await db.jail_heist_check(ctx, ctx.author):
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

                await db.execute('UPDATE members SET university = null, study_prog = 0, study_start = 0, final_announced = FALSE WHERE id = $1;', ctx.author.id)

                await ctx.send(f"**{ctx.author.name}** unenrolled from **{current.capitalize()}**.")

            else:
                await ctx.send("Unenrollment timed out.")

    @commands.command()
    @commands.max_concurrency(1, per=commands.BucketType.channel)
    async def final(self, ctx):


        async with self.client.pool.acquire() as db:

            if ctx.author.id in self.finals:
                return await ctx.send("You are already taking your finals.")
            
            current = await db.get_member_val(ctx.author.id, 'university')
            if not current:
                await ctx.send("You are not enrolling at a university.")
                return

            university = find_university(current)
            
            if find_next_day(university, await db.get_member_val(ctx.author.id, 'study_start')) != 0:
                await ctx.send("You cannot take your finals yet.")
                return

            if not await db.jail_heist_check(ctx, ctx.author):
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

            self.finals.append(ctx.author.id)
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
            
            
            prog = await db.get_member_val(ctx.author.id, 'study_prog')
            prog = 100

            if prog >= random.randint(1, 100):
                await ctx.send(f"✅ You passed the finals from **{university.name}** and got your major in **{university.major}**! ✅")

                majors = await db.get_member_val(ctx.author.id, 'majors')
                majors.append(university.major)
                await db.set_member_val(ctx.author.id, 'majors', majors)
            else:
                await ctx.send(f"❌ You failed the final.. well looks like you have to try again. ❌")

            self.finals.remove(ctx.author.id)

            await db.execute('UPDATE members SET university = NULL, study_prog = 0, study_start = 0, final_announced = FALSE WHERE id = $1;', ctx.author.id)

    @commands.command()
    @commands.max_concurrency(1, per=commands.BucketType.member)
    async def majors(self, ctx, *, member:discord.Member=None):

        if not member:
            member = ctx.author

        async with self.client.pool.acquire() as db:

            majors = await db.get_member_val(member.id, 'majors')        

        if not majors:
            embed = discord.Embed(color=0x48157a, title="Majors", description="None")
        else:
            embed = discord.Embed(color=0x48157a, title="Majors")

            for major in majors:
                embed.add_field(name=discord.utils.escape_markdown("_____"), value=major, inline=True) # noqa pylint: disable=anomalous-backslash-in-string
        
        embed.set_author(name=member.name, icon_url=member.avatar_url_as(static_format='jpg'))

        await ctx.send(embed=embed)

    
    @commands.command()
    @commands.max_concurrency(1, per=commands.BucketType.channel)
    async def study(self, ctx):

        if ctx.author.id in self.studying:
            return await ctx.send("You are already studying.")

        async with self.client.pool.acquire() as db:

            university = await db.get_member_val(ctx.author.id, 'university')

            if not university:
                await ctx.send('You are not enrolling at a university.')
                return

            if not await db.jail_heist_check(ctx, ctx.author):
                return

            studyc = await db.get_member_val(ctx.author.id, 'studyc')
            if studyc > time.time():
                await ctx.send(f'You must wait {splittime(studyc)} before you can study again.')
                return

            university = find_university(university)

            started = await db.get_member_val(ctx.author.id, 'study_start')
            time_left = ( started + university.days * 86400 ) - int(time.time())

            if time_left <= 0:
                await ctx.send("You may no longer study, you must take your finals now.")
                return

            correct = 0

            self.studying.append(ctx.author.id)

            with open('./storage/jsons/mode.json') as f:
                mode = json.load(f)

            if ctx.author.premium_since and mode == 'event' and await db.get_member_val(ctx.author.id, 'in_event'):

                await ctx.send("*Premium perks are disabled during events*")
                premium = False
                await asyncio.sleep(2)

            elif ctx.author.premium_since:
                premium = True
            else:
                premium = False

            studygames = minigames.Studygames(self.client)
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

            if correct > 3:
                correct = 3
                extra = True
        
            

            points = get_range_value(university.low_increment, university.high_increment, correct)

            if extra:
                points += random.randint(1, 3)


            

            study_prog = await db.get_member_val(ctx.author.id, 'study_prog')
            study_prog += points

            text = f"**{ctx.author.name}** studied at **{university.name}** and got a {points}% higher chance of passing the finals.\n"

            if study_prog > university.max_study:
                study_prog = university.max_study
                text += f"They have hit their maximum study limit of {university.max_study}%."
            else:
                text += f"They now have a total of {study_prog}% chance to pass the finals."

            await db.set_member_val(ctx.author.id, 'study_prog', study_prog)

            await db.set_member_val(ctx.author.id, 'studyc', int(time.time()) + university.cooldown_minutes * 60)

            self.studying.remove(ctx.author.id)
            await ctx.send(text)


    @commands.command()
    async def jobs(self, ctx):
                                    # embed title linked with tutorial
        embed = discord.Embed(color=0x3d9c17, title="Jobs", description="""__**Key**__:\n💸 - Salary
🕑 - Work Cooldown
🎓 - Major Requirements

_ _""")

        for work_job in work_jobs:
            if not (requirements := work_job.requirements):
                requirements = ["None"]

            embed.add_field(name=f"{work_job.emoji} {work_job.name}", value=f"""💸 - ${work_job.salary[0][0]} - ${work_job.salary[-1][-1]}
🕑 - {minisplittime(work_job.cooldown)}
🎓 - {", ".join(requirements)}""", inline=True)

        await ctx.send(embed=embed)

    
    @commands.command()
    async def apply(self, ctx, *, name=None):
        
        if not name:
            await ctx.send("Incorrect command usage:\n`.apply job`")
            return

        if not (job := find_job(name.title())):
            await ctx.send(f"There is no job called **{name}**. Use `.jobs` to get a list of jobs.")
            return

        async with self.client.pool.acquire() as db:

            if not await db.jail_heist_check(ctx, ctx.author): return

            if (applyc := await db.get_member_val(ctx.author.id, 'applyc')) > time.time():
                await ctx.send(f"You must wait {splittime(applyc)} before you can apply for another job.")
                return
            
            if await db.get_member_val(ctx.author.id, 'job'):
                await ctx.send("You already have a job.")
                return

            majors = await db.get_member_val(ctx.author.id, 'majors')

            for major in job.requirements:
                if major not in majors:
                    await ctx.send("You do not have all the required majors to apply for this job.")
                    return

            await db.set_member_val(ctx.author.id, 'job', job.name)

                                # message below linked to tutorial
            await ctx.send(f"You have successfully recieved the job **{job.name}**.")

    
    @commands.command(aliases=["retire", "unapply"])
    async def quit(self, ctx):

        async with self.client.pool.acquire() as db:

            if not (job := await db.get_member_val(ctx.author.id, 'job')):
                return await ctx.send("You do not have a job.")

            if not await db.jail_heist_check(ctx, ctx.author): return

            await ctx.send("Are you sure you want to quit your job? You will not be able to apply to another job for 12 hours. Respond with `y` or `yes` to proceed.")

            try:
                response = await self.client.wait_for('message', check=lambda m: m.channel == ctx.channel and m.author.id == ctx.author.id, timeout=20)
            except asyncio.TimeoutError:
                return await ctx.send("Quit timed out.")

            response = response.content.lower()
            
            if response == 'yes' or response == 'y':                                                          # 12 hours
                await db.execute('UPDATE members SET job = NULL, applyc = $1 WHERE id = $2', int(time.time()) + 43200, ctx.author.id)

                if job.lower().startswith(('a', 'e', 'i', 'o', 'u')):
                    article = 'an'
                else:
                    article = 'a'

                await ctx.send(f"You have quit your job as {article} **{job}**.")

            else:
                await ctx.send("Quit cancelled.")


    @commands.command()
    async def job(self, ctx, *, member:discord.Member=None):

        if not member:
            member = ctx.author

        async with self.client.pool.acquire() as db:

            if not (job := await db.get_member_val(member.id, 'job')):
                return await ctx.send(f"**{member.name}** does not have a job.")

        if job.lower().startswith(('a', 'e', 'i', 'o', 'u')):
            article = 'an'
        else:
            article = 'a'

        await ctx.send(f"**{member.name}** is working as {article} **{job}**.")


        
    @commands.command()
    @commands.max_concurrency(1, per=commands.BucketType.channel)
    async def work(self, ctx):

        if ctx.author.id in self.working:
            return await ctx.send("You are already working.")

        async with self.client.pool.acquire() as db:

            if not (job := await db.get_member_val(ctx.author.id, 'job')):
                await ctx.send(f"You do not have a job.\nUse `.apply job` to apply for a job.")
                return
            
            if not await db.jail_heist_check(ctx, ctx.author): return

            elif (workc := await db.get_member_val(ctx.author.id, 'workc')) > time.time():
                await ctx.send(f'You must wait {splittime(workc)} before you can work again.')
                return


            self.working.append(ctx.author.id)

            with open('./storage/jsons/mode.json') as f:
                mode = json.load(f)

            in_event = await db.get_member_val(ctx.author.id, 'in_event')

        if ctx.author.premium_since and mode == 'event' and in_event:

            await ctx.send("*Premium perks are disabled during events*")
            premium = False
            await asyncio.sleep(2)

        elif ctx.author.premium_since:
            premium = True
        else:
            premium = False

        correct = 0

        for x in range(5):

            if x == 3:
                if premium:
                    await ctx.send(f"**{ctx.author.name}** has __premium__ and gets two extra tasks!")
                    await asyncio.sleep(2)
                else:
                    break

            await ctx.send("Get ready...")
            await asyncio.sleep(3)

            if await minigames.work_game(self.client, job, ctx, correct, x+1):
                correct += 1
            
            await asyncio.sleep(2)

        extra = 0

        if correct > 3:
            extra = correct - 3
            correct = 3
        
        job = find_job(job)

        earnings = job.salary[correct]
        earnings = random.randint(earnings[0], earnings[1])

        for _ in range(extra):
            earnings += random.randint(20, 40)

        async with self.client.pool.acquire() as db:
        
            money = await db.get_member_val(ctx.author.id, 'money')
            money += earnings
            await db.set_member_val(ctx.author.id, 'money', money)

            await db.set_member_val(ctx.author.id, 'workc', int(time.time()) + (job.cooldown * 60))

        if job.name.lower().startswith(('a', 'e', 'i', 'o', 'u')):
            article = 'an'
        else:
            article = 'a'

        self.working.remove(ctx.author.id)
                            # message linked with tutorial
        await ctx.send(f"💰 **{ctx.author.name}** worked as {article} **{job.name}** and successfully completed {correct+extra} tasks, earning ${earnings}. 💰")


    
    @commands.command()
    @commands.max_concurrency(1, per=commands.BucketType.channel)
    async def practice(self, ctx):

        if ctx.author.id in self.working:
            return await ctx.send("You are already working.")

        async with self.client.pool.acquire() as db:

            if not (job := await db.get_member_val(ctx.author.id, 'job')):
                await ctx.send(f"You do not have a job.")
                return

        self.working.append(ctx.author.id)
        correct = 0

        for x in range(3):

            await ctx.send("Get ready...")
            await asyncio.sleep(3)

            if await minigames.work_game(self.client, job, ctx, correct, x+1):
                correct += 1
            
            await asyncio.sleep(2)


        if job.lower().startswith(('a', 'e', 'i', 'o', 'u')):
            article = 'an'
        else:
            article = 'a'

        self.working.remove(ctx.author.id) 
        
        # message linked with tutorial
        await ctx.send(f"**{ctx.author.name}** practiced as {article} **{job}** and successfully completed {correct} tasks.")
        



    

def setup(client):
    client.add_cog(Jobs(client))