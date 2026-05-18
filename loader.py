import ssl
import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.bot import api as bot_api

from data import config

PROXY = getattr(config, "PROXY", None)

if PROXY:
    _original_make_request = bot_api.make_request

    async def _patched_make_request(session, server, token, method, data=None, files=None, **kwargs):
        kwargs['ssl'] = False
        return await _original_make_request(session, server, token, method, data, files, **kwargs)

    bot_api.make_request = _patched_make_request

bot = Bot(token=config.BOT_TOKEN, parse_mode=types.ParseMode.HTML, proxy=PROXY)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
