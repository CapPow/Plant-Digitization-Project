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
    CoLQuery = ET.parse(urllib.request.urlopen('http://webservice.catalogueoflife.org/col/webservice?name=' + ('+'.join(identQuery)), timeout=30))
    # we need to be able to choose the best possible (most up-to-date) scientific name from XML results
    rootCoLQuery = CoLQuery.getroot()
    for result in rootCoLQuery.findall('result'):
        for tag in result.findall('accepted_name'):
            name = tag.find('name').text
            nameStatus = tag.find('name_status').text
            name_html = tag.find('name_html').find('i').tail
            print("name: " + name)
            print("nameStatus: " + nameStatus)
            print("name_html: " + name_html)

    # scientific name for plant specimen
    if (rootCoLQuery.attrib['error_message']) is "":
        text = rootCoLQuery.find('result/name_status').text
        text = text.lower()
        if 'synonym' in text:
            sciName = (rootCoLQuery.find('result/accepted_name/name').text)
            results.append(str(sciName))
        else:
            sciName = (rootCoLQuery.find('result/name').text)
            results.append(str(sciName))

        # authorship
        auth = ((rootCoLQuery.find('result/name_html/i').tail).strip())
        if auth != '' and auth != 'L.':
            auth = re.sub(r'\d+','',auth)
            auth = auth.rstrip(', ')
        return results
    else:
        return []
