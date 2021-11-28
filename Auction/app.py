from flask import Flask, g, flash, abort, make_response, redirect, render_template, request, session, url_for, jsonify, send_from_directory
from markupsafe import escape
import functools
import sqlite3
from tempfile import gettempdir
from datetime import datetime, date
import os
from werkzeug.utils import secure_filename
from os.path import join, dirname, realpath              #Necessary Imports


UPLOAD_FOLDER = 'static/images/'                      # Defines where to put images added by the user
ALLOWED_EXTENSIONS = ['jpg']                          # Defines what type of images are acceptable
basedir = os.path.abspath(os.path.dirname(__file__))     

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.before_request                    # Defines the session before any page is loaded
def user_logged_in():
    user_id = session.get('uname')
    if user_id is None:
        g.user = None
    else:
        g.user='set'
    
 
 
def login_required(view):              #For pages that require a login, this function makes sure that
    @functools.wraps(view)             # the user is logged in before letting them access that page
    def wrapped_view(**kwargs):
        if session.get("uname") is None:
            return redirect(url_for("login"))
        return view(**kwargs)
    return wrapped_view 

 
def allowed_file(filename):            #Defines whether an image upload is allowed
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/')                        #Automatically redirects the user to the homepage when entering the url
def start():
    return redirect(url_for("home"))

@app.route('/register', methods=['GET', 'POST']) #Defines the route to the register page
def register():
    if request.method == 'POST':
        return do_the_registration(request.form['uname'], request.form['pwd'])
    else:
        return show_the_registration_form();

    
def show_the_registration_form():                 #loads register.html
    return render_template('register.html',page=url_for('register'))

def do_the_registration(u,p):   #Creates and adds to a table of users and their passwords 
    con = sqlite3.connect('registered_users.db')
    try:
        con.execute('CREATE TABLE users (name TEXT, pwd INT)')
        print ('Table created successfully');
    except:
        pass
    
    con.close()  
    
    con = sqlite3.connect('registered_users.db')
    con.execute("INSERT INTO users values(?,?);", (u, p))
    con.commit()
    con.close()  

    return show_the_login_form()    # Redirects to login.html right after registering

@app.route('/login', methods=['GET', 'POST']) #Defines the route to the login page
def login():
    session.clear()
    if request.method == 'POST':
        return do_the_login(request.form['uname'], request.form['pwd'])
    else:
        return show_the_login_form()
    

    
def show_the_login_form():
    return render_template('login.html',page=url_for('login')) #loads login.html

def do_the_login(u,p):   #Checks if the user input matches any username/password combos in the database
    con = sqlite3.connect('registered_users.db')
    cur = con.cursor();
    cur.execute("SELECT count(*) FROM users WHERE name=? AND pwd=?;", (u, p))
    if(int(cur.fetchone()[0]))>0:
        session['uname'] = request.form['uname']
        request.cookies.get('uname')
        return redirect(url_for("home"))
    else:
        abort(403)
         
        
@app.route('/logout')  #Cancels the users session and redirects them to the homepage
def logout():
 session.pop('uname', None)
 return redirect(url_for('home')) 


        
@app.errorhandler(403) 
def wrong_details(error):
    return render_template('wrong_details.html'), 403



@app.route('/home') #Defines the route to the homepage
def home(): #Connects to the database of items so they can be displayed in home.html
    con = sqlite3.connect("user_items.db")
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("SELECT * from userItems")
    rows = cur.fetchall();
    
    return render_template('homepage.html' ,page=url_for('home'), rows = rows)

@app.route('/new_item', methods=['GET', 'POST'])
@login_required #Checks that the user is logged in before accessing this page
def new_item():
          
    if request.method == 'POST':  #Allows user to add the item name, description and an image
        user = session["uname"]
        file = request.files['img']
        if file.filename == '':
            flash('No selected file')
            return redirect(url_for("home"))
            
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(basedir, app.config['UPLOAD_FOLDER'], filename))# Saves the uploaded image into /static/images
            time_start = datetime.now().strftime('%d-%m-%Y %H:%M:%S') #records a timestamp of the item addition
            
            return add_new_item(request.form['iname'], request.form['desc'], time_start, user)
        
        
    else:
        return show_new_item_form();

@app.route('/my_items')
@login_required
def my_items(): #Connects to the database of items so they can be displayed in my_items.html
    user = session["uname"]
    con = sqlite3.connect("user_items.db")
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("SELECT * from userItems WHERE userID=:user", {"user": user}) #Only displays items that were submitted by the user who is currently logged in
    rows = cur.fetchall();

    return render_template("my_items.html",rows = rows) #loads my_items.html
  
        

    
    
def show_new_item_form(): 
    return render_template('new_item.html',page=url_for('new_item')) #loads new_item.html


def add_new_item(i,d,t,u): #Creates and adds to a table of submitted Items
                
    con = sqlite3.connect('user_items.db')
    try:
        con.execute('CREATE TABLE userItems (iname TEXT, desc TEXT, time_start TEXT, userID TEXT)')
        print ('Table created successfully');
    except:
        pass
    
    con.close()  
    
    con = sqlite3.connect('user_items.db')
    con.execute("INSERT INTO userItems values(?,?,?,?)",(i,d,t,u))
    con.commit()
    con.close()
    
    return redirect(url_for("home"))


    




