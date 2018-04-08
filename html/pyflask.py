from flask import Flask, render_template, request, redirect, url_for, make_response
import MySQLdb, traceback, time

app=Flask(__name__)

conn = MySQLdb.connect(host='projectdb.cehud0y2r1tl.us-east-2.rds.amazonaws.com', user='root', passwd='passWord', db='Books')

@app.route("/")
def index():
        return render_template("index.html")

@app.route("/newaccount")
def newaccount():
        return render_template("newaccount.html")

@app.route("/index.html")
def mainPage():
        return render_template("index.html")

#signUp --> get data and place into database
@app.route("/signUp", methods=["POST"])
def signUp():
        name = str(request.form["name"])
        username = str(request.form["username"])
        password = str(request.form["password"])
        conn = MySQLdb.connect(host='projectdb.cehud0y2r1tl.us-east-2.rds.amazonaws.com', user='root', passwd='passWord', db='Books')
        #database cursor
        x = conn.cursor()
        new_user__query = "INSERT INTO Users (Name, Username, Password) Values ('%s', '%s', '%s')" % (name, username, password)
        try:
                x.execute(new_user__query)
                #time.sleep(2)
                conn.commit()
                return render_template("index.html")
        except Exception:
                #print ("\n User wasn't add \n") #User probably already exists, will deal with this later
                traceback.print_exc()
                #print ("\n \n")
                #print(new_user__query)
                return render_template("newaccount.html")

@app.route("/login", methods=['POST'])
def login():
        index_username = str(request.form["username"])
        index_password = str(request.form["password"])
        x = conn.cursor()
        login_query = "Select * from Users where Username='%s'" % (index_username)
        #print (login_query)
        x.execute(login_query)
        #time.sleep(2)
        data_line = x.fetchone()
        if(data_line is not None and data_line[1] == index_username and data_line[2] == index_password):
                table_query = "SELECT * FROM allBooks LIMIT 75"
                x.execute(table_query)
                data = x.fetchall()
                username = request.form["username"]
                resp = make_response(render_template("welcome.html", data=data))
                resp.set_cookie('user', username)
                resp.set_cookie('data_limit', '75')
                return resp
        return render_template("index.html")
        
@app.route("/next", methods=['POST'])
def next():
        lim = int(request.cookies.get('data_limit'))
        conn = MySQLdb.connect(host='projectdb.cehud0y2r1tl.us-east-2.rds.amazonaws.com', user='root', passwd='passWord', db='Books')
        #database cursor
        x = conn.cursor()
        if(lim < 7080):
                table_query = "SELECT * FROM allBooks LIMIT 75 OFFSET %s" %(lim)
                x.execute(table_query)
                data = x.fetchall()
                resp = make_response(render_template("welcome.html", data=data))
                resp.set_cookie('data_limit', str(lim+75))
                return resp
        table_query = "SELECT * FROM allBooks LIMIT 75"
        x.execute(table_query)
        data = x.fetchall()
        resp = make_response(render_template("welcome.html", data=data))
        resp.set_cookie('data_limit', '75')
        return resp

@app.route("/previous", methods=['POST'])
def previous():
        lim = int(request.cookies.get('data_limit'))
        conn = MySQLdb.connect(host='projectdb.cehud0y2r1tl.us-east-2.rds.amazonaws.com', user='root', passwd='passWord', db='Books')
        #database cursor
        x = conn.cursor()
        if(lim > 75):
                table_query = "SELECT * FROM allBooks LIMIT 75 OFFSET %s" %(lim-150)
                x.execute(table_query)
                data = x.fetchall()
                resp = make_response(render_template("welcome.html", data=data))
                resp.set_cookie('data_limit', str(lim-150))
                return resp
        table_query = "SELECT * FROM allBooks LIMIT 75"
        x.execute(table_query)
        data = x.fetchall()
        resp = make_response(render_template("welcome.html", data=data))
        resp.set_cookie('data_limit', '75')
        return resp

@app.route("/search", methods=['POST'])
def search():
        return render_template("search.html")
        
