from environs import Env

env = Env()
env.read_env()

BOT_TOKEN = env.str("BOT_TOKEN")
ADMINS = env.list("ADMINS")
IP = env.str("ip")
PORT = env.int("PORT", default=8006)
WEBHOOK_HOST = env.str("WEBHOOK_HOST", default=None)
PROXY = env.str("PROXY", default=None)