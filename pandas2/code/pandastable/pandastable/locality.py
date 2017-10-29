# Author
# License
import requests

# status codes
# link -> https://developers.google.com/maps/documentation/geocoding/intro#StatusCodes
# link -> https://developers.google.com/maps/documentation/geocoding/intro#ReverseGeocoding


def reverseGeoCall(latitude, longitude):
    apiKey = 'add yours'
    apiUrl = 'https://maps.googleapis.com/maps/api/geocode/json?latlng=' + str(latitude) + ',' + str(longitude) + '&key=' + apiKey
    apiCall = requests.get(apiUrl)

    # error checking here
    status = apiCall.json()['status']
    if status == 'OK':
        results = apiCall.json()['results']
        addressComponents = results[0]['address_components']
        return addressComponents
    else:
        return str(status)