@app.route("/results", methods=['POST'])
def results():
        conn = MySQLdb.connect(host='projectdb.cehud0y2r1tl.us-east-2.rds.amazonaws.com', user='root', passwd='passWord', db='Books')
        #database cursor
        x = conn.cursor()
        cat = request.form['category']
        searchval = request.form['value']
        price = request.form['price']
        site = request.form['site']
        if searchval == '':
                if price == 'Select Option':
                        if site == 'Select Option':
                                table_query = "SELECT * FROM allBooks LIMIT 75"
                                x.execute(table_query)
                                data = x.fetchall()
                                resp = make_response(render_template("welcome.html", data=data))
                                resp.set_cookie('data_limit', '75')
                                return resp
                        else:
                                table_query = "SELECT * FROM allBooks WHERE Site = '%s' LIMIT 75" %(site)
                                x.execute(table_query)
                                data = x.fetchall()
                                numrows = x.rowcount
                                table_query2 = "SELECT * FROM allBooks WHERE Site = '%s'" %(site)
                                x.execute(table_query2)
                                maxrows = x.rowcount
                                resp = make_response(render_template("results.html", data=data))
                                resp.set_cookie('maxrows', str(maxrows))
                                resp.set_cookie('retrows', str(numrows))
                                resp.set_cookie('query', table_query)
                                return resp
                if price == 'Low to High':
                        if site == 'Select Option':
                                table_query = "SELECT * FROM allBooks ORDER BY CAST(Price AS DECIMAL(10,2)) ASC LIMIT 75"
                                x.execute(table_query)
                                data = x.fetchall()
                                numrows = x.rowcount
                                table_query2 = "SELECT * FROM allBooks ORDER BY CAST(Price AS DECIMAL(10,2)) ASC"
                                x.execute(table_query2)
                                maxrows = x.rowcount
                                resp = make_response(render_template("results.html", data=data))
                                resp.set_cookie('maxrows', str(maxrows))
                                resp.set_cookie('retrows', str(numrows))
                                resp.set_cookie('query', table_query)
                                return resp
                        else:
                                table_query = "SELECT * FROM allBooks WHERE Site = '%s' ORDER BY CAST(Price AS DECIMAL(10,2)) ASC LIMIT 75" %(site)
                                x.execute(table_query)
                                data = x.fetchall()
                                numrows = x.rowcount
                                table_query2 = "SELECT * FROM allBooks WHERE Site = '%s' ORDER BY CAST(Price AS DECIMAL(10,2)) ASC" %(site)
                                x.execute(table_query2)
                                maxrows = x.rowcount
                                resp = make_response(render_template("results.html", data=data))
                                resp.set_cookie('maxrows', str(maxrows))
                                resp.set_cookie('retrows', str(numrows))
                                resp.set_cookie('query', table_query)
                                return resp
                 else:
                        if site == 'Select Option':
                                table_query = "SELECT * FROM allBooks ORDER BY CAST(Price AS DECIMAL(10,2)) DESC LIMIT 75"
                                x.execute(table_query)
                                data = x.fetchall()
                                numrows = x.rowcount
                                table_query2 = "SELECT * FROM allBooks ORDER BY CAST(Price AS DECIMAL(10,2)) DESC"
                                x.execute(table_query2)
                                maxrows = x.rowcount
                                resp = make_response(render_template("results.html", data=data))
                                resp.set_cookie('maxrows', str(maxrows))
                                resp.set_cookie('retrows', str(numrows))
                                resp.set_cookie('query', table_query)
                                return resp
                        else:
                                table_query = "SELECT * FROM allBooks WHERE Site = '%s' ORDER BY CAST(Price AS DECIMAL(10,2)) DESC LIMIT 75" %(site)
                                x.execute(table_query)
                                data = x.fetchall()
                                numrows = x.rowcount
                                table_query2 = "SELECT * FROM allBooks WHERE Site = '%s' ORDER BY CAST(Price AS DECIMAL(10,2)) DESC" %(site)
                                x.execute(table_query2)
                                maxrows = x.rowcount
                                resp = make_response(render_template("results.html", data=data))
                                resp.set_cookie('maxrows', str(maxrows))
                                resp.set_cookie('retrows', str(numrows))
                                resp.set_cookie('query', table_query)
                                return resp
        else:
                if price == 'Select Option':
                        if site == 'Select Option':
                                table_query = "SELECT * FROM allBooks WHERE %s LIKE '%%%s%%' LIMIT 75" %(cat, searchval)
                                x.execute(table_query)
                                data = x.fetchall()
                                numrows = x.rowcount
                                table_query2 = "SELECT * FROM allBooks WHERE %s LIKE '%%%s%%'" %(cat, searchval)
                                x.execute(table_query2)
                                maxrows = x.rowcount
                                resp = make_response(render_template("results.html", data=data))
                                resp.set_cookie('maxrows', str(maxrows))
                                resp.set_cookie('retrows', str(numrows))
                                resp.set_cookie('query', table_query)
                                return resp
                        else:
                                table_query = "SELECT * FROM allBooks WHERE %s LIKE '%%%s%%' AND Site = '%s' LIMIT 75" %(cat, searchval, site)
                                x.execute(table_query)
                                data = x.fetchall()
                                numrows = x.rowcount
                                table_query2 = "SELECT * FROM allBooks WHERE %s LIKE '%%%s%%' AND Site = '%s'" %(cat, searchval, site)
                                x.execute(table_query2)
                                maxrows = x.rowcount
                                resp = make_response(render_template("results.html", data=data))
                                resp.set_cookie('maxrows', str(maxrows))
                                resp.set_cookie('retrows', str(numrows))
                                resp.set_cookie('query', table_query)
                                return resp
                if price == 'Low to High':
                        if site == 'Select Option':
                                table_query = "SELECT * FROM allBooks WHERE %s LIKE '%%%s%%' ORDER BY CAST(Price AS DECIMAL(10,2)) ASC LIMIT 75" %(cat, searchval)
                                x.execute(table_query)
                                data = x.fetchall()
                                numrows = x.rowcount
                                table_query2 = "SELECT * FROM allBooks WHERE %s LIKE '%%%s%%' ORDER BY CAST(Price AS DECIMAL(10,2)) ASC" %(cat, searchval)
                                x.execute(table_query2)
                                maxrows = x.rowcount
                                resp = make_response(render_template("results.html", data=data))
                                resp.set_cookie('maxrows', str(maxrows))
                                resp.set_cookie('retrows', str(numrows))
                                resp.set_cookie('query', table_query)
                                return resp
                        else:
                                table_query = "SELECT * FROM allBooks WHERE %s LIKE '%%%s%%' AND Site = '%s' ORDER BY CAST(Price AS DECIMAL(10,2)) ASC LIMIT 75" %(cat, searchval, site)
                                x.execute(table_query)
                                data = x.fetchall()
                                numrows = x.rowcount
                                table_query2 = "SELECT * FROM allBooks WHERE %s LIKE '%%%s%%' AND Site = '%s' ORDER BY CAST(Price AS DECIMAL(10,2)) ASC" %(cat, searchval, site)
                                x.execute(table_query2)
                                maxrows = x.rowcount
                                resp = make_response(render_template("results.html", data=data))
                                resp.set_cookie('maxrows', str(maxrows))
                                resp.set_cookie('retrows', str(numrows))
                                resp.set_cookie('query', table_query)
                                return resp
                else:
                        if site == 'Select Option':
                                table_query = "SELECT * FROM allBooks WHERE %s LIKE '%%%s%%' ORDER BY CAST(Price AS DECIMAL(10,2)) DESC LIMIT 75" %(cat, searchval)
                                x.execute(table_query)
                                data = x.fetchall()
                                numrows = x.rowcount
                                table_query2 = "SELECT * FROM allBooks WHERE %s LIKE '%%%s%%' ORDER BY CAST(Price AS DECIMAL(10,2)) DESC" %(cat, searchval)
                                x.execute(table_query2)
                                maxrows = x.rowcount
                                resp = make_response(render_template("results.html", data=data))
                                resp.set_cookie('maxrows', str(maxrows))
                                resp.set_cookie('retrows', str(numrows))
                                resp.set_cookie('query', table_query)
                                return resp
                        else:
                                table_query = "SELECT * FROM allBooks WHERE %s LIKE '%%%s%%' AND Site = '%s' ORDER BY CAST(Price AS DECIMAL(10,2)) DESC LIMIT 75" %(cat, searchval, site)
                                x.execute(table_query)
                                data = x.fetchall()
                                numrows = x.rowcount
                                table_query2 = "SELECT * FROM allBooks WHERE %s LIKE '%%%s%%' AND Site = '%s' ORDER BY CAST(Price AS DECIMAL(10,2)) DESC" %(cat, searchval, site)
                                x.execute(table_query2)
                                maxrows = x.rowcount
                                resp = make_response(render_template("results.html", data=data))
                                resp.set_cookie('maxrows', str(maxrows))
                                resp.set_cookie('retrows', str(numrows))
                                resp.set_cookie('query', table_query)
                                return resp
                                
