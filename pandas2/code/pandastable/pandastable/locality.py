# Author
# License
import requests

# status codes
# link -> https://developers.google.com/maps/documentation/geocoding/intro#StatusCodes
# link -> https://developers.google.com/maps/documentation/geocoding/intro#ReverseGeocoding
def genLocality(latitude, longitude):
    apiKey = 'AIzaSyCwugFdGLz6QUtcYqD1z0PKKsYJhay3vIg'
    apiUrl = 'https://maps.googleapis.com/maps/api/geocode/json?latlng=' + str(latitude) + ',' + str(longitude) + '&key=' + apiKey
    apiCall = requests.get(apiUrl)
    # error checking here
    status = apiCall.json()['status']
    
    results = apiCall.json()['results']
    addressComponents = results[0]['address_components']
    return addressComponents


def dolittle():
    print("Do little called")
    return
