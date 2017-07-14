import os
import logging
import json
import math
import re
import random
import ast

from aiotg import Bot, chat
from database import db, text_search, text_delete

greeting = """
✋ 歡迎使用! 🎧
"""

help = """
輸入關鍵字來搜尋音樂資料庫。
在關鍵字後輸入`type:TYPE`來限定音樂格式，像這樣:
```棒棒勝 type:flac```
```棒棒勝 type:mp3```
```棒棒勝 type:mpeg```
若同時想搜尋作者和曲名，請用 `>` 隔開 (預設為作者、曲名都納入搜尋)，像這樣:
```棒棒勝>洨安之歌```
也可以搭配`type`指令，像這樣:
```棒棒勝>洨安之歌 type:flac```
輸入 `/stats` 來獲取 bot 資訊。
用 `/music` 指令來在群聊內使用棒棒勝 Music Bot，像這樣:
`/music 棒棒勝`
對於一個音樂文件回覆 `/add` 來新增至資料庫。
此外，本 bot 也支援 inline mode。
在所有地方輸入 `@(bot_username)` 加空格後便可搜尋音樂。
"""

not_found = """
找不到資料 :/
"""
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

@bot.handle("audio")
async def add_track(chat, audio):
    if "title" not in audio:
        await chat.send_text("傳送失敗...是不是你的音樂檔案少了資訊標籤? :(")
        return

    if (str(chat.sender) == 'N/A'):
        sendervar = os.environ.get('CHANNEL_NAME')
    else:
        sendervar = str(chat.sender)
    matchedMusic = await db.tracks.find_one({"$and":[{'title': str(audio.get("title"))},{'performer': str(audio.get("performer"))}]})
    if (matchedMusic):
        if not int(audio.get("file_size")) > int(matchedMusic["file_size"]):
            await chat.send_text("資料庫裡已經有這首囉 owo")
            logger.info("%s 傳送了重複的歌曲 %s %s", sendervar, str(audio.get("performer")), str(audio.get("title")))
            await bot.send_message(logChannelID,sendervar + " 傳送了重複的歌曲 " + str(audio.get("performer")) + " - " + str(audio.get("title")))
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
            await chat.send_text("檔案大小較資料庫內的大，已取代!")
            logger.info("%s 傳送了大小較大的歌曲 %s %s", sendervar, str(audio.get("performer")), str(audio.get("title")))
            await bot.send_message(logChannelID,sendervar + " 傳送了大小較大的歌曲 " + str(audio.get("performer")) + " - " + str(audio.get("title")))
            return
    doc = audio.copy()
    try:
        if (chat.sender["id"]):
            doc["sender"] = chat.sender["id"]
    except:
        doc["sender"] = os.environ.get("CHANNEL")
        
    await db.tracks.insert(doc)
    logger.info("%s 新增了 %s %s", sendervar, doc.get("performer"), doc.get("title"))
    await bot.send_message(logChannelID,sendervar + " 新增了 " + str(doc.get("performer")) + " - " + str(doc.get("title")))
    if (sendervar != os.environ.get('CHANNEL_NAME')):
        await chat.send_text(sendervar + " 新增了 " + str(doc.get("performer")) + " - " + str(doc.get("title")) + " !")

@bot.command(r'/add')
async def add(chat, match):
    audio = chat.message['reply_to_message']['audio']
    if "title" not in audio:
        await chat.send_text("傳送失敗...是不是你的音樂檔案少了資訊標籤? :(")
        return

    if (str(chat.sender) == 'N/A'):
        sendervar = os.environ.get('CHANNEL_NAME')
    else:
        sendervar = str(chat.sender)
    if (await db.tracks.find_one({ "file_id": audio["file_id"] })):
        await chat.send_text("資料庫裡已經有這首囉 owo")
        logger.info("%s 傳送了重複的歌曲 %s %s", sendervar, str(audio.get("performer")), str(audio.get("title")))
        await bot.send_message(logChannelID,sendervar + " 傳送了重複的歌曲 " + str(audio.get("performer")) + " - " + str(audio.get("title")))
        return

    doc = audio.copy()
    try:
        if (chat.sender["id"]):
            doc["sender"] = chat.sender["id"]
    except:
        doc["sender"] = os.environ.get("CHANNEL")
        
    await db.tracks.insert(doc)
    logger.info("%s 新增了 %s %s", sendervar, doc.get("performer"), doc.get("title"))
    await bot.send_message(logChannelID, sendervar + " 新增了 " + str(doc.get("performer")) + " - " + str(doc.get("title")))
    if (sendervar != os.environ.get('CHANNEL_NAME')):
        await chat.send_text(sendervar + " 新增了 " + str(doc.get("performer")) + " - " + str(doc.get("title")) + " !")
        
