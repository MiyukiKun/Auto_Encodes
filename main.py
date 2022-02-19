from telethon import events
from config import app, bot, bot_username, BASE, FFMPEG, FFMPEGCMD, FFMPEGID, DESTINATION
from FastTelethonhelper import fast_upload, fast_download
import subprocess
import asyncio
import utils
import os

Locked = True
queue = []


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


@bot.on(events.NewMessage(pattern=f"/encode{bot_username}"))
async def _(event):
    global Locked
    if Locked == False:
        Locked = True
        try:
            msg = await event.get_reply_message()
            cmd = await bot.get_messages(FFMPEG, ids=FFMPEGCMD)
            e1080 = False
            if '-1080' in event.text:
                e1080 = True
            await utils.encode(msg, cmd, e1080)
        except:
            pass
        Locked = False

@bot.on(events.NewMessage(pattern=f"/start{bot_username}"))
async def _(event):
    await event.reply("Im Alive")


@bot.on(events.NewMessage(pattern=f"/ls{bot_username}"))
async def _(event):
    p = subprocess.Popen(f'ls -lh downloads', stdout=subprocess.PIPE, shell=True)
    x = await event.reply(p.communicate()[0].decode("utf-8", "replace").strip())
    await asyncio.sleep(15)
    await x.delete()


@bot.on(events.NewMessage(pattern=f"/up{bot_username}"))
async def _(event):
    path = event.raw_text.split(' ', 1)[-1]
    r = await event.reply("Uploading...")
    res_file = await fast_upload(bot, path, r)
    try:
        await bot.send_message(DESTINATION, file=res_file, force_document=True)
    except:
        await event.reply(file=res_file, force_document=True)


@bot.on(events.NewMessage(pattern=f"/del{bot_username}"))
async def _(event):
    path = event.raw_text.split(' ', 1)[-1]
    try:
        os.remove(path)
        await event.reply("Deleted")
    except Exception as e:
        await event.reply(str(e))


@bot.on(events.NewMessage(pattern=f"/addq{bot_username}"))
async def _(event):
    global Locked
    if Locked == True:
        await event.reply("Cant update queue when encode is in progress.")
        return
    msg = await event.get_reply_message()
    queue.append(msg.id)

    await event.reply(f"Added to Queue \nQueue: {queue}")


@bot.on(events.NewMessage(pattern=f"/aq{bot_username}"))
async def _(event):
    args =  event.raw_text.split(" ")
    msg = await event.get_reply_message()
    if len(args) == 1:
        args.append(5)
    for i in range(msg.id, msg.id+int(args[1])):
            queue.append(i)

    await event.reply(f"Added to Queue \nQueue: {queue}")


@bot.on(events.NewMessage(pattern=f"/clearq{bot_username}"))
async def _(event):
    global Locked
    if Locked == True:
        await event.reply("Cant update queue when encode is in progress.")
        return
    global queue
    queue = []
    await event.reply(f"Cleared")


@bot.on(events.NewMessage(pattern=f"/sq{bot_username}"))
async def _(event):
    global Locked
    if Locked == False:
        global queue
        Locked = True
        for i in queue:
            try:
                msg = await bot.get_messages(event.chat_id, ids=i)
                cmd = await bot.get_messages(FFMPEG, ids=FFMPEGCMD)
                await utils.encode(msg, cmd)
            except Exception as e:
                await event.reply(f"[{i}] skipped due to error\n\n{e}")
        queue = []
        await event.reply("Queue cleared.")
        Locked = False            


@bot.on(events.NewMessage(pattern=f"/restart{bot_username}"))
async def _(event):
    try:
        app.restart()
    except Exception as e:
        await event.reply(e)



loop.run_until_complete(dl_ffmpeg())

bot.start()

bot.run_until_disconnected()
