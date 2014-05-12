from flask import Flask

def display_days(string):
    """ Jinja filter for converting a list of days in number to be human
        readable days in 1-2 chars
    """ 
    convert_list= ['M', 'Tu', 'W', 'Th', 'F', 'Sa', 'Su']
    new_days = []
    for days in string.split(','):
        new_days.append(convert_list[int(days)])
    new_days = ','.join(new_days)
    return new_days

def display_type(string):
    if string == 1:
        return 'ALARM'
    else:
        return 'DISABLE ALARM'


app = Flask(__name__)

# Set the filter to display human readable days
app.jinja_env.filters['display_days'] = display_days
app.jinja_env.filters['display_type'] = display_type
app.secret_key = 'some_secret'

from app import views
