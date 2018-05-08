'''
will be used to make new table
update old table structure --> new PK = ISBN + Source

go through data 
if site has ',' then: PK is ISBN plus Source
get all books made with this, and insert into updated_books table
'''
import threading, sys, time,urllib,MySQLdb,traceback, requests, re

conn = MySQLdb.connect(host='projectdb.cehud0y2r1tl.us-east-2.rds.amazonaws.com', user='root', passwd='passWord', db='Books')
x = conn.cursor()


#get all rows 
row_query = "select * from Booklist where site not like '%,%' " #get all single source books
x.execute(row_query)
rows = list(x.fetchall())

for i in range(0, len(rows)):
	addbook_query = "INSERT INTO allBooks(Title, Author, Publisher, ISBN, Genre, Price, Site, booksSold) VALUES ('%s', '%s', '%s','%s', '%s', '%s', '%s', '0')" %(rows[i][0], rows[i][1], rows[i][2], rows[i][3],rows[i][4],rows[i][5],rows[i][6])
	x.execute(addbook_query)
	print("inserted: ", rows[i][3])
print("completed")
conn.commit()