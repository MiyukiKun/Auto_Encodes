import os
import dotenv
from telethon import TelegramClient

dotenv.load_dotenv('.env')

api_id = os.environ.get('API_ID')
api_hash = os.environ.get('API_HASH')
bot_token = os.environ.get('BOT_TOKEN')
bot_username = os.environ.get('BOT_USERNAME')

BASE = os.environ.get('BASE')
if not BASE:
    from sample_config import BASE as b
    BASE = b

FFMPEG = os.environ.get('FFMPEG')
if not FFMPEG:
    from sample_config import FFMPEG as f
    FFMPEG = int(f)

DESTINATION = os.environ.get('DESTINATION')
if not DESTINATION:
    from sample_config import DESTINATION as d
    DESTINATION = int(d)

FFMPEGID = os.environ.get('FFMPEGID')
if not FFMPEGID:
    from sample_config import FFMPEGID as f
    FFMPEGID = f

FFMPEGID = FFMPEGID.split()
for i in range(len(FFMPEGID)):
    FFMPEGID[i] = int(FFMPEGID[i])


FFMPEGCMD = os.environ.get('FFMPEGCMD')
if not FFMPEGCMD:
    from sample_config import FFMPEGCMD as c
    FFMPEGCMD = int(c)

BASE = int(BASE)
FFMPEG = int(FFMPEG)
FFMPEGCMD = int(FFMPEGCMD)
DESTINATION = int(DESTINATION)

bot = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)
