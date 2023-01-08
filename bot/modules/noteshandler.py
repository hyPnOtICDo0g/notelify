from . import constants
from telegram import Update
from time import perf_counter
from telegram.error import BadRequest
from .dbhandler import DBHandler as dbh
from bot.helpers.filters import CustomFilters
from bot.helpers.utilities import Utilities as utils
from bot import application, config, db_data, LOGGER
from telegram.ext import ContextTypes, CommandHandler
from psycopg2.errors import SyntaxError, NumericValueOutOfRange

class NotesHandler:
    @staticmethod
    async def view(update: Update) -> None:
        '''Display notes uploaded by a professor'''
        res = dbh.fetch(
                'file_name, message_id, subject_abbr, module_no, total_requests',
                'notes',
                f'professor_tgid = {update.effective_user.id}')
        if res:
            await update.effective_message.reply_markdown(utils.build_view(res))
        else:
            await update.effective_message.reply_text('Nothing uploaded.')

    @staticmethod
    async def add(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        '''Validate and add notes to the table'''
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
            user = utils.find_role(update)
            # build value tuple
            values = (
                file_name,
                subject_name,
                context.args[1].upper(),
                module_no,
                update.effective_user.id,
                utils.find_dept(user, update),
                forwarded_message_id.message_id)
            # add the notes' details to DB
            dbh.write('notes', values)
            LOGGER.info(f'NOTES - ADD | Professor: {update.effective_user.id} | Notes: {file_name}')
        except IndexError:
            await update.effective_message.reply_markdown(constants.NOTES_ADD_HELPSTRING)
        except KeyError:
            await update.effective_message.reply_text('Invalid subject, it does not exist.')
        except (ValueError, NumericValueOutOfRange):
            await update.effective_message.reply_text('Invalid module number.')
        else:
            await update.effective_message.reply_markdown('*Successfully added notes to database.*')

    @staticmethod
    async def remove(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        '''Validate and delete notes from the table'''
        try:
            # check if the message ID is an integer
            message_id = int(context.args[1])
            # return value of delete() indicates whether a record was deleted or not
            res = dbh.delete('notes', f'professor_tgid = {update.effective_user.id} AND message_id = {message_id}')
            if res:
                # this function will try to delete the notes from the channel
                # but if the message is older than 48hrs the message cannot be deleted
                # by the bot due to the restrictions imposed on the telegram bot API
                await context.bot.delete_message(chat_id=int(config['CHANNEL_ID']), message_id=message_id)
                await update.effective_message.reply_markdown('*Successfully removed notes from database.*')
                LOGGER.info(f'NOTES - REMOVE | Professor: {update.effective_user.id} | ID: {message_id}')
            else:
                raise ValueError
        except IndexError:
            await update.effective_message.reply_markdown(constants.NOTES_REMOVE_HELPSTRING)

    @staticmethod
    async def replace(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        '''Validate and update existing notes in the table'''
        try:
            # check if the message ID is an integer
            message_id = int(context.args[1])
            # check if message is a document
            file_name = update.message.reply_to_message.document.file_name
            # check if the message_id exists in the table
            res = dbh.fetch(
                'message_id', 'notes',
                f'professor_tgid = {update.effective_user.id} AND message_id = {message_id}')
            if res:
                # forward new notes if the message_id is found
                forwarded_message_id = await utils.forwardMessage(update, context, config['CHANNEL_ID'])
                # delete old notes in the channel
                await context.bot.delete_message(chat_id=int(config['CHANNEL_ID']), message_id=message_id)
                # update database with new message_id
                values = (forwarded_message_id.message_id, file_name, update.effective_user.id, context.args[1])
                dbh.update('notes', 'message_id = %s, file_name = %s', 'professor_tgid = %s AND message_id = %s', values)
                await update.effective_message.reply_markdown('*Successfully replaced notes.*')
                LOGGER.info(f'NOTES - REPLACE | Professor: {update.effective_user.id} | OLD ID: {message_id}')
            else:
                raise ValueError
        except IndexError:
            await update.effective_message.reply_markdown(constants.NOTES_REPLACE_HELPSTRING)

    @classmethod
    async def notes(cls, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        '''Handler method for all notes functions'''
        try:
            match context.args[0]:
                case 'view':
                    await cls.view(update)
                case 'add':
                    # context.args ==> [subject_abbr, module_no]
                    await cls.add(update, context)
                case 'remove':
                    # context.args ==> [message_id]
                    await cls.remove(update, context)
                case 'replace':
                    # context.args ==> [message_id]
                    await cls.replace(update, context)
                case _:
                    await update.effective_message.reply_text('Invalid Method.')
        except IndexError:
            await update.effective_message.reply_markdown(constants.NOTES_HELPSTRING)
        # common exceptions handled below
        except ValueError:
            await update.effective_message.reply_text('Invalid ID, Try again.')
        except AttributeError:
            await update.effective_message.reply_text('Document not found, Try again.')
        except BadRequest:
            await update.effective_message.reply_text('Unknown error, Contact bot manager.')
            LOGGER.error(f'FAILED CHANNEL MSG OPERATION | Professor: {update.effective_user.id}')

class SearchHandler:
    @staticmethod
    async def prof(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        '''Search for all notes by a professor'''
        start = perf_counter()
        # check if the professor exists
        check = dbh.fetch('name, telegram_id', 'professor', f"abbreviation = '{context.args[1]}'")
        if check:
            # retrieve all notes by a specific professor
            res = dbh.fetch(
                    'file_name, message_id, subject_abbr, module_no, total_requests',
                    'notes',
                    f'professor_tgid = {check[0][1]}')
            if res:
                # build search results string and send a response
                await update.effective_message.reply_markdown(
                    f'{utils.build_find_str(len(res), context, perf_counter() - start)}{utils.build_view(res)}'
                    f'\n\n{constants.AUTHOR_STRING.format(first=check[0][0], user_id=check[0][1])}')
                # increment `total_requests` of all retrieved notes by 1
                values = (check[0][1],)
                dbh.update('notes', 'total_requests = total_requests + 1', 'professor_tgid = %s', values)
            else:
                raise NameError
        else:
            raise SyntaxError

    @staticmethod
    async def sub(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        '''Search for all notes by a subject'''
        start = perf_counter()
        try:
            # default module number set to -1
            module_no = -1
            # check if the subject exists
            subject_name = db_data['subject'][context.args[1].upper()]

            try:
                module_no = int(context.args[2])
            except IndexError:
                pass

            res = dbh.raw(f"""
                SELECT n.file_name, n.message_id, n.module_no, n.total_requests, n.professor_tgid, p.name
                FROM notes n, professor p
                WHERE n.subject_abbr = '{context.args[1].upper()}' AND n.professor_tgid=p.telegram_id AND
                    CASE
                        WHEN {module_no} <> -1
                            THEN n.module_no = {module_no}
                        ELSE
                            TRUE
                        END""")

            if res:
                results_str = constants.VIEW_STRING.replace('• Subject: *{subject}*\n', '') + f'\n• {constants.AUTHOR_STRING}'
                await update.effective_message.reply_markdown(
                    utils.build_find_str(len(res), context, perf_counter() - start)
                    + '\n'.join([results_str.format(
                        file=file_name,
                        group_id=int(config['CHANNEL_ID'][4:]),
                        id=message_id,
                        module=module_no,
                        req=total_requests,
                        first=name,
                        user_id=professor_tgid
                    ) for file_name, message_id, module_no, total_requests, professor_tgid, name in res]))
                for x in res:
                    values = (x[1],)
                    dbh.update('notes', 'total_requests = total_requests + 1','message_id = %s', values)
            else:
                raise NameError
        except KeyError:
            await update.effective_message.reply_text('Invalid subject, it does not exist.')
        except ValueError:
            await update.effective_message.reply_text('Invalid module number. Pass integer arguments only.')

    @classmethod
    async def search(cls, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        '''Handler method for all search functions'''
        try:
            match context.args[0]:
                case 'prof':
                    # context.args ==> [professor_abbr]
                    await cls.prof(update, context)
                case 'sub':
                    # () -> optional argument
                    # context.args ==> [subject_abbr (, module_no)]
                    await cls.sub(update, context)
                case _:
                    await update.effective_message.reply_text('Invalid search filter.')
        except IndexError:
            await update.effective_message.reply_markdown(constants.SEARCH_HELPSTRING)
        except SyntaxError:
            await update.effective_message.reply_text('Invalid professor abbreviation.')
        except NameError:
            await update.effective_message.reply_text('No results found.')

class StatsHandler:
    @staticmethod
    async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        '''Display database statistics'''
        total = dbh.raw('''
            SELECT
                (SELECT COUNT(*) FROM student) AS cstudent,
                (SELECT COUNT(*) FROM professor) AS cprof,
                (SELECT COUNT(*) FROM notes) AS cnotes,
                (SELECT SUM(total_requests) FROM notes) AS snotes,
                (SELECT COUNT(*) FROM department) AS cdept''')

        popular = dbh.raw('''
            SELECT n.file_name, n.subject_abbr, n.module_no, n.professor_tgid, n.message_id, n.total_requests, p.name
            FROM notes n, professor p
            WHERE n.professor_tgid=p.telegram_id AND n.total_requests = (SELECT MAX(total_requests) FROM notes) LIMIT 1''')

        # welp
        if not popular:
            popular = [(None,) * 7]

        await update.effective_message.reply_markdown(constants.STATS_STRING.format(
            students=total[0][0],
            professor=total[0][1],
            notes=total[0][2],
            search=total[0][3],
            dept=total[0][4] - 1,
            file=popular[0][0],
            group_id=config['CHANNEL_ID'][4:],
            id=popular[0][4],
            subject=popular[0][1],
            module=popular[0][2],
            req=popular[0][5],
            first=popular[0][6],
            user_id=popular[0][3]))

application.add_handler(CommandHandler('notes', NotesHandler.notes, block=False, filters=CustomFilters.professor_filter))
application.add_handler(CommandHandler('search', SearchHandler.search, block=False, filters=CustomFilters.user_filter))
application.add_handler(CommandHandler('stats', StatsHandler.stats, block=False, filters=CustomFilters.user_filter))
