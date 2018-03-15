'''
#bookoutlet scrapper
#will have to do genre by genre 
#all from barnes and nobles ' best sellers' page by genre
#look at line 20 for website example

@Author -> Usama Sajid
'''
import bs4
import threading, sys, time,urllib,MySQLdb,traceback, requests
from urllib.request import urlopen as uReq, Request
from bs4 import BeautifulSoup as soup

'''
url = 'http://bookoutlet.com/Store/Browse?Nc=31&Ns=1421&page=%d&size=24&sort=popularity_0' %(2)
site = uReq(url)
page_html = site.read()
page_soup = soup(page_html, "html.parser")
books = page_soup.findAll("div", {"class":"float-fix"})
link_to_book_info = books[0].find("a")['href']
new_site = uReq('http://bookoutlet.com/' + str(link_to_book_info))
new_site_html = new_site.read()
new_site.close()
new_page_soup = soup(new_site_html, "html.parser")
product_detail = new_page_soup.find(itemprop="name")
ISBN_NUM = product_detail.getText()
'''

def getISBN(req,i, x):
    site = uReq(str(req) + str(x))
    page_html = site.read()
    page_soup = soup(page_html, "html.parser")
    books = page_soup.findAll("div", {"class":"float-fix"})
    if(books[i] is None):
        return None
    link_to_book_info = books[i].find("a")['href']
    new_site = uReq('http://bookoutlet.com/' + str(link_to_book_info))
    new_site_html = new_site.read()
    new_site.close()
    new_page_soup = soup(new_site_html, "html.parser")
    product_detail = new_page_soup.find(itemprop="isbn")
    ISBN_NUM = product_detail.getText()
    return ISBN_NUM

def getPublisher(req, i, x):
    site = uReq(str(req) + str(x))
    page_html = site.read()
    page_soup = soup(page_html, "html.parser")
    books = page_soup.findAll("div", {"class":"float-fix"})
    if(books[i] is None):
        return None
    link_to_book_info = books[i].find("a")['href']
    new_site = uReq('http://bookoutlet.com/' + str(link_to_book_info))
    new_site_html = new_site.read()
    new_site.close()
    new_page_soup = soup(new_site_html, "html.parser")
    product_detail = new_page_soup.find(itemprop="publisher")
    publisher = product_detail.getText()
    return publisher

def getAuthor(req, i, x):
    site = uReq(str(req) + str(x))
    page_html = site.read()
    page_soup = soup(page_html, "html.parser")
    books = page_soup.findAll("div", {"class":"float-fix"})
    if(books[i] is None):
        return None
    link_to_book_info = books[i].find("a")['href']
    new_site = uReq('http://bookoutlet.com/' + str(link_to_book_info))
    new_site_html = new_site.read()
    new_site.close()
    new_page_soup = soup(new_site_html, "html.parser")
    product_detail = new_page_soup.find(itemprop="author")
    author = product_detail.getText()
    return author

def getName(req, i, x):
    site = uReq(str(req) + str(x))
    page_html = site.read()
    page_soup = soup(page_html, "html.parser")
    books = page_soup.findAll("div", {"class":"float-fix"})
    if(books[i] is None):
        return None
    link_to_book_info = books[i].find("a")['href']
    new_site = uReq('http://bookoutlet.com/' + str(link_to_book_info))
    new_site_html = new_site.read()
    new_site.close()
    new_page_soup = soup(new_site_html, "html.parser")
    product_detail = new_page_soup.find(itemprop="name")
    name = product_detail.getText()
    return name

conn = MySQLdb.connect(host='projectdb.cehud0y2r1tl.us-east-2.rds.amazonaws.com', user='root', passwd='passWord', db='Books')
conn2 = conn = MySQLdb.connect(host='projectdb.cehud0y2r1tl.us-east-2.rds.amazonaws.com', user='root', passwd='passWord', db='Books')
x = conn.cursor()
x2 = conn2.cursor()

def threadInsert(url, genre_type, t_name, cursor_name):
    miss = 0
    hit = 0
    for y in range(1,7):
        site = uReq(str(url) + str(y))
        page_html = site.read()
        page_soup = soup(page_html, "html.parser")
        books = page_soup.findAll("div", {"class":"float-fix"})
        if(len(books) == 0):
            break
        for i in range(0,24):
            print(t_name)
            if(books[i] is None):
                break
            name = getName(url,i, y)
            ISBN = getISBN(url,i, y)
            author = getAuthor(url,i, y)
            price = books[i].find("div", {"class":"price"}).getText()
            book_publisher = getPublisher(url,i, y)
            if book_publisher is None or name is None or author is None or ISBN is None:
                continue
            #Query -> add book to Allbooks table
            addbook_query = "INSERT INTO Booklist(Title, Author, Publisher, ISBN, Genre, Price, Site, Count) VALUES ('%s', '%s', '%s','%s', '%s', '%s', 'bookoutlet', '100')" %(name.replace("'", ""), author, book_publisher.replace("'", ""), ISBN,str(genre_type),price)
            i+1
            try:
                cursor_name.execute(addbook_query)
                time.sleep(1)
                print(name + " by " + author+ ", ISBN " + ISBN + " Price: " + price + " Genre: "+genre_type)
                hit=hit+1
            except Exception: #will add to site source
                get_query = "Select * from Booklist where ISBN='%s'" % (ISBN)
                cursor_name.execute(get_query)
                data_line = x.fetchone()
                time.sleep(2)
                if data_line is None or "bookoutlet" in str(data_line[6]):
                               continue
                new_source = str(data_line[6]) + ", bookoutlet"
                update_query = "UPDATE Booklist SET Site='%s' Where ISBN='%s' " %(new_source, ISBN)
                cursor_name.execute(update_query)
                time.sleep(2)
                print('\n')
                traceback.print_exc()
                print(str(update_query) + '\n')
                miss=miss+1
                continue
    #commit all to DB
    conn.commit()
    print("miss: "+ str(miss))
    print('\n')
    print("hit: " + str(hit))

thread1 = threading.Thread(target=threadInsert, args=('http://bookoutlet.com/Store/Browse?Nc=39&page=', 'HISTORY', 'thread1', x))
thread2 = threading.Thread(target=threadInsert, args=('http://bookoutlet.com/Store/Browse?Nc=18&page=', 'COMPUTERS', 'thread2', x2))
thread3 = threading.Thread(target=threadInsert, args=('http://bookoutlet.com/Store/Browse?Nc=62&page=', 'PETS', 'thread3'))
thread4 =  threading.Thread(target=threadInsert, args=('http://bookoutlet.com/Store/Browse?Nc=55&page=', 'NATURE', 'thread4'))
thread1.start()
time.sleep(1)
thread2.start()
#thread3.start()
#thread4.start()

#only using two threads at a time, dont want any DB crashes
#had to overload the packets parameters on RDS to allow threading, kept crashing
'''
------------------------------------------------------------------------------------------------------------------------------
                                                      Sources
SCIFI:
http://bookoutlet.com/Store/Browse?Nc=31&Ns=1421&page=

MANGA:
http://bookoutlet.com/Store/Browse?Nc=17&Ns=716&page=

PETS:
http://bookoutlet.com/Store/Browse?Nc=62&page=

NATURE:
http://bookoutlet.com/Store/Browse?Nc=55&page=

COMPUTERS:
http://bookoutlet.com/Store/Browse?Nc=18&page=

HISTORY:
http://bookoutlet.com/Store/Browse?Nc=39&page=


'''