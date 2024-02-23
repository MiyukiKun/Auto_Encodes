import time
import asyncio
from FastTelethonhelper import fast_upload, fast_download
from config import bot
import os
import libtorrent as lt
import datetime
from config import DESTINATION
import shutil 

D = str(DESTINATION).replace("-100", "")

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

async def encode(msg, r, file, cmd, res):
    command = cmd.text.replace('[file]', file)
    if res == 1080:
        command = command.replace("-vf scale=1280:720", "-vf scale=1920:1080")
    elif res == 360:
        command = command.replace("-vf scale=1280:720", "-vf scale=640:360")
    c = await msg.reply(command)
    o = await run(f'{command}')
    x = await msg.reply(o[-2000:]) 
    res_file = await fast_upload(client = bot, file_location = f"./downloads/[AG] {file}", reply = r)
    
    os.remove(f"./downloads/[AG] {file}")
    try:
        y = await bot.send_message(DESTINATION,f"[AG] [{res}p] {file}", file=res_file, force_document=True)
    except:
        y = await msg.reply(f"[AG] [{res}p] {file}", file=res_file, force_document=True)
    await msg.reply(f"Encoding done....\n`./downloads/[AG] {file}`\nt.me/c/{D}/{y.id}")
    await asyncio.sleep(5)
    await x.delete()
    await c.delete()

async def download_torrent(link, event):
    ses = lt.session()
    ses.listen_on(6881, 6891)
    params = {
        'save_path': 'downloads',
        'storage_mode': lt.storage_mode_t(2)
    }

    handle = lt.add_magnet_uri(ses, link, params)
    ses.start_dht()

    begin = time.time()
    print(datetime.datetime.now())

    message = await bot.send_message(event.chat_id,"Downloading Metadata...")
    while (not handle.has_metadata()):
        time.sleep(1)
    await bot.edit_message(event.chat_id,message,"Got Metadata, Starting Torrent Download...")

    await bot.edit_message(event.chat_id,message,f"Starting, {handle.name()}")
    while (handle.status().state != lt.torrent_status.seeding):
        s = handle.status()
        state_str = ['queued', 'checking', 'downloading metadata', \
                'downloading', 'finished', 'seeding', 'allocating']
        size_bytes = s.total_wanted
        size_mb = size_bytes/(1024*1024)
        size_gb = size_bytes/(1024*1024*1024)
        size = size_mb
        byte = "MB"
        if size_gb > 1:
            size = size_gb
            byte = "GB"
        await bot.edit_message(event.chat_id,message,"%s \n\nSize: %.2f %s\n\n %.2f%% complete (down: %.1f kb/s up: %.1f kB/s peers: %d) %s " % \
        (handle.name(), size,byte, s.progress * 100, s.download_rate / 1000, s.upload_rate / 1000, \
        s.num_peers, state_str[s.state]))
        time.sleep(5)

    end = time.time()

    await bot.edit_message(event.chat_id,message,f"{handle.name()} COMPLETE")

    await bot.send_message(event.chat_id, f"Elapsed Time: {int((end-begin)//60)} min :{int((end-begin)%60)} sec")

    return handle.name()

def delete_files(folder):
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.removd(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))
