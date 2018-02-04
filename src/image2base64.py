# script to convert image to byte array
# then encode the byte array to base64 to embed image data

import tkinter
from PIL import Image, ImageTk
import base64

with open("/image/location/image.png", "rb") as imageFile:
    f = imageFile.read()
    b = bytearray(f)

enc = base64.b64encode(b)
