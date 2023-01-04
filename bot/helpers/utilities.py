from typing import Union
from bot import config, db_data
from bot.modules import constants
from .filters import CustomFilters
from telegram import Message, Update
from telegram.ext import ContextTypes
from bot.modules.dbhandler import DBHandler as dbh

class Utilities:
    @staticmethod
    def find_role(update: Update) -> Union[str, None]:
        '''Find the role of an user'''
        if CustomFilters.admin_filter.check_update(update):
            return 'admin'
        elif CustomFilters.professor_filter.check_update(update):
            return 'professor'
        elif CustomFilters.student_filter.check_update(update):
            return 'student'
        else:
            return None

    @staticmethod
    def find_dept(user: Union[str, None], update: Update) -> Union[str, None]:
        '''Find the department an user belongs to'''
        if user == 'admin':
            return 'ADMIN'
        elif user is not None:
            res = dbh.fetch('department_id', user, f'telegram_id = {update.effective_user.id}')
            return {x for x, y in db_data['department'].items() if y['department_id'] == res[0][0]}.pop()
        return None

    @staticmethod
    def build_view(res: list) -> str:
        """Construct a string containing all notes' attributes"""
        return '\n'.join(
            [constants.VIEW_STRING.format(
                file=file_name,
                group_id=config['CHANNEL_ID'][4:],
                id=message_id,
                subject=subject_abbr,
                module=module_no,
                req=total_requests
            ) for file_name, message_id, subject_abbr, module_no, total_requests in res])

    @staticmethod
    def build_find_str(number: int, context: ContextTypes.DEFAULT_TYPE, time: float) -> str:
        '''Construct a search response string'''
        return f"Found *{number}* result(s) matching the query *{' '.join(context.args)}* in _{'%.2f' % time}s_\n"

    @staticmethod
    async def forwardMessage(update: Update, context: ContextTypes.DEFAULT_TYPE, chat_id: str) -> Message:
        '''
        Copy (forward) a message and return a `Message` object
        containing the message_id of a forwarded message
        '''
        return await context.bot.copyMessage(
            from_chat_id=update.effective_user.id,
            chat_id=int(chat_id),
            message_id=update.message.reply_to_message.message_id)
