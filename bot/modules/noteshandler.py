from . import constants
from telegram import Update
from .dbhandler import DBHandler as dbh
from bot.helpers.filters import CustomFilters
from bot.helpers.utilities import Utilities as utils
from bot import application, config, db_data, LOGGER
from telegram.ext import ContextTypes, CommandHandler

class NotesHandler:
    @staticmethod
    async def view(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        '''PLACEHOLDER'''
        res = dbh().fetch(
                'file_name, message_id, subject_abbr, module_no',
                'notes',
                f'professor_tgid = {update.effective_user.id}')
        if res:
            await update.effective_message.reply_markdown('\n'.join(
                [constants.VIEW_STRING.format(
                    file=file_name,
                    group_id=config['CHANNEL_ID'][4:],
                    id=message_id,
                    subject=subject_abbr,
                    module=module_no
                ) for file_name, message_id, subject_abbr, module_no in res]))
        else:
            await update.effective_message.reply_text('Nothing uploaded.')

    @staticmethod
    async def add(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        '''PLACEHOLDER'''
        # set of sanity checks below, exceptions are caught on failure
        try:
            # check if a subject is valid
            subject_name = db_data['subject'][context.args[1].upper()]
            # check if the module number is an integer
            module_no = int(context.args[2])
            # check if the replied message is a document
            file_name = update.message.reply_to_message.document.file_name
            # if all checks pass, forward the document to the channel
            forwarded_message_id = await utils.forwardMessage(update, context, config['CHANNEL_ID'])
            # build value tuple
            values = (
                file_name,
                subject_name,
                context.args[1].upper(),
                module_no,
                update.effective_user.id,
                utils.find_dept('professor', update),
                forwarded_message_id.message_id)
            # add the notes' details to DB
            dbh().write(
                'notes (file_name, subject_name, subject_abbr, module_no, professor_tgid, department, message_id)',
                values)
            LOGGER.info(f'NOTES - ADD | Professor: {update.effective_user.id} | Notes: {file_name}')
        except IndexError:
            await update.effective_message.reply_text('PLACEHOLDER - ADD HELP')
        except KeyError:
            await update.effective_message.reply_text('Invalid subject, it does not exist.')
        except ValueError:
            await update.effective_message.reply_text('Invalid module number. Pass integer arguments only.')
        else:
            await update.effective_message.reply_markdown('*Successfully added notes to database.*')

    @staticmethod
    async def remove(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        '''PLACEHOLDER'''
        # this function won't delete the notes from the channel
        # due to the 48hr message age limit imposed on the telegram bot API
        try:
            # check if the message ID is an integer
            message_id = int(context.args[1])
            # return value of delete() indicates whether a record was deleted or not
            res = dbh().delete('notes', f'professor_tgid = {update.effective_user.id} AND message_id = {message_id}')
            if res:
                await update.effective_message.reply_markdown('*Successfully removed notes from database.*')
                LOGGER.info(f'NOTES - REMOVE | Professor: {update.effective_user.id} | ID: {message_id}')
            else:
                raise ValueError
        except IndexError:
            await update.effective_message.reply_markdown('PLACEHOLDER - REMOVE HELP')

    @staticmethod
    async def replace(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        try:
            # check if the message ID is an integer
            message_id = int(context.args[1])
            # check if message is a document
            update.message.reply_to_message.document.file_name
            # check if the message_id exists in the database
            res = dbh().fetch(
                'message_id', 'notes',
                f'professor_tgid = {update.effective_user.id} AND message_id = {message_id}')
            if res:
                # forward new notes if the message_id is found
                forwarded_message_id = await utils.forwardMessage(update, context, config['CHANNEL_ID'])
                # update database with new message_id
                dbh().update(
                    'notes',
                    f'message_id = {forwarded_message_id.message_id}',
                    f'professor_tgid = {update.effective_user.id} AND message_id = {context.args[1]}')
                await update.effective_message.reply_markdown('*Successfully replaced notes.*')
                LOGGER.info(f'NOTES - REPLACE | Professor: {update.effective_user.id} | OLD ID: {message_id}')
            else:
                raise ValueError
        except IndexError:
            await update.effective_message.reply_markdown('PLACEHOLDER - REPLACE HELP')

async def notes(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    '''PLACEHOLDER'''
    try:
        match context.args[0]:
            case 'view':
                await NotesHandler.view(update, context)
            case 'add':
                # context.args ==> [function, subject_abbr, module_no]
                await NotesHandler.add(update, context)
            case 'remove':
                # context.args ==> [message_id]
                await NotesHandler.remove(update, context)
            case 'replace':
                # context.args ==> [message_id]
                await NotesHandler.replace(update, context)
            case _:
                await update.effective_message.reply_text('Invalid Method.')
    except IndexError:
        await update.effective_message.reply_markdown('PLACEHOLDER - NOTES HELP')
    # common exceptions handled below
    except ValueError:
        await update.effective_message.reply_text('Invalid ID, Try again.')
    except AttributeError:
        await update.effective_message.reply_text('Document not found, Try again.')

application.add_handler(CommandHandler('notes', notes, block=False, filters=CustomFilters.professor_filter))
