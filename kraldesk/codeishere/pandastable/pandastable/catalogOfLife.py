# Author
# License

import urllib
import xml.etree.ElementTree as ET
import re


# takes scientific name (string argument)
# returns up-to-date scientific name of plant
# may also return authorship
# uses Catalog of Life
def colNameSearch(scientificName):
    results = []
    identification = str(scientificName).split()
    if scientificName != '':
        identQuery = [identification[0]]
    else:
        return []
    if len(identification) > 1:
        identQuery.append(identification[1])
        if len(identification) > 2:
            identQuery.append(identification[-1])

    # can view XML results by using link and sci name
    CoLQuery = (ET.parse(urllib.request.urlopen('http://webservice.catalogueoflife.org/col/webservice?name=' + ('+'.join(identQuery)))).getroot())

    # scientific name for plant specimen
    if (CoLQuery.attrib['error_message']) is "":
        text = CoLQuery.find('result/name_status').text
        text = text.lower()
        if 'synonym' in text:
            sciName = (CoLQuery.find('result/accepted_name/name').text)
            results.append(str(sciName))
            print("(synonym) scientific name: " + sciName)
        else:
            sciName = (CoLQuery.find('result/name').text)
            print("scientific name: " + sciName)
            results.append(str(sciName))
        # authorship
        auth = ((CoLQuery.find('result/name_html/i').tail).strip())
        # assuming we don't want empty L. ... not sure what this means
        if auth != '' and auth != 'L.':
            auth = re.sub(r'\d+','',auth)
            auth = auth.rstrip(', ')
            results.append(str(auth))
            for elem in results:
                print("results is: " + str(elem))
        return results
    else:
        return []
