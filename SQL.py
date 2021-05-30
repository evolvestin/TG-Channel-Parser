# -*- coding: utf-8 -*-
import sqlite3
sql_patterns = ['database is locked', 'no such table']


class SQL:
    def __init__(self, database):
        def dict_factory(cursor, row):
            dictionary = {}
            for idx, col in enumerate(cursor.description):
                dictionary[col[0]] = row[idx]
            return dictionary
        self.connection = sqlite3.connect(database, timeout=100, check_same_thread=False)
        self.connection.execute('PRAGMA journal_mode = WAL;')
        self.connection.execute('PRAGMA synchronous = OFF;')
        self.connection.row_factory = dict_factory
        self.cursor = self.connection.cursor()

    # ------------------------------------------------------------------------------------------ UTILITY BEGIN
    def request(self, sql, fetchone=None):
        lock = True
        while lock is True:
            lock = False
            try:
                with self.connection:
                    self.cursor.execute(sql)
            except IndexError and Exception as error:
                for pattern in sql_patterns:
                    if pattern in str(error):
                        lock = True
                if lock is False:
                    raise error

        if fetchone:
            return self.cursor.fetchone()
        else:
            return self.cursor.fetchall()

    def close(self):
        self.connection.close()

    def update(self, table, item_id, dictionary):
        self.request(f"UPDATE {table} SET {self.upd_kv(dictionary)} WHERE id = '{item_id}'")
    # ------------------------------------------------------------------------------------------ UTILITY END

    # ------------------------------------------------------------------------------------------ TRANSFORM BEGIN
    @staticmethod
    def ins_dict_items(dictionary):
        """Преобразование dict в строки с keys и values (только для INSERT или REPLACE)"""
        values = []
        for key in dictionary:
            value = dictionary.get(key)
            if value is None:
                values.append('NULL')
            elif type(value) == dict:
                values.append(f'"{value}"')
            else:
                values.append(f"'{value}'")
        return ', '.join(dictionary.keys()), ', '.join(values)

    @staticmethod
    def upd_kv(dictionary):
        """Преобразование dict в строку key=value, key=value ... (только для UPDATE)"""
        items = []
        for key in dictionary:
            value = dictionary.get(key)
            if value is None:
                value = 'NULL'
            elif type(value) == dict:
                value = f'"{value}"'
            elif type(value) == list and len(value) == 1 and type(value[0]) == str:
                value = value[0]
            else:
                value = f"'{value}'"
            items.append(f'{key}={value}')
        return ', '.join(items)

    def ins_kv(self, dictionary):
        """Готовая строка значений для запроса (только для INSERT или REPLACE)"""
        keys, values = self.ins_dict_items(dictionary)
        return f'({keys}) VALUES ({values})'
    # ------------------------------------------------------------------------------------------ TRANSFORM END
