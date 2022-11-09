import mysql.connector as connector
from utils import * 

con = connector.connect(host='localhost', user='root', password='sql123', database='institution')

cur = con.cursor()

print(get_data(cur, 'faculty', ['tid', 'fname', 'age']))