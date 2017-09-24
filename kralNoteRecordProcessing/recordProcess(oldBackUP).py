import time, urllib.request, urllib.parse, urllib.error, simplejson
import pandas as pd
import xml.etree.ElementTree as ET #Python native XML parser
import geocoder #This could(should) be replaced with an XML alternative using the above import.
import time

recordDF = pd.read_csv('FieldRecords.csv')

#
#TODO
#Can vastly reduce GPS API calls by lumping all groups with exactly == coords and
#replicating the fields instead of recalling the data.
#
############

############

recordDF['siteNum'] = recordDF['othercatalognumbers'].str.split('-').str[0]
recordDF['specNum'] = recordDF['othercatalognumbers'].str.split('-').str[1]
#Set up site / specimen columns from the field Numbers.
siteGroups = (recordDF.groupby('siteNum')['scientificName'].unique())
#also get a set of scientificnames grouped according to the site numbers they were in.

#This section could be improved by combining with the for index spec/field num determinations below.

def recordCell(row,col,val):
    recordDF.set_value(row,col,val)

for index, record in recordDF.iterrows():
    if  pd.notnull(recordDF.loc[index,'scientificName']):
        time.sleep(.1) #I HATE doing this, AND I don't know if it is necessary. BUT many example codes and
        #SO examples often add this delay, not entirely sure it is necessary.

#Field automation techniques:
        
    #starting with GPS > google (possibly others) Geolocation field translations
        try:
            latitude = record['decimalLatitude']
            longitude = record['decimalLongitude']
            g = geocoder.google([latitude,longitude],method='reverse')

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

        except (IOError, ValueError) as e: #IO Error is the return from geocoder recieving bad info. Not sure how to warn user that
                        #some fields will be left blank when this happens. the PRINT is a temporary solution for me.
            print('IOError, probably bad or missing GPS')
            pass
    ######################This section handles the Scientific Name (identification) >  Catalog of Life (COL) interactions##################

    #COL is the standard which all symbitota portals verify consistency with taxonmic nameing conventions.
    #This means, old names are normalized into commonly accepted ones and proper authorities (person who discovered it) are entered.

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

            
        #Look, just what 'is' a species is in scientific contention. So, to address this we're taking the first two (binomial) names, which are accepted and then
        #attaching whatever is at the end (if anything).
        #This means we address the many forms of "this is sorta different than others of the same species" like "Variety" and "subspecies."                

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
                        time.sleep(2.5)

                else:
                    print('\nCatalog of Life returned this error: ' + (CoLQuery.attrib['error_message']))
                    print('something is wrong with the name: ' , ' '.join(identification),'\n')
                    time.sleep(2.5)


        except IOError: #IO Error is the return from geocoder recieving bad info. Not sure how to warn user that
                        #some fields will be left blank when this happens. the PRINT is a temporary solution for me.
            print('IOError, something went wrongwith CatalogOfLife query')
            pass

#################################################################################################################
#Time to concat the associated Taxa fields#

#NOTE Should complete previous iteration first then do this to adjust the sci name fields before concating them.
        
    assTaxaGroup = (siteGroups.get(record['siteNum']).tolist())

    assTaxaGroup = sorted([str(item.rstrip()) for item in assTaxaGroup if not (pd.isnull(item) or item is record['scientificName'])])
   
    if len(assTaxaGroup) > 0: #are there any other taxa found at this site?
        existingAssTaxa = ', ' + record['associatedTaxa'] #if so, let's add some joiner formatting.
    else:
        existingAssTaxa = record['associatedTaxa'] #if not, don't include the formatting.

    assTaxaStr = (', '.join(assTaxaGroup) + existingAssTaxa) #then join the user entered to the generated lists

    recordCell(index,'associatedTaxa',assTaxaStr)

    

  
#tempDF = recordDF.sort_values(['othercatalognumbers']).groupby('othercatalognumbers', sort=False)
#.scientificName.apply(', '.join).reset_index(name='assTaxaList')
#print(tempDF)

recordDF.to_csv(('processedFieldRecords.csv'),encoding='utf-8') #save the record list as a processed one.

