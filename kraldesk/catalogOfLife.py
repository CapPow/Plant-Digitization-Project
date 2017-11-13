#!/usr/bin/env python
# Author
# License

import urllib.request
import re
import xml.etree.ElementTree as ET
import html
import sys


# catalog of life scientific name search
# queries catalog of life with a scientific name
# returns the most up-to-date, accepted, scientific name for a specimen
# or an error message to calling function
def colNameSearch(givenScientificName):
    identification = str(givenScientificName).split()
    if givenScientificName != '':
        identQuery = [identification[0]]
    # no sci-name in row
    else:
        return 'empty_string'
    if len(identification) > 1:
        identQuery.append(identification[1])
        if len(identification) > 2:
            identQuery.append(identification[-1])
    CoLQuery = ET.parse(urllib.request.urlopen('http://webservice.catalogueoflife.org/col/webservice?name={}&response=terse'.format('+'.join(identQuery)), timeout=30)).getroot()

    #<status>accepted name|ambiguous synonym|misapplied name|privisionally acceptedname|synomym</status>  List of potential name status
    for result in CoLQuery.findall('result'):
        nameStatus = result.find('name_status').text
        if nameStatus == 'accepted name':
            name = result.find('name').text
            try:
                authorityName = result.find('name_html').find('i').tail
            except AttributeError:
                authorityName = html.unescape(result.find('name_html').text)
                authorityName = authorityName.split('</i> ')[1]
            authorityName = re.sub(r'\d+','',str(authorityName))
            authorityName = authorityName.strip().rstrip(',')
            return (name,authorityName)
        elif 'synonym' in nameStatus:
            return colNameSearch(result.find('accepted_name/name').text)
        else:
            return 'not_accepted_or_syn'
