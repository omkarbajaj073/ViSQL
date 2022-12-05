from PyQt6.QtWidgets import *
import os
from constants import *

# help_msg = '''
# Things to include - 
# 1. Title contains database name
# 2. Path to the visql file for queries
# 3. Need to put in the quotes for yourself
# 4. Queries - simple drop downs
# 5. Creation - simple dropdowns
# '''

path = os.path.join(os.environ['USERPROFILE'], 'Desktop', 'ViSQL_log.txt')

help_msg = f'''
ViSQL User Guide

1. Accessing a database
    + The title of the ViSQL window indicates whether a databse has been selected or not.
    + If the message reads (NO DATABASE SELECTED), please proceed as indicated below.
        - In the Database Functions dropdown, click Select Database. A dropdown of available databses will appear.
    + To create a databse, click Create Database in the same dropdown.

2. History of all queries performed
    + A log of all queries performed can be found at {path}

3. Note on inputting data (conditions/select/update/aggregate functions)
    + For varchar data type, the user must enter the string with quotes.
    + This applies to anywhere table data is being inputted or referenced.
    + Example: For conditions of relational type, a comparison of a varchar attribute must be done as shown:
        - <attribute> | <operator> | "string"
        - name = "monty python"


MySQL metadata
    + host: {host}
    + user: {user}

'''

class Help(QDialog):
  def __init__(self):
    super().__init__()
    
    layout = QVBoxLayout()
    layout.addWidget(QLabel(help_msg))
    
    # TODO: 
    self.setLayout(layout)
    