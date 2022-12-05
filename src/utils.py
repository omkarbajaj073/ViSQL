import os
from datetime import datetime as time
from PyQt6.QtWidgets import *
import mysql.connector as connector

from constants import *


class MessageDialog(QDialog):
  '''Dialog box for messages indicating the success or failure of processes'''
  def __init__(self, msg):
    super().__init__()
    layout = QVBoxLayout()
    layout.addWidget(QLabel(msg))
    self.setLayout(layout)


def get_databases():
  '''Get all databases on the host and user (see constants.py)'''
  try:
    con = connector.connect(host=host, user=user, password=password)
    cur = con.cursor()
    cur.execute('show databases')
    dbs = cur.fetchall()
    dbs = map(lambda i: i[0], dbs) # Extract the datbase name
    return dbs
  
  except Exception as e:
    dialog = MessageDialog(str(e))
    dialog.exec()


def create_database(name):
  '''Create database on given connection'''
  try:
    con = connector.connect(host=host, user=user, password=password)
    cur = con.cursor()
    query = f'create database {name}'
    cur.execute(query)
    con.close()
    save_to_file(query)

  except Exception as e:
    dialog = MessageDialog(str(e))
    dialog.exec()


def get_table_attributes(cur, table):
  '''Get attributes of a given table'''
  try:
    cur.execute(f'show columns from {table}')
    cols = cur.fetchall()
    cols = list(map(lambda i: i[0], cols)) # Extract the attribute name
    return cols
  
  except Exception as e:
    dialog = MessageDialog(str(e))
    dialog.exec()

   
def get_tables(cur):
  '''Get tables in a given database (cursor must be from connection to that db)'''
  try:
    cur.execute('show tables')
    tables = cur.fetchall()
    tables = map(lambda i: i[0], tables) # Extract the table name
    return tables
  
  except Exception as e:
    dialog = MessageDialog(str(e))
    dialog.exec()


def get_data(cur, table, attributes, constraints=None, order_by=None):
  '''Get data from the table'''
  
  att_str = ', '.join(attributes) # Format attributes
  query = f'''select {att_str} from {table}''' # Initialize query
  
  if constraints: # If conditions exist, add a where clause
    query += f" where {' and '.join(constraints)}"
    
  if order_by is not None: # Add order by clause if necessary
    query += f" order by {order_by}"

  try:
    cur.execute(query)
    save_to_file(query)
    return cur.fetchall() # Return result of the query
  
  except Exception as e:
    dialog = MessageDialog(str(e))
    dialog.exec()
    
    
def update_data(cur, table, attribute, value, constraints=None):
  '''Update data in a table'''
  
  query = f'''update {table} set {attribute}={value}''' # Initialise basic query structure
  if constraints: # If conditions exist, add where clause
    query += f" where {' and '.join(constraints)}"

  try:
    cur.execute(query)
    save_to_file(query)
    dialog = MessageDialog("Updated data")
    dialog.exec()
  except Exception as e:
    dialog = MessageDialog(str(e))
    dialog.exec()


def group_by_data(cur, table, func, attribute, constraints, group_attr):
  '''Aggregate function queries'''
  
  if func == 'count(*)': # Format the query according to the function
    func = 'count'
    attribute = '*'
  query = f'''select {group_attr}, {func}({attribute}) from {table}'''
  
  if constraints: # If conditions exist, add where clause
    query += f" where {' and '.join(constraints)}"
    
  query += f" group by {group_attr}" # Group by clause
  
  try:
    cur.execute(query)
    save_to_file(query)
    return cur.fetchall()
  except Exception as e:
    dialog = MessageDialog(str(e))
    dialog.exec()


def create_table(cur, name, attributes):
  '''Create table from attributes'''
  
  query = f'''create table {name} ({','.join(attributes)})''' # format basic query string
  try:
    cur.execute(query)
    save_to_file(query)
  
  except Exception as e:
    dialog = MessageDialog(str(e))
    dialog.exec()

  
def delete_table(cur, name):
  '''Delete table in database'''
  query = f'''drop table {name}'''
  try:
    cur.execute(query)
    save_to_file(query)
    dialog = MessageDialog("Table deleted!")
    dialog.exec()
  
  except Exception as e:
    dialog = MessageDialog(str(e))
    dialog.exec()


def format_attribute(name, data, not_null, pk, default):
  '''Format attribute constraints into string format before building query'''
  att = f'{name} {data} '
  if not_null:
    att += 'not null '
  if pk:
    att += 'primary key '
  if default:
    att += f'default {default}'
  return att


def format_insert_data(data):
  '''Format attribute constraints into string format before building query'''
  formatted = []
  for relation in data:
    row = []
    for item in relation:
      row.append(eval(item))

    formatted.append(tuple(row))
  return formatted


def insert_data(con, table, data):
  '''Run insertion of data into table'''
  cur = con.cursor()
  query = f'''insert into {table} values'''

  for row in data:
    query += f" {row},"

  query = query.rstrip(',')

  try:
    cur.execute(query)
    con.commit()
    save_to_file(query)
    dialog = MessageDialog("Data Inserted!")
    dialog.exec()

  except Exception as e:
    dialog = MessageDialog(str(e))
    dialog.exec()


def delete_rows(con, table, constraints):
  '''Delete rows in tables'''
  cur = con.cursor()
  query = f'''delete from {table}'''

  if constraints: # If condition exist, add where clause
    query += f" where {' and '.join(constraints)}"

  try:
    cur.execute(query)
    con.commit()
    save_to_file(query)
    dialog = MessageDialog("Deleted data")
    dialog.exec()

  except Exception as e:
    dialog = MessageDialog(str(e))
    dialog.exec()


def natural_join(cur, table1, table2):
  '''Natural join query'''
  query = f"select * from {table1} natural join {table2}"
  try:
    cur.execute(query)
    results = cur.fetchall()
    return results
  except Exception as e:
    dialog = MessageDialog(str(e))
    dialog.exec()
    

def save_to_file(query):
  '''Save all commands run in a given session to a file'''
  # Path of the file - desktop of the default user in the current system
  path = os.path.join(os.environ['USERPROFILE'], 'Desktop', 'ViSQL_log.txt')
  try:
    # If first time using the application, log the host, user, and time of creation of the session
    with open(path, 'x') as f:
      f.write(f"""/* METADATA:
      host: {host}
      user: {user}
      created: {time.now()} */\n\n""")

  except FileExistsError:
    pass
  
  # Logging all queries
  with open(path, 'a') as f:
    f.write(f'/* {time.now()} */\n')
    f.write(f'{query};\n\n')