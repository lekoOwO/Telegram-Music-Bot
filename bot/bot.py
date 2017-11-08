import os
import logging
import json
import math
import re
import random
import ast

from aiotg import Bot, chat
from database import db, text_search, text_delete

if os.environ.get('LANG') == 'zh-TW':
    from zh_TW import greeting, help, not_found, texts
elif os.environ.get('LANG') == 'en-US':
    from en_US import greeting, help, not_found, texts
else:
    from zh_TW import greeting, help, not_found, texts

bot = Bot(
    api_token=os.environ.get('API_TOKEN'),
    name=os.environ.get('BOT_NAME'),
    botan_token=os.environ.get("BOTAN_TOKEN")
)
logger = logging.getLogger("musicbot")
channel = bot.channel(os.environ.get('CHANNEL'))
logChannelID = os.environ.get("LOGCHN_ID")

async def getAdmin(ID=logChannelID):
    raw = ast.literal_eval(str(await bot.api_call("getChatAdministrators",chat_id=ID)))
    i=0
    adminDict = []
    while i < len(raw['result']):
        if 'last_name' in raw['result'][i]['user']:
            adminDict.append({
            'id':raw['result'][i]['user']['id'],
            'username':raw['result'][i]['user']['username'],
            'first_name':raw['result'][i]['user']['first_name'],
            'last_name':raw['result'][i]['user']['last_name']})
        else:
            adminDict.append({
            'id':raw['result'][i]['user']['id'],
            'username':raw['result'][i]['user']['username'],
            'first_name':raw['result'][i]['user']['first_name'],
            'last_name':''})
        i += 1
    return adminDict

async def isAdmin(ID):
    i=0
    adminList = await getAdmin()
    while i<len(adminList):
        if adminList[i]['id'] == ID:
            return 1
        i += 1
    return 0

async def say(text):
    await bot.send_message(logChannelID, text)
    logger.info(text)
    return 0

@bot.handle("audio")
async def add_track(chat, audio):
    if "title" not in audio:
        await chat.send_text(texts['tagNotFound'])
        return

    if (str(chat.sender) == 'N/A'):
        sendervar = os.environ.get('CHANNEL_NAME')
    else:
        sendervar = str(chat.sender)
    matchedMusic = await db.tracks.find_one({"$and":[{'title': str(audio.get("title"))},{'performer': str(audio.get("performer"))}]})
    if (matchedMusic):
        if not int(audio.get("file_size")) > int(matchedMusic["file_size"]):
            await chat.send_text(texts['musicExists'])
            await say(texts['sentExistedMusic'](sendervar, str(audio.get("performer")), str(audio.get("title"))))
            return
        else:
            await text_delete(str(audio.get("performer"))+ '>' + str(audio.get("title")))
            doc = audio.copy()
            try:
                if (chat.sender["id"]):
                    doc["sender"] = chat.sender["id"]
            except:
                doc["sender"] = os.environ.get("CHANNEL")
            await db.tracks.insert(doc)
            await chat.send_text(texts['replaced'])
            await say(texts['sentLargerMusic'](sendervar, str(audio.get("performer")), str(audio.get("title"))))
            return
    doc = audio.copy()
    try:
        if (chat.sender["id"]):
            doc["sender"] = chat.sender["id"]
    except:
        doc["sender"] = os.environ.get("CHANNEL")
        
    await db.tracks.insert(doc)
    await say(texts['addMusic'](sendervar, str(doc.get("performer")), str(doc.get("title"))))
    if (sendervar != os.environ.get('CHANNEL_NAME')):
        await chat.send_text(texts['addMusic'](sendervar, str(doc.get("performer")), str(doc.get("title"))) + " !")

@bot.command(r'/add')
async def add(chat, match):
    audio = chat.message['reply_to_message']['audio']
    if "title" not in audio:
        await chat.send_text(texts['tagNotFound'])
        return

    if (str(chat.sender) == 'N/A'):
        sendervar = os.environ.get('CHANNEL_NAME')
    else:
        sendervar = str(chat.sender)
    if (await db.tracks.find_one({ "file_id": audio["file_id"] })):
        await chat.send_text(texts['musicExists'])
        await say(texts['sentExistedMusic'](sendervar, str(audio.get("performer")), str(audio.get("title"))))
        return

    doc = audio.copy()
    try:
        if (chat.sender["id"]):
            doc["sender"] = chat.sender["id"]
    except:
        doc["sender"] = os.environ.get("CHANNEL")
        
    await db.tracks.insert(doc)
    await say(texts['addMusic'](sendervar, str(doc.get("performer")), str(doc.get("title"))))
    if (sendervar != os.environ.get('CHANNEL_NAME')):
        await chat.send_text(texts['addMusic'](sendervar, str(doc.get("performer")), str(doc.get("title"))) + " !")
        
