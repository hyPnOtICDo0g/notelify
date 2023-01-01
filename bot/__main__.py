from bot import config, application
from .modules.dbhandler import DBHandler
from .modules import userhandler, noteshandler

if __name__ == '__main__':
    try:
        # create tables and load required data into `db_data`
        DBHandler().create().load()
        application.run_polling()
    except AttributeError:
        pass
