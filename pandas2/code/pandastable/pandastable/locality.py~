# Author
# License
import requests


def genLocality(latitude, longitude):
    apiKey = 'AIzaSyCwugFdGLz6QUtcYqD1z0PKKsYJhay3vIg'
    apiUrl = 'https://maps.googleapis.com/maps/api/geocode/json?latlng=' + str(latitude) + ',' + str(longitude) + '&key=' + apiKey
    # add some error checking
    apiCall = requests.get(apiUrl)
    results = apiCall.json()['results']
    formattedAddress = results[0]['formatted_address']
    return formattedAddress


test = genLocality(34.716603, -85.196637)

print("address is: " + test)
