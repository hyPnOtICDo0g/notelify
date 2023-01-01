from bot import db_data
from typing import Union
from telegram import Update
from .filters import CustomFilters
from bot.modules.dbhandler import DBHandler as dbh

class Utilities:
    @staticmethod
    def find_role(update: Update) -> str:
        '''Find the role of an user'''
        if CustomFilters.student_filter.check_update(update):
            return 'student'
        elif CustomFilters.professor_filter.check_update(update):
            return 'professor'
        else:
            return 'admin'

    @staticmethod
    def find_dept(user: str, update: Update) -> Union[str, None]:
        '''Find the department an user belongs to'''
        if user != 'admin':
            res = dbh().fetch('department_id', user, f'telegram_id = {update.effective_user.id}')
        else:
            return None
        return {x for x, y in db_data['department'].items() if y['department_id'] == res[0][0]}.pop()
