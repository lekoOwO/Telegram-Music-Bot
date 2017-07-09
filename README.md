# Telegram Music Bot

[![LAUNCH ON OpenShift](http://launch-shifter.rhcloud.com/launch/light/LAUNCH%20ON.svg)](https://openshift.redhat.com/app/console/application_type/custom?&cartridges[]=python-3.5&initial_git_url=https://github.com/rexx0520/Telegram-Music-Bot&name=Telegram%20Music%20Bot)

## Description

This is a Telegram music catalog bot.
Was originated and  improved from [szastupov/musicbot](//github.com/szastupov/musicbot) .



## Usage

Simply type in keywords to search from the database.

Simply send music files to add to the database.

Command  `/help`  for help.

`type:TYPE` after keywords to restrict the type of result.


>```Xiaoan type:flac```
>
>```Xiaoan type:mp3``` ( `mp3` was converted to `mpeg` in bot since mp3 is not a mime-type.)
> 
>```Xiaoan type:mpeg```

Seperate the artist and song by `>` .


>```Xiaoan>The song of early-spring```

It also works great with `type`.


>```Xiaoan>The song of early-spring type:flac```

Command  `/stats`  for the status of bot.

Command `/music`  to send music files from this bot in a group chat.


>```/music Xiaoan```

Songs which was uploaded to the music channel will be sync to the database.



## Environment Variables

**API_TOKEN** : Bot's API Token.

**BOT_NAME** : Bot's name.


**CHANNEL** : Music channel's ID.

**CHANNEL_NAME** : Music channel's name.

**LOGCHN_ID** : log channel's chat ID. (with `-`)


**REST_PORT** : REST API's port. Usually `8080`.

**REST_HOST** : REST API's host. Usually `0.0.0.0`.


**MONGO_HOST** : MongoDB 's URL.

e.g. :  `mongodb://user:pwd@host/python`

**MONGO_DB_NAME** : MongoDB Database's name.