@app.route("/nextResult", methods=['POST'])
def nextResult():
        max = int(request.cookies.get('maxrows'))
        query = request.cookies.get('query')
        num = int(request.cookies.get('retrows'))
        conn = MySQLdb.connect(host='projectdb.cehud0y2r1tl.us-east-2.rds.amazonaws.com', user='root', passwd='passWord', db='Books')
        #database cursor
        x = conn.cursor()
        if num < max:
                new_query = query+" OFFSET %s" %(str(num))
                x.execute(new_query)
                numrows = x.rowcount
                data = x.fetchall()
                resp = make_response(render_template("results.html", data=data))
                resp.set_cookie('retrows', str(numrows+num))
                return resp
        if num == max:
                x.execute(query)
                numrows = x.rowcount
                data = x.fetchall()
                resp = make_response(render_template("results.html", data=data))
                resp.set_cookie('retrows', str(numrows))
                return resp

@app.route("/addToCart", methods=['POST'])
def addToCart():
        index_item = str(request.form.get('item'))
        #print(index_item)
        y = index_item.split("\', ")
        title = y[0]
        title = title.replace("(", "")
        title = title.strip('\'')
        author = y[1]
        author = author.strip()
        author = author.strip('\'')
        return render_template("addtocart.html", title=title, author=author, item=index_item)

