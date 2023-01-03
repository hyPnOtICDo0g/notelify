from . import constants
from telegram import Update
from re import match, IGNORECASE
from .dbhandler import DBHandler as dbh
from bot.helpers.filters import CustomFilters
from bot import application, db_data, mutex, LOGGER
from bot.helpers.utilities import Utilities as utils
from telegram.ext import ContextTypes, CommandHandler
from psycopg2.errors import UniqueViolation, UndefinedTable

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    '''PLACEHOLDER'''
    if CustomFilters.user_filter.check_update(update):
        await update.effective_message.reply_text(constants.START_MESSAGE)
    else:
        await update.effective_message.reply_text('Oops! Not an authorized user.')
        LOGGER.info(f'UNAUTHORIZED | UID: {update.message.chat.id} | UN: {update.message.chat.username}')

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    '''PLACEHOLDER'''
    await update.effective_message.reply_markdown_v2(constants.HELPSTRING)

async def register(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    '''PLACEHOLDER'''
    try:
        # context.args ==> [usn, dept_name]
        context.args[0]
        if update.message.chat.id in db_data['student']:
            raise UniqueViolation
        elif len(context.args) == 2 \
            and match('^\d[a-z]{2}\d{2}[a-z]{2}\d{3}$', context.args[0], IGNORECASE):
            values = (
                update.effective_user.first_name,
                context.args[0].upper(),
                update.effective_user.id,
                db_data['department'][context.args[1]]['department_id'])
            dbh().write('student', values)
            async with mutex:
                db_data['student'].append(update.effective_user.id)
            LOGGER.info(f'REGISTER | Student: {update.effective_user.id} | USN: {context.args[0].upper()}')
            await update.effective_message.reply_markdown(
                constants.REG_MESSAGE.format(
                    first=update.effective_user.first_name,
                    id=update.effective_user.id,
                    bot=context.bot.username))
        else:
            raise KeyError
    except UniqueViolation:
        await update.effective_message.reply_text('Already registered.')
    except KeyError:
        await update.effective_message.reply_text('Incorrect format, try again.')
    except IndexError:
        await update.effective_message.reply_markdown(constants.REG_HELPSTRING)

async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    '''PLACEHOLDER'''
    user = utils.find_role(update)
    await update.effective_message.reply_markdown(constants.PROFILE_STRING.format(
        name=update.effective_user.first_name,
        username=update.effective_user.username,
        id=update.effective_user.id,
        role=user,
        dept=utils.find_dept(user, update)))

async def unregister(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    '''PLACEHOLDER'''
    try:
        user = utils.find_role(update)
        # return value of delete() is ignored here as the only
        # users who can use this command are students and professors
        # and they are handled using exceptions
        dbh().delete(user, f'telegram_id = {update.effective_user.id}')
        async with mutex:
            db_data[user].remove(update.effective_user.id)
        await update.effective_message.reply_markdown('*Unregistered. Bot access revoked.*')
        LOGGER.info(f'UNREGISTER | {user.capitalize()}: {update.effective_user.id}')
    except UndefinedTable:
        await update.effective_message.reply_text('Admins cannot unregister. Contact bot manager.')

application.add_handler(CommandHandler('profile', profile, block=False))
application.add_handler(CommandHandler('help', help, block=False, filters=CustomFilters.user_filter))
application.add_handler(CommandHandler('start', start, block=False, filters=~CustomFilters.group_filter))
application.add_handler(CommandHandler('register', register, block=False, filters=CustomFilters.group_filter))
application.add_handler(CommandHandler('unregister', unregister, block=False, filters=~CustomFilters.group_filter & CustomFilters.user_filter))
