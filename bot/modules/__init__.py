from textwrap import dedent

class constants:
    TABLES = (
            '''CREATE TABLE manager(
                username TEXT NOT NULL,
                telegram_id int PRIMARY KEY
            );''',

            '''CREATE TABLE department(
                name VARCHAR(6) NOT NULL,
                department_id CHAR(5) PRIMARY KEY,
                branch TEXT NOT NULL
            );''',

            '''CREATE TABLE professor(
                name TEXT NOT NULL,
                abbreviation VARCHAR(3) NOT NULL,
                telegram_id int PRIMARY KEY,
                department_id CHAR(5) NOT NULL,
                FOREIGN KEY(department_id) REFERENCES DEPARTMENT(department_id)
            );''',

            '''CREATE TABLE student(
                name TEXT NOT NULL,
                usn CHAR(10) PRIMARY KEY,
                telegram_id int UNIQUE NOT NULL,
                department_id CHAR(5) NOT NULL,
                FOREIGN KEY(department_id) REFERENCES DEPARTMENT(department_id)
            );''',

            '''CREATE TABLE notes(
                file_name TEXT NOT NULL,
                subject_name TEXT NOT NULL,
                subject_abbr VARCHAR(5) UNIQUE NOT NULL,
                module_no INT NOT NULL,
                professor_tgid int,
                department VARCHAR(6) NOT NULL,
                message_id INT PRIMARY KEY,
                total_requests INT DEFAULT 0 NOT NULL,
                FOREIGN KEY(professor_tgid) REFERENCES professor(telegram_id) ON DELETE SET NULL
            );'''
        )

    BOTCOMMANDS = [
            ('help', 'To get this message'),
            ('search', 'Search for lecture notes'),
            ('stats', 'Display database statistics'),
            ('register', 'Register for bot access [STUDENT]'),
            ('notes', 'View / Add / Remove / Replace lecture notes [PROFESSOR]')
        ]

    ENV_VARS = {
        'BOT_TOKEN',
        'DATABASE_URL',
        'OWNER_ID',
        'GROUP_ID',
        'CHANNEL_ID'
    }

    START_MESSAGE = dedent('''
        Send me a search query.
        Use /help for further instructions.''')

    REG_MESSAGE = dedent('''
        *Thank you for registering* [{first}](tg://user?id={id})!
        _You can continue to use the bot here:_ @{bot}''')

    HELPSTRING = dedent('''
        \> *_Global Commands_*:
        • */help*: _To get this message_
        • */profile*: _Display profile information_
        • */search*: _Search for lecture notes of any department_
        • */stats*: _Display stats of registered users and notes_

       \> *_Student Commands_*:
        • */register*: _Register with your USN and Department for bot access_
        • */unregister*: _Unregister and delete your data_

        \> *_Professor Commands_*:
        • */notes*: _Manage / View uploaded notes_

        *Detailed usage is displayed on clicking any of the above\.*''')

    REG_HELPSTRING = dedent('''
        • The */register* command takes an USN and Department Name.
        • Use it in this format: `/register USN DEPT_NAME`
        • The bot's DM can be used for further usage.''')

    PROFILE_STRING = dedent('''
        • Name: *{name}*
        • Username: @{username}
        • Telegram ID: `{id}`
        • Role: *{role}*
        • Department: *{dept}*''')

    VIEW_STRING = dedent('''
        • File: [{file}](https://t.me/c/{group_id}/{id})
        • ID: `{id}`
        • Subject: *{subject}*
        • Module: *{module}*
        • Total requests: *{req}*''')

    AUTHOR_STRING = 'Author: [{first}](tg://user?id={user_id})'
