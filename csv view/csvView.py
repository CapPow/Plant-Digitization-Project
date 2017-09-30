from tkinter import *
from tkinter import Tk, ttk
from tkinter.filedialog import askopenfilename, asksaveasfilename
import os
import csv
from PIL import Image
#####record processing imports#########
import time
import urllib.request
import requests
import urllib.parse
import urllib.error
import pandas as pd
import xml.etree.ElementTree as ET #Python native XML parser
import geocoder #This could(should) be replaced with an XML alternative using the above import.
#######################################

 
def donothing():
   x = 0

def openCsvFile():
   csvName = askopenfilename(initialdir=os.getcwd(),filetypes=(('csv File','*.csv'),),title = 'Select csv File')
   loadCsvFile(csvName)
   prepCsvAsDataFrame(csvName) # do this for the recordProcessing steps


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

def openLogoFile():
    logoPath = askopenfilename(initialdir=os.getcwd(),filetypes=(('Image Files',('*.jpg','*.png','*.bmp')),),title = 'Select csv File')
    loadLogoFile(logoPath)
    
def loadLogoFile(name):
   logoImg = Image.open(name)

##########Adding in Functions from recordProcess.py ################

def prepCsvAsDataFrame(csvName):
   
   global recordDF #Should change this to some sort of class method? for Cleaner Python?
   recordDF = pd.read_csv(csvName) #Read the selected Data into a Pandas DataFrame (Used for record Processing functions)
   recordDF['siteNum'] = (recordDF['othercatalognumbers'].str.split('-').str[0]).replace("'","")
   recordDF['specNum'] = recordDF['othercatalognumbers'].str.split('-').str[1]
   #Set up site / specimen columns from the field Numbers.
   recordDF['coordinateUncertaintyInMeters'] = round(recordDF['coordinateUncertaintyInMeters']).astype(int)
   #^^^ round the uncertenty to whole meters for label brevity
   global retryCounter
   retryCounter = 0 #necessary to keep a run away recursive error loop. (probably a better way to handle this. See revGeoLocate Function's error handling.
   #^^^ This probably belongs somewhere else to keep the code neat?
   
def recordProcess():
   global recordDF
   for index, record in recordDF.iterrows():
       if  (pd.notnull(record['scientificName']) and record['specNum'].isnumeric()):
           time.sleep(.1)#Give api requests a brief breather.
           revGeoLocate(index, record)#start with locality info seach
           CoLNameSearch(index, record) #then get any extra scientific name information

   for index, record in recordDF.iterrows(): #run this in a seperate iteration so the CoL stuff has happened for each row
       if  (pd.notnull(record['scientificName']) and record['specNum'].isnumeric()):
           associatedTaxaConcat(index,record)

   recordDF['county'] = recordDF['county'].str.replace(' County','') #dump word 'county' in county column.
   colDropList = ['siteNum','specNum','path'] #These fields are for processing use, the user shouldn't need them anymore.
   recordDF = recordDF.drop(colDropList,1) #dump the helper columns (DWC won't know them)

def saveProcessedRecords():
   saveFileName = asksaveasfilename(initialdir=os.getcwd(),filetypes=(('csv','*.csv'),),title = 'Save As')
   recordDF.to_csv((saveFileName),encoding='utf-8') #save the record list as a processed one.
   #^^^^Currently this just dumps it into the folder. "Save As" is probably wise.

def revGeoLocate(index,record):
    try:
        global retryCounter
        latitude = record['decimalLatitude']
        longitude = record['decimalLongitude']
#GOOGLE API KEY ENTER HERE        
        gAPI = ''
        #g = geocoder.google([latitude,longitude],method='reverse')
        g = geocoder.google([latitude,longitude],method='reverse',key=gAPI)
        colDict = {'country':g.country_long,'stateProvince':g.state_long,'county':g.county,'municipality':g.city,'path':g.street}
        #dictionary to store the column name to the cell value.
        autoLocalityList = [] #empty list to build the locality string from
        for item in list(colDict.keys()): #for each key in the dictionary, do stuff..
            dictValue = colDict.get(item)
            recordCell(index,item,dictValue)

            if not (item =='country'): #omit country from the locality string (but still store it in a field)
                autoLocalityList.append(dictValue)

        autoLocalityList.append(recordDF.get_value(index,'locality')) #Build locality string.
        recordCell(index,'locality',(", ".join(autoLocalityList))) #save this row and move on.
        retryCounter = 0

    except (IOError, ValueError) as e: #IO Error is the return from geocoder recieving bad info. Not sure how to warn user that
                    #some fields will be left blank when this happens. the PRINT is a temporary solution for me.
        print(e,': probably bad or missing GPS')
        pass
    except TypeError as e:
        print('\n',e, ': GeoLocate Request Denied on index # ',index)
    except requests.ConnectionError:      #If the web has an issue, wait a second and rety (up to 3 times.)
        if retryCounter < 3:
            print('request time out, retrying...')
            time.sleep(1)
            revGeoLocate(index,record)
            retryCounter = retryCounter + 1
        else:
            retryCounter = 0
            print('multiple requests failed, giving up')
            pass

