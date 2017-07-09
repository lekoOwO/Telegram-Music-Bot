# Telegram 音樂 bot

[![部屬到 OpenShift](http://launch-shifter.rhcloud.com/launch/light/部屬到.svg)](https://openshift.redhat.com/app/console/application_type/custom?&cartridges[]=python-3.5&initial_git_url=https://github.com/rexx0520/Telegram-Music-Bot&name=Telegram%20Music%20Bot)

## 簡介

這是一個 Telegram 的 音樂 Bot

由 [szastupov/musicbot](//github.com/szastupov/musicbot) 改進而成。



## 用法

輸入關鍵字來搜尋音樂資料庫，傳送音樂檔案以增加至資料庫。

輸入 `/help` 來獲取說明

在關鍵字後輸入`type:TYPE`來限定音樂格式，像這樣:


>```棒棒勝 type:flac```
>
>```棒棒勝 type:mp3```
>
>```棒棒勝 type:mpeg```

若同時想搜尋作者和曲名，請用 `>` 隔開 (預設為作者、曲名都納入搜尋)，像這樣:


>```棒棒勝>洨安之歌```

也可以搭配`type`指令，像這樣:


>```棒棒勝>洨安之歌 type:flac```

輸入 `/stats` 來獲取 bot 資訊。

用 `/music` 指令來在群聊內使用棒棒勝 Music Bot，像這樣:


>```/music 棒棒勝```

丟進音樂頻道的歌曲將會被同步至資料庫。



## 環境變數

**API_TOKEN** : Bot 的 API Token

**BOT_NAME** : Bot 的名字


**CHANNEL** : 音樂頻道 ID

**CHANNEL_NAME** : 音樂頻道的名字

**LOGCHN_ID** : log 頻道的 chat ID (記得帶負號)


**REST_PORT** : REST API 的埠

**REST_HOST** : REST API 的主機IP，通常是 `0.0.0.0`


**MONGO_HOST** : MongoDB 的網址

例如 : `mongodb://user:pwd@host/python`

**MONGO_DB_NAME** : MongoDB 資料庫的名字
