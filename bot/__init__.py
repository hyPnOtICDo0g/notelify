from json import load
from os import environ
from asyncio import Lock
from .modules import constants
from sys import exit as exitnow
from dotenv import dotenv_values
from logging import basicConfig, getLogger, INFO
from telegram.ext import Application, ApplicationBuilder

# bot commands
async def post_init(application: Application) -> None:
    '''Callback function to set bot commands after bot initialization'''
    await application.bot.set_my_commands(constants.BOTCOMMANDS)

# a mutex lock to access shared states
mutex = Lock()

# logging
basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=INFO
)
LOGGER = getLogger(__name__)

# maintain a dict for quick validation checks
db_data = {
    'admin': [],
    'student': [],
    'professor': [],
    'department': {},
    'subject': {}
}

try:
    # department data
    with open('dept.json') as fp:
        x = load(fp)
    db_data['department'] = x['department']
    db_data['subject'] = x['subject']
    # env variables
    config = {
        **dotenv_values('.env'),
        **environ
    }
    if not all(bool(config[x]) is not False for x in constants.ENV_VARS):
        raise KeyError
except (FileNotFoundError, ValueError, KeyError):
    LOGGER.critical('JSON file or env variables are missing or corrupt! Exiting.')
    exitnow(1)

application = (
    ApplicationBuilder()
    .token(config['BOT_TOKEN'])
    .concurrent_updates(True)
    .post_init(post_init)
    .build()
)