@bot.command(r'/admin')
async def admin(chat, match):
    if not await isAdmin(chat.sender['id']):
        logger.info("%s 查詢了管理員名單，遭到拒絕。", str(chat.sender))
        await bot.send_message(logChannelID, str(chat.sender) + ' 查詢了管理員名單，遭到拒絕。')
        await chat.send_text("存取遭拒。")
        return
    else:
        logger.info("%s 查詢了管理員名單", str(chat.sender))
        await bot.send_message(logChannelID, str(chat.sender) + ' 查詢了管理員名單')
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
        logger.info("%s 意圖刪除 '%s'，遭到拒絕。", str(chat.sender), text)
        await bot.send_message(logChannelID, str(chat.sender) + ' 意圖刪除 ' + text + '，遭到拒絕。')
        await chat.send_text("存取遭拒。")
        return
    else:
        msg = text.split(" type:")
        art = msg[0].split('>')
        i=0
        cursor = await text_delete(text)
        
        if (len(art) == 2):
            if (len(msg) == 2):
                logger.info("%s 刪除了 %i 個 %s 格式的 %s 的 %s", chat.sender, cursor, msg[1].upper(), art[0], art[1])
                await bot.send_message(logChannelID,str(chat.sender) + " 刪除了 " + str(cursor) + ' 個 ' + msg[1].upper() + " 格式的 " + art[0] + "的" + art[1])
            elif (len(msg) == 1):
                logger.info("%s 刪除了 %i 個 %s 的 %s", chat.sender, cursor, art[0], art[1])
                await bot.send_message(logChannelID,str(chat.sender) + " 刪除了 " + str(cursor) + ' 個 '  + art[0] + "的" + art[1])
        elif (len(msg) == 2):
            logger.info("%s 刪除了 %i 個 %s 格式的 %s", chat.sender, cursor, msg[1].upper(), msg[0])
            await bot.send_message(logChannelID,str(chat.sender) + " 刪除了 " + str(cursor) + ' 個 '  + msg[1].upper() + " 格式的 " + msg[0])
        elif (len(msg) == 1):
            logger.info("%s 刪除了 %i 個 %s", chat.sender, cursor, iq.query)
            await bot.send_message(logChannelID,str(chat.sender) + " 刪除了 " + str(cursor) + ' 個 '  + str(text))
        else:
            logger.info("刪除元素個數有問題RR")
            await bot.send_message(logChannelID,"刪除元素個數有問題RRR")
            await bot.send_message(logChannelID,"(text , msg , len(msg)) = " + str(text) + " , " + str(msg) + " , " + str(len(msg)))
            logger.info("(text , msg , len(msg)) = (%s , %s , %d)", str(text), str(msg), len(msg))

@bot.command(r'@%s (.+)' % bot.name)
@bot.command(r'/music@%s (.+)' % bot.name)
@bot.command(r'/music (.+)')
def music(chat, match):
    return search_tracks(chat, match.group(1))

@bot.command(r'/me')
def whoami(chat, match):
    return chat.reply(chat.sender["id"])


