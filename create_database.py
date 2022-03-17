import sqlite3

connection = sqlite3.connect('test_database.sqlite')
cursor = connection.cursor()

with open('create_database.sql', 'r', encoding='utf-8') as script:
    text_script = script.read()

cursor.executescript(text_script)
cursor.close()
connection.close()

