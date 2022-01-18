import sqlite3
from jinjasql import JinjaSql
import sys
import traceback

j = JinjaSql(param_style='pyformat')

'''This file is a container for classes that handle SQLite database functionalities. Currently only support for a few features:
-Connecting to existing database
-Create table in database
-Insert SINGLE entry into database
-Checking if entry exists (returns bool)
-Error handler that should catch most exceptions thrown.'''


# SQLParameter is a container for defining parameters in a SQL table.
class SQLParameter:
    def __init__(self, var_type=None, name=None, constraint='', is_primary=False):
        self.var_type = var_type
        self.name = name
        self.constraint = constraint
        self.is_primary = is_primary


# Object that represents a database that already exists locally.
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

    def execute_command(self, cmd):
        # Pass any valid SQL command to this method.
        if self.connection and self.cursor:
            try:
                self.cursor.execute(cmd)
                self.connection.commit()
            except sqlite3.Error as er:
                self.error_handler(er)

    def create_table(self, table_name, params: list[SQLParameter]):
        # Format parameters into an executable SQL command.
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

        command = 'CREATE TABLE IF NOT EXISTS {0} (?);'.format(table_name), (formatted_parameters,)

        try:
            self.cursor.execute(command)
            self.connection.commit()
            print('Created table: ' + table_name)
        except sqlite3.Error as er:
            self.error_handler(er)

    def check_row(self, component, table_name, col_name=None):
        # Method checks existence of table entry in table_name based on component.
        command = 'SELECT EXISTS(SELECT 1 FROM {0} WHERE {1}="{2}");'.format(table_name, col_name, component)
        try:
            self.cursor.execute(command)
            if self.cursor.fetchone()[0]:
                return True
            else:
                return False
        except sqlite3.Error as er:
            self.error_handler(er)

    def fetch_all(self, table_name):
        # This method extracts every row from table, table_name, in connected database. Return is a list of tuples
        if self.connection and self.cursor:
            command = 'SELECT * FROM ' + table_name
            self.cursor.execute(command)
            result = self.cursor.fetchall()
            return result

    def update_table(self, table_name=None, column=None, val=None, comparator_name=None, comparator=None):
        if not column:
            return
        try:
            self.cursor.execute(r'UPDATE {0} SET ("{1}"={2}) WHERE {3}={4}'.format(table_name, column, val, comparator_name, comparator))
        except sqlite3.Error as er:
            self.error_handler(er)


    @staticmethod
    def error_handler(er):
        print('SQLite error: %s' % (' '.join(er.args)))
        print("Exception class is: ", er.__class__)
        print('SQLite traceback: ')
        exc_type, exc_value, exc_tb = sys.exc_info()
        print(traceback.format_exception(exc_type, exc_value, exc_tb))

    def sqlite_insert(self, table, num_vals, row):
        # programmatically generate sql insert command
        # isolate column headers and values from row input
        new_row = list()
        for i in row:
            if type(i) is str and not '':
                new_val = '"' + i + '"'
            else:
                new_val = i
            new_row.append(new_val)

        # use cols and vals to generate sql insert string, tailored to specific SQL table. Maybe could change to switch/case
        #insert_command = 'INSERT INTO {0} VALUES('.format(table) + num_vals + ');'
        insert_command = 'INSERT INTO {0} VALUES({1});'.format(table, num_vals)

        # commit table insert to database
        try:
            self.connection.cursor().execute(insert_command, new_row)
            self.connection.commit()
            print('SQL Insert successful.')
            return
        except sqlite3.Error as er:
            SqliteDatabase.error_handler(er)

    def disconnect_database(self):
        if self.connection:
            self.connection.close()
        else:
            print('No connection to close.')
        return