@bot.command(r'\((\d+)/\d+\) 下一頁 "(.+)"')
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
            logger.info("%s 搜尋了 %s 格式的 %s 的 %s", iq.sender, msg[1].upper(), art[0], art[1])
            await bot.send_message(logChannelID,str(iq.sender) + " 搜尋了 " + msg[1].upper() + " 格式的 " + art[0] + "的" + art[1])
            cursor = await text_search(iq.query)
            results = [inline_result(iq.query, t) for t in await cursor.to_list(10)]
            await iq.answer(results)
        elif (len(msg) == 1):
            logger.info("%s 搜尋了 %s 的 %s", iq.sender,  art[0], art[1])
            await bot.send_message(logChannelID,str(iq.sender) + " 搜尋了 " + art[0] + "的" + art[1])
            cursor = await text_search(iq.query)
            results = [inline_result(iq.query, t) for t in await cursor.to_list(10)]
            await iq.answer(results)
    elif (len(msg) == 2):
        logger.info("%s 搜尋了 %s 格式的 %s", iq.sender, msg[1].upper(), msg[0])
        await bot.send_message(logChannelID,str(iq.sender) + " 搜尋了 " + msg[1].upper() + " 格式的 " + msg[0])
        cursor = await text_search(iq.query)
        results = [inline_result(iq.query, t) for t in await cursor.to_list(10)]
        await iq.answer(results)
    elif (len(msg) == 1):
        logger.info("%s 搜尋了 %s", iq.sender, iq.query)
        await bot.send_message(logChannelID,str(iq.sender) + " 搜尋了 " + str(iq.query))
        cursor = await text_search(iq.query)
        results = [inline_result(iq.query, t) for t in await cursor.to_list(10)]
        await iq.answer(results)
    else:
        logger.info("元素個數有問題RR")
        await bot.send_message(logChannelID,"元素個數有問題RRR")
        await bot.send_message(logChannelID,"(iq.query , msg , len(msg)) = " + str(iq.query) + " , " + str(msg) + " , " + str(len(msg)))
        logger.info("(iq.query , msg , len(msg)) = (%s , %s , %d)", str(iq.query), str(msg), len(msg))


@bot.command(r'/music(@%s)?$' % bot.name)
def usage(chat, match):
    return chat.send_text(greeting, parse_mode='Markdown')


@bot.command(r'/start')
async def start(chat, match):
    tuid = chat.sender["id"]
    if not (await db.users.find_one({ "id": tuid })):
        logger.info("新用戶 %s", chat.sender)
        await bot.send_message(logChannelID,"新用戶 " + str(chat.sender))
        await db.users.insert(chat.sender.copy())

    await chat.send_text(greeting, parse_mode='Markdown')


@bot.command(r'/stop')
async def stop(chat, match):
    tuid = chat.sender["id"]
    await db.users.remove({ "id": tuid })

    logger.info("%s 退出了", chat.sender)
    await bot.send_message(logChannelID,str(chat.sender) + " 退出了")
    await chat.send_text("掰掰! 😢")


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
        return (await chat.send_text("統計資訊還沒好!"))

    size = human_size(aggr[0]["size"])
    text = '%d 首歌曲, %s' % (count, size)

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
                logger.info("%s 搜尋了 %s 的 %s", chat.sender, author, song)
                await bot.send_message(logChannelID,str(chat.sender) + " 搜尋了 " + author + " 的 " + song)
            else:
                logger.info("%s 搜尋了 %s 格式的 %s 的 %s", chat.sender, typel[1].upper(), author, song)
                await bot.send_message(logChannelID,str(chat.sender) + " 搜尋了 " + typel[1].upper() + " 格式的 " + author + " 的 " + song)
        elif (len(typel) == 1):
            logger.info("%s 搜尋了 %s", chat.sender, query)
            await bot.send_message(logChannelID,str(chat.sender) + " 搜尋了 " + str(query))
        else:
            logger.info("%s 搜尋了 %s 格式的 %s", chat.sender, typel[1].upper(), typel[0])
            await bot.send_message(logChannelID,str(chat.sender) + " 搜尋了 " + typel[1].upper() + " 格式的 " + str(typel[0]))

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
            kb = [['(%d/%d) 下一頁 "%s"' % (page+1, pages, query)]]
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
            "title" : "{} - {}".format(track.get("performer", "未知藝術家"),track.get("title", "無標題")),
            "input_message_content" : noinline
            }
    return results