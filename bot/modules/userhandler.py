from . import constants
from telegram import Update
from re import match, IGNORECASE
from .dbhandler import DBHandler as dbh
from bot.helpers.filters import CustomFilters
from bot.helpers.utilities import Utilities as utils
from telegram.ext import ContextTypes, CommandHandler
from bot import application, config, db_data, mutex, LOGGER
from psycopg2.errors import UniqueViolation, UndefinedTable, StringDataRightTruncation

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    '''Greets an user when the bot is used for the first time'''
    if CustomFilters.user_filter.check_update(update):
        await update.effective_message.reply_text(constants.START_MESSAGE)
    else:
        await update.effective_message.reply_text('Oops! Not an authorized user.')
        LOGGER.info(f'UNAUTHORIZED | UID: {update.message.chat.id} | UN: {update.message.chat.username}')

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    '''Display the help message'''
    await update.effective_message.reply_markdown_v2(constants.HELPSTRING)

async def register(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    '''Register students for bot access'''
    try:
        # context.args ==> [usn, dept_name]
        context.args[0]
        if context.args[1] == 'admin':
            raise KeyError
        elif update.message.chat.id in db_data['student']:
            raise UniqueViolation
        elif (len(context.args) == 2
            and match(constants.USN_REGEX, context.args[0], IGNORECASE)):
            values = (
                update.effective_user.first_name,
                context.args[0].upper(),
                update.effective_user.id,
                db_data['department'][context.args[1].lower()]['department_id'])
            dbh.write('student', values)
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
    '''Display user profile attributes'''
    user = utils.find_role(update)
    await update.effective_message.reply_markdown(constants.PROFILE_STRING.format(
        name=update.effective_user.first_name,
        username=update.effective_user.username,
        id=update.effective_user.id,
        role=user,
        dept=utils.find_dept(user, update)))

async def unregister(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    '''Remove user details from the table and revoke bot access'''
    try:
        user = utils.find_role(update)
        # return value of delete() is ignored here as the only
        # users who can use this command are students and professors
        # and they are handled using exceptions
        dbh.delete(user, f'telegram_id = {update.effective_user.id}')
        async with mutex:
            db_data[user].remove(update.effective_user.id)
        await update.effective_message.reply_markdown('*Unregistered. Bot access revoked.*')
        LOGGER.info(f'UNREGISTER | {user.capitalize()}: {update.effective_user.id}')
    except UndefinedTable:
        await update.effective_message.reply_text('Admins cannot unregister. Contact bot manager.')

async def regprof(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    '''Undocumented command to register professors using a secret message'''
    try:
        # context.args ==> [secret_code, professor_abbr, department]
        if context.args[2] == 'admin':
            raise KeyError
        elif context.args[0] == config['PROF_SECRET']:
            values = (
                update.effective_user.first_name,
                context.args[1],
                update.effective_user.id,
                db_data['department'][context.args[2].lower()]['department_id'])
            dbh.write('professor', values)
            async with mutex:
                db_data['professor'].append(update.effective_user.id)
            await update.effective_message.reply_markdown('*Successfully registered.*')
            LOGGER.info(f'REGISTER | Professor: {update.effective_user.id} | Abbr: {context.args[1].upper()}')
        else:
            await update.effective_message.reply_text('Incorrect secret code.')
    except IndexError:
        await update.effective_message.reply_markdown(constants.REGPROF_HELPSTRING)
    except KeyError:
        await update.effective_message.reply_text('Invalid department.')
    except UniqueViolation:
        await update.effective_message.reply_text('Already registered.')
    except StringDataRightTruncation:
        await update.effective_message.reply_text('Abbreviation must be less than 4 characters.')

application.add_handler(CommandHandler('profile', profile, block=False))
application.add_handler(CommandHandler('help', help, block=False, filters=CustomFilters.user_filter))
application.add_handler(CommandHandler('start', start, block=False, filters=~CustomFilters.group_filter))
application.add_handler(CommandHandler('regprof', regprof, block=False, filters=~CustomFilters.group_filter))
application.add_handler(CommandHandler('register', register, block=False, filters=CustomFilters.group_filter))
application.add_handler(CommandHandler('unregister', unregister, block=False, filters=~CustomFilters.group_filter & CustomFilters.user_filter))
