# Author
# License

import urllib


# returns a list
def colNameSearch(scientificName):
    results = []
    identification = str(scientificName).split()
    if len(identification) == 1:
        identQuery = identification
    elif len(identification) == 2:
        genus = identification[0]
        species = identification[1]
        identQuery = [genus, species]
    elif len(identification) > 2:
        genus = identification[0]
        species = identification[1]
        infraspecies = identification[-1]
        identQuery = [genus, species, infraspecies]

    #This returns an XML from COL of all known info on that Name
    CoLQuery = (ET.parse(urllib.request.urlopen('http://webservice.catalogueoflife.org/col/webservice?name=' + ('+'.join(identQuery)))).getroot())

    if (CoLQuery.attrib['error_message']) is "":

        # If the name given to CoL is not up to date
        if CoLQuery.find('result/name_status').text == 'synonym':

            # Return the Up to date Name
            sciName = (CoLQuery.find('result/accepted_name/name').text)

        # Otherwise, use the passed name (except normalized by their return) why? Any use to this?
        else:
            sciName = (CoLQuery.find('result/name').text)
            # recordCell(index,'scientificName',sciName)
            results.append(sciName)

        # don't want to throw exceptions
        # just handle missing data
        # otherwise we'll have weird things happening to GUI event flow
        try:
            auth = ((CoLQuery.find('result/name_html/i').tail).strip())
            # recordCell(index,'scientificNameAuthorship',auth)
            results.append(auth)
        except AttributeError:
            print('Catalog of Life Failed to find Authority for: ' , identification , '\n')

        # return list of results
        return results

    else:
        print('\nCatalog of Life returned this error: ' + (CoLQuery.attrib['error_message']))
        print('something is wrong with the name: ' , ' '.join(identification),'\n')
