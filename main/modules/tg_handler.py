
import asyncio
import time
import aiohttp
import requests
import aiofiles
import sys

from main.modules.compressor import compress_video

from main.modules.utils import episode_linker, get_duration, get_epnum, status_text, get_filesize, b64_to_str, str_to_b64, send_media_and_reply, get_durationx

from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from main.modules.uploader import upload_video
from main.modules.thumbnail import generate_thumbnail

import os

from main.modules.db import del_anime, save_uploads

from main.modules.downloader import downloader

from main.modules.anilist import get_anilist_data, get_anime_img, get_anime_name

from config import INDEX_USERNAME, UPLOADS_USERNAME, UPLOADS_ID, INDEX_ID, PROGRESS_ID, LINK_ID

from main import app, queue, status

from pyrogram.errors import FloodWait

from pyrogram import filters

from main.inline import button1

status: Message

async def tg_handler():

    while True:

        try:

            if len(queue) != 0:

                i = queue[0]  

                i = queue.pop(0)

                id, name, video = await start_uploading(i)

                await del_anime(i["title"])

                await save_uploads(i["title"])

                await status.edit(await status_text("Sleeping For 5 Minutes..."),reply_markup=button1)

                await asyncio.sleep(30)

            else:                

                if "Idle..." in status.text:

                    try:

                        await status.edit(await status_text("Idle..."),reply_markup=button1)

                    except:

                        pass

                await asyncio.sleep(30)

                

        except FloodWait as e:

            flood_time = int(e.x) + 5

            try:

                await status.edit(await status_text(f"Floodwait... Sleeping For {flood_time} Seconds"),reply_markup=button1)

            except:

                pass

            await asyncio.sleep(flood_time)

        except:

            pass

            

