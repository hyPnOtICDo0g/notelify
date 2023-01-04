from __future__ import annotations

from . import constants
from typing import Union
from sys import exit as exitnow
from bot import config, db_data, LOGGER
from psycopg2 import connect, DatabaseError
from psycopg2.errors import DuplicateTable, UniqueViolation

class DBHandler:
    @classmethod
    def connect(cls) -> None:
        '''Create a new database session'''
        try:
            cls.conn = connect(config['DATABASE_URL'])
            cls.cur = cls.conn.cursor()
        except DatabaseError as e:
            LOGGER.error(e)

    @classmethod
    def disconnect(cls) -> None:
        '''Commit pending transactions and close database connection'''
        cls.conn.commit()
        cls.cur.close()
        cls.conn.close()

    @classmethod
    def create(cls) -> DBHandler:
        '''Create all the required tables'''
        try:
            cls.connect()
            for x in constants.TABLES:
                cls.cur.execute(x)
            cls.disconnect()
            LOGGER.info('Tables created.')
        except DuplicateTable:
            LOGGER.info('Tables exist.')
        except AttributeError:
            LOGGER.critical('Database not found, Exiting.')
            exitnow(1)
        finally:
            return cls

    @classmethod
    def write(cls, table: str, values: tuple) -> None:
        '''Insert records to a table'''
        query = f'INSERT INTO {table} VALUES(' + ', '.join(['%s'] * len(values)) + ')'
        cls.connect()
        cls.cur.execute(query, values)
        cls.disconnect()

    @classmethod
    def fetch(
            cls,
            fields: str,
            table: str,
            where: Union[bool, str] = True,
            limit: Union[int, str] = 'all') -> list[tuple]:
        '''Fetch data from a table'''
        try:
            # not sure if this line is prone to SQL injections in general
            # please open an issue if that's the case
            query = f'SELECT {fields} FROM {table} WHERE {where} LIMIT {limit}'
            cls.connect()
            cls.cur.execute(query)
            return cls.cur.fetchall()
        finally:
            cls.disconnect()

    @classmethod
    def delete(cls, table: str, where: str) -> int:
        '''Remove records from a table'''
        query = f'DELETE FROM {table} WHERE {where}'
        cls.connect()
        cls.cur.execute(query)
        cls.disconnect()
        return cls.cur.rowcount

    @classmethod
    def update(cls, table: str, set: str, where: str, values: tuple) -> None:
        '''Modify existing records in a table'''
        query = f'UPDATE {table} SET {set} WHERE {where}'
        cls.connect()
        cls.cur.execute(query, values)
        cls.disconnect()

    @classmethod
    def raw(cls, query: str) -> list[tuple]:
        '''Perform a raw SQL query and return records'''
        try:
            cls.connect()
            cls.cur.execute(query)
            return cls.cur.fetchall()
        finally:
            cls.disconnect()

    @classmethod
    def load(cls) -> None:
        '''Load data from and into a table during startup'''
        db_data['admin'] += [x[0] for x in cls.fetch('telegram_id', 'manager')] # + [int(config['OWNER_ID'])]
        db_data['professor'] += [x[0] for x in cls.fetch('telegram_id', 'professor')] # + [int(config['OWNER_ID'])]
        db_data['student'] += [x[0] for x in cls.fetch('telegram_id', 'student')]
        try:
            for x, y in db_data['department'].items():
                values = (x, y['department_id'], y['branch'])
                cls.write('department', values)
        except UniqueViolation:
            pass
        LOGGER.info('Information loaded.')
