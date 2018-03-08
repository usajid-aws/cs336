'''
#Barnes Noble scrapper 
#will have to do genre by genre 
#all from barnes and nobles ' best sellers' page by genre
#look at line 20 for website example

@Author -> Usama Sajid
'''
import traceback
import bs4
import sys
import urllib
import MySQLdb
from urllib.request import urlopen as uReq
from bs4 import BeautifulSoup as soup

#parses side page to get ISBN number
def getISBN(i, x):
	   
	    site = uReq('https://www.barnesandnoble.com/b/books/history/_/N-1fZ29Z8q8Z11km?Nrpp=20&Ns=P_Sales_Rank&page=' + str(x))
	    page_html = site.read()
	    site.close()
	    page_soup = soup(page_html, "html.parser")
	    books = page_soup.findAll("div", {"class":"col-lg-8 product-info-listView"})
	    link_to_book_info = books[i].find("a")['href']
	    new_site = uReq('https://www.barnesandnoble.com/' + str(link_to_book_info))
	    new_site_html = new_site.read()
	    new_site.close()
	    new_page_soup = soup(new_site_html, "html.parser")
	    product_detail = new_page_soup.find("table", {"class":"plain"})
	    ISBN_NUM = product_detail.find('tr')
	    return ISBN_NUM.text

def getPublisher(i, x):
	   
	    site = uReq('https://www.barnesandnoble.com/b/books/history/_/N-1fZ29Z8q8Z11km?Nrpp=20&Ns=P_Sales_Rank&page=' + str(x))
	    page_html = site.read()
	    site.close()
	    page_soup = soup(page_html, "html.parser")
	    books = page_soup.findAll("div", {"class":"col-lg-8 product-info-listView"})
	    link_to_book_info = books[i].find("a")['href']
	    new_site = uReq('https://www.barnesandnoble.com/' + str(link_to_book_info))
	    new_site_html = new_site.read()
	    new_site.close()
	    new_page_soup = soup(new_site_html, "html.parser")
	    product_detail = new_page_soup.find("table", {"class":"plain"})
	    Publisher_Name = product_detail.find("a").text
	    return Publisher_Name




#DB connector
conn = MySQLdb.connect(host='projectdb.cehud0y2r1tl.us-east-2.rds.amazonaws.com', user='root', passwd='passWord', db='Books')

#already made Allbooks table, here just in case
#new_table_query = "CREATE TABLE " + "Booklist" + "(Title varchar(100) NOT NULL, Author varchar(100) NOT NULL, Publisher varchar(100) NOT NULL, ISBN varchar(100) NOT NULL, Genre varchar(100) NOT NULL, Price varchar(10) NOT NULL, Site varchar(100) NOT NULL, Count varchar(25) NOT NULL, PRIMARY KEY (ISBN))"

x = conn.cursor()
#x.execute(new_table_query)



file_name = "barnesandnoble_scifi.csv"
f = open(file_name, "w")
header = "Title, Author, ISBN, Genre, Price, Site"
f.write(header)
miss = 0
hit = 0


for y in range(1,6):
	site = uReq('https://www.barnesandnoble.com/b/books/history/_/N-1fZ29Z8q8Z11km?Nrpp=20&Ns=P_Sales_Rank&page=' + str(y))
	page_html = site.read()
	site.close()
	page_soup = soup(page_html, "html.parser")
	books = page_soup.findAll("div", {"class":"col-lg-8 product-info-listView"})
	for i in range(0,20):
		book_name = books[i].find("a")
		book_ISBN = getISBN(i, y)
		book_authors = books[i].findAll("div", {"class":"contributors"})
		book_price = books[i].find("a", {"class":"current"})
		book_publisher = getPublisher(i, y)
		name = book_name.text.replace("'", "")
		author = book_authors[0].a.text
		ISBN = book_ISBN.strip()[10:]
		price = book_price.text		
		#Query -> add book to Allbooks table
		addbook_query = "INSERT INTO Booklist(Title, Author, Publisher, ISBN, Genre, Price, Site, Count) VALUES ('%s', '%s', '%s','%s', 'HISTORY', '%s', 'barnesandnoble', '100')" %(name, author, book_publisher.replace("'", ""), ISBN, price)
		i+1
		try:
			x.execute(addbook_query)
			print(book_name.text + " by " + book_authors[0].a.text + ", ISBN " + book_ISBN.strip()[10:] + " Price: " + price)
			hit=hit+1
		except Exception:
			print("\n prob already in \n\n")
			print(addbook_query)
			print('\n')
			traceback.print_exc()
			print('\n')
			miss=miss+1
			continue



#commit all to DB
conn.commit()
print("miss: "+ str(miss))
print('\n')
print("hit: " + str(hit))

'''
----------------------------------------------------------------------------------------------------------------------------
                                                       BARNES AND NOBLES SOURCES USED
SCIFI
https://www.barnesandnoble.com/b/books/science-fiction-fantasy/_/N-1fZ29Z8q8Z180l?Nrpp=20&page=

MYSTERY
https://www.barnesandnoble.com/b/books/mystery-crime/_/N-1fZ29Z8q8Z16g4?Nrpp=20&Ns=P_Sales_Rank&page=

MANGA
https://www.barnesandnoble.com/b/books/graphic-novels-comics/manga/_/N-1fZ29Z8q8Zucc?Nrpp=20&Ns=P_Sales_Rank&page=

BUISNESS
https://www.barnesandnoble.com/b/books/business/_/N-1fZ29Z8q8Zt82?Nrpp=20&Ns=P_Sales_Rank&page=

ROMANCE
https://www.barnesandnoble.com/b/books/romance/_/N-1fZ29Z8q8Z17y3?Nrpp=20&Ns=P_Sales_Rank&page=

COMPUTERS
https://www.barnesandnoble.com/b/books/computers/_/N-1fZ29Z8q8Zug4?Nrpp=20&Ns=P_Sales_Rank&page=

POETRY
https://www.barnesandnoble.com/b/books/poetry/_/N-1fZ29Z8q8Z1pqh?Nrpp=20&Ns=P_Sales_Rank&page=

PHILOSOPHY
https://www.barnesandnoble.com/b/nook-books/philosophy/_/N-1fZ8qaZ1fe7?Nrpp=20&Ns=P_Sales_Rank&page=

HISTORY
https://www.barnesandnoble.com/b/books/history/_/N-1fZ29Z8q8Z11km?Nrpp=20&Ns=P_Sales_Rank&page=
'''

