from flask import Flask, render_template, request,redirect, url_for
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
	#database cursor
	x = conn.cursor()
	new_user__query = "INSERT INTO Users (Name, Username, Password) Values ('%s', '%s', '%s')" % (name, username, password)
	try:
		x.execute(new_user__query)
		time.sleep(2)
		conn.commit()
		return redirect('http://ec2-18-220-2-41.us-east-2.compute.amazonaws.com/')
	except Exception:
		#print ("\n User wasn't add \n") #User probably already exists, will deal with this later
		traceback.print_exc()
		#print ("\n \n")
		#print(new_user__query)
		return redirect('http://127.0.0.1:5000/')

@app.route("/login", methods=['POST'])
def login():
	index_username = str(request.form["username"])
	index_password = str(request.form["password"])
	x = conn.cursor()
	login_query = "Select * from Users where Username='%s'" % (index_username)
	#print (login_query)
	x.execute(login_query)
	time.sleep(2)
	data_line = x.fetchone()
	if(data_line is not None and data_line[1] == index_username and data_line[2] == index_password):
		user = data_line[0]
		return render_template("welcome.html", user=user)
	return "<h2> unsuccessful login, password dont match or user does not exist!</h2>"
	
	
	


if __name__ == "__main__":
	app.run(debug=True)
