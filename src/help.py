from PyQt6.QtWidgets import *



help_msg = '''
Things to include - 
1. Title contains database name
2. Path to the visql file for queries
3. Need to put in the quotes for yourself
4. Queries - simple drop downs
5. Creation - simple dropdowns
'''


class Help(QDialog):
  def __init__(self):
    super().__init__()
    
    layout = QVBoxLayout()
    layout.addWidget(QLabel(help_msg))
    
    # TODO: 
    self.setLayout(layout)
    