import sqlite3

class Database:
    def __init__(self, db_name='todo.db'):
        self.connection = sqlite3.connect(db_name)
        self.cursor = self.connection.cursor()
        self._create_table()
    
    def _create_table(self):
        self.cursor.execute(""" 

        

""")

        