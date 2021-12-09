import sqlite3
from jinjasql import JinjaSql
import sys
import traceback

j = JinjaSql(param_style='pyformat')


class SQLParameter:
    def __init__(self, var_type=None, name=None, constraint='', is_primary=False):
        self.var_type = var_type
        self.name = name
        self.constraint = constraint
        self.is_primary = is_primary


class SqliteDatabase:
    def __init__(self):
        self.connection = None
        self.cursor = None

    def connect_database(self, database):
        try:
            self.connection = sqlite3.connect(database)
            self.cursor = self.connection.cursor()
            print('Successfully connected to: ' + database)
        except sqlite3.Error as er:
            self.error_handler(er)

    def create_table(self, table_name, params: list[SQLParameter]):
        num_params = len(params) - 1
        formatted_parameters = ''
        for param in params:
            if param.is_primary:
                variable = param.name + ' ' + param.var_type + ' ' + 'PRIMARY KEY'
            else:
                variable = param.name + ' ' + param.var_type + ' ' + param.constraint
            if params.index(param) != num_params:
                variable += ', '
            formatted_parameters += variable

        command = 'CREATE TABLE IF NOT EXISTS ' + table_name + '(' + formatted_parameters + ' );'

        try:
            self.cursor.execute(command)
            self.connection.commit()
            print('Created table: ' + table_name)
        except sqlite3.Error as er:
            self.error_handler(er)

    def check_row(self, component, table_name):
        try:
            self.cursor.execute('SELECT count(*) FROM "{0}" WHERE id = ?'.format(table_name), (component,))
            data = self.cursor.fetchone()[0]
            if data == 0:
                return False
            else:
                return True
        except sqlite3.Error as er:
            self.error_handler(er)

    @staticmethod
    def error_handler(er):
        print('SQLite error: %s' % (' '.join(er.args)))
        print("Exception class is: ", er.__class__)
        print('SQLite traceback: ')
        exc_type, exc_value, exc_tb = sys.exc_info()
        print(traceback.format_exception(exc_type, exc_value, exc_tb))


def connect_discord(db):
    try:
        conn = sqlite3.connect(db)
        print('Connection successful!')
        return conn
    except sqlite3.Error as er:
        SqliteDatabase.error_handler(er)


def sqlite_insert(conn, table, column_headers, row):
    # programmatically generate sql insert command
    # isolate column headers and values from row input
    new_row = list()
    for i in row:
        if type(i) is str and not '':
            new_val = '"' + i + '"'
        else:
            new_val = i
        new_row.append(new_val)
    cols = ', '.join('{}'.format(col) for col in column_headers)
    vals = ', '.join('{}'.format(col) for col in new_row)

    # use cols and vals to generate sql insert string, tailored to specific SQL table. Maybe could change to switch/case
    sql = 'INSERT INTO {0} VALUES (?)'.format(table, vals)

    # commit table insert to database
    try:
        conn.cursor().execute(sql, row)
        conn.commit()
        print('SQL Insert successful.')
        return
    except sqlite3.Error as er:
        SqliteDatabase.error_handler(er)
