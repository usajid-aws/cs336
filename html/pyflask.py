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
                return redirect('http://ec2-18-219-162-61.us-east-2.compute.amazonaws.com/')
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
                table_query = "SELECT * FROM Booklist LIMIT 50"
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
        y = index_item.split(",")
        title = y[0]
        title = title.replace("(", "")
        title = title.strip('\'')
        author = y[1]
        author = author.strip(' ')
        author = author.strip('\'')
        return render_template("addtocart.html", title=title, author=author, item=index_item)

@app.route("/addingToCart", methods=['POST'])
def addingToCart():
        qty = request.form.get('quantity')
        name = request.cookies.get('user')
        index_item = str(request.form.get('item'))
        y = index_item.split(",")
        isbn = y[3]
        isbn = isbn.replace("'", "")
        isbn = isbn.strip()
        site = y[6]
        site = site.replace("'", "")
        site = site.strip()
        conn = MySQLdb.connect(host='projectdb.cehud0y2r1tl.us-east-2.rds.amazonaws.com', user='root', passwd='passWord', db='Books')
        #database cursor
        x = conn.cursor()
        new_user__query = "INSERT INTO Cart (Username, ISBN, Site, qtyDesired) Values ('%s', '%s', '%s', '%s')" % (name, isbn, site, qty)
        try:
                x.execute(new_user__query)
                #time.sleep(2)
                #print(new_user__query)
                conn.commit()
                return "<h2>"+isbn+" "+site+" "+qty+" "+name+"</h2>"
        except Exception:
                #print ("\n User wasn't add \n") #User probably already exists, will deal with this later
                traceback.print_exc()
                #print ("\n \n")
                #print(new_user__query)
                return "<h2>error!</h2>"

if __name__ == "__main__":
        app.run(debug=True)