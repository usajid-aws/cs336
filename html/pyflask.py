from flask import Flask, render_template, request, redirect, url_for, make_response
import MySQLdb, traceback, time

app=Flask(__name__)

conn = MySQLdb.connect(host='projectdb.cehud0y2r1tl.us-east-2.rds.amazonaws.com', user='root', passwd='passWord', db='Books')

@app.route("/")
def index():
        return render_template("index.html")

@app.route("/newaccount.html")
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
                return redirect('http://ec2-18-188-67-244.us-east-2.compute.amazonaws.com/')
        except Exception:
                #print ("\n User wasn't add \n") #User probably already exists, will deal with this later
                traceback.print_exc()
                #print ("\n \n")
                #print(new_user__query)
                return "<h2>username already exists!</h2>"

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
                user = data_line[0]
                table_query = "SELECT * FROM allBooks LIMIT 50"
                x.execute(table_query)
                data = x.fetchall()
                username = request.form["username"]
                resp = make_response(render_template("welcome.html", user=user, data=data))
                resp.set_cookie('user', username)
                return resp
        return "<h2>unsuccessful login, password does not match or user does not exist!</h2>"

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

if __name__ == "__main__":
        app.run(debug=True)