@app.route("/addingToCart", methods=['POST'])
def addingToCart():
        qty = request.form.get('quantity')
        name = request.cookies.get('user')
        index_item = str(request.form.get('item'))
        y = index_item.split("\', ")
        isbn = y[3]
        isbn = isbn.replace("'", "")
        isbn = isbn.strip()
        site = y[6]
        site = site.replace("'", "")
        site = site.strip()
        conn = MySQLdb.connect(host='projectdb.cehud0y2r1tl.us-east-2.rds.amazonaws.com', user='root', passwd='passWord', db='Books')
        #database cursor
        x = conn.cursor()
        check_query = "SELECT * FROM Cart WHERE Username = '%s' AND ISBN = '%s' AND Site = '%s'" % (name, isbn, site)
        x.execute(check_query)
        conn.commit()
        data = x.fetchone()
        num = y[7]
        z = num.split(",")
        available = z[1]
        available = available.replace(")","")
        available = available.replace("'", "")
        available = available.strip()
        available = available.strip('L')
        if data is not None:
                if int(qty) + int(data[3]) <= int(available):
                        update_cart_query = "UPDATE Cart SET qtyDesired = '%s' WHERE Username = '%s' AND ISBN = '%s' AND Site = '%s'" % (str(int(qty) + int(data[3])), name, isbn, site)
                        x.execute(update_cart_query)
                        conn.commit()
                show_cart_query = "SELECT * FROM Cart INNER JOIN allBooks WHERE Cart.ISBN = allBooks.ISBN AND Cart.Site = allBooks.Site AND Username = '%s'" %(name)
                x.execute(show_cart_query)
                conn.commit()
                data = x.fetchall()
                return render_template("cart.html", user=name, data=data)
        new_cart_query = "INSERT INTO Cart (Username, ISBN, Site, qtyDesired) Values ('%s', '%s', '%s', '%s')" % (name, isbn, site, qty)
        if int(available) >= int(qty):
                x.execute(new_cart_query)
                #time.sleep(2)
                #print(new_user__query)
                conn.commit()
        show_cart_query = "SELECT * FROM Cart INNER JOIN allBooks WHERE Cart.ISBN = allBooks.ISBN AND Cart.Site = allBooks.Site AND Username = '%s'" %(name)
        x.execute(show_cart_query)
        conn.commit()
        data = x.fetchall()
        return render_template("cart.html", data=data)
        
