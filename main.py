from telethon import events
from config import bot, bot_username, BASE, FFMPEG, FFMPEGCMD, FFMPEGID, DESTINATION
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
            name = event.raw_text.split(" ")
            if len(name) == 1:
                name = None
            else:
                name = name[-1]
            msg = await event.get_reply_message()
            cmd = await bot.get_messages(FFMPEG, ids=FFMPEGCMD)
            if '-1080' in event.text:
                res = 1080
            elif '-720' in event.text:
                res = 720
            elif '-360' in event.text:
                res = 360
            r = await msg.reply("Downloading...")
            file = await fast_download(client = bot, msg = msg, reply = r, download_folder = "./downloads/")
            pfile = file.split("/")[-1]
            await utils.encode(msg, r, pfile, cmd, res, name)
            os.remove(file)
            await r.delete()
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
        name_format = event.raw_text.split(" ")[1]
        start_ep = int(event.raw_text.split(" ")[2])
        for i in queue:
            try:
                msg = await bot.get_messages(event.chat_id, ids=i)
                cmd = await bot.get_messages(FFMPEG, ids=FFMPEGCMD)
                r = await msg.reply("Downloading...")
                file = await fast_download(client = bot, msg = msg, reply = r, download_folder = "./downloads/")
                pfile = file.split("/")[-1]
                name = name_format.replace("UwU", str(start_ep))
                await utils.encode(msg, r, pfile, cmd, 360, name.replace("RES", "360p")
                await utils.encode(msg, r, pfile, cmd, 720, name.replace("RES", "720p")
                await utils.encode(msg, r, pfile, cmd, 1080 name.replace("RES", "1080p")
                os.remove(file)
                await r.delete()
            except Exception as e:
                await event.reply(f"[{i}] skipped due to error\n\n{e}")
        queue = []
        await event.reply("Queue cleared.")
        Locked = False


@bot.on(events.NewMessage(pattern=f"/download{bot_username}"))
async def _(event):
    data = event.text.split(" ")
    if "magnet" in data[1] or "torrent" in data[1]:
        r = await event.reply("Downloading...")
        f = await utils.download_torrent(data[1], r)
        for root, subdirectories, files in os.walk('./downloads'):
            for file in files:
                f = os.path.join(root, file)
                file = await fast_upload(bot, f, r)
                await bot.send_message(event.chat_id, f, file=file, force_document= True)
        utils.delete_files('downloads')
        await r.delete()


@bot.on(events.NewMessage(pattern=(f"/sthumb{bot_username}")))
async def thumb(event):
    x = await event.get_reply_message()
    thumb = await bot.download_media(x.photo)
    with open(thumb, "rb") as f:
        pic = f.read()
    with open("thumb.png", "wb") as f:
        f.write(pic)
    await event.reply("Set as default thumbnail")


@bot.on(events.NewMessage(pattern=(f"/cthumb{bot_username}")))
async def clear_thumb(event):
    with open("thumb.png", "w") as f:
        f.write("")
    await event.reply("cleared thumbnail")


@bot.on(events.NewMessage(pattern=(f"/vthumb{bot_username}")))
async def view(event):
    try:
        await event.reply("current default thumbnail", file="thumb.png")
    except:
        await event.reply("No default thumbnail set")



loop.run_until_complete(dl_ffmpeg())

bot.start()

bot.run_until_disconnected()
