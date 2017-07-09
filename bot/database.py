import os
import pymongo
from motor.motor_asyncio import AsyncIOMotorClient
import re
from functools import reduce

client = AsyncIOMotorClient(host=os.environ.get('MONGO_HOST'))
db = client[os.environ.get('MONGO_DB_NAME')]



def text_search(query):
    typel = query.split(" type:")
    if (query.find(">") == -1):
        if (len(typel) == 1):
            typef = 'audio'
        elif (typel[1] == 'mp3'):
            typef = 'mpeg'
        else:
            typef = typel[1]
        keyword = typel[0].split(" ")
        keyword_regex = re.compile (reduce(lambda x,y: x+'(?=.*?'+y+')', keyword) + '.*?', re.IGNORECASE)
        return db.tracks.find(
            {"$and":[
                {'mime_type': re.compile (typef, re.IGNORECASE)},
                {"$or":[
                    {'title': keyword_regex},
                {'performer': keyword_regex}
                ]}]},
            { 'score': { '$meta': 'textScore' } }).sort([('score', {'$meta': 'textScore'})])
    elif (query.find(">") != -1):
        art = typel[0].split(">")
        if (len(typel) == 1):
            typef = 'audio'
        elif (typel[1] == 'mp3'):
            typef = 'mpeg'
        else:
            typef = typel[1]
        title = art[1].split(" ")
        performer = art[0].split(" ")
        return db.tracks.find(
            {"$and":[
                {'mime_type': re.compile (typef, re.IGNORECASE)},
                {"$and":[
                    {'title': re.compile (reduce(lambda x,y: x+'(?=.*?'+y+')', title) + '.*?', re.IGNORECASE)},
                {'performer': re.compile (reduce(lambda x,y: x+'(?=.*?'+y+')', performer) + '.*?', re.IGNORECASE)}
                ]}]},
            { 'score': { '$meta': 'textScore' } }).sort([('score', {'$meta': 'textScore'})])

async def prepare_index():
    await db.tracks.create_index([
        ("title", pymongo.TEXT),
        ("performer", pymongo.TEXT)
    ])
    await db.tracks.create_index([
        ("file_id", pymongo.ASCENDING)
    ])
    await db.users.create_index("id")
