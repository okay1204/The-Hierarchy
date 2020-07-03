import discord
from discord.ext import commands, tasks
import asyncio
import sqlite3
from sqlite3 import Error
from utils import rightCategory
import os
import bottokens

client = commands.Bot(command_prefix = '.')
client.remove_command('help')

def notinapplications(ctx):
    return ctx.channel.id != 716720359818133534

#Defining own read and write for different database
def read_value(table, where, what, value):
    conn = sqlite3.connect('fun.db')
    c = conn.cursor()
    c.execute(f'SELECT {value} FROM {table} WHERE {where} = ?', (what,))
    reading = c.fetchone()
    conn.close()
    reading = reading[0]
    return reading

def write_value(table, where, what, value, overwrite):
    conn = sqlite3.connect('fun.db')
    c = conn.cursor()
    c.execute(f"UPDATE {table} SET {value} = {overwrite} WHERE {where} = ?", (what,))
    conn.commit()
    conn.close()

@client.event
async def on_ready():
    print(f"Logged in as {client.user}.\nID: {client.user.id}")
    await client.change_presence(status=discord.Status.online, activity=discord.Game(name=' '))


@client.event
async def on_message(message):
    counting = client.get_channel(721444345353470002)
    sentences = client.get_channel(721475839153143899)
     #Endless counting channel
    if message.author.bot:
        return



    if message.channel == counting:
        content = message.content
        #Grabing last number from here
        conn = sqlite3.connect('fun.db')
        c = conn.cursor()
        c.execute('SELECT number FROM counting')
        currentnumber = c.fetchone()
        conn.close()
        currentnumber = currentnumber[0] 
        #to here
        nextnumber = currentnumber + 1
        if content.lower() == 'next':
            await counting.send(f"**{nextnumber}**")
            return
        elif message.content.startswith('.warn') or message.content.startswith('.kick') or message.content.startswith('.ban') or message.content.startswith('.report') or message.content.startswith('.tag'):
            return
        elif str(nextnumber) in content:
            #Writing number from here
            conn = sqlite3.connect('fun.db')
            c = conn.cursor()
            c.execute(f"UPDATE counting SET number = ?", (nextnumber,))
            c.execute(f"UPDATE counting SET lastmsgid = ?", (message.id,))
            conn.commit()
            conn.close()
            #to here
        else:
            await message.delete()
            await counting.send(f"Your message must have the next number in it, {message.author.mention}.", delete_after=3)
        return
    
    
    #For sentences
    elif message.channel == sentences:
        content = message.content
        if message.content.startswith('.warn') or message.content.startswith('.kick') or message.content.startswith('.ban') or message.content.startswith('.report') or message.content.startswith('.tag'):
            return
        elif " " in content:
            await message.delete()
            await sentences.send(f"You can't send two words in one message, {message.author.mention}.", delete_after=3)
            return
        #Grabing last author from here
        conn = sqlite3.connect('fun.db')
        c = conn.cursor()
        c.execute('SELECT prevauthor FROM sentences')
        prevauthor = c.fetchone()
        conn.close()
        prevauthor = prevauthor[0] 
        #to here
        authorid = message.author.id
        if authorid == prevauthor:
            await message.delete()
            await sentences.send(f"You can't send two messages in a row, {message.author.mention}.", delete_after=3)
        else:
            #Writing data from here
            conn = sqlite3.connect('fun.db')
            c = conn.cursor()
            c.execute("UPDATE sentences SET prevauthor = ?", (authorid,))
            c.execute("UPDATE sentences SET lastmsgid = ?", (message.id,))
            conn.commit()
            conn.close()
            #to here
        return

    await client.process_commands(message)

@client.event
async def on_raw_message_edit(payload):
    counting = 721444345353470002
    sentences = 721475839153143899
    if payload.channel_id == counting:
        counting = client.get_channel(721444345353470002)
        message = await counting.fetch_message(payload.message_id)
        #Grabing data from here
        conn = sqlite3.connect('fun.db')
        c = conn.cursor()
        c.execute('SELECT number FROM counting')
        currentnumber = c.fetchone()
        c.execute('SELECT lastmsgid FROM counting')
        lastmsgid = c.fetchone()
        conn.close()
        currentnumber = currentnumber[0]
        lastmsgid = lastmsgid[0] 
        #to here
        if str(currentnumber) not in message.content and payload.message_id == lastmsgid:
            await message.delete()


    if payload.channel_id == sentences :
        sentences = client.get_channel(sentences)
        message = await sentences.fetch_message(payload.message_id)
        #Grabing data from here
        conn = sqlite3.connect('fun.db')
        c = conn.cursor()
        c.execute('SELECT lastmsgid FROM sentences')
        lastmsgid = c.fetchone()
        conn.close()
        lastmsgid = lastmsgid[0] 
        #to here
        if " " in message.content and payload.message_id == lastmsgid:
            await message.delete()

