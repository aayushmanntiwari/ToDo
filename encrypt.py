import pybase64
import urllib

def Encode(value):
    return pybase64.b64encode(str.encode(value))

def Decode(value):
    return pybase64.b64decode(value).decode("utf_8") 


def Todict(data):
    return urllib.parse.urlencode(data)
