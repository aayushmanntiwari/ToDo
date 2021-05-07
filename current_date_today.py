from urllib.request import urlopen
import datetime
from datetime import date

def custom_today_date():
    res = urlopen('http://just-the-time.appspot.com/')
    result = res.read().strip().decode('utf-8').split(' ')[0]
    if result is not None:
        return result
    else:
        current_date = date.today().isoformat()
        return current_date