@app.route("/deleteFromCart", methods=['POST'])
def deleteFromCart():
        index_item = str(request.form.get('item'))
        name = request.cookies.get('user')
        y = index_item.split("\', ")
        isbn = y[1]
        isbn = isbn.replace("'", "")
        isbn = isbn.strip()
        site = y[2]
        site = site.replace("'", "")
        site = site.strip()
        conn = MySQLdb.connect(host='projectdb.cehud0y2r1tl.us-east-2.rds.amazonaws.com', user='root', passwd='passWord', db='Books')
        #database cursor
        x = conn.cursor()
        delete_query = "DELETE FROM Cart WHERE Username = '%s' AND ISBN = '%s' AND Site = '%s'" % (name, isbn, site)
        x.execute(delete_query)
        conn.commit()
        show_cart_query = "SELECT * FROM Cart INNER JOIN allBooks WHERE Cart.ISBN = allBooks.ISBN AND Cart.Site = allBooks.Site AND Username = '%s'" %(name)
        x.execute(show_cart_query)
        conn.commit()
        data = x.fetchall()
        return render_template("cart.html", data=data)

@app.route("/updateQuantity", methods=['POST'])
def updateQuantity():
        qty = request.form.get('quantity')
        index_item = str(request.form.get('item'))
        name = request.cookies.get('user')
        y = index_item.split("\', ")
        isbn = y[1]
        isbn = isbn.replace("'", "")
        isbn = isbn.strip()
        site = y[2]
        site = site.replace("'", "")
        site = site.strip()
        conn = MySQLdb.connect(host='projectdb.cehud0y2r1tl.us-east-2.rds.amazonaws.com', user='root', passwd='passWord', db='Books')
        #database cursor
        x = conn.cursor()
        check_query = "SELECT * FROM Cart WHERE Username = '%s' AND ISBN = '%s' AND Site = '%s'" % (name, isbn, site)
        x.execute(check_query)
        conn.commit()
        data = x.fetchone()
        num = y[10]
        z = num.split(",")
        available = z[1]
        available = available.replace(")","")
        available = available.replace("'", "")
        available = available.strip()
        available = available.strip('L')
        if int(qty) <= int(available):
                update_query = "UPDATE Cart SET qtyDesired = '%s' WHERE Username = '%s' AND ISBN = '%s' AND Site = '%s'" % (qty, name, isbn, site)
                x.execute(update_query)
                conn.commit()
        show_cart_query = "SELECT * FROM Cart INNER JOIN allBooks WHERE Cart.ISBN = allBooks.ISBN AND Cart.Site = allBooks.Site AND Username = '%s'" %(name)
        x.execute(show_cart_query)
        conn.commit()
        data = x.fetchall()
        return render_template("cart.html", data=data)

