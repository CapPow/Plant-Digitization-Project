# Author
# License
import requests

def genLocality(latitude, longitude):
    apiKey = 'AIzaSyCwugFdGLz6QUtcYqD1z0PKKsYJhay3vIg'
    apiUrl = 'https://maps.googleapis.com/maps/api/geocode/json?latlng=' + str(latitude) + ',' + str(longitude) + '&key=' + apiKey
    # add some error checking for api call
    apiCall = requests.get(apiUrl)
    results = apiCall.json()['results']
    # guaranteed to return 8 elements
    # see link -> https://developers.google.com/maps/documentation/geocoding/intro#ReverseGeocoding
    addressComponents = results[0]['address_components']
    return addressComponents


def dolittle():
    print("Do little called")
    return