@client.event
async def on_raw_message_delete(payload):
    counting = 721444345353470002
    sentences = 721475839153143899
    if payload.channel_id == counting:
        counting = client.get_channel(counting)
        #Grabing last message from here
        conn = sqlite3.connect('fun.db')
        c = conn.cursor()
        c.execute('SELECT lastmsgid FROM counting')
        lastmsgid = c.fetchone()
        conn.close()
        lastmsgid = lastmsgid[0] 
        #to here
        if payload.message_id == lastmsgid:
            async for message in counting.history(limit=100):
                if message.content.lower() == "next" or message.author.bot or message.content.startswith('.warn') or message.content.startswith('.kick') or message.content.startswith('.ban') or message.content.startswith('.report') or message.content.startswith('.tag'):
                    continue
                else:
                    newmsg = message
                    break
            #Writing new data from here
            conn = sqlite3.connect('fun.db')
            c = conn.cursor()
            c.execute("UPDATE counting SET lastmsgid = ?", (newmsg.id,))
            #Grabing last number from here
            c.execute('SELECT number FROM counting')
            number = c.fetchone()
            number = number[0]
            number -= 1
            #to here
            c.execute("UPDATE counting SET number = ?", (number,))
            conn.commit()
            conn.close()
            #to here


    elif payload.channel_id == sentences:
        sentences = client.get_channel(sentences)
        #Grabing last message from here
        conn = sqlite3.connect('fun.db')
        c = conn.cursor()
        c.execute('SELECT lastmsgid FROM sentences')
        lastmsgid = c.fetchone()
        conn.close()
        lastmsgid = lastmsgid[0] 
        #to here
        if payload.message_id == lastmsgid:
            async for message in sentences.history(limit=100):
                if message.author.bot or message.content.startswith('.warn') or message.content.startswith('.kick') or message.content.startswith('.ban') or message.content.startswith('.report') or message.content.startswith('.tag'):
                    continue
                else:
                    newmsg = message
                    break
            #Writing new data from here
            conn = sqlite3.connect('fun.db')
            c = conn.cursor()
            c.execute("UPDATE sentences SET lastmsgid = ?", (newmsg.id,))
            c.execute("UPDATE sentences SET prevauthor = ?", (newmsg.author.id,))
            conn.commit()
            conn.close()
            #to here


@client.command()
@commands.check(rightCategory)
async def tagcreate(ctx, name=None, privacy=None, *, content=None):
    if not name:
        await ctx.send('Enter a name for your tag.')
        return
    if not privacy:
        await ctx.send('Enter a privacy setting for your tag.')
        return
    if not content:
        await ctx.send('Enter some content for your tag.')
        return

    privacy = privacy.lower()
    if privacy != "private" and privacy != "public":
        await ctx.send("Enter a valid privacy option. (`private`, `public`)")
        return
    
    if content.startswith('.'):
        await ctx.send('You cannot start the content of your tag with a period.')
        return

    author = ctx.author

    #Checking for duplicate tags
    conn = sqlite3.connect('fun.db')
    c = conn.cursor()
    c.execute('SELECT name FROM tags')
    tempnames = c.fetchall()
    conn.close()
    names = []
    for x in tempnames:
        names.append(x[0])
    if name in names:
        await ctx.send(f'There is already a tag called `{name}`.')
        return

    #Checking for multiple tags
    conn = sqlite3.connect('fun.db')
    c = conn.cursor()
    c.execute('SELECT author FROM tags WHERE author = ?', (author.id,))
    tagsby = c.fetchall()
    conn.close()
    if len(tagsby) >= 3:

        #Checking for premium
        conn = sqlite3.connect('hierarchy.db')
        c = conn.cursor()
        c.execute('SELECT premium FROM members WHERE id = ?', (author.id,))
        premium = c.fetchone()
        conn.close()
        premium = premium[0]
        if premium == "False" and author.id != 322896727071784960: #My own id
            await ctx.send("You may only have up to 3 tags. Upgrade to __premium__ to get up to 10!")
            return
        elif len(tagsby) >= 10 and author.id != 322896727071784960:
            await ctx.send("You have may only have up to 10 tags.")
            return


    conn = sqlite3.connect('fun.db')
    c = conn.cursor()
    c.execute(f"INSERT INTO tags (name, author, content, privacy) VALUES (?, ?, ?, ?)", (name, author.id, content, privacy))
    conn.commit()
    conn.close()

    await ctx.send("🏷️ Tag successfully created. 🏷️")

