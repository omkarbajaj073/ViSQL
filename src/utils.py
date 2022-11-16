import mysql.connector as connector
import logging

logging.basicConfig(level=logging.DEBUG)

def get_databases():
  con = connector.connect(host='localhost', user='root', password='sql123')
  cur = con.cursor()
  cur.execute('show databases')
  dbs = cur.fetchall()
  dbs = map(lambda i: i[0], dbs)
  return dbs


def create_database(name):
  con = connector.connect(host='localhost', user='root', password='sql123')
  cur = con.cursor()
  cur.execute(f'create database {name}')
  con.close()

def get_table_attributes(cur, table):
  cur.execute(f'show columns from {table}')
  cols = cur.fetchall()
  cols = list(map(lambda i: i[0], cols))
  return cols


def get_tables(cur):
  cur.execute('show tables')
  tables = cur.fetchall()
  tables = map(lambda i: i[0], tables)
  return tables

def get_data(cur, table, attributes, order_by=None):
  att_str = ','.join(attributes)
  query = f'''
  select {att_str} from {table}
  '''
  if order_by is not None:
    query += f"order by {order_by}"

  cur.execute(query)
  return cur.fetchall()


def create_table(cur, name, attributes):
  query = f'''
  create table {name} ({','.join(attributes)});
  '''
  query = query.strip()
  logging.debug(f'{query=}')
  cur.execute(query)


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