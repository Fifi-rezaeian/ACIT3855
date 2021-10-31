import mysql.connector

db_conn = mysql.connector.connect(host="kafkaservice.eastus2.cloudapp.azure.com", user="user", 
password="password", database="events")

db_cursor = db_conn.cursor()

db_cursor.execute('''
            DROP TABLE order_details, scheduled_order
''')

db_conn.commit()
db_conn.close()
