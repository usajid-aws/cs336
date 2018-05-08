'''
-------------------------------------------

Book Scrapper for amazon.com
@Author --> Usama S.

------------------------------------------- '''

import bs4
import threading, sys, time,urllib,MySQLdb,traceback, requests, re
from urllib.request import urlopen as uReq, Request
from bs4 import BeautifulSoup as soup
 

conn = MySQLdb.connect(host='', user='', passwd='', db='Books')
conn2  = MySQLdb.connect(host='m', user='', passwd='', db='Books')
x = conn.cursor()
x2 = conn2.cursor()

def threadInsert(url, genre_type, t_name, cursor_name, conn_name):
	miss = 0
	hit = 0
	for y in range(1,50):
		headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'}
		url2 = (url + str(y))		
		site = requests.get(url2, headers=headers)
		time.sleep(1)
		page_soup = soup(site.content, 'html.parser')
		time.sleep(1)
		books = page_soup.findAll("div", {"class":"s-item-container"})
		#time.sleep(2)
		for i in range(0,12):
			#print("books: ", len(books), url2, i, t_name)
			href=''
			try:
				href = books[i].find("a", {"class":"a-link-normal"})['href'] # href
			except Exception as e:
				time.sleep(.3)
				headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36'}
				url2 = url + str(y)		
				site = requests.get(url2, headers=headers)
				page_soup = soup(site.content, 'html.parser')
				time.sleep(1)
				books = page_soup.findAll("div", {"class":"s-item-container"})
				if(len(books) == 0 or books is None):
					break
				print("\nresolved\n")
				i=0
			hrefs = books[i].findAll('div',{"class":"a-row"})
			for h in range (0, len(hrefs)):
				try:
					href=hrefs[h].find('a', href=True)['href']
					time.sleep(.5)
					i=0
					if("amazon" in href):
						break
					#break
				except Exception as p:
					traceback.print_exc()
					continue
			book_info_site = requests.get(href, headers=headers)
			info_soup = soup(book_info_site.content, 'html.parser')
			time.sleep(1.5)
			try:
				title = info_soup.find("span", {"id":"productTitle"}).text.replace("'", "")
				author = info_soup.find("span", {"class":"author"}).find("a", {"class":"a-link-normal"}).text
				price = info_soup.find("span", {"class":"a-color-price"}).text[1:]
			except Exception as ex:
				continue
			if('Visit Amazon' in author):
				author = author[15:]		
            #ISBN
			ISBN = ""
			ISBN_list = info_soup.find("table", {"id":"productDetailsTable"}).findAll("li")
			for i in range(0, len(ISBN_list)):
				ISBN_CHECK = ISBN_list[i].b.text[:len(ISBN_list[i].b.text)]
				if("13" in ISBN_CHECK):
					ISBN = ISBN_list[i].b.next_sibling.strip().replace("-", "") #ISBN
			
			#Publisher
			Publisher = ""
			info_list = info_soup.find("table", {"id":"productDetailsTable"}).findAll("li")
			for i in range(0, len(info_list)):
				PC = info_list[i].b.text[:len(info_list[i].b.text)]
				if(PC == "Publisher:"):
					Publisher = info_list[i].b.next_sibling.strip().replace("'", "") #Publisher
					Publisher = re.split('; | [(|)] ', Publisher)[0]
			#Query -> add book to Allbooks table
			addbook_query = "INSERT INTO Booklist(Title, Author, Publisher, ISBN, Genre, Price, Site, Count) VALUES ('%s', '%s', '%s','%s', '%s', '%s', 'Amazon', '100')" %(title, author, Publisher, ISBN,str(genre_type),price)
			try:
				cursor_name.execute(addbook_query)
				time.sleep(1)
				print("inserted on ", t_name)
				hit=hit+1
			except Exception as e2:
				#print(e2, '\n', t_name)
				get_query = "Select * from Booklist where ISBN='%s'" % (ISBN)
				try:
					cursor_name.execute(get_query)
					time.sleep(1)
					data_line = cursor_name.fetchone()
					time.sleep(2)
					if data_line is None or "Amazon" in str(data_line[6]):
						if(data_line is None):
							print("data_line None\n")
						else:
							print("passed")
						continue
					new_source = ((str(data_line[6])).strip() + ", Amazon").strip()
					new_price = str(data_line[5]) + ", " + str(price)
					update_query = "UPDATE Booklist SET Site='%s' Where ISBN='%s' " %(new_source, ISBN)
					update_price = "UPDATE Booklist SET Price='%s' Where ISBN='%s' " %(new_price, ISBN)
					cursor_name.execute(update_query)
					time.sleep(2)
					cursor_name.execute(update_price)
					time.sleep(2)
					miss=miss+1
					print("updated on ", t_name, ISBN, '\n')
					conn_name.commit()
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
					print("\n exiting hit the roof \n\n")
					sys.exit(0)
	#commit all to DB
	conn_name.commit()
	time.sleep(2)
	print("miss: "+ str(miss))
	print('\n')
	print("hit: " + str(hit))

thread1 = threading.Thread(target=threadInsert, args=('https://www.amazon.com/s/ref=lp_22_pg_2?rh=n%3A283155%2Cn%3A%211000%2Cn%3A22&page=', 'RELIGION', 'thread1', x, conn))
thread2 = threading.Thread(target=threadInsert, args=('https://www.amazon.com/s/ref=sr_pg_2?rh=n%3A283155%2Ck%3Apet+books&page=', 'PETS', 'thread2', x2, conn2))
thread1.start()
#time.sleep(1.5)
#thread2.start()

'''
Topics:

Business
LAW
SCIFI
ROMANCE
MYSTERY
COMPUTERS
HISTORY
PETS
RELIGION

'''