@app.route("/checkout", methods=['POST'])
def checkout():
        name = request.cookies.get('user')
        conn = MySQLdb.connect(host='projectdb.cehud0y2r1tl.us-east-2.rds.amazonaws.com', user='root', passwd='passWord', db='Books')
        #database cursor
        x = conn.cursor()
        show_cart_query = "SELECT * FROM Cart INNER JOIN allBooks WHERE Cart.ISBN = allBooks.ISBN AND Cart.Site = allBooks.Site AND Username = '%s'" %(name)
        x.execute(show_cart_query)
        conn.commit()
        data = x.fetchall()
        total_query = "SELECT SUM(CAST(Price AS DECIMAL(10,2))*qtyDesired) FROM (allBooks INNER JOIN Cart ON allBooks.Site = Cart.Site AND allBooks.ISBN = Cart.ISBN) WHERE Username= '%s'" %(name)
        x.execute(total_query)
        conn.commit()
        tottup = x.fetchall()
        tot = str(tottup)
        if tot == '((None,),)':
                return render_template("checkout.html", data=data, tot="0.00")
        tot = tot.replace("((Decimal('", "")
        tot = tot.replace("'),),)", "")
        return render_template("checkout.html", data=data, tot=tot)

@app.route("/placeOrder", methods=['POST'])
def placeOrder():
        name = request.cookies.get('user')
        address = str(request.form['address'])
        conn = MySQLdb.connect(host='projectdb.cehud0y2r1tl.us-east-2.rds.amazonaws.com', user='root', passwd='passWord', db='Books')
        #database cursor
        x = conn.cursor()
        total_query = "SELECT SUM(CAST(Price AS DECIMAL(10,2))*qtyDesired) FROM (allBooks INNER JOIN Cart ON allBooks.Site = Cart.Site AND allBooks.ISBN = Cart.ISBN) WHERE Username= '%s'" %(name)
        x.execute(total_query)
        conn.commit()
        tottup = x.fetchall()
        tot = str(tottup)
        if tot == '((None,),)':
                return render_template("cart.html")
        tot = tot.replace("((Decimal('", "")
        tot = tot.replace("'),),)", "")
        new_order_query = "INSERT INTO Orders(Username, Address, Total) Values('%s', '%s', '%s')" %(name, address, tot)
        x.execute(new_order_query)
        conn.commit()
        new_books_query = "INSERT INTO orderedBooks(OrderID, ISBN, Site, qtyOrdered) SELECT OrderID, Cart.ISBN, Cart.Site, qtyDesired FROM Orders INNER JOIN Cart INNER JOIN allBooks WHERE Cart.ISBN = allBooks.ISBN AND Cart.Site = allBooks.Site AND Cart.Username = Orders.Username AND Cart.Username = '%s' AND OrderID= (SELECT MAX(OrderID) FROM Orders) AND qtyDesired <= booksAvailable" %(name)
        x.execute(new_books_query)
        conn.commit()
        delete_old_query = "DELETE FROM Cart WHERE Username = '%s'" %(name)
        x.execute(delete_old_query)
        conn.commit()
        update_book_qty = "UPDATE allBooks INNER JOIN orderedBooks ON (orderedBooks.ISBN = allBooks.ISBN AND orderedBooks.Site = allBooks.Site) SET allBooks.booksAvailable = allBooks.booksAvailable - orderedBooks.qtyOrdered, allBooks.booksSold = allBooks.booksSold + orderedBooks.qtyOrdered WHERE OrderID = (SELECT MAX(OrderID) FROM Orders)"
        x.execute(update_book_qty)
        conn.commit()
        show_orders_query = "SELECT Orders.OrderID, Address, SUM(qtyOrdered), Total FROM Orders INNER JOIN orderedBooks WHERE Orders.OrderID = orderedBooks.OrderID AND Orders.Username = '%s' GROUP BY Orders.OrderID" %(name)
        x.execute(show_orders_query)
        conn.commit()
        data = x.fetchall()
        return render_template("orderdashboard.html", data=data)
        