async def start_uploading(data):

    try:

        title = data["title"]
        title = title.replace("Dr. Stone - New World", "Dr Stone New World")
        title = title.replace("Opus.COLORs", "Opus COLORs")
        title = title.replace(" Isekai wa Smartphone to Tomo ni. 2", " Isekai wa Smartphone to Tomo ni 2")
        link = data["link"]
        name, ext = title.split(".")

        name += f" @animxt." + ext

        KAYO_ID = -1001159872623
        uj_id = 1159872623
        DATABASE_ID = -1001642923224
        bin_id = -1001700435443
        name = name.replace(f" @animxt.","").replace(ext,"").strip()
        id, img, tit = await get_anime_img(get_anime_name(title))
        msg = await app.send_photo(bin_id,photo=img,caption=title)
        img, caption = await get_anilist_data(title)

        print("Downloading --> ",name)
        await asyncio.sleep(5)
        await status.edit(await status_text(f"Downloading {name}"),reply_markup=button1)

        file = await downloader(msg,link,size,title)

        await msg.edit(f"Download Complete : {name}")
        print("Encoding --> ",name)

        await status.edit(await status_text(f"Encoding {name}"),reply_markup=button1)

        duration = get_duration(file)
        durationx = get_durationx(file)
        filed = os.path.basename(file)
        filed = filed.replace(filed[-14:], ".mkv")
        filed = filed.replace("【推しの子】", "")
        filed = filed.replace("(CR 1920x1080 AVC AAC MKV)", "[1080p Web-DL]")
        filed = filed.replace("[1080p]", "[1080p Web-DL]")
        filed = filed.replace("2nd Season", "S2")
        filed = filed.replace("3rd Season", "S3")
        razo = filed.replace("[1080p Web-DL]", "[720p x265] @animxt")
        fpath = "downloads/" + filed
        ghostname = name
        ghostname = ghostname.replace("(CR 1920x1080 AVC AAC MKV)", "")
        ghostname = ghostname.replace("[1080p]", "")
        ghostname = ghostname.replace("2nd Season", "S2")
        ghostname = ghostname.replace("3rd Season", "S3")
        subtitle = subtitle.replace("][", ", ")
        subtitle = subtitle.replace("[", "")
        subtitle = subtitle.replace("]", "")     
        subtitle = subtitle.replace("ENG", "English")
        subtitle = subtitle.replace("POR-BR", "Portuguese (Brazil)")
        subtitle = subtitle.replace("SPA-LA", "Spanish (Latin America)")
        subtitle = subtitle.replace("SPA", "Spanish")
        subtitle = subtitle.replace("ARA", "Arabic")
        subtitle = subtitle.replace("FRE", "French")
        subtitle = subtitle.replace("GER", "German")
        subtitle = subtitle.replace("ITA", "Italian")
        subtitle = subtitle.replace("RUS", "Russian")
        subtitle = subtitle.replace("HIN", "Hindi")
        subtitle = subtitle.replace("RUM", "Romanian")
        subtitle = subtitle.replace("FIN", "Finnish")
        subtitle = subtitle.replace("MAY", "Malaysian")
        subtitle = subtitle.replace("SWE", "Swedish")
        subtitle = subtitle.replace("GRE", "Greek")
        subtitle = subtitle.replace("HEB", "Hebrew")
        subtitle = subtitle.replace("JPN", "Japanese")
        subtitle = subtitle.replace("POL", "Polish")
        subtitle = subtitle.replace("DUT", "Dutch")
        subtitle = subtitle.replace("FIL", "Filipino")
        subtitle = subtitle.replace("CES", "Czech")
        subtitle = subtitle.replace("HRV", "Croatian")
        subtitle = subtitle.replace("HUN", "Hungarian")
        subtitle = subtitle.replace("UKR", "Ukranian")
        main = await app.send_photo(KAYO_ID,photo=img,caption=caption)
        guessname = f"**{ghostname}**" + "\n" + f"__({tit})__" + "\n" + "━━━━━━━━━━━━━━━━━━━" + "\n" + "✓  `1080p x264 Web-DL`" + "\n" + f"✓  `العربية (Saudi Arabia), Deutsch (Germany), English (US), Español (Latin America), Español (España), Français (France), हिंदी (India), Italian (Italy), Português (Brasil), Русский (Russia) ~ Subs`" + "\n" + "#Source #WebDL"
        
        thumbnail = await generate_thumbnail(id,file)

        videox = await app.send_document(

                DATABASE_ID,

            document=file,
            
            caption=guessname,

            file_name=filed,

            force_document=True,
                        
            thumb=thumbnail

            )   
        os.rename(file, fpath)
        sourcefileid = str(videox.message_id)
        source_link = f"https://telegram.me/somayukibot?start=animxt_{str_to_b64(sourcefileid)}"
        com_id = int(main.message_id) + 1
        encom_id = int(main.message_id) + 2
        comment = f"t.me/c/{uj_id}/{com_id}?thread={com_id}"
        encomment = f"t.me/c/{uj_id}/{encom_id}?thread={encom_id}"
        repl_markup=InlineKeyboardMarkup([[InlineKeyboardButton(
                                                              "🐌TG FILE", url=source_link)]])
        enrepl_markup=InlineKeyboardMarkup([[InlineKeyboardButton(
                                                              "💬Comments", url=encomment)]])
        orgtext =  "**#Source_File**" + "\n" + f"**‣ File Name: `{filed}`**" + "\n" + "**‣ Video**: `1080p x264`" + "\n" + "**‣ Audio**: `Japanese`" + "\n" + f"**‣ Subtitle**: `العربية (Saudi Arabia), Deutsch (Germany), English (US), Español (Latin America), Español (España), Français (France), हिंदी (India), Italian (Italy), Português (Brasil), Русский (Russia)`" + "\n" + f"**‣ File Size**: `{nyaasize}`" + "\n" + f"**‣ Duration**: {durationx}" + "\n" + f"**‣ Downloads**: [🔗Telegram File]({source_link})"
        await asyncio.sleep(5)
        untextx = await main.reply_text(orgtext)
        await asyncio.sleep(3)
        unitext = await untextx.edit(orgtext, reply_markup=repl_markup)
        await asyncio.sleep(5)
        sourcetext =  f"**#Encoded_File**" + "\n" + f"**‣ File Name**: `{razo}`" + "\n" + "**‣ Video**: `720p HEVC x265 10Bit`" + "\n" + "**‣ Audio**: `Japanese`" + "\n" + f"**‣ Subtitle**: `العربية (Saudi Arabia), Deutsch (Germany), English (US), Español (Latin America), Español (España), Français (France), हिंदी (India), Italian (Italy), Português (Brasil), Русский (Russia)`"
        untext = await main.reply_text(sourcetext)
        await asyncio.sleep(2)
        await app.send_sticker(KAYO_ID,"CAACAgUAAxkBAAEU_9FkRrLoli952oqIMVFPftW12xYLRwACGgADQ3PJEsT69_t2KrvBLwQ")
        os.rename(fpath,"video.mkv")
        await asyncio.sleep(5)
        compressed = await compress_video(duration,untext,name,sourcetext)
        
        dingdong = await untext.edit(sourcetext)


        if compressed == "None" or compressed == None:

            print("Encoding Failed Uploading The Original File")

            os.rename("video.mkv",fpath)

        else:

            os.rename("out.mkv",fpath)
  
        print("Uploading --> ",name)

        await status.edit(await status_text(f"Uploading {name }"),reply_markup=button1)
        video = await upload_video(msg,fpath,id,tit,name,size,sourcetext,untext) 
        try:

            os.remove("video.mkv")

            os.remove("out.mkv")

            os.remove(file)

            os.remove(fpath)

        except:

            pass     

    except FloodWait as e:

        flood_time = int(e.x) + 5

        try:

            await status.edit(await status_text(f"Floodwait... Sleeping For {flood_time} Seconds"),reply_markup=button1)

        except:

            pass

        await asyncio.sleep(flood_time)

    return  id, name, video
