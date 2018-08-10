from tkinter import *
from core import Table
import dialogs
import pandas as pd

class PDDesktop(Frame):
        """Initiate the GUI"""
        def __init__(self, parent=None):
            self.parent = parent
            Frame.__init__(self)
            self.main = self.master
            self.main.geometry('800x400+200+100')
            self.main.title('PD-Desktop')
            f = Frame(self.main)
            f.pack(fill=BOTH,expand=1)
            df = pd.DataFrame()
            self.table = pt = Table(f, dataframe=df,
                                    showtoolbar=True, showstatusbar=False)
            self.createMenuBar()
            pt.show()
            #return

        def createMenuBar(self):
                """Create the menu bar for the application. """
        
                self.menu = Menu(self.main)
                self.file_menu={'01New Project':{'cmd': self.table.new},
                                '02Load Records':{'cmd':self.table.importCSV},
                                '03Save As':{'cmd':self.table.saveAs},
                                '04sep':'',
                                '05Export for Database':{'cmd':self.table.saveForDatabase},
                                '06Make Labels':{'cmd':self.table.genLabelPDF},
                                '07sep':'',
                                '08Quit':{'cmd':self.quit}}
        
                self.file_menu = self.createPulldown(self.menu,self.file_menu)
                self.menu.add_cascade(label='File',menu=self.file_menu['var'])
        
                self.edit_menu={'01Undo Last Change':{'cmd': self.table.undo},
                                '02Preferences' :{'cmd': self.table.showPrefs},
                                '03sep':'',
                                '04Find/Replace':{'cmd':self.findText},
                                '05sep':'',
                                '06Add Row Site to Records':{'cmd': self.table.addSite},
                                '07Add Row From Site':{'cmd':self.table.addRowFromSite}
                                }
                self.edit_menu = self.createPulldown(self.menu,self.edit_menu)
                self.menu.add_cascade(label='Edit',menu=self.edit_menu['var'])
        
        
#                self.view_menu={'01Zoom In':{'cmd': lambda: self._call('zoomIn')},
#                                '02Zoom Out':{'cmd': lambda: self._call('zoomOut')},
#                                '03Wrap Columns':{'cmd': lambda: self._call('setWrap')},
#                                '04sep':'',
#                                '05Dark Theme':{'cmd': lambda: self._call('setTheme', name='dark')},
#                                '06Bold Theme':{'cmd': lambda: self._call('setTheme', name='bold')},
#                                '07Default Theme':{'cmd': lambda: self._call('setTheme', name='default')},
#                                }
#                self.view_menu = self.createPulldown(self.menu,self.view_menu)
#                self.menu.add_cascade(label='View',menu=self.view_menu['var'])
#        
#                self.table_menu={'01Describe Table':{'cmd':self.describe},
#                                 '02Convert Column Names':{'cmd':lambda: self._call('convertColumnNames')},
#                                 '03Convert Numeric':{'cmd': lambda: self._call('convertNumeric')},
#                                 '04Clean Data': {'cmd': lambda: self._call('cleanData')},
#                                 '05Find Duplicates': {'cmd': lambda: self._call('findDuplicates')},
#                                 '06Correlation Matrix':{'cmd': lambda: self._call('corrMatrix')},
#                                 '07Concatenate Tables':{'cmd':self.concat},
#                                 '08Table to Text':{'cmd': lambda: self._call('showasText')},
#                                 '09Table Info':{'cmd': lambda: self._call('showInfo')},
#                                 '10sep':'',
#                                 '11Transform Values':{'cmd': lambda: self._call('transform')},
#                                 '12Group-Aggregate':{'cmd': lambda: self._call('aggregate')},
#                                 '13Merge/Concat Tables': {'cmd': lambda: self._call('doCombine')},
#                                 '14Pivot Table':{'cmd': lambda: self._call('pivot')},
#                                 '15Melt Table':{'cmd': lambda: self._call('melt')},
#                                 '16Time Series Resampling':{'cmd': lambda: self._call('resample')}
#                                }
#                self.table_menu = self.createPulldown(self.menu,self.table_menu)
#                self.menu.add_cascade(label='Tools',menu=self.table_menu['var'])
#        
#                self.dataset_menu={'01Sample Data':{'cmd':self.sampleData},
#                                 '03Iris Data':{'cmd': lambda: self.getData('iris.csv')},
#                                 '03Tips Data':{'cmd': lambda: self.getData('tips.csv')},
#                                 '04Stacked Data':{'cmd':self.getStackedData},
#                                 '05Pima Diabetes':
#                                     {'cmd': lambda: self.getData('pima.csv')},
#                                 '06Titanic':
#                                     {'cmd': lambda: self.getData('titanic3.csv')},
#                                 '07miRNA expression':
#                                     {'cmd': lambda: self.getData('miRNA.csv')},
#                                 '08CO2 time series':
#                                     {'cmd': lambda: self.getData('co2-ppm-mauna-loa.csv')}
#                                 }
#                self.dataset_menu = self.createPulldown(self.menu,self.dataset_menu)
#                self.menu.add_cascade(label='Datasets',menu=self.dataset_menu['var'])
#        
#                self.plots_menu={'01Store plot':{'cmd':self.addPlot},
#                                 '02Clear plots':{'cmd':self.updatePlotsMenu},
#                                 '03PDF report':{'cmd':self.pdfReport},
#                                 '04sep':''}
#                self.plots_menu = self.createPulldown(self.menu,self.plots_menu)
#                self.menu.add_cascade(label='Plots',menu=self.plots_menu['var'])
#        
#                self.plugin_menu={'01Update Plugins':{'cmd':self.discoverPlugins},
#                                  '02Install Plugin':{'cmd':self.installPlugin},
#                                  '03sep':''}
#                self.plugin_menu=self.createPulldown(self.menu,self.plugin_menu)
#                self.menu.add_cascade(label='Plugins',menu=self.plugin_menu['var'])
        
                self.help_menu={'01Online Help':{'cmd':self.table.helpDocumentation}}

                self.help_menu=self.createPulldown(self.menu,self.help_menu)
                self.menu.add_cascade(label='Help',menu=self.help_menu['var'])
        
                self.main.config(menu=self.menu)
                return
        
        def createPulldown(self, menu, dict):
            """Create pulldown menu, returns a dict.
            Args:
                dict: dictionary of the form -
                {'01item name':{'cmd':function name, 'sc': shortcut key}}
            """
    
            var = Menu(menu,tearoff=0)
            dialogs.applyStyle(var)
            items = list(dict.keys())
            items.sort()
            for item in items:
                if item[-3:] == 'sep':
                    var.add_separator()
                else:
                    command = dict[item]['cmd']
                    label = '%-25s' %(item[2:])
                    if 'img' in dict[item]:
                        img = dict[item]['img']
                    else:
                        img = None
                    if 'sc' in dict[item]:
                        sc = dict[item]['sc']
                        #bind command
                        #self.main.bind(sc, command)
                    else:
                        sc = None
                    var.add('command', label=label, command=command, image=img,
                            compound="left")#, accelerator=sc)
            dict['var'] = var
            return dict
        def findText(self):
    
            table = self.table
            if hasattr(table, 'searchframe') and table.searchframe != None:
                table.searchframe.close()
            else:
                table.findText()
            return


app = PDDesktop()
#launch the app
app.mainloop()
