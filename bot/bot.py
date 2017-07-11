import os
import logging
import json
import math
import re
import random

from aiotg import Bot, chat
from database import db, text_search

greeting = """
This is a Music bot!
"""

help = """
Simply type in keywords to search from the database.
Simply send music files to add to the database.
Command `/help` for help.
type:TYPE after keywords to restrict the type of result.
```Xiaoan type:flac```
```Xiaoan type:mp3``` ( mp3 was converted to mpeg in bot since mp3 is not a mime-type.)
```Xiaoan type:mpeg```
Seperate the artist and song by > .
```Xiaoan>The song of early-spring```
It also works great with type.
```Xiaoan>The song of early-spring type:flac```
Command /stats for the status of bot.
Command /music to return music files from this bot in a group chat.
```/music Xiaoan```
Reply `/add` to a music file in a group chat to add music file to the database.
Songs which was uploaded to the music channel will be sync to the database.
This bot supports inline mode, too.
"""

not_found = """
Data not found ._.
"""
bot = Bot(
    api_token=os.environ.get('API_TOKEN'),
    name=os.environ.get('BOT_NAME'),
    botan_token=os.environ.get("BOTAN_TOKEN")
)

logger = logging.getLogger("musicbot")
channel = bot.channel(os.environ.get('CHANNEL'))
@bot.handle("audio")
async def add_track(chat, audio):
    if "title" not in audio:
        await chat.send_text("Failed...No Id3 tag found :(")
        return
    if (str(chat.sender) == 'N/A'):
        sendervar = os.environ.get('CHANNEL_NAME')
    else:
        sendervar = str(chat.sender)
    if (await db.tracks.find_one({ "file_id": audio["file_id"] })):
        await chat.send_text("The song has already been added to the database owo")
        logger.info("%s sent a existed music %s %s", sendervar, str(audio.get("performer")), str(audio.get("title")))
        await bot.send_message(os.environ.get("LOGCHN_ID"),sendervar + " sent a existed music " + str(audio.get("performer")) + " - " + str(audio.get("title")))
        return
    doc = audio.copy()
    try:
        if (chat.sender["id"]):
            doc["sender"] = chat.sender["id"]
    except:
        doc["sender"] = os.environ.get("CHANNEL")
        
    await db.tracks.insert(doc)
    logger.info("%s added %s %s", sendervar, doc.get("performer"), doc.get("title"))
    await bot.send_message(os.environ.get("LOGCHN_ID"),sendervar + " added " + str(doc.get("performer")) + " - " + str(doc.get("title")))
    if (sendervar != os.environ.get('CHANNEL_NAME')):
        await chat.send_text(sendervar + " added " + str(doc.get("performer")) + " - " + str(doc.get("title")) + " !")

@bot.command(r'/add')
async def add(chat, match):
    audio = chat.message['reply_to_message']['audio']
    if "title" not in audio:
        await chat.send_text("Failed...No Id3 tag found :(")
        return
    if (str(chat.sender) == 'N/A'):
        sendervar = os.environ.get('CHANNEL_NAME')
    else:
        sendervar = str(chat.sender)
    if (await db.tracks.find_one({ "file_id": audio["file_id"] })):
        await chat.send_text("The song has already been added to the database owo")
        logger.info("%s sent a existed music %s %s", sendervar, str(audio.get("performer")), str(audio.get("title")))
        await bot.send_message(os.environ.get("LOGCHN_ID"),sendervar + " sent a existed music " + str(audio.get("performer")) + " - " + str(audio.get("title")))
        return
    doc = audio.copy()
    try:
        if (chat.sender["id"]):
            doc["sender"] = chat.sender["id"]
    except:
        doc["sender"] = os.environ.get("CHANNEL")
        
    await db.tracks.insert(doc)
    logger.info("%s added %s %s", sendervar, doc.get("performer"), doc.get("title"))
    await bot.send_message(os.environ.get("LOGCHN_ID"),sendervar + " added " + str(doc.get("performer")) + " - " + str(doc.get("title")))
    if (sendervar != os.environ.get('CHANNEL_NAME')):
        await chat.send_text(sendervar + " added " + str(doc.get("performer")) + " - " + str(doc.get("title")) + " !")
    
@bot.command(r'@%s (.+)' % bot.name)
@bot.command(r'/music@%s (.+)' % bot.name)
@bot.command(r'/music (.+)')
def music(chat, match):
    return search_tracks(chat, match.group(1))


@bot.command(r'\((\d+)/\d+\) Next page "(.+)"')
def more(chat, match):
    page = int(match.group(1))
    return search_tracks(chat, match.group(2), page)


@bot.default
def default(chat, message):
    return search_tracks(chat, message["text"])

