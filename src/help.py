from PyQt6.QtWidgets import *

class Help(QDialog):
  def __init__(self):
    super().__init__()
    
    layout = QVBoxLayout()
    layout.addWidget(QLabel("Sanity check!!"))
    
    # TODO: 
    self.setLayout(layout)
    