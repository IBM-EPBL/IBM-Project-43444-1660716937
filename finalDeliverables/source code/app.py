from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL

import MySQLdb.cursors
import re
from sendemail import usermail,agentmail
app = Flask(__name__)

app.secret_key='a'

app.config['MYSQL_HOST'] = 'remotemysql.com'
app.config['MYSQL_USER'] = 'cmD4MqEFox'
app.config['MYSQL_PASSWORD'] = 'szmvOT91Pl'
app.config['MYSQL_DB'] = 'cmD4MqEFox'
mysql = MySQL(app)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/registertemp',methods=["POST","GET"])
def registertemp():
    return render_template("register.html")

@app.route('/uploaddata',methods =['GET','POST'])
def register():
    msg = ''
    if request.method == 'POST':
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        address = request.form['address']
        cursor = mysql.connection.cursor()
        
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM users WHERE username = % s', (username, ))
    account = cursor.fetchone()
    print(account)
    if account:
        msg = 'Account already exists !'
    elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
        msg = 'Invalid email address !'
    elif not re.match(r'^[A-Za-z0-9_.-]*$', username):
        msg = 'name must contain only characters and numbers !'
    else:
        cursor.execute('INSERT INTO users VALUES (NULL,% s,% s,% s,% s,% s,% s)',(firstname,lastname,username,email,password,address,))
        mysql.connection.commit()
        msg = 'Dear % s You have successfully registered!'%(username)
    return render_template('register.html',a = msg,indicator="success")

@app.route('/login',methods=["POST","GET"])
def login():
    return render_template("login.html")

@app.route('/logindata',methods=["POST","GET"])
def logindata():
    global userid
    msg = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM users WHERE username = % s AND password = % s', (username, password, ))
        account = cursor.fetchone()
        print (account)
        if account:
            session['id'] = account[0]
            userid =  account[0]
            session['username'] = account[1]
            return redirect(url_for('dashboard'))
        else:
            msg = 'Incorrect username / password !'
            return render_template('login.html', b = msg,indicator="failure")
    else:
        return render_template("login.html",msg="ERROR")
@app.route('/home')
def dashboard():
    if 'id' in session:
        username = session['username']
        return render_template('userdashboard.html',name=username)

@app.route('/profile',methods=["POST","GET"])
def profile():
    if 'id' in session:
        uid = session['id']
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM users WHERE id = % s', (uid,))    
        cursor.connection.commit()
        acc = cursor.fetchone()
        return render_template('userprofile.html',fullname=acc[1]+acc[2],username=acc[3],email=acc[4],address=acc[6])

@app.route('/addcomplaint',methods=["POST","GET"])
def comp():
    if 'id' in session:
        return render_template('userlodgecomp.html')

