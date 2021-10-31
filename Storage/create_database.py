""" script to create two database tables, one for each of your events, in a SQLite database. """

import sqlite3

conn = sqlite3.connect('readings.sqlite')

c = conn.cursor()
c.execute('''
          CREATE TABLE order_details
          (id INTEGER PRIMARY KEY ASC, 
           customer_id VARCHAR(250) NOT NULL,
           resturant_name VARCHAR(250) NOT NULL,
           delivery_loc VARCHAR(250) NOT NULL,
           price INTEGER NOT NULL,
           date_created VARCHAR(100) NOT NULL)
          ''')


c.execute('''
          CREATE TABLE scheduled_order
          (id INTEGER PRIMARY KEY ASC, 
           customer_id VARCHAR(250) NOT NULL,
           resturant_name VARCHAR(250) NOT NULL,
           delivery_loc VARCHAR(250) NOT NULL,
           scheduled_time VARCHAR(100) NOT NULL,
           date_created VARCHAR(100) NOT NULL)
          ''')

conn.commit()
conn.close()