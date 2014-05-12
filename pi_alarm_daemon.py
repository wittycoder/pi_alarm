#!/usr/bin/python

# This clock deamon will check the time against the databse and light LEDs
# from Rasperry Pi GPIO based on the database entry for alarms

import time
import RPi.GPIO as GPIO

try:
    import sqlite3
except:
    print 'Required import sqlite3 not found, exiting...'
    sys.exit(1)

R_LED = 22
Y_LED = 17
G_LED = 27

class LightClockDb:
    def __init__(self):
        self.db_cache = []
        #self.DATABASE = 'clock.db'
        self.DATABASE = '/opt/pi_alarm/clock.db'
        self.db_connection = sqlite3.connect(self.DATABASE)

        # Try to create the table if it doesn't exist yet
        try:
            with self.db_connection:
                self.db_connection.execute('''CREATE TABLE alarms
                     (id INTEGER PRIMARY KEY NOT NULL,
                      time TEXT,
                      type INTEGER,
                      repeat_days TEXT)''')
        except sqlite3.OperationalError:
            print 'Table already exists, skipped create'

        # Setup the GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(R_LED, GPIO.OUT)
        GPIO.setup(Y_LED, GPIO.OUT)
        GPIO.setup(G_LED, GPIO.OUT)
        # Setup normal non-alarm light condition
        GPIO.output(R_LED, False)
        GPIO.output(Y_LED, False)
        GPIO.output(G_LED, True)

    def FillDummyData(self):
        """ Only used for testing without the web UI in order to add to DB """
     
        # Test code to insert fake values:
        alarms = [('20:30', 0, '0,1,2,3,4,5,6'),
                  ('07:15', 1, '0,1,2,3,4,5,6'),
                  ('01:30', 0, '0,1,2,3,4,5,6'),
                  ('03:45', 1, '1,2'),
                 ]
        try:
            with self.db_connection:
                self.db_connection.executemany("INSERT INTO alarms VALUES(NULL,?,?,?)", alarms)
        except sqlite3.IntegrityError:
            print 'Alarm value already exists'

        #for row in self.db_connection.execute('SELECT * FROM alarms ORDER BY time'):
        #    print row

    def UpdateDbCache(self):
        # Check if cache is empty and get all items in DB if so

        # If we have items in the cache we should really only update if the
        # ids have changed
        # TODO: Add a notification table to the DB, but for now just update everytime
        # if not self.db_cache:
        self.db_cache = []
        results = self.db_connection.execute('SELECT * FROM alarms ORDER BY id').fetchall()
        #print len(results)
        for row in results:
            row_dict = {}
            # process each row and add to the list
            row_dict['days'] = self.ConvertDayNumber(row[3])
            row_dict['hour'], row_dict['min'] = row[1].split(':')
            row_dict['action'] = row[2]
            #print row_dict
            self.db_cache.append(row_dict)
        

    def ConvertDayNumber(self, days):
        """ Convert day string into numbers corresponding with python time
            days 0-6
        """
        day_nums = []
        # If there are days split it, otherwise all days
        if days:
            day_nums = [day for day in days.split(',')]
        else:
            day_nums = [0,1,2,3,4,5,6]
        return day_nums

    def TriggerAlarm(self, action):
        print 'Alarming for action: ' + str(action)
        if action == 1:
            GPIO.output(R_LED, True)
            GPIO.output(Y_LED, True)
            GPIO.output(G_LED, False)
        else:
            # Setup normal non-alarm light condition
            GPIO.output(R_LED, False)
            GPIO.output(Y_LED, False)
            GPIO.output(G_LED, True)
            
    def CheckAlarmTime(self, cur_time):
        #print self.db_cache
        for alarm in self.db_cache:
            #print alarm
            #print cur_time[6]
            # First check that we have the right day
            if str(cur_time[6]) in alarm['days']:
                #print "Right Day"
                # If we have they day, check the hour
                if cur_time[3] == int(alarm['hour']):
                    #print "Right Hour"
                    # Check correct Minute
                    if cur_time[4] == int(alarm['min']):
                        #print "Right Min"
                        self.TriggerAlarm(alarm['action'])

if __name__ == '__main__':
    # Create and connect to the DB
    light_clock = LightClockDb()

    while(1):
        # For now just update the DB cache everytime through
        light_clock.UpdateDbCache()
        # Get the current time
        cur_time = time.localtime()
        # Check if the time is right to alarm based on the current time
        light_clock.CheckAlarmTime(cur_time)
        # lets try to be smart about sleeping so we end up on a minute boundary
        time.sleep(60 - cur_time[5])