@app.route('/complaint',methods=["POST","GET"])
def complaint():
    if request.method == "POST":
        if 'id' in session:
            msg = ''
            uid=session['id']
            selectcategory = request.form['selectcategory']
            selectsubcategory = request.form['selectsubcategory']
            complainttype = request.form['type']
            state = request.form['state']
            complaint = request.form.get('complaint')
            date = request.form['date']
            cursor = mysql.connection.cursor()
            cursor.execute("SELECT * FROM users WHERE id = % s",(uid,))
            acc = cursor.fetchone()
            email = acc[4]
            cursor.execute('INSERT INTO complaintdetails VALUES (NULL,% s,% s,% s,% s,% s,% s,% s,% s)',(uid,selectcategory,selectsubcategory,complainttype,state,complaint,date,'pending'))
            cursor.connection.commit()
            msg = 'You have successfully registered your complaint'
            TEXT1 = """\<!DOCTYPE html>
                    <html>
                    <body>
                        <div class="containter" style="display: block;">
                            <h3 style="font-size: 24px; font-family:serif"> Dear """+acc[1]+" "+acc[2]+""", </h3>
                            <div class="side" style="width: 400px; height: 150px; padding:30px; border-radius:10px; position:relative; left:100px;" >
                                <div class="details"style="position:relative;left:60px; font-size:20px;text-align:left;">
                                    <p style=" font-weight:bold;">Your complaint has been succesfully registered...!!</p>
                                    <p style=" font-weight:bold;">One of our agent is assigned , will surely resolve your complaint as soon as possible</p>
                                    <p style=" font-weight:bold;">Please check the complaint history tab for status of complaint.</p>
                                </div>
                            </div>
                        </div>
                    </body>
                    </html>"""
            TEXT = """\<!DOCTYPE html>
                    <html>
                    <body>
                        <div class="containter" style="display: block;">
                            <h3 style="font-size: 24px; font-family:serif"> New Complaint from """+acc[1]+" "+acc[2]+""" </h3>
                            <div class="side" style="width: 400px; height: 150px; padding:30px; border-radius:10px; position:relative; left:100px;" >
                                <div class="details"style="position:relative; top:20px; left:60px; font-size:20px;text-align:left;">
                                    <p style=" font-weight:bold;"> Complaint Description :</p>
                                    <p>"""+complaint+"""</p>
                                </div>
                            </div>
                        </div>
                    </body>
                    </html>"""
            agentemail = 'agentcustomercareregistry@gmail.com'
            usermail(TEXT1,email)
            agentmail(TEXT,agentemail)
            return render_template('userlodgecomp.html',a = msg)


@app.route('/view',methods=["POST","GET"])
def view():
    if 'id' in session:
        return render_template('comphistory.html')

@app.route('/comphistory',methods=['POST','GET'])
def compview(): 
    if 'id' in session:
        uid=session['id']
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM complaintdetails WHERE userid = % s',(uid,))
        cursor.connection.commit()
        comp = cursor.fetchall()
        return render_template('usercomphist.html',complaints = comp)

@app.route('/admin')
def admin():
    return render_template('admin.html')

@app.route('/adminpage')
def adminpage():
    return render_template('admin dashboard.html')

@app.route('/adminlog',methods=["POST","GET"])
def adminlog():
    msg = ''
    email = request.form['email']
    password = request.form['password']
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM admininfo  WHERE email = % s and password = % s',(email,password))
    cursor.connection.commit()
    logged = cursor.fetchone()
    if(logged):
        msg = 'successfully loggedin'
        return render_template("admin dashboard.html",a=msg)
    else:
        return render_template("admin.html",a="Incorrect email/password")

@app.route('/adcomplainthist',methods=['POST','GET'])
def adcomplainthist(): 
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM complaintdetails')
        cursor.connection.commit()
        comp = cursor.fetchall()
        return render_template('admincomphist.html',complaints = comp)
            
@app.route('/loggout')
def loggout():
    if 'id ' in session:
        session.pop('id',None)
        session.pop('email',None)
        session.pop('password',None)
    return redirect(url_for('home'))
    
@app.route('/logout')
def logout():
    if 'id ' in session:
        session.pop('id',None)
        session.pop('name',None)    
        session.pop('username',None)
    return redirect(url_for('home'))
    
@app.route('/agent',methods=["POST","GET"])
def agent():
    return render_template('agent.html')

@app.route('/agentdata',methods=["POST","GET"])
def agentdata():
    msg = ''
    username = request.form['username']
    password = request.form['password']
    cursor = mysql.connection.cursor()
    cursor.execute('INSERT INTO agentinfo VALUES (NULL,% s,% s)',(username,password))
    cursor.connection.commit()
    msg = 'Agent has been created successfully'
    return render_template('agent.html',a = msg)


@app.route('/solved/<no>')
def solved(no):
    i = no
    cursor = mysql.connection.cursor()
    cursor.execute("UPDATE complaintdetails SET status = % s WHERE id = % s",("Solved",i))
    cursor.connection.commit()
    return render_template('admincomphist.html',a="Complaint Resolved")

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=8080)