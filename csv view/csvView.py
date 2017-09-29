from tkinter import *
from tkinter import Tk, ttk
from tkinter.filedialog import askopenfilename
import os
import csv

 
def donothing():
   x = 0

def openCsvFile():
    name = askopenfilename(initialdir=os.getcwd(),filetypes=(('csv File','*.csv'),),title = 'Select csv File')
    loadCsvFile(name)

def loadCsvFile(name):
    with open(name, newline = "") as file:
        reader = csv.reader(file)

        # r and c tell us where to grid the labels
        r = 0
        for col in reader:
          c = 0
          for row in col:
             # i've added some styling
             label = Label(root, width = 10, height = 2, \
                                   text = row, relief = RIDGE)
             label.grid(row = r, column = c)
             c += 1
          r += 1

    
root = Tk()

menubar = Menu(root)
filemenu = Menu(menubar, tearoff=0)
filemenu.add_command(label="New", command=donothing)
filemenu.add_command(label="Open", command=openCsvFile)
filemenu.add_command(label="Save", command=donothing)
filemenu.add_separator()
filemenu.add_command(label="Exit", command=root.destroy)
menubar.add_cascade(label="File", menu=filemenu)
 
helpmenu = Menu(menubar, tearoff=0)
helpmenu.add_command(label="Help Index", command=donothing)
helpmenu.add_command(label="About...", command=donothing)
menubar.add_cascade(label="Help", menu=helpmenu)
 
editmenu = Menu(menubar, tearoff=0)
editmenu.add_command(label="Cut", command=donothing)
editmenu.add_command(label="Copy", command=donothing)
editmenu.add_command(label="Past", command=donothing)
editmenu.add_command(label="Duplicate Line", command=donothing)
editmenu.add_command(label="Toggle Case", command=donothing)
menubar.add_cascade(label="Edit",menu=editmenu)
 
root.config(menu=menubar)
root.mainloop()



