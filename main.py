from telethon import events
from config import bot
from FastTelethonhelper import Timer, fast_upload, fast_download, Timer
import subprocess
import asyncio

BASE = -1001361915166
FFMPEG = -1001514731412
FFMPEGID = (2, 3, 4)
FFMPEGCMD = 5
Locked = True

loop = asyncio.get_event_loop()

async def dl_ffmpeg():
    global CMD
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


@bot.on(events.NewMessage(pattern="/encode"))
async def _(event):
    if Locked == False:
        msg = await event.get_reply_message()
        r = await event.reply("Downloading..")
        file = await fast_download(bot, msg, r, "")
        await r.edit("Encoding........")
        cmd = await bot.get_messages(FFMPEG, ids=FFMPEGCMD)
        command = cmd.text.replace('[file]', file)
        p = subprocess.Popen(f'./{command}', stdout=subprocess.PIPE, shell=True)
        timer = Timer(time_between=20)
        while True:
            line = p.stdout.readline()
            if not line:
                break
            if timer.can_send():
                line = line.decode('utf-8')
                print(line)
                await r.edit(line)

        res_file = await fast_upload(bot, f"[AG] {file}", r)
        await event.reply(file=res_file, force_document=True)
    

@bot.on(events.NewMessage(pattern="/start"))
async def _(event):
    await event.reply("Im Alive")


@bot.on(events.NewMessage(pattern="/ls"))
async def _(event):
    p = subprocess.Popen(f'ls -lh .', stdout=subprocess.PIPE, shell=True)
    asyncio.sleep(1)
    await event.reply(p.stdout.decode("utf-8", "replace").strip())
    



loop.run_until_complete(dl_ffmpeg())

bot.start()

bot.run_until_disconnected()



