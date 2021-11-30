import asyncio
from FastTelethonhelper import fast_upload, fast_download
from config import bot
import os
DESTINATION = -1001463218112


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
    file = await fast_download(bot, msg, r, "./downloads/")
    file = file.split("/")[-1]
    print(file)
    await r.edit("Encoding........")
    command = cmd.text.replace('[file]', file)
    await msg.reply(command)
    o = await run(f'{command}')
    x = await msg.reply(o[-2000:]) 
    res_file = await fast_upload(bot, f"./downloads/[AG] {file}", r)
    os.remove(f"./downloads/{file}")
    os.remove(f"./downloads/[AG] {file}")
    try:
        await bot.send_message(DESTINATION,f"./downloads/[AG] {file}", file=res_file, force_document=True)
    except:
        await msg.reply(f"./downloads/[AG] {file}", file=res_file, force_document=True)
    await asyncio.sleep(5)
    await x.delete()
