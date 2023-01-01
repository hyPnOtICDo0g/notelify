from bot import db_data
from typing import Union
from telegram import Update
from .filters import CustomFilters
from telegram.ext import ContextTypes
from bot.modules.dbhandler import DBHandler as dbh

class Utilities:
    @staticmethod
    def find_role(update: Update) -> Union[str, None]:
        '''Find the role of an user'''
        if CustomFilters.student_filter.check_update(update):
            return 'student'
        elif CustomFilters.professor_filter.check_update(update):
            return 'professor'
        elif CustomFilters.admin_filter.check_update(update):
            return 'admin'
        else:
            return None

    @staticmethod
    def find_dept(user: Union[str, None], update: Update) -> Union[str, None]:
        '''Find the department an user belongs to'''
        if user not in ('admin', None):
            res = dbh().fetch('department_id', user, f'telegram_id = {update.effective_user.id}')
            return {x for x, y in db_data['department'].items() if y['department_id'] == res[0][0]}.pop()
        return None

    @staticmethod
    async def forwardMessage(update: Update, context: ContextTypes.DEFAULT_TYPE, chat_id: str) -> int:
        return await context.bot.copyMessage(
            from_chat_id=update.effective_user.id,
            chat_id=int(chat_id),
            message_id=update.message.reply_to_message.message_id)
