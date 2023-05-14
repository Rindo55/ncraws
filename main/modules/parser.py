import asyncio
from main.modules.schedule import update_schedule
from main.modules.usschedule import update_schedulex
from main.modules.utils import status_text
from main import status
from main.modules.db import get_animesdb, get_uploads, save_animedb
import feedparser
from main import queue
from main.inline import button1

def trim_title(title: str):
    title = title.rsplit(' ', 1)[0]
    title = title.replace("【推しの子】 鬼滅之刃 刀匠村篇 / ", "")
    title = title.replace("Dr. Stone - New World", "Dr Stone New World")
    title = title.replace("Opus.COLORs", "Opus COLORs")
    title = title.replace("Ousama Ranking - Yuuki no Takarabako", "Ousama Ranking Yuuki no Takarabako")
    title = title.replace(" Isekai wa Smartphone to Tomo ni. 2", " Isekai wa Smartphone to Tomo ni 2")
    title = title.replace("Kimetsu no Yaiba: Katanakaji no Sato-hen - 06 (CR 1920x1080 AVC AAC MKV)", "Demon Slayer Kimetsu No Yaiba To the Swordsmith Village - 06")
    ext = ".mkv"
    title = title + ext
    return title
def trim_link(link: str):
    link = link.replace("https://ouo.si/download/", "")
    return link
def parse():
    a = feedparser.parse("https://ouo.si/feed?q=kimetsu")
    b = a["entries"]
    b = b[0:1]
    data = []    

    for i in b:
        item = {}
        item['title'] = trim_title(i['title'])  
        item['link'] = "magnet:?xt=urn:btih:" + trim_link(i['link'])
        data.append(item)
    data.reverse()
    return data

async def auto_parser():
    while True:
        try:
            await status.edit(await status_text("Parsing Rss, Fetching Magnet Links..."),reply_markup=button1)
        except:
            pass

        rss = parse()
        data = await get_animesdb()
        uploaded = await get_uploads()

        saved_anime = []
        for i in data:
            saved_anime.append(i["name"])

        uanimes = []
        for i in uploaded:
            uanimes.append(i["name"])
        
        for i in rss:
            if i["title"] not in uanimes and i["title"] not in saved_anime:
                if ".mkv" in i["title"] or ".mp4" in i["title"]:
                    title = i["title"]
                    await save_animedb(title,i)

        data = await get_animesdb()
        for i in data:
            if i["data"] not in queue:
                queue.append(i["data"])    
                print("Saved ", i["name"])   

        try:
            await status.edit(await status_text("Idle..."),reply_markup=button1)
            await update_schedule()
            await asyncio.sleep(6)
            await update_schedulex()
        except:
            pass

        await asyncio.sleep(30)
