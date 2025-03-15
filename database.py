import mysql.connector

# Establish a connection to the MySQL database
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="utts-db"
)

cursor = conn.cursor()

# Query to fetch bus schedules
cursor.execute("SELECT * FROM bus_schedules")
bus_schedules = cursor.fetchall()

# Query to fetch buses
cursor.execute("SELECT * FROM buses")
buses = cursor.fetchall()

# Query to fetch routes
cursor.execute("SELECT * FROM routes")
routes = cursor.fetchall()

# Query to fetch users
cursor.execute("SELECT * FROM users")
users = cursor.fetchall()

# Close the connection
cursor.close()
conn.close()

# Print results
print("Bus Schedules:", bus_schedules)
print("Buses:", buses)
print("Routes:", routes)
print("Users:", users)
