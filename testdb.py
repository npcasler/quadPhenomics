import sqlite3
import parse
conn = sqlite3.connect('example.db')

c = conn.cursor()

# Create table
#c.execute("CREATE TABLE sensor ( id integer, x float, y float, plot_id text)")

# Insert a row of data
c.execute("INSERT INTO sensor(id, x, y)  VALUES(?, ?, ?)", (9999, -96.6191591, 39.13228314))

# Save (commit) the changes
conn.commit()

# We can also close the connection if we are done with it.
# Just be sure any changes have been committed or they will be lost.
conn.close()
