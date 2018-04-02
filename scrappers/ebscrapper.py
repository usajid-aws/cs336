''' 
scrapper for ebooks
@author --> Usama S.
'''


import bs4
import threading, sys, time,urllib,MySQLdb,traceback, requests
from urllib.request import urlopen as uReq, Request
from bs4 import BeautifulSoup as soup



conn = MySQLdb.connect(host='projectdb.cehud0y2r1tl.us-east-2.rds.amazonaws.com', user='root', passwd='passWord', db='Books')
conn2  = MySQLdb.connect(host='projectdb.cehud0y2r1tl.us-east-2.rds.amazonaws.com', user='root', passwd='passWord', db='Books')
x = conn.cursor()
x2 = conn2.cursor()

def get_ISBN(req,i, x):
	site = uReq(str(req)+ str(x))
	page_html = site.read()
	site.close()
	page_soup = soup(page_html, "html.parser")
	books = page_soup.findAll("li", {"class":"search-row"})
	out_source = books[i].find("span", {"class":"book-title"}).find('a')['href'].encode('utf-8').decode('ascii', 'ignore').strip()
	outer_site = uReq(out_source)
	outer_html = outer_site.read()
	outer_site.close()
	outer_soup = soup(outer_html, "html.parser")
	ISBN_Info = outer_soup.find("div", {"class":"isbn-info"})
	for b in range (0, (len(ISBN_Info.findAll("div")))):
		conn = MySQLdb.connect(host='projectdb.cehud0y2r1tl.us-east-2.rds.amazonaws.com', user='root', passwd='passWord', db='Books')
		x = conn.cursor()
		
		if(ISBN_Info is None):
			continue
		get_query = "Select * from Booklist where ISBN='%s'" % (ISBN_Info.findAll("div")[b].text)
		x.execute(get_query)
		time.sleep(2)
		data_line = x.fetchone()
		if(data_line is not None):
			print("ISBN Exists, returning")
			return ISBN_Info.findAll("div")[b].text
	return ISBN_Info.findAll("div")[0].text

def threadInsert(url, genre_type, t_name, cursor_name, conn_name):
	miss = 0
	hit = 0
	for y in range(1,12):
		site = uReq(str(url) + str(y))
		page_html = site.read()
		site.close()
		page_soup = soup(page_html, "html.parser")
		books = page_soup.findAll("li", {"class":"search-row"})
		for i in range(0,10):
			name = books[i].find("span", {"class":"book-title"}).text.replace("'", "")
			author = books[i].find("span", {"class":"author"}).text[3:]
			extra_data = books[i].find("div", {"class":"additional-info"}).text.split(';')
			book_publisher = extra_data[0].replace("'", "")
			price = extra_data[1].strip().replace(" ", "")
			if(len(price) > 10):
				price = extra_data[1].strip()[2:9].replace(" ", "")
			else:
				price = extra_data[1].strip()[2:].replace(" ", "")
			ISBN = get_ISBN(url,i, y)
			#Query -> add book to Allbooks table
			addbook_query = "INSERT INTO Booklist(Title, Author, Publisher, ISBN, Genre, Price, Site, Count) VALUES ('%s', '%s', '%s','%s', '%s', '%s', 'ebooks', '100')" %(name, author, book_publisher, ISBN,str(genre_type),price)
			try:
				cursor_name.execute(addbook_query)
				time.sleep(1)
				
				print("inserted")
				hit=hit+1
			except Exception:
				
				get_query = "Select * from Booklist where ISBN='%s'" % (ISBN)
				traceback.print_exc()
				
				try:
					cursor_name.execute(get_query)
					time.sleep(1)
					data_line = cursor_name.fetchone()
					time.sleep(2)
					if len(data_line) is 0 or "ebooks" in str(data_line[6]):
						
						continue
					new_source = str(data_line[6]) + ", ebooks"
					new_price = str(data_line[5]) + ", " + str(price)
					update_query = "UPDATE Booklist SET Site='%s' Where ISBN='%s' " %(new_source, ISBN)
					update_price = "UPDATE Booklist SET Price='%s' Where ISBN='%s' " %(new_price, ISBN)
					cursor_name.execute(update_query)
					time.sleep(2)
					cursor_name.execute(update_price)
					time.sleep(2)
					miss=miss+1
					print("updated")
					continue
				except Exception:
					traceback.print_exc()
					conn_name = MySQLdb.connect(host='projectdb.cehud0y2r1tl.us-east-2.rds.amazonaws.com', user='root', passwd='passWord', db='Books')
					cursor_name = conn_name.cursor()
					time.sleep(2)
					conn_name.commit()
					print("miss: "+ str(miss))
					print('\n')
					print("hit: " + str(hit))
					print('\n')
					traceback.print_exc()
					print("\n exiting hit the roof \n\n")
					sys.exit(0)
	#commit all to DB
	conn_name.commit()
	print("miss: "+ str(miss))
	print('\n')
	print("hit: " + str(hit))

thread1 = threading.Thread(target=threadInsert, args=('https://www.ebooks.com/subjects/religion/?sortBy=&sortOrder=&RestrictBy=&countryCode=us&page=', 'RELIGION', 'thread1', x, conn))
thread2 = threading.Thread(target=threadInsert, args=('https://www.ebooks.com/subjects/music/?sortBy=&sortOrder=&RestrictBy=&countryCode=us&page=', 'MUSIC,FILM, AND PERFMORMING ARTS', 'thread2', x2, conn2))
thread1.start()
#time.sleep(3)
#thread2.start()

'''
----------------------------------------------------------------------------------------------------------------------------
                                                       Sources

SCIFI:
https://www.ebooks.com/subjects/science-fiction/?sortBy=&sortOrder=&RestrictBy=&countryCode=us&page=

COMPUTERS:
https://www.ebooks.com/subjects/computers/?sortBy=&sortOrder=&RestrictBy=&countryCode=us&page=

PETS:
https://www.ebooks.com/subjects/pets/?sortBy=&sortOrder=&RestrictBy=&countryCode=us&page=

ROMANCE:
https://www.ebooks.com/subjects/romance/?sortBy=&sortOrder=&RestrictBy=&countryCode=us&page=

LAW:
https://www.ebooks.com/subjects/law/?sortBy=&sortOrder=&RestrictBy=&countryCode=us&page=

RELIGION:
https://www.ebooks.com/subjects/religion/?sortBy=&sortOrder=&RestrictBy=&countryCode=us&page=2

HISTORY:
https://www.ebooks.com/subjects/history/?sortBy=&sortOrder=&RestrictBy=&countryCode=us&page=2

BUSINESS:
https://www.ebooks.com/subjects/business/?sortBy=&sortOrder=&RestrictBy=&countryCode=us&page=2

PHILOSOPHY:
https://www.ebooks.com/subjects/philosophy/?sortBy=&sortOrder=&RestrictBy=&countryCode=us&page=2

POETRY:
https://www.ebooks.com/subjects/poetry/?sortBy=&sortOrder=&RestrictBy=&countryCode=us&page=2

NATURE:
https://www.ebooks.com/subjects/nature/?sortBy=&sortOrder=&RestrictBy=&countryCode=us&page=2

MEDICINE AND NURSING

MYSTERY:
https://www.ebooks.com/subjects/fiction-mystery-ebooks/14544/?page=2

MUSIC,FILM, AND PERFMORMING ARTS
https://www.ebooks.com/subjects/music/?sortBy=&sortOrder=&RestrictBy=&countryCode=us&page=2

RELIGION




'''