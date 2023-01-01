from __future__ import annotations

from . import constants
from typing import Union
from sys import exit as exitnow
from bot import config, db_data, LOGGER
from psycopg2 import connect, DatabaseError
from psycopg2.errors import DuplicateTable, UniqueViolation

class DBHandler:
    def __init__(self) -> None:
        self.conn = None
        self.cur = None

    def connect(self) -> None:
        '''PLACEHOLDER'''
        try:
            self.conn = connect(config['DATABASE_URL'])
            self.cur = self.conn.cursor()
        except DatabaseError as e:
            LOGGER.error(e)

    def disconnect(self) -> None:
        '''PLACEHOLDER'''
        self.conn.commit()
        self.cur.close()
        self.conn.close()

    def create(self) -> DBHandler:
        '''PLACEHOLDER'''
        try:
            self.connect()
            for x in constants.TABLES:
                self.cur.execute(x)
            self.disconnect()
            LOGGER.info('Tables created.')
        except DuplicateTable:
            LOGGER.info('Tables exist.')
        except AttributeError:
            LOGGER.critical('Database not found, Exiting.')
            exitnow(1)
        finally:
            return self

    def write(self, table: str, values: tuple) -> None:
        '''PLACEHOLDER'''
        # not sure if this line is prone to SQL injections
        # please open an issue if that's the case
        query = f'INSERT INTO {table} VALUES(' + ', '.join(['%s'] * len(values)) + ')'
        self.connect()
        self.cur.execute(query, values)
        self.disconnect()

    def fetch(
            self,
            fields: str,
            table: str,
            where: Union[bool, str] = True,
            limit: Union[int, str] = 'all') -> list[tuple]:
        '''PLACEHOLDER'''
        try:
            query = f'SELECT {fields} FROM {table} WHERE {where} LIMIT {limit}'
            self.connect()
            self.cur.execute(query)
            return self.cur.fetchall()
        finally:
            self.disconnect()

    def delete(self, table: str, where: str) -> int:
        '''PLACEHOLDER'''
        query = f'DELETE FROM {table} WHERE {where}'
        self.connect()
        self.cur.execute(query)
        self.disconnect()
        return self.cur.rowcount

    def update(self, table: str, set: str, where: str) -> None:
        '''PLACEHOLDER'''
        query = f'UPDATE {table} SET {set} WHERE {where}'
        self.connect()
        self.cur.execute(query)
        self.disconnect()

    def raw(self, query: str) -> list[tuple]:
        '''PLACEHOLDER'''
        try:
            self.connect()
            self.cur.execute(query)
            return self.cur.fetchall()
        finally:
            self.disconnect()

    def load(self) -> None:
        '''PLACEHOLDER'''
        db_data['admin'] += [x[0] for x in self.fetch('telegram_id', 'manager')] # + [int(config['OWNER_ID'])]
        db_data['professor'] += [x[0] for x in self.fetch('telegram_id', 'professor')] # + [int(config['OWNER_ID'])]
        db_data['student'] += [x[0] for x in self.fetch('telegram_id', 'student')]
        try:
            for x, y in db_data['department'].items():
                values = (x, y['department_id'], y['branch'])
                self.write('department', values)
        except UniqueViolation:
            pass
        LOGGER.info('Information loaded.')
