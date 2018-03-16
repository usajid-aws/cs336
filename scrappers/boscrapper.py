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
conn2  = MySQLdb.connect(host='projectdb.cehud0y2r1tl.us-east-2.rds.amazonaws.com', user='root', passwd='passWord', db='Books')
x = conn.cursor()
x2 = conn2.cursor()

def threadInsert(url, genre_type, t_name, cursor_name, conn_name):
    miss = 0
    hit = 0
    for y in range(1,10):
        site = uReq(str(url) + str(y))
        page_html = site.read()
        page_soup = soup(page_html, "html.parser")
        books = page_soup.findAll("div", {"class":"float-fix"})
        print("page: " + str(y) + " thread: " + t_name) 
        if(len(books) == 0):
            break
        for i in range(0,24):
            #print(t_name)
            if(books[i] is None):
                break
            name = getName(url,i, y)
            ISBN = getISBN(url,i, y)
            author = getAuthor(url,i, y)
            price = books[i].find("div", {"class":"price"}).getText()
            book_publisher = getPublisher(url,i, y)
            if book_publisher is None or name is None or author is None or ISBN is None:
                print("obj is None")
                continue
            #Query -> add book to Allbooks table
            addbook_query = "INSERT INTO Booklist(Title, Author, Publisher, ISBN, Genre, Price, Site, Count) VALUES ('%s', '%s', '%s','%s', '%s', '%s', 'bookoutlet', '100')" %(name.replace("'", ""), author, book_publisher.replace("'", ""), ISBN,str(genre_type),price)
            i+1
            try:
                cursor_name.execute(addbook_query)
                time.sleep(1)
                hit=hit+1
            except Exception: #will add to site source
                get_query = "Select * from Booklist where ISBN='%s'" % (ISBN)
                traceback.print_exc()
                print("caught first Exception \n")
                try: #try within try to make sure no double access to DB
                    cursor_name.execute(get_query)
                    time.sleep(1)
                    data_line = x.fetchone()
                    time.sleep(2)
                    if data_line is None or "bookoutlet" in str(data_line[6]):
                     #print("try two break")
                     continue
                    new_source = str(data_line[6]) + ", bookoutlet"
                    new_price = str(data_line[5]) + ", " + str(price)
                    update_query = "UPDATE Booklist SET Site='%s' Where ISBN='%s' " %(new_source, ISBN)
                    update_price = "UPDATE Booklist SET Price='%s' Where ISBN='%s' " %(new_price, ISBN)
                    cursor_name.execute(update_query)
                    time.sleep(2)
                    cursor_name.execute(update_price)
                    time.sleep(2)
                    miss=miss+1
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
                    sys.exit(0) #will cancel out one thread

                   
    #commit all to DB
    conn.commit()
    print("miss: "+ str(miss))
    print('\n')
    print("hit: " + str(hit))

thread1 = threading.Thread(target=threadInsert, args=('http://bookoutlet.com/Store/Browse?Nc=31&Ns=1393&page=', 'ROMANCE', 'thread1', x, conn))
thread2 = threading.Thread(target=threadInsert, args=('http://bookoutlet.com/Store/Browse?Nc=18&page=', 'COMPUTERS', 'thread2', x2, conn2))
thread1.start()
#time.sleep(3)
#thread2.start()


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

BUISNESS:
http://bookoutlet.com/Store/Browse?Nc=9&page=

LAW:
http://bookoutlet.com/Store/Browse?Nc=45

PHILOSOPHY:
http://bookoutlet.com/Store/Browse?Nc=63

POETRY:
http://bookoutlet.com/Store/Browse?Nc=66

MEDICINE AND NURSING:
http://bookoutlet.com/Store/Browse?Nc=52

RELIGION:
http://bookoutlet.com/Store/Browse?Nc=71

MYSTERY:
http://bookoutlet.com/Store/Browse?Nc=31&Ns=1082&page=

MUSIC,FILM, AND PERFMORMING ART:
http://bookoutlet.com/Store/Browse?Nc=53

ROMANCE:
http://bookoutlet.com/Store/Browse?Nc=31&Ns=1393&page=
'''