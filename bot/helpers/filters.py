from telegram import Message
from bot import config, db_data
from telegram.ext.filters import MessageFilter

# prevent unauthorised access to the bot
class CustomFilters:
    class AdminFilter(MessageFilter):
        def filter(self, message: Message) -> bool:
            '''Restrict access to admins only'''
            return message.from_user.id in db_data['admin']
    admin_filter = AdminFilter()

    class StudentFilter(MessageFilter):
        def filter(self, message: Message) -> bool:
            '''Restrict access to students only'''
            return message.from_user.id in db_data['student']
    student_filter = StudentFilter()

    class ProfessorFilter(MessageFilter):
        def filter(self, message: Message) -> bool:
            '''Restrict access to professors only'''
            return message.from_user.id in db_data['professor']
    professor_filter = ProfessorFilter()

    class UserFilter(MessageFilter):
        def filter(self, message: Message) -> bool:
            '''Restrict access to admins, professors and students only'''
            return (message.from_user.id in db_data['admin']
                    or message.from_user.id in db_data['professor']
                    or message.from_user.id in db_data['student'])
    user_filter = UserFilter()

    class GroupFilter(MessageFilter):
        def filter(self, message: Message) -> bool:
            '''Restrict access to a certain group only'''
            return message.chat.id == int(config['GROUP_ID'])
    group_filter = GroupFilter()
