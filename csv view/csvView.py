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
import re
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
   if 'scientificName' not in recordDF:
      recordDF['scientificName'] = ''
   #Set up site / specimen columns from the field Numbers, add in scientificName field (if not present).
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


def revGeoLocate(index,record):
    try:
        global retryCounter
        latitude = record['decimalLatitude']
        longitude = record['decimalLongitude']
#GOOGLE API KEY ENTER HERE        
        gAPI = 
        #g = geocoder.google([latitude,longitude],method='reverse')
        g = geocoder.google([latitude,longitude],method='reverse',key=gAPI)
        print(g)
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
##################################################################################################################
############## CoL query Code ###########################

def CoLNameSearch(index, record):
    try:

        identification = str(recordDF.get_value(index,'scientificName')) #Pulling the user entered scientificName value from table.
        
        if not identification == "nan": #nan is what Pandas fills in for "Not a number"
            identification = identification.split() #Split the identification string into a list of individual words.
            identLevel = len(identification) #count the list of words to det how far into the indentification the user went (genus = 1, species =2, extra crap >2 like "subspecies", or "variety")
            genus = identification[0] #Genus would be the first word in the list
            identQuery = [genus] #building the phrase to query CoL.

#The if block below addresses the fact that there are many partially accepted names beyond the first 2,
#and they might have all sorts of abbrevitations like "Genus species ssp. subspecies" or "Genus species var. variety"

            if (identLevel > 1): #if the identification was more than only genus, then add it to the query
                species = identification[1] #next word should be a species name
                identQuery.append(species) #add species to the phrase to query CoL
                if (identLevel > 2): #If the identification had more text than 2 words then it could be a ton of stuff.
                    infraspecies = identification[-1] #the only word left we might care about is the very last word in the list of words.
                    identQuery.append(infraspecies) #add the last word int he list to the first and second.

            #The line below returns an XML from COL of all known info about the query that was built above.
            CoLQuery = (ET.parse(urllib.request.urlopen('http://webservice.catalogueoflife.org/col/webservice?name=' + ('+'.join(identQuery)))).getroot())

         #This makes sure there was no error message returned from the query.
        if (CoLQuery.attrib['error_message']) is "":

         #the block below handles name changes, if necessary. THIS is the point to offer the user an option to accept or decline
         #the suggested name change.
            if CoLQuery.find('result/name_status').text == 'synonym': #If the name given to CoL is not up to date
                sciName = (CoLQuery.find('result/accepted_name/name').text) #save the up to date name to variable sciName
            else:
                sciName = (CoLQuery.find('result/name').text) #saves the scientific name from the returned value
                                                             #which by any account should be the same as the one sent in excepting
                                                            #Captalization mistakes. We could handle this differently.

            recordCell(index,'scientificName',sciName)  #THIS Line actually edits the existing scientificName field.

#Block Blow will Attempt to strip down the 'authority' field to the basic name, names and or random characters such as: "Joe Smith,(L.)"
            try:
                auth = ((CoLQuery.find('result/name_html/i').tail).strip())
                auth = re.sub(r'\d+','',auth)
                auth = auth.rstrip(', ')
                recordCell(index,'scientificNameAuthorship',auth) #Helper function to update the cell with the new string.

#IF the attempt fails, it'll be an attribute failure, because there is NO authority returned for this. My error handling
#was to print the warning to the user and move on with the process anyways. This means the process does not stop, only warns.

            except AttributeError:
                print('Catalog of Life Failed to find Authority for: ' , identification , '\n')

#Returning to the if statement above, if it is infact returned with an "error mesasge" then warn the use the name is probably
#Misspelled (or it is something new they've discovered and named) At any rate, it does not exist in CoL.
#Again, this does not stop the process, only warns the user that nothing can be done with THIS scientific name.
#This is 99% of the time going to be because of a typo on the user's part. So we should get the message to them.
        else:
            print('\nCatalog of Life returned this error: ' + (CoLQuery.attrib['error_message']))
            print('something is wrong with the name: ' , ' '.join(identification),'\n')



    except IOError: #If some IOError is returned from the CoL Query, handle it by printing a warning to the user.
                   # This does not stop the process, only warns the user and moves on.
        print('IOError, something went wrongwith CatalogOfLife query')
        pass #Pass just means to pass the exception off to ... nowhere and ignore it now that we've handled it (by warning)

#The code below must be called after CoL Queries. It handles building the associated taxa field.
      
def associatedTaxaConcat(index,record):

#This uses Pandas Groupby Function to lump all records with the same site Number togeather, which also have unique scientificNames
    siteGroups = (recordDF.groupby('siteNum')['scientificName'].unique()) 

    assTaxaGroup = (siteGroups.get(record['siteNum']).tolist()) #Add each record in the group to a list

    #List comprehension for sorting (alphabetically) the list according to scientific names
    assTaxaGroup = sorted([str(item.rstrip()) for item in assTaxaGroup if not (pd.isnull(item) or item is record['scientificName'])])

    if len(assTaxaGroup) > 0: #are there any other taxa found at this site?
        existingAssTaxa = ', ' + record['associatedTaxa'] #if so, join them into a string
        
    else:
        existingAssTaxa = record['associatedTaxa'] #if not, don't include them.
    assTaxaStr = (', '.join(assTaxaGroup) + str(existingAssTaxa)) #either way, join the user entered stuff to the generated lists
    if not assTaxaStr == 'nan':  #I don't know why, sometimes a 'nan' slips through, so I'm checking for it before updating cell.
        recordCell(index,'associatedTaxa',assTaxaStr) #Helper function to update the cell. with new string.

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


