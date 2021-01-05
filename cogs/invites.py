# pylint: disable=import-error

import discord
from discord.ext import commands
import json
import time
import sqlite3
import os
import asyncio
import random

# To import from different path
import sys
sys.path.insert(1 , os.getcwd())

from utils import (read_value, write_value, leaderboard,
rolecheck, splittime, bot_check, in_use, jail_heist_check, around,
remove_item, remove_use, add_item, add_use, log_command)


# cog for tracking invites by players and making sure they complete the tutorial

class Invites(commands.Cog):

    def __init__(self, client):
        self.client = client

        asyncio.create_task(self.initialize_invites())


    async def initialize_invites(self):

        self.last_removed = None
        
        invites = await self.client.mainGuild.invites()

        self.invites = []

        for invite in invites:
            self.invites.append({'code': invite.code, 'max_age': invite.max_age, 'uses': invite.uses, 'max_uses': invite.max_uses, 'created_at': invite.created_at, 'inviter': invite.inviter})

        
        # making sure all existing members can't be invited again
        
        # getting list of all ids
        conn = sqlite3.connect('./storage/databases/hierarchy.db')
        c = conn.cursor()
        c.execute('SELECT id FROM members;')
        all_ids = c.fetchall()
        conn.close()

        # writing them to invites db
        conn = sqlite3.connect('./storage/databases/invites.db')
        c = conn.cursor()
        for userid in all_ids:
            try:
                c.execute('INSERT INTO inviters (member_id, inviter_id) VALUES (?, 0);', (userid[0],))
            except sqlite3.IntegrityError:
                pass
        conn.commit()
        conn.close()

    async def cog_check(self, ctx):
        if ctx.channel.category.id != self.client.rightCategory:
            return False
        else:
            return True

    @commands.Cog.listener()
    async def on_invite_create(self, invite):
        
        self.invites.append({'code': invite.code, 'max_age': invite.max_age, 'uses': invite.uses, 'max_uses': invite.max_uses, 'created_at': invite.created_at, 'inviter': invite.inviter})

    @commands.Cog.listener()
    async def on_invite_delete(self, invite):


        for stored_invite in self.invites:
            if invite.code == stored_invite['code']:
                self.invites.remove(stored_invite)

                self.last_removed = stored_invite
                break

    
    @commands.Cog.listener()
    async def on_member_join(self, member):
        
        # getting rid of all invites that expired
        self.invites = list(filter(lambda invite: invite['created_at'].timestamp() + invite['max_age'] > time.time() if invite['max_age'] else True, self.invites))

        current_invites = await self.client.mainGuild.invites()

        # just in case the member joined without an invite somehow
        inviter_id = None

        bot = False


        # in case the invite was deleted due to hitting max uses
        invite_removed = False
        if self.last_removed and self.last_removed['uses'] + 1 == self.last_removed['max_uses']:
            invite_removed = True
        
        # matching old invites with new ones
        paired = {}

        for invite in self.invites:
            for current_invite in current_invites:

                if invite['code'] == current_invite.code:
                    paired[current_invite] = invite

        for new, old in paired.items():

            if new.uses == old['uses'] + 1:

                if not new.inviter.bot:
                    bot = True

                inviter_id = new.inviter.id


        if not inviter_id and invite_removed:

            if not self.last_removed['inviter'].bot:
                bot = True

            inviter_id = self.last_removed['inviter'].id


        elif not inviter_id or bot:
            inviter_id = 0

        conn = sqlite3.connect('./storage/databases/invites.db')
        c = conn.cursor()

        try:
            c.execute('INSERT INTO inviters (member_id, inviter_id) VALUES (?, ?);', (member.id, inviter_id))
            
        # if the member already has an inviter
        except sqlite3.IntegrityError:
            c.execute('UPDATE inviters SET in_guild = 1 WHERE member_id = ?', (member.id,))
        
        finally:
            conn.commit()
            conn.close()


        await self.initialize_invites()

    @commands.Cog.listener()
    async def on_member_remove(self, member):

        conn = sqlite3.connect('./storage/databases/invites.db')
        c = conn.cursor()
        c.execute('UPDATE inviters SET in_guild = 0 WHERE member_id = ?', (member.id,))
        conn.commit()
        conn.close()


    @commands.command()
    async def resetinvites(self, ctx):

        if ctx.channel.id != self.client.adminChannel: return

        with open('./storage/text/englishwords.txt') as f:
            word = random.choice(f.read().splitlines())
        # for confirmation
        await ctx.send(f"Are you sure you want to reset all invites? Type `{word}` to proceed.")

        try:
            response = await self.client.wait_for('message', check=lambda m: m.channel == ctx.channel and m.author == ctx.author, timeout=20)
        except:
            return await ctx.send("Save timed out.")

        if response.content.lower() != word.lower(): return await ctx.send("Reset cancelled.")

        conn = sqlite3.connect('./storage/databases/invites.db')
        c = conn.cursor()
        c.execute("UPDATE inviters SET inviter_id = 0, tutorial = 0, in_guild = -1;")
        conn.commit()
        conn.close()

        await ctx.send("Reset all invites.")
        await log_command(self.client, ctx)


    @commands.command()
    async def invitecount(self, ctx, member: discord.Member = None):

        if not member:
            member = ctx.author

        if not await bot_check(self.client, ctx, member):
            return

        embed = discord.Embed(color=0xfffeff,
        description="Pending invites means those who haven't completed the tutorial.\nCompleted invites means those who have, in other words invites that count.")
        embed.set_author(name=f"{member.name}'s invite count", icon_url=member.avatar_url_as(static_format='jpg'))


        conn = sqlite3.connect('./storage/databases/invites.db')
        c = conn.cursor()
        c.execute('SELECT COUNT(*) FROM inviters WHERE inviter_id = ? AND tutorial = 0 AND in_guild = 1', (member.id,))
        pending_count = c.fetchone()[0]
        c.execute('SELECT COUNT(*) FROM inviters WHERE inviter_id = ? AND tutorial = 1 AND in_guild = 1', (member.id,))
        completed_count = c.fetchone()[0]
        conn.close()

        embed.add_field(name="Total", value=str(pending_count+completed_count))
        embed.add_field(name="Pending", value=str(pending_count))
        embed.add_field(name="Completed", value=str(completed_count))

        await ctx.send(embed=embed)
        

    @commands.command(name="invites", aliases=['invitesm'])
    async def invites_list(self, ctx, group = "", member: discord.Member = None):

        if not member:
            member = ctx.author

        if not await bot_check(self.client, ctx, member):
            return

        group = group.lower()

        # all is alias for total
        if group == 'all':
            group = 'total'

        if group not in ('total', 'pending', 'completed'):
            return await ctx.send(f'Incorrect command usage:\n`.invites all/pending/completed (member)`')


        embed = discord.Embed(color=0xfffeff)
        embed.set_author(name=f"{member.name}'s {group} invites", icon_url=member.avatar_url_as(static_format='jpg'))

        conn = sqlite3.connect('./storage/databases/invites.db')
        c = conn.cursor()

        if group == 'total':
            c.execute('SELECT member_id FROM inviters WHERE inviter_id = ? AND in_guild = 1', (member.id,))

        elif group == 'pending':
            c.execute('SELECT member_id FROM inviters WHERE inviter_id = ? AND tutorial = 0 AND in_guild = 1', (member.id,))

        elif group == 'total':
            c.execute('SELECT member_id FROM inviters WHERE inviter_id = ? AND tutorial = 1 AND in_guild = 1', (member.id,))

        userids = c.fetchall()
        conn.close()

        userids = [userid[0] for userid in userids]

        mobile = False
        if ctx.message.content.startswith('.invitesm'):
            mobile = True
        else:
            mobile = False

        for userid in userids:

            member_name = self.client.mainGuild.get_member(userid)

            if mobile:
                member_name = member_name.name
            else:
                member_name = member_name.mention

            embed.add_field(name=discord.utils.escape_markdown('_____'), value=member_name)

        
        if not len(embed.fields):
            embed = discord.Embed(color=0xfffeff, description="None")
            embed.set_author(name=f"{member.name}'s {group} invites", icon_url=member.avatar_url_as(static_format='jpg'))

        await ctx.send(embed=embed)


        
    @commands.command(aliases=['invitesleadm'])
    async def inviteslead(self, ctx):
        guild = self.client.mainGuild


        embed = discord.Embed(color = 0xfffeff)
        embed.set_author(name='✉️ Invites Leaderboard ✉️')

        invites = []


        conn = sqlite3.connect('./storage/databases/hierarchy.db')
        c = conn.cursor()
        c.execute("""
        SELECT id
        FROM members;
        """)
        userids = c.fetchall()
        conn.close()

        userids = [userid[0] for userid in userids]

        conn = sqlite3.connect('./storage/databases/invites.db')
        c = conn.cursor()

        for userid in userids:
            c.execute("""
            SELECT COUNT(*)
            FROM inviters
            WHERE inviter_id = ? AND in_guild = 1 AND tutorial = 1;
            """, (userid,))

            count = c.fetchone()[0]

            invites.append((userid, count))

        conn.close()

        invites = list(filter(lambda x: guild.get_member(x[0]), invites))
        invites.sort(key=lambda member: member[1], reverse=True)

        if ctx.message.content.startswith('.invitesleadm'):
            mobile = True
        else:
            mobile = False


        for x in range(5):

            if mobile:
                member_name = guild.get_member(invites[x][0]).name
            else:
                member_name = f"<@{invites[x][0]}>"

            if x == 0:
                embed.add_field(name='__________',value=f'1. {member_name} 🥇 - {invites[x][1]}',inline=False)
            elif x == 1:
                embed.add_field(name='__________',value=f'2. {member_name} 🥈 - {invites[x][1]}',inline=False)
            elif x == 2:
                embed.add_field(name='__________',value=f'3. {member_name} 🥉 - {invites[x][1]}',inline=False)
            else:
                embed.add_field(name='__________',value=f'{x+1}. {member_name} - {invites[x][1]}',inline=False)


        await ctx.send(embed=embed)


    @commands.command(aliases=['invitesaroundm'])
    async def invitesaround(self, ctx, find=None, *, member:discord.Member=None):


        if not member: 
            member = ctx.author
        
        if not await bot_check(self.client, ctx, member):
            return

        if not find:
            find = 3
        try:
            find = int(find)

        except:
            await ctx.send('Incorrect command usage:\n`.eventaround (range) (member)`')
            return

        if find < 1 or find > 12:
            await ctx.send('Enter a number from 1-12 for `range`.')
            return

        guild = self.client.mainGuild


        invites = []


        conn = sqlite3.connect('./storage/databases/hierarchy.db')
        c = conn.cursor()
        c.execute("""
        SELECT id
        FROM members;
        """)
        userids = c.fetchall()
        conn.close()

        userids = [userid[0] for userid in userids]

        conn = sqlite3.connect('./storage/databases/invites.db')
        c = conn.cursor()

        for userid in userids:
            c.execute("""
            SELECT COUNT(*)
            FROM inviters
            WHERE inviter_id = ? AND in_guild = 1 AND tutorial = 1;
            """, (userid,))

            count = c.fetchone()[0]

            invites.append((userid, count))

        conn.close()

        invites = list(filter(lambda x: guild.get_member(x[0]), invites))
        invites.sort(key=lambda member: member[1], reverse=True)


        ids = list(map(lambda x: x[0], invites))
        
        try:
            index = ids.index(member.id)
        except ValueError:
            invites.append((member.id, 0))
            ids.append(member.id)
            index = ids.index(member.id)


        lower_index = index-find

        if lower_index < 0:
            lower_index = 0

        higher_index = index+find+1
        length = len(invites)

        if higher_index > length:
            higher_index = length

        result = invites[lower_index:higher_index]

        avatar = member.avatar_url_as(static_format='jpg')
        embed = discord.Embed(color=0xfffeff)
        embed.set_author(name=f"✉️ Around {member.name} ✉️",icon_url=avatar)

        place = ids.index(result[0][0])+1


        if ctx.message.content.startswith('.invitesaroundm'):
            mobile = True
        else:
            mobile = False


        for person in result:

            if mobile:
                member_name = guild.get_member(person[0]).name
            else:
                member_name = f"<@{person[0]}>"

            medal = ''
            mk = ''
            if place == 1:
                medal = '🥇 '
            elif place == 2:
                medal = '🥈 '
            elif place == 3:
                medal = '🥉 '
            if member.id == person[0]:
                mk = '**'


            embed.add_field(name='__________', value=f'{mk}{place}. {member_name} {medal}- {person[1]}{mk}', inline=False)
            place += 1


        if find > 5:
            await ctx.send('Embed too large, check your DMs.')
            await ctx.author.send(embed=embed)

        else:
            await ctx.send(embed=embed)





def setup(client):
    client.add_cog(Invites(client))