@bot.command(r'/admin')
async def admin(chat, match):
    if not await isAdmin(chat.sender['id']):
        await say(texts['inquiredAdminListRefused'](str(chat.sender)))
        await chat.send_text(texts['denied'])
        return
    else:
        await say(texts['inquiredAdminList'](str(chat.sender)))
        raw = await getAdmin()
        adminStr=''
        i=0
        while i<len(raw):
            adminStr += raw[i]['first_name']+' '+raw[i]['last_name']+'\n'
            i += 1
        await chat.send_text(adminStr)

@bot.command(r'/delete (.+)')
async def delete(chat, match):
    text = match.group(1)
    if not await isAdmin(chat.sender['id']):
        await say(texts['deleteRefused'](chat.sender, text))
        await chat.send_text(texts['denied'])
        return
    else:
        msg = text.split(" type:")
        art = msg[0].split('>')
        i=0
        cursor = await text_delete(text)
        
        if (len(art) == 2):
            if (len(msg) == 2):
                await say(texts['deleteNumTypeArt'](chat.sender, str(cursor), msg[1].upper(), art[0], art[1]))
            elif (len(msg) == 1):
                await say(texts['deleteNumArt'](chat.sender, str(cursor), art[0], art[1]))
        elif (len(msg) == 2):
            await say(texts['deleteNumType'](chat.sender, str(cursor), msg[1].upper(), msg[0]))
        elif (len(msg) == 1):
            await say(texts['deleteNum'](chat.sender, str(cursor), text))
        else:
            await say(texts['deleteError'])
            await say("(text , msg , len(msg)) = " + str(text) + " , " + str(msg) + " , " + str(len(msg)))

@bot.command(r'@%s (.+)' % bot.name)
@bot.command(r'/music@%s (.+)' % bot.name)
@bot.command(r'/music (.+)')
def music(chat, match):
    return search_tracks(chat, match.group(1))

@bot.command(r'/me')
def whoami(chat, match):
    return chat.reply(chat.sender["id"])

@bot.command(r'\((\d+)/\d+\) %s "(.+)"' % texts['nextPage'])
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
            await say(texts['searchTypeArt'](str(iq.sender), msg[1].upper(), art[0], art[1]))
            cursor = await text_search(iq.query)
            results = [inline_result(iq.query, t) for t in await cursor.to_list(10)]
            await iq.answer(results)
        elif (len(msg) == 1):
            await say(texts['searchArt'](str(iq.sender), art[0], art[1]))
            cursor = await text_search(iq.query)
            results = [inline_result(iq.query, t) for t in await cursor.to_list(10)]
            await iq.answer(results)
    elif (len(msg) == 2):
        await say(texts['searchType'](str(iq.sender), msg[1].upper(), msg[0]))
        cursor = await text_search(iq.query)
        results = [inline_result(iq.query, t) for t in await cursor.to_list(10)]
        await iq.answer(results)
    elif (len(msg) == 1):
        await say(texts['search'](str(iq.sender), iq.query))
        cursor = await text_search(iq.query)
        results = [inline_result(iq.query, t) for t in await cursor.to_list(10)]
        await iq.answer(results)
    else:
        await say(texts['searchError'])
        await say("(iq.query , msg , len(msg)) = " + str(iq.query) + " , " + str(msg) + " , " + str(len(msg)))


@bot.command(r'/music(@%s)?$' % bot.name)
def usage(chat, match):
    return chat.send_text(greeting, parse_mode='Markdown')


@bot.command(r'/start')
async def start(chat, match):
    tuid = chat.sender["id"]
    if not (await db.users.find_one({ "id": tuid })):
        await say(texts['newUser'](str(chat.sender)))
        await db.users.insert(chat.sender.copy())

    await chat.send_text(greeting, parse_mode='Markdown')


@bot.command(r'/stop')
async def stop(chat, match):
    tuid = chat.sender["id"]
    await db.users.remove({ "id": tuid })

    await say(texts['exit'](str(chat.sender)))
    await chat.send_text(texts['bye'])


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
        return (await chat.send_text(texts['statsNotReady']))

    size = human_size(aggr[0]["size"])
    text = texts['musicCalc'](str(count), str(size))

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
                await say(texts['searchArt'](str(chat.sender), author, song))
            else:
                await say(texts['searchTypeArt'](str(chat.sender), typel[1].upper(), author, song))
        elif (len(typel) == 1):
            await say(texts['search'](str(chat.sender), query))
        else:
            await say(texts['searchType'](str(chat.sender), typel[1].upper(), typel[0]))

        limit = 3
        offset = (page - 1) * limit

        tempCursor = await text_search(query)
        cursor = tempCursor.skip(offset).limit(limit)
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
            kb = [['(%d/%d) %s "%s"' % (page+1, pages, texts['nextPage'], query)]]
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
    results = {
            "type": "document",
            "id": track["file_id"] + str(random.randint(0,99)),
            "document_file_id": track["file_id"],
            "title" : "{} - {}".format(track.get("performer", texts['unknownArtist']),track.get("title", texts['untitled'])),
            }
    return results