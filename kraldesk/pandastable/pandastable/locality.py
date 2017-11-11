# Author
# License
import requests

# status codes
# link -> https://developers.google.com/maps/documentation/geocoding/intro#StatusCodes
# link -> https://developers.google.com/maps/documentation/geocoding/intro#ReverseGeocoding


def reverseGeoCall(latitude, longitude):
    apiKey = 'AIzaSyCwugFdGLz6QUtcYqD1z0PKKsYJhay3vIg'
    apiUrl = 'https://maps.googleapis.com/maps/api/geocode/json?latlng=' + str(latitude) + ',' + str(longitude) + '&key=' + apiKey
    apiCall = requests.get(apiUrl)

    status = apiCall.json()['status']
    # api returns OK (query went through, received results)
    if status == 'OK':
        results = apiCall.json()['results']
        addressComponents = results[0]['address_components']
        return addressComponents
    # some error occured
    # will be indicated by the status
    else:
        status = str(status)
        return status