def CoLNameSearch(index, record):
    try:

        identification = str(recordDF.get_value(index,'scientificName'))
        
        if not identification == "nan":  #empty strings return false in python, therefore if mystring asks if mystring is not empty.
            identification = identification.split() #Get the identification entered by the user as a list of words
            identLevel = len(identification)
            genus = identification[0]
            identQuery = [genus]
            
            if (identLevel > 1):
                species = identification[1]
                identQuery.append(species)
                if (identLevel > 2):
                    infraspecies = identification[-1] #Super cool, index from end of array syntax!
                    identQuery.append(infraspecies)
            #^^^^Deciding what to do based on how many words the sciName was. 1=genus, 2=genus species 3=taxonomic grab bag (so only keep last word)
            CoLQuery = (ET.parse(urllib.request.urlopen('http://webservice.catalogueoflife.org/col/webservice?name=' + ('+'.join(identQuery)))).getroot()) #This returns an XML from COL of all known info on that Name
        if (CoLQuery.attrib['error_message']) is "":

            if CoLQuery.find('result/name_status').text == 'synonym': #If the name given to CoL is not up to date
                sciName = (CoLQuery.find('result/accepted_name/name').text) #Return the Up to date Name
            else:           #Otherwise, use the passed name (except normalized by their return) why? Any use to this?
                sciName = (CoLQuery.find('result/name').text)

            recordCell(index,'scientificName',sciName)

            try:
                auth = ((CoLQuery.find('result/name_html/i').tail).strip())
                recordCell(index,'scientificNameAuthorship',auth)
            except AttributeError:
                print('Catalog of Life Failed to find Authority for: ' , identification , '\n')


        else:
            print('\nCatalog of Life returned this error: ' + (CoLQuery.attrib['error_message']))
            print('something is wrong with the name: ' , ' '.join(identification),'\n')



    except IOError: #IO Error is the return from geocoder recieving bad info. Not sure how to warn user that
                #some fields will be left blank when this happens. the PRINT is a temporary solution for me.
        print('IOError, something went wrongwith CatalogOfLife query')
        pass

def associatedTaxaConcat(index,record):
    siteGroups = (recordDF.groupby('siteNum')['scientificName'].unique())
    #^^^^get a set of scientificnames grouped according to the site numbers they were in.
    assTaxaGroup = (siteGroups.get(record['siteNum']).tolist())
    assTaxaGroup = sorted([str(item.rstrip()) for item in assTaxaGroup if not (pd.isnull(item) or item is record['scientificName'])])
    if len(assTaxaGroup) > 0: #are there any other taxa found at this site?
        existingAssTaxa = ', ' + record['associatedTaxa'] #if so, let's add some joiner formatting.
        
    else:
        existingAssTaxa = record['associatedTaxa'] #if not, don't include the formatting.
    assTaxaStr = (', '.join(assTaxaGroup) + str(existingAssTaxa)) #then join the user entered to the generated lists
    if not assTaxaStr == 'nan':             #This is a sloppy fix to occasional nan's slipping through for unknown reasons.
        recordCell(index,'associatedTaxa',assTaxaStr)

def recordCell(row,col,val):
    recordDF.set_value(row,col,val)
####################################################################

root = Tk()

menubar = Menu(root)
filemenu = Menu(menubar, tearoff=0)
filemenu.add_command(label="New", command=donothing)
filemenu.add_command(label="Open", command=openCsvFile)
filemenu.add_command(label="Process Records", command=recordProcess)
filemenu.add_command(label="Save Records As", command=saveProcessedRecords)
filemenu.add_separator()
filemenu.add_command(label="Exit", command=root.destroy)
menubar.add_cascade(label="File", menu=filemenu)
 
editmenu = Menu(menubar, tearoff=0)
editmenu.add_command(label="Select Collection Logo", command=openLogoFile)
menubar.add_cascade(label="Edit",menu=editmenu)

helpmenu = Menu(menubar, tearoff=0)
helpmenu.add_command(label="Help Index", command=donothing)
helpmenu.add_command(label="About...", command=donothing)
menubar.add_cascade(label="Help", menu=helpmenu)
 
root.config(menu=menubar)
root.mainloop()







