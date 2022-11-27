from PyQt6.QtWidgets import *
import mysql.connector as connector
import logging
from constants import *
from datetime import datetime as time

import os

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


def get_data(cur, table, attributes, constraints=None, order_by=None):
  att_str = ', '.join(attributes)
  query = f'''select {att_str} from {table}'''
  # * FLAG @Ananth Use this to add the constraints to the query. 
  if constraints:
    query += f" where {' and '.join(constraints)}"
    
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
    
    
def update_data(cur, table, attribute, value, constraints=None):
  query = f'''update {table} set {attribute}={value}'''
  if constraints:
    query += f" where {' and '.join(constraints)}"

  logging.debug(f'{query=}')

  try:
    cur.execute(query)
    save_to_file(query)
    dialog = SuccessDialog("Updated data")
    dialog.exec()
  except Exception as e:
    dialog = ErrorDialog(str(e))
    dialog.exec()


def group_by_data(cur, table, func, attribute, constraints, group_attr):
  if func == 'count(*)':
    func = 'count'
    attribute = '*'
  query = f'''select {group_attr}, {func}({attribute}) from {table}'''
  
  if constraints:
    query += f" where {' and '.join(constraints)}"
    
  query += f" group by {group_attr}"

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

def format_insert_data(data):
  formatted = []
  for relation in data:
    row = []
    for item in relation:
      row.append(eval(item))

    formatted.append(tuple(row))

  logging.debug(f'{formatted=}')

  return formatted

    
def insert_data(con, table, data):
  cur = con.cursor()
  query = f'''insert into {table} values'''

  for row in data:
    query += f" {row},"

  query = query.rstrip(',')

  logging.info(f'{query=}')

  try:
    cur.execute(query)
    con.commit()
    save_to_file(query)
    dialog = SuccessDialog("Data Inserted!")
    dialog.exec()

  except Exception as e:
    dialog = ErrorDialog(str(e))
    dialog.exec()

def delete_rows(con, table, constraints):
  cur = con.cursor()
  query = f'''delete from {table}'''

  if constraints:
    query += f" where {' and '.join(constraints)}"

  logging.info(f'{query=}')

  try:
    cur.execute(query)
    con.commit()
    save_to_file(query)
    dialog = SuccessDialog("Deleted data")
    dialog.exec()

  except Exception as e:
    dialog = ErrorDialog(str(e))
    dialog.exec()


def natural_join(cur, table1, table2):
  query = f"select * from {table1} natural join {table2}"
  logging.debug(f'{query=}')
  try:
    cur.execute(query)
    results = cur.fetchall()
    return results
  except Exception as e:
    dialog = ErrorDialog(str(e))
    dialog.exec()
    


def save_to_file(query):
  # ! database being currently used cannot be logged
  path = os.path.join(os.environ['USERPROFILE'], 'Desktop', 'ViSQL_log.txt')
  try:
    with open(path, 'x') as f:
      f.write(f"""/* METADATA:
      host: {host}
      user: {user}
      created: {time.now()} */\n\n""")

  except FileExistsError:
    pass

  # with open('C:/Users/Admin/Desktop/ViSQL_log.txt', 'a') as f:
  with open(path, 'a') as f:
    f.write(f'/* {time.now()} */\n')
    f.write(f'{query};\n\n')