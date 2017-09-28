import time
import urllib.request
import urllib.parse
import urllib.error
import pandas as pd
import xml.etree.ElementTree as ET #Python native XML parser
import geocoder #This could(should) be replaced with an XML alternative using the above import.

recordDF = pd.read_csv('FieldRecords.csv')

#
#TODO
#Can reduce GPS API calls by lumping all groups with exactly == coords

#Should notify user of scientific name changes resulting from CoL interaction
#Was suggested to offer a notification of suggested changes with confirmation dialogs.

def recordCell(row,col,val):
    recordDF.set_value(row,col,val)

def roundGPSUncertainty():  #Rounds off the uncertainty value.
    recordDF['coordinateUncertaintyInMeters'] = round(recordDF['coordinateUncertaintyInMeters']).astype(int)

def revGeoLocate(index,record):
    try:
        
        latitude = record['decimalLatitude']
        longitude = record['decimalLongitude']
        
        gAPI = 'AIzaSyC1RdfLi4N2FhjnhzoMG4hOHpXVfV_9iVM'
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
    except requests.exceptions.Timeout:     #If the web has an issue, wait a second and rety (up to 3 times.)
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

    
#Look, just what 'is' a species is in scientific contention.
#So, to address this we're taking the first two (binomial) names and
#attaching whatever is at the end (if anything).

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

    assTaxaGroup = (siteGroups.get(record['siteNum']).tolist())
    assTaxaGroup = sorted([str(item.rstrip()) for item in assTaxaGroup if not (pd.isnull(item) or item is record['scientificName'])])
    if len(assTaxaGroup) > 0: #are there any other taxa found at this site?
        existingAssTaxa = ', ' + record['associatedTaxa'] #if so, let's add some joiner formatting.
        
    else:
        existingAssTaxa = record['associatedTaxa'] #if not, don't include the formatting.
    if existingAssTaxa == 'nan':             #This is a sloppy fix to occasional nan's slipping through for unknown reasons.
        existingAssTaxa = ''
    assTaxaStr = (', '.join(assTaxaGroup) + str(existingAssTaxa)) #then join the user entered to the generated lists
    recordCell(index,'associatedTaxa',assTaxaStr)


#################################################
               #Process workflow#
    
recordDF['siteNum'] = (recordDF['othercatalognumbers'].str.split('-').str[0]).replace("'","")
recordDF['specNum'] = recordDF['othercatalognumbers'].str.split('-').str[1]
#Set up site / specimen columns from the field Numbers.

roundGPSUncertainty() #round the uncertenty to whole meters for label brevity

retryCounter = 0 #necessary to keep a run away recursive error loop. (probably a better way to handle this. See revGeoLocate Function's error handling.

for index, record in recordDF.iterrows():
    if  (pd.notnull(record['scientificName']) and record['specNum'].isnumeric()):
        time.sleep(.1)#Give api requests a brief breather.
        revGeoLocate(index, record)#start with locality info seach
        CoLNameSearch(index, record) #then get any extra scientific name information


siteGroups = (recordDF.groupby('siteNum')['scientificName'].unique())
#get a set of scientificnames grouped according to the site numbers they were in.

for index, record in recordDF.iterrows(): #run this in a seperate iteration so the CoL stuff has happened for each row
    if  (pd.notnull(record['scientificName']) and record['specNum'].isnumeric()):
        associatedTaxaConcat(index,record)

recordDF['county'] = recordDF['county'].str.replace(' County','') #dump word 'county' in county column.

colDropList = ['siteNum','specNum','path']
recordDF = recordDF.drop(colDropList,1) #dump the helper columns (DWC won't know them)

recordDF.to_csv(('processedFieldRecords.csv'),encoding='utf-8') #save the record list as a processed one.

input('Take Note of the Errors and Press "Enter" To Exit')
time.sleep(1)
