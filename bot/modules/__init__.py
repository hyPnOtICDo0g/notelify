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
                subject_abbr VARCHAR(5) NOT NULL,
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
        'CHANNEL_ID',
        'PROF_SECRET'
    }

    USN_REGEX = '^\d[a-z]{2}\d{2}[a-z]{2}\d{3}$'

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

    NOTES_HELPSTRING = dedent('''
        > *Functions available*:
        • `view`: _Display list of notes uploaded by you_
        • `add`: _Add notes to the database_
        • `remove`: _Remove notes from the database_
        • `replace`: _Replace existing notes with updated notes_

        > *Usage*:
            `/notes <function> [arguments]`

        *Detailed argument usage is displayed on executing a function.*''')

    NOTES_ADD_HELPSTRING = dedent('''
        • _This function can be used to share notes uploaded to telegram._
        • _Notes are added by replying to the required document._
        • _It expects two arguments, subject abbreviation & module no._

        *Example*:
            `/notes add dbms 4` _(reply to document first)_''')

    NOTES_REMOVE_HELPSTRING = dedent('''
        • _This command expects one argument, the message ID._
        • _The message ID can be obtained by using the view function._

        *Example*:
            `/notes remove 2521`''')

    NOTES_REPLACE_HELPSTRING = dedent('''
        • _If existing notes require an update, this function can be used._
        • _It expects one argument, the message ID of the existing notes._
        • _Notes can be replaced by replying to the new document._

        *Example*:
            `/notes replace 4821` _(reply to document first)_''')

    SEARCH_HELPSTRING = dedent('''
        > *Search filters* _[search by]_:
        • `prof`: _professor_ | args: _professor abbreviation_
        • `sub`: _subject_ | args: _subject abbreviation [module no.]_

        > *Usage*:
            `/search <filter> [arguments]`

        > *Examples*:
            _Search for DBMS notes_: `/search sub dbms`
            _Search for notes by professor_ *jks*: `/search prof jks`''')

    REGPROF_HELPSTRING = dedent('''
        > *Usage*:
            `/regprof <secret_code> <abbreviation> <department>`''')


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

    STATS_STRING = (dedent('''
        > *Total*:
        • Registered students: {students}
        • Registered professors: {professor}
        • Notes uploaded: {notes}
        • Search requests: {search}
        • Departments: {dept}

        > *Most popular*:''')
        + VIEW_STRING.replace('File', 'Notes')
        + f"\n• {AUTHOR_STRING.replace('Author', 'Professor')}")
