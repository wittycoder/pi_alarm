from flask import render_template, g, request, url_for, redirect, flash, Markup, make_response
from app import app
import sqlite3
import datetime
import subprocess
import os
from werkzeug.utils import secure_filename

#INSTALL_DIR = '/home/pi/pi_alarm/'
INSTALL_DIR = '/opt/pi_alarm/'

DATABASE = INSTALL_DIR + 'clock.db'

UPLOAD_FOLDER = INSTALL_DIR + 'uploads'
ALLOWED_EXTENSIONS = set(['wav', 'ogg', 'flac', 'pcm', 'mp3'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

"""
class AddForm(Form):
    time = fields.TimeField()
    action = fields.StringField()
    repeat_days = fields.StringField()
"""

@app.route('/')
@app.route('/index')
def index():
    now = datetime.datetime.now()
    timestring = now.strftime("%Y-%m-%d %H:%M")
    rows = []
    with app.app_context():
        cur = get_db().execute('SELECT * FROM alarms ORDER BY id')
        rows = cur.fetchall()
    # Go through rows and convert days to human readable format
    templateData = {
        'title': 'Pi Alarm Clock',
        'time': timestring,
        'alarms': rows,
    }
    return render_template('layout.html', **templateData)

@app.route('/create', methods=['GET'])
def create_alarm():
    return _create_alarm(False)

@app.route('/api/create', methods=['GET'])
def create_alarm_api():
    return _create_alarm(True)

def _create_alarm(api=False):
    """ This internal method will create an alarm based on user input
        Only limited validation at this point... called by api and user create
        api param controls the format of the responses/redirects
    """
    hours = request.args.get('hour')
    minutes = request.args.get('min')
    # check that there are values in the hours/minutes
    if not hours or not minutes:
        if api:
            return 'Error in request', 404
        else:
            flash(Markup('<h2>ERROR! Empty hours/minutes in time</h2>'))
            return redirect('', code=307)

    hours = int(hours)
    minutes = int(minutes)
    if hours in range(24) and minutes in range(60):
        time = "{0:02d}:".format(hours) + "{0:02d}".format(minutes)
    else:
        if api:
            return 'Error in request', 404
        else:
            flash(Markup('<h2>ERROR! Input time invalid</h2>'))
            return redirect('', code=307)

    alarm_type = request.args.get('type')

    days = [request.args.get('M'), request.args.get('Tu'),
            request.args.get('W'), request.args.get('Th'),
            request.args.get('F'), request.args.get('Sa'),
            request.args.get('Su'),]
    day_string = ','.join(filter(None, days))
    if not day_string:
        day_string = '0,1,2,3,4,5,6'
    add_alarm(time,
              alarm_type,
              day_string)
    if api:
        return 'Success', 200
    else:
        flash(Markup('<h2>Added new Alarm</h2>'))
        # No need to generate a new page, just go back to index to show main page
        return redirect('', code=307)

@app.route('/edit/<int:id>')
def edit(id):
    flash(Markup('<h2>ERROR! Edit not implemented</h2>'))
    return redirect('', code=307)
    
@app.route('/delete/<int:id>')
def delete(id):
    try:
        get_db().execute('DELETE FROM alarms WHERE id=%s' % id)
        get_db().commit()
    except sqlite.IntegrityError:
        flash(Markup('<h2>ERROR! Alarm ID not found</h2>'))
        return redirect('', code=307)
    flash(Markup('<h2>Alarm ID %s removed</h2>' % id))
    return redirect('', code=307)

@app.route('/turnoff', methods=['GET'])
def turnoff():
    flash(Markup('<h2>Turning OFF light within a minute</h2>'))
    return redirect('', code=307)

@app.route('/turnon', methods=['GET'])
def turnon():
    flash(Markup('<h2>Turning ON light within a minute</h2>'))
    return redirect('', code=307)

@app.route('/brown_turnon', methods=['GET'])
def brown_turnon():
    flash(Markup('<h2>Turning ON Brown Noise</h2>'))
    subprocess.Popen(['bash', INSTALL_DIR + 'scripts/play_brown_noise.sh', '720'])
    return redirect('', code=307)

@app.route('/brown_turnoff', methods=['GET'])
def brown_turnoff():
    flash(Markup('<h2>Turning OFF Brown Noise</h2>'))
    # Just start with my standard use case and play for 12 hours
    subprocess.Popen(['bash', INSTALL_DIR + 'scripts/stop_brown_noise.sh'])
    return redirect('', code=307)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

# TODO: UNUSED
@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('uploaded_file',
                                    filename=filename))
        return '''
        <!doctype html>
        <title>Upload Success</title>
        <h1>Upload Success</h1>
        '''
    else:
        return '''
        <!doctype html>
        <title>Upload new File</title>
        <h1>Upload new File</h1>
        <form action="" method=post enctype=multipart/form-data>
          <p><input type=file name=file>
             <input type=submit value=Upload>
        </form>
        '''


def add_alarm(time, alarm_type, repeat_days):
    """ Only used for testing without the web UI in order to add to DB """
    alarm = [(time, alarm_type, repeat_days)]
    try:
        # Insert and commit
        get_db().executemany("INSERT INTO alarms VALUES(NULL,?,?,?)", alarm)
        get_db().commit()
    except sqlite3.IntegrityError:
        # TODO: This isn't working, currently multiples can be added.
        flash(Markup('<h2>ERROR! Alarm value already exists</h2>'))
        return redirect('', code=307)

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()
