from tkinter import *
from core import Table
import pandas as pd

class TestApp(Frame):
        """Basic test frame for the table"""
        def __init__(self, parent=None):
            self.parent = parent
            Frame.__init__(self)
            self.main = self.master
            self.main.geometry('600x400+200+100')
            self.main.title('KralDesk')
            f = Frame(self.main)
            f.pack(fill=BOTH,expand=1)
            df = pd.DataFrame()
            self.table = pt = Table(f, dataframe=df,
                                    showtoolbar=True, showstatusbar=False)
            pt.show()
            return

app = TestApp()
#launch the app
app.mainloop()
