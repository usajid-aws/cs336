import threading, sys, time,urllib,MySQLdb,traceback, requests, re

conn = MySQLdb.connect(host='projectdb.cehud0y2r1tl.us-east-2.rds.amazonaws.com', user='root', passwd='passWord', db='Books')
x = conn.cursor()

#row_query = "select * from Booklist where site like '%amazon%' "
row_query = "select * from Booklist where site = 'ebooks, Amazon' "
x.execute(row_query)
rows = list(x.fetchall())
#if len(rows) at 6 is 6, update
'''
for i in range(0, len(rows)):
	if(len(rows[i][6]) is 6 and 'Amazon' in rows[i][6]):
		update_query =  "UPDATE Booklist SET Price='%s' Where ISBN='%s' " %(rows[i][5].strip(), rows[i][3])
		x.execute(update_query)
		try:
			print("updated: ", rows[i][0])
		except Exception:
			continue

print("done")
conn.commit()

'''
count = 0
for i in range(0, len(rows)):
	try:
		test_data = rows[i][5].split(',')
		fixed_data = test_data[1].strip()
		insert_data = str(test_data[0]) + ', ' + str(fixed_data)
		print(insert_data)
		count = count + 1
		update_query =  "UPDATE Booklist SET Price='%s' Where ISBN='%s' " %(insert_data, rows[i][3])
		x.execute(update_query)
	except Exception as e:
			continue
print("done")
conn.commit()
