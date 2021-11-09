from telethon import events
from config import bot
import telethon.sync
from FastTelethonhelper import fast_upload, fast_download
import subprocess
import asyncio
from utils import run
import os

BASE = -1001361915166
FFMPEG = -1001514731412
DESTINATION = -1001463218112
D = 1463218112
FFMPEGID = (2, 3, 4)
FFMPEGCMD = 5
Locked = True
botusername = bot.get_me().username



loop = asyncio.get_event_loop()

async def dl_ffmpeg():
    global Locked
    message = "Starting up..."
    a = await bot.send_message(BASE, "Starting up...")
    r = await bot.send_message(BASE, "Downloading ffmpeg files now.....")
    msgs = await bot.get_messages(FFMPEG, ids=FFMPEGID)
    cmd = await bot.get_messages(FFMPEG, ids=FFMPEGCMD)
    for msg in msgs:
        s = await fast_download(bot, msg, r, "")
        subprocess.call(f"chmod 777 ./{s}", shell=True)
        message = f"{message}\n{s} Downloaded" 
        await a.edit(message)     
    await r.edit(f"FFMPEG download complete, and the active command is: \n\n`{cmd.text}`")
    Locked = False


@bot.on(events.NewMessage(pattern=f"/encode@{botusername}"))
async def _(event):
    if Locked == False:
        msg = await event.get_reply_message()
        r = await event.reply("Downloading..")
        file = await fast_download(bot, msg, r, "./downloads/")
        file = file.split("/")[-1]
        print(file)
        await r.edit("Encoding........")
        cmd = await bot.get_messages(FFMPEG, ids=FFMPEGCMD)
        command = cmd.text.replace('[file]', file)
        await event.reply(command)
        o = await run(f'{command}')
        x = await event.reply(o[-2000:]) 
        res_file = await fast_upload(bot, f"./downloads/[AG] {file}", r)
        os.remove(f"./downloads/{file}")
        os.remove(f"./downloads/[AG] {file}")
        try:
            y = await bot.send_message(DESTINATION,f"./downloads/[AG] {file}", file=res_file, force_document=True)
        except:
            await event.reply(f"./downloads/[AG] {file}", file=res_file, force_document=True)
        await event.reply(f"Encoding done....\n`./downloads/[AG] {file}`\nt.me/c/{D}/{y.id}")
        await asyncio.sleep(5)
        await x.delete()

@bot.on(events.NewMessage(pattern=f"/start@{botusername}"))
async def _(event):
    await event.reply("Im Alive")


@bot.on(events.NewMessage(pattern=f"/ls@{botusername}"))
async def _(event):
    if Locked == False:
        p = subprocess.Popen(f'ls -lh downloads', stdout=subprocess.PIPE, shell=True)
        x = await event.reply(p.communicate()[0].decode("utf-8", "replace").strip())
        await asyncio.sleep(15)
        await x.delete()


@bot.on(events.NewMessage(pattern=f"/up@{botusername}"))
async def _(event):
    if Locked == False:
        path = event.raw_text.split(' ', 1)[-1]
        r = await event.reply("Uploading...")
        res_file = await fast_upload(bot, path, r)
        try:
            await bot.send_message(DESTINATION, file=res_file, force_document=True)
        except:
            await event.reply(file=res_file, force_document=True)


@bot.on(events.NewMessage(pattern=f"/del@{botusername}"))
async def _(event):
    if Locked == False:
        path = event.raw_text.split(' ', 1)[-1]
        try:
            os.remove(path)
            await event.reply("Deleted")
        except Exception as e:
            await event.reply(str(e))
        


loop.run_until_complete(dl_ffmpeg())

bot.start()

bot.run_until_disconnected()
