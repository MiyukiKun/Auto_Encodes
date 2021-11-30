import asyncio
from config import bot
import os
import time
import datetime as dt
from FastTelethon import download_file, upload_file

DESTINATION = -1001463218112
D = 1463218112


class Timer:
    def __init__(self, time_between=5):
        self.start_time = time.time()
        self.time_between = time_between

    def can_send(self):
        if time.time() > (self.start_time + self.time_between):
            self.start_time = time.time()
            return True
        return False

def human_readable_size(size, decimal_places=2):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB', 'PB']:
        if size < 1024.0 or unit == 'PB':
            break
        size /= 1024.0
    return f"{size:.{decimal_places}f} {unit}"

def progress_bar_str(done, total):
    percent = round(done/total*100, 2)
    final = f"Percent: {percent}%\n{human_readable_size(done)}/{human_readable_size(total)}"
    return final 

async def run(cmd):
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE)

    stdout, stderr = await proc.communicate()

    print(f'[{cmd!r} exited with {proc.returncode}]')
    if stdout:
        return f'[stdout]\n{stdout.decode()}'
    if stderr:
        return f'[stderr]\n{stderr.decode()}'

async def encode(msg, cmd):
    r = await msg.reply("Downloading..")
    file = await fast_download(client = bot, msg =  msg, reply = r)
    file = file.split("/")[-1]
    print(file)
    await r.edit("Encoding........")
    command = cmd.text.replace('[file]', file)
    await msg.reply(command)
    o = await run(f'{command}')
    x = await msg.reply(o[-2000:]) 
    res_file = await fast_upload(client = bot, file_location = f"./downloads/[AG] {file}", reply = r)
    os.remove(f"./downloads/{file}")
    os.remove(f"./downloads/[AG] {file}")
    try:
        y = await bot.send_message(DESTINATION,f"./downloads/[AG] {file}", file=res_file, force_document=True)
    except:
        y = await msg.reply(f"./downloads/[AG] {file}", file=res_file, force_document=True)
    await msg.reply(f"Encoding done....\n`./downloads/[AG] {file}`\nt.me/c/{D}/{y.id}")
    await asyncio.sleep(5)
    await x.delete()


async def fast_download(client, msg, reply, progress_bar_function = progress_bar_str):
    timer = Timer()

    async def progress_bar(downloaded_bytes, total_bytes):
        if timer.can_send():
            data = progress_bar_function(downloaded_bytes, total_bytes)
            await reply.edit(f"Downloading...\n{data}")

    file = msg.document
    filename = msg.file.name
    dir = "downloads/"

    try:
        os.mkdir("downloads/")
    except:
        pass

    if not filename:
        filename = (
            "video_" + dt.now().isoformat("_", "seconds") + ".mp4"
                    )
                    
    download_location = dir + filename

    with open(download_location, "wb") as f:
        if reply != None:
            await download_file(
                client=client, 
                location=file, 
                out=f,
                progress_callback=progress_bar
            )
        else:
            await download_file(
                client=client, 
                location=file, 
                out=f,
            )
    await reply.edit("Finished downloading")
    return download_location


async def fast_upload(client, file_location, reply, progress_bar_function = progress_bar_str):
    timer = Timer()
    name = file_location.split("/")[-1]
    async def progress_bar(downloaded_bytes, total_bytes):
        if timer.can_send():
            data = progress_bar_function(downloaded_bytes, total_bytes)
            await reply.edit(f"Uploading...\n{data}")
    
    with open(file_location, "rb") as f:
        the_file = await upload_file(
            client=client,
            file=f,
            name=name,
        )
        
    await reply.edit("Finished uploading")
    return the_file