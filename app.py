from aiogram import executor

from loader import dp, bot
import middlewares, filters, handlers
from utils.notify_admins import on_startup_notify
from utils.set_bot_commands import set_default_commands
from utils.db_api.database import create_tables
from data import config

WEBHOOK_PATH = f"/bot/{config.BOT_TOKEN}"


async def on_startup(dispatcher):
    create_tables()
    await set_default_commands(dispatcher)
    await on_startup_notify(dispatcher)
    if config.WEBHOOK_HOST:
        webhook_url = f"{config.WEBHOOK_HOST}{WEBHOOK_PATH}"
        await bot.set_webhook(webhook_url)


async def on_shutdown(dispatcher):
    if config.WEBHOOK_HOST:
        await bot.delete_webhook()
    await dispatcher.storage.close()
    await dispatcher.storage.wait_closed()


if __name__ == '__main__':
    if config.WEBHOOK_HOST:
        executor.start_webhook(
            dispatcher=dp,
            webhook_path=WEBHOOK_PATH,
            on_startup=on_startup,
            on_shutdown=on_shutdown,
            host=config.IP,
            port=config.PORT,
        )
    else:
        executor.start_polling(dp, on_startup=on_startup)
