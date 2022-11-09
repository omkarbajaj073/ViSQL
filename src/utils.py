import mysql.connector as connector

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
  cols = map(lambda i: i[0], cols)
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