@app.route("/orderDetails", methods=['POST'])
def orderDetails():
        index_item = str(request.form.get('item'))
        l = index_item.split(",")
        y = l[0]
        y = y.strip("(")
        y = y.strip("L")
        conn = MySQLdb.connect(host='projectdb.cehud0y2r1tl.us-east-2.rds.amazonaws.com', user='root', passwd='passWord', db='Books')
        #database cursor
        x = conn.cursor()
        order_books_query = "SELECT * FROM orderedBooks INNER JOIN allBooks WHERE orderedBooks.ISBN = allBooks.ISBN AND orderedBooks.Site = allBooks.Site AND OrderID = '%s'" %(y)
        x.execute(order_books_query)
        conn.commit()
        data = x.fetchall()
        order_query = "SELECT * FROM Orders WHERE OrderID = '%s'" %(y)
        x.execute(order_query)
        conn.commit()
        orderdata = x.fetchall()
        return render_template("orderdetails.html", data=data, orderdata=orderdata)

@app.route("/orderDashboard", methods=['POST'])
def orderDashboard():
        name = request.cookies.get('user')
        conn = MySQLdb.connect(host='projectdb.cehud0y2r1tl.us-east-2.rds.amazonaws.com', user='root', passwd='passWord', db='Books')
        #database cursor
        x = conn.cursor()
        show_orders_query = "SELECT Orders.OrderID, Address, SUM(qtyOrdered), Total FROM Orders INNER JOIN orderedBooks WHERE Orders.OrderID = orderedBooks.OrderID AND Orders.Username = '%s' GROUP BY Orders.OrderID" %(name)
        x.execute(show_orders_query)
        conn.commit()
        data = x.fetchall()
        return render_template("orderdashboard.html", data=data)

@app.route("/cart", methods=['POST'])
def cart():
        name = request.cookies.get('user')
        conn = MySQLdb.connect(host='projectdb.cehud0y2r1tl.us-east-2.rds.amazonaws.com', user='root', passwd='passWord', db='Books')
        #database cursor
        x = conn.cursor()
        show_cart_query = "SELECT * FROM Cart INNER JOIN allBooks WHERE Cart.ISBN = allBooks.ISBN AND Cart.Site = allBooks.Site AND Username = '%s'" %(name)
        x.execute(show_cart_query)
        conn.commit()
        data = x.fetchall()
        return render_template("cart.html", data=data)

@app.route("/books", methods=['POST'])
def books():
        conn = MySQLdb.connect(host='projectdb.cehud0y2r1tl.us-east-2.rds.amazonaws.com', user='root', passwd='passWord', db='Books')
        #database cursor
        x = conn.cursor()
        table_query = "SELECT * FROM allBooks LIMIT 75"
        x.execute(table_query)
        data = x.fetchall()
        resp = make_response(render_template("welcome.html", data=data))
        resp.set_cookie('data_limit', '75')
        return resp

@app.route("/logout", methods=['POST'])
def logout():
        return render_template("index.html")
        
@app.route("/patternOne", methods=['POST'])
def patternOne():
        conn = MySQLdb.connect(host='projectdb.cehud0y2r1tl.us-east-2.rds.amazonaws.com', user='root', passwd='passWord', db='Books')
        #database cursor
        x = conn.cursor()
        table_query = "SELECT AVG((CAST(Price AS DECIMAL(10,2)))) FROM allBooks"
        x.execute(table_query)
        data = x.fetchall()
        y = str(data[0])
        y = y.strip("Decimal('")
        y = y.strip("'),)")
        price = y
        return render_template("patternOne.html", price=price)

@app.route("/patternTwo", methods=['POST'])
def patternTwo():
        conn = MySQLdb.connect(host='projectdb.cehud0y2r1tl.us-east-2.rds.amazonaws.com', user='root', passwd='passWord', db='Books')
        #database cursor
        x = conn.cursor()
        table_query = "SELECT COUNT(*), Genre FROM allBooks GROUP BY Genre ORDER BY COUNT(*) DESC LIMIT 1"
        x.execute(table_query)
        item = str(x.fetchall())
        item = item.split(",")
        y = item[1]
        y = y.strip(")")
        y = y.replace("'", "")
        genre = y
        z = item[0]
        z = z.strip("((")
        z = z.strip("L")
        qty = z
        return render_template("patternTwo.html", qty=qty, genre=genre)

if __name__ == "__main__":
        app.run(debug=True)