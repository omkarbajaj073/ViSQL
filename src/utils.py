from PyQt6.QtWidgets import *
import mysql.connector as connector
import logging
from constants import *
from datetime import datetime as time

logging.basicConfig(level=logging.DEBUG)

class ErrorDialog(QDialog):
  def __init__(self, error):
    super().__init__()
    layout = QVBoxLayout()
    layout.addWidget(QLabel(error))
    self.setLayout(layout)

class SuccessDialog(QDialog):
  def __init__(self, txt):
    super().__init__()
    layout = QVBoxLayout()
    layout.addWidget(QLabel(txt))
    self.setLayout(layout)
    

def get_databases():
  try:
    con = connector.connect(host=host, user=user, password=password)
    cur = con.cursor()
    cur.execute('show databases')
    dbs = cur.fetchall()
    dbs = map(lambda i: i[0], dbs)
    return dbs
  
  except Exception as e:
    dialog = ErrorDialog(str(e))
    dialog.exec()


def create_database(name):
  try:
    con = connector.connect(host=host, user=user, password=password)
    cur = con.cursor()
    query = f'create database {name}'
    cur.execute(query)
    con.close()
    save_to_file(query)

  except Exception as e:
    dialog = ErrorDialog(str(e))
    dialog.exec()

def get_table_attributes(cur, table):
  try:
    cur.execute(f'show columns from {table}')
    cols = cur.fetchall()
    cols = list(map(lambda i: i[0], cols))
    return cols
  
  except Exception as e:
    dialog = ErrorDialog(str(e))
    dialog.exec()
  
  
  

def get_tables(cur):
  try:
    cur.execute('show tables')
    tables = cur.fetchall()
    tables = map(lambda i: i[0], tables)
    return tables
  
  except Exception as e:
    dialog = ErrorDialog(str(e))
    dialog.exec()


def get_data(cur, table, attributes, order_by=None):
  att_str = ', '.join(attributes)
  query = f'''select {att_str} from {table}'''
  if order_by is not None:
    query += f" order by {order_by}"

  logging.debug(f'{query=}')

  try:
    cur.execute(query)
    save_to_file(query)

    return cur.fetchall()
  
  except Exception as e:
    dialog = ErrorDialog(str(e))
    dialog.exec()


def create_table(cur, name, attributes):
  query = f'''create table {name} ({','.join(attributes)})'''
  query = query.strip()
  logging.debug(f'{query=}')

  try:
    cur.execute(query)
    save_to_file(query)
  
  except Exception as e:
    dialog = ErrorDialog(str(e))
    dialog.exec()
  

def delete_table(cur, name):
  query = f'''drop table {name}'''
  logging.debug(f'{query=}')
  try:
    cur.execute(query)
    save_to_file(query)
    
    dialog = SuccessDialog("Table deleted!")
    dialog.exec()
  
  except Exception as e:
    dialog = ErrorDialog(str(e))
    dialog.exec()

def format_attribute(name, data, not_null, pk, default):
  att = f'{name} {data} '
  if not_null:
    att += 'not null '
  if pk:
    att += 'primary key '
  if default:
    att += 'default '
    if data == 'Integer':
      att += f'{default}'
    else:
      att += f'\'{default}\''
  return att
    

def insert_data(cur, table, data):
  pass

def delete_rows(cur, table, constraints):
  pass

def save_to_file(query):
  # ! database being currently used cannot be logged
  try:
    with open('C:/Users/User/Desktop/ViSQL_log.txt', 'x') as f:
      f.write(f"""/* METADATA:
      host: localhost
      user: root
      created: {time.now()} */\n\n""")

  except FileExistsError:
    pass

  with open('C:/Users/User/Desktop/ViSQL_log.txt', 'a') as f:
    f.write(f'/* {time.now()} */\n')
    f.write(f'{query};\n\n')