@client.command()
@commands.check(rightCategory)
async def tagdelete(ctx, *, name=None):
    if not name:
        await ctx.send("Enter the name of the tag you want to delete.")
        return
    
    conn = sqlite3.connect('fun.db')
    c = conn.cursor()
    c.execute('SELECT name, author FROM tags WHERE name = ?', (name,))
    tag = c.fetchone()
    conn.close()

    if not tag:
        await ctx.send("Tag not found.")
        return
    elif tag[1] != ctx.author.id:
        await ctx.send("This tag does not belong to you.")
        return

    conn = sqlite3.connect('fun.db')
    c = conn.cursor()
    c.execute(f"DELETE FROM tags WHERE name = ?", (name,))
    conn.commit()
    conn.close()

    await ctx.send("🏷️ Tag successfully deleted. 🏷️")

@client.command()
@commands.check(rightCategory)
async def tagedit(ctx, name=None, option=None, *, setting=None):
    if not name:
        await ctx.send("Enter the name of the tag you want to edit.")
    if not option:
        await ctx.send("Enter the option of the tag you want to edit. (`privacy`, `content`)")
    
    #Grabbing tag
    conn = sqlite3.connect('fun.db')
    c = conn.cursor()
    c.execute('SELECT name, author FROM tags WHERE name = ?', (name,))
    tag = c.fetchone()
    conn.close()

    if not tag:
        await ctx.send("Tag not found.")
        return
    elif tag[1] != ctx.author.id:
        await ctx.send("This tag does not belong to you.")
        return


    option = option.lower()
    if option != "content" and option != "privacy":
        await ctx.send("Enter a valid option. (`privacy`, `content`)")
        return
    
    if not setting:
        await ctx.send(f"Enter what you want to change the {option} to.")

    if option == "privacy":
        setting = setting.lower()
        if setting != "private" and setting != "public":
            await ctx.send("Enter a valid privacy option. (`private`, `public`)")
            return
        
        conn = sqlite3.connect('fun.db')
        c = conn.cursor()
        c.execute("UPDATE tags SET privacy = ? WHERE name = ?", (setting, name))
        conn.commit()
        conn.close()

        await ctx.send(f"🏷️ Tag's privacy successfully updated to {setting}. 🏷️")
    
    else:
        conn = sqlite3.connect('fun.db')
        c = conn.cursor()
        c.execute("UPDATE tags SET content = ? WHERE name = ?", (setting, name))
        conn.commit()
        conn.close()

        await ctx.send(f"🏷️ Tag's content successfully updated. 🏷️")

        
        
    

@client.command()
@commands.check(rightCategory)
async def tags(ctx, member:discord.Member=None):
    if not member:
        user = ctx.author
    else:
        user = member

    conn = sqlite3.connect('fun.db')
    c = conn.cursor()
    c.execute('SELECT name, privacy FROM tags WHERE author = ?', (user.id,))
    tags = c.fetchall()
    conn.close()

    if not tags:
        if ctx.author == user:
            await ctx.send("You don't have any tags.")
        else:
            await ctx.send(f"**{member.name}** does not have any tags.")
        return
    

    text = f"**{user.name}**'s tags:"
    for tag in tags:
        text += f"\n`{tag[1].capitalize()}` {tag[0]}"
    
    try:
        await ctx.send(text)
    except:
        await ctx.send("Text Overload: Text was too long to send in one message.")

@client.command()
@commands.check(notinapplications)
async def tag(ctx, *, name=None):
    if not name:
        await ctx.send("Enter the name of the tag.")
        return
    
    #Grabbing privacy and content
    conn = sqlite3.connect('fun.db')
    c = conn.cursor()
    c.execute('SELECT privacy, content, author FROM tags WHERE name = ?', (name,))
    tag = c.fetchone()
    conn.close()

    if not tag:
        await ctx.send("Tag not found.")
        return
    elif tag[0] == "private" and ctx.author.id != tag[2]:
        await ctx.send("This tag is private.")
        return
    
    await ctx.send(tag[1])


@tags.error
async def member_not_found_error(ctx, error):
    if isinstance(error, commands.CheckAnyFailure) or isinstance(error, commands.CheckFailure):
        pass
    elif isinstance(error, commands.BadArgument):
        await ctx.send('Member not found.')
    else:
        print(error)


    


client.run(os.environ.get("fun"))