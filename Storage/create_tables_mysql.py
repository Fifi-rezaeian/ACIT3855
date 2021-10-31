import mysql.connector

db_conn = mysql.connector.connect(host="kafkaservice.eastus2.cloudapp.azure.com", user="user", 
password="password", database="events")

db_cursor = db_conn.cursor()
db_cursor.execute('''
          CREATE TABLE order_details
          (id INT NOT NULL AUTO_INCREMENT, 
           customer_id VARCHAR(250) NOT NULL,
           resturant_name VARCHAR(250) NOT NULL,
           delivery_loc VARCHAR(250) NOT NULL,
           price INTEGER NOT NULL,
           date_created VARCHAR(100) NOT NULL,
           CONSTRAINT order_details_pk PRIMARY KEY (id))
''')

db_cursor.execute('''
          CREATE TABLE scheduled_order
          (id INT NOT NULL AUTO_INCREMENT, 
           customer_id VARCHAR(250) NOT NULL,
           resturant_name VARCHAR(250) NOT NULL,
           delivery_loc VARCHAR(250) NOT NULL,
           scheduled_time VARCHAR(100) NOT NULL,
           date_created VARCHAR(100) NOT NULL,
           CONSTRAINT scheduled_order_pk PRIMARY KEY (id))
''')

db_conn.commit()
db_conn.close()