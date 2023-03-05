from tkinter                 import PhotoImage, SW
from NeacCore.NeacLocation   import NeacLocation
from random                  import randrange

class NeacStation(NeacLocation):
    
    def __init__(self, coordHelper):
        NeacLocation.__init__(self)
        self.name           = ""
        self.id             = 0
        self.label_position = 'N'
        self.coordHelper    = coordHelper

    def set_id(self, id):
        self.id = id

    def set_name(self, name):
        self.name = name

    def set_label_position(self, position):
        self.labelPosition = position