@bot.inline
async def inline(iq):
    msg = iq.query.split(" type:")
    art = msg[0].split('>')
    if (len(art) == 2):
        if (len(msg) == 2):
            logger.info("%s searched %s music %s - %s", iq.sender, msg[1].upper(), art[0], art[1])
            await bot.send_message(os.environ.get("LOGCHN_ID"),str(iq.sender) + " searched " + msg[1].upper() + " music " + art[0] + " - " + art[1])
            cursor = text_search(iq.query)
            results = [inline_result(iq.query, t) for t in await cursor.to_list(10)]
            await iq.answer(results)
        elif (len(msg) == 1):
            logger.info("%s searched %s - %s", iq.sender,  art[0], art[1])
            await bot.send_message(os.environ.get("LOGCHN_ID"),str(iq.sender) + " searched " + art[0] + " - " + art[1])
            cursor = text_search(iq.query)
            results = [inline_result(iq.query, t) for t in await cursor.to_list(10)]
            await iq.answer(results)
    elif (len(msg) == 2):
        logger.info("%s searched %s music %s", iq.sender, msg[1].upper(), msg[0])
        await bot.send_message(os.environ.get("LOGCHN_ID"),str(iq.sender) + " searched " + msg[1].upper() + " music " + msg[0])
        cursor = text_search(iq.query)
        results = [inline_result(iq.query, t) for t in await cursor.to_list(10)]
        await iq.answer(results)
    elif (len(msg) == 1):
        logger.info("%s searched %s", iq.sender, iq.query)
        await bot.send_message(os.environ.get("LOGCHN_ID"),str(iq.sender) + " searched " + str(iq.query))
        cursor = text_search(iq.query)
        results = [inline_result(iq.query, t) for t in await cursor.to_list(10)]
        await iq.answer(results)
    else:
        logger.info("ERROR")
        await bot.send_message(os.environ.get("LOGCHN_ID"),"ERROR")
        await bot.send_message(os.environ.get("LOGCHN_ID"),"(iq.query , msg , len(msg)) = " + str(iq.query) + " , " + str(msg) + " , " + str(len(msg)))
        logger.info("(iq.query , msg , len(msg)) = (%s , %s , %d)", str(iq.query), str(msg), len(msg))


@bot.command(r'/music(@%s)?$' % bot.name)
def usage(chat, match):
    return chat.send_text(greeting, parse_mode='Markdown')


@bot.command(r'/start')
async def start(chat, match):
    tuid = chat.sender["id"]
    if not (await db.users.find_one({ "id": tuid })):
        logger.info("New user %s", chat.sender)
        await bot.send_message(os.environ.get("LOGCHN_ID"),"New user " + str(chat.sender))
        await db.users.insert(chat.sender.copy())

    await chat.send_text(greeting, parse_mode='Markdown')


@bot.command(r'/stop')
async def stop(chat, match):
    tuid = chat.sender["id"]
    await db.users.remove({ "id": tuid })

    logger.info("%s exited", chat.sender)
    await bot.send_message(os.environ.get("LOGCHN_ID"),str(chat.sender) + " exited")
    await chat.send_text("Goodbye! 😢")


@bot.command(r'/help')
def usage(chat, match):
    return chat.send_text(help, parse_mode='Markdown')


@bot.command(r'/stats')
async def stats(chat, match):
    count = await db.tracks.count()
    group = {
        "$group": {
            "_id": None,
            "size": {"$sum": "$file_size"}
        }
    }
    cursor = db.tracks.aggregate([group])
    aggr = await cursor.to_list(1)

    if len(aggr) == 0:
        return (await chat.send_text("Info not prepared yet!"))

    size = human_size(aggr[0]["size"])
    text = '%d songs, %s' % (count, size)

    return (await chat.send_text(text))


def human_size(nbytes):
    suffixes = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
    rank = int((math.log10(nbytes)) / 3)
    rank = min(rank, len(suffixes) - 1)
    human = nbytes / (1024.0 ** rank)
    f = ('%.2f' % human).rstrip('0').rstrip('.')
    return '%s %s' % (f, suffixes[rank])


def send_track(chat, keyboard, track):
    return chat.send_audio(
        audio=track["file_id"],
        title=track.get("title"),
        performer=track.get("performer"),
        duration=track.get("duration"),
        reply_markup=json.dumps(keyboard)
    )


async def search_tracks(chat, query, page=1):
    if(str(chat.sender) != "N/A"):
        typel = query.split(" type:")
        if (query.find(">") != -1):
            art = typel[0].split('>')
            author = art[0]
            song = art[1]
            if (len(typel) == 1):
                logger.info("%s searched %s - %s", chat.sender, author, song)
                await bot.send_message(os.environ.get("LOGCHN_ID"),str(chat.sender) + " searched " + author + " - " + song)
            else:
                logger.info("%s searched %s music %s - %s", chat.sender, typel[1].upper(), author, song)
                await bot.send_message(os.environ.get("LOGCHN_ID"),str(chat.sender) + " searched " + typel[1].upper() + " music " + author + " - " + song)
        elif (len(typel) == 1):
            logger.info("%s searched %s", chat.sender, query)
            await bot.send_message(os.environ.get("LOGCHN_ID"),str(chat.sender) + " searched " + str(query))
        else:
            logger.info("%s searched %s music %s", chat.sender, typel[1].upper(), typel[0])
            await bot.send_message(os.environ.get("LOGCHN_ID"),str(chat.sender) + " searched " + typel[1].upper() + " music " + str(typel[0]))

        limit = 3
        offset = (page - 1) * limit

        cursor = text_search(query).skip(offset).limit(limit)
        count = await cursor.count()
        results = await cursor.to_list(limit)

        if count == 0:
            await chat.send_text(not_found)
            return

        # Return single result if we have exact match for title and performer
        if results[0]['score'] > 2:
            limit = 1
            results = results[:1]

        newoff = offset + limit
        show_more = count > newoff

        if show_more:
            pages = math.ceil(count / limit)
            kb = [['(%d/%d) Next page "%s"' % (page+1, pages, query)]]
            keyboard = {
                "keyboard": kb,
                "resize_keyboard": True
            }
        else:
            keyboard = { "hide_keyboard": True }

        for track in results:
            await send_track(chat, keyboard, track)


def inline_result(query, track):
    global seed
    seed = query + str(random.randint(0,9999999))
    random.seed(query + str(random.randint(0,9999999)))
    noinline ={
        "message_text": track.get("performer", "") + ">" + track.get("title", "")
    }
    results = {
            "type": "document",
            "id": track["file_id"] + str(random.randint(0,99)),
            "document_file_id": track["file_id"],
            "title" : "{} - {}".format(track.get("performer", "Unknown Artist"),track.get("title", "Untitled")),
            "input_message_content" : noinline
            }
    return results