#!/usr/bin/python

# This clock deamon will check the time against the databse and light LEDs
# from Rasperry Pi GPIO based on the database entry for alarms

import time

try:
    import sqlite3
except:
    print 'Required import sqlite3 not found, exiting...'
    sys.exit(1)

class LightClockDb:
    def __init__(self):
        self.db_cache = []
        #self.DATABASE = 'clock.db'
        DATABASE = '/opt/pi_alarm/clock.db'
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

    def FillPlus1Min(self, cur_time):
        """ Only used for testing without the web UI in order to add to DB """
        minute_to_insert = cur_time[4]+1
        if cur_time[5] > 10:
            minute_to_insert += 1

        # Test code to insert fake values:
        alarms = [('%s:%s' % (cur_time[3], minute_to_insert), 0, '0,1,2,3,4,5,6'),
                 ]
        try:
            with self.db_connection:
                self.db_connection.executemany("INSERT INTO alarms VALUES(NULL,?,?,?)", alarms)
                self.db_connection.commit()
        except sqlite3.IntegrityError:
            print 'Alarm value already exists'

        for row in self.db_connection.execute('SELECT * FROM alarms ORDER BY time'):
            print row

if __name__ == '__main__':
    # Create and connect to the DB
    light_clock = LightClockDb()
    cur_time = time.localtime()
    print cur_time
    light_clock.FillPlus1Min(cur_time)
