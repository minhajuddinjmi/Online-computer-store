import mysql.connector as c

db = c.connect(host="localhost",user="root", password="12345", database="ecommerce_project")

if db.is_connected():
    print(True)

cursor = db.cursor();


#value = ('suddin','saeed Uddin','CK 50/52 Hakak tola', 'saeed@gmail.com','9696958394Saeed')
# inset data into database
#cursor.execute("insert into user values ('{}','{}','{}', '{}','{}');".format('misbah','misbah','F-117','elmm@gmail.com','kjsdka'))


#db.commit()

# fetch data from database
cursor.execute("Select * from user")
ks = cursor.fetchall()
for i in ks:
    print(i)

# fetchmany
# fetchone
print(ks)

