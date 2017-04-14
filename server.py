from flask import Flask, render_template, redirect, request, session, flash
import re, md5
from mysqlconnection import MySQLConnector

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

app = Flask(__name__)
mysql = MySQLConnector(app, 'thewall_db')
app.secret_key = 'this is secret'

@app.route('/')
def index():
  return render_template('index.html')


@app.route('/register', methods = ['POST'])
def register():
    print request.form
    #store if we validations (variable)
    errors = []
    # chekc form info for correct information
    fname = request.form['first_name']
    lname = request.form['last_name']
    email = request.form['email']
    password = request.form['password']
    password_confirmation = request.form['password_confirmation']

    if len(fname) < 2:
     errors.append('First name is too short!')
    if len(lname) < 2:
     errors.append('Last name is too short!')
    # if not fname.isaplha():
    #   errors.append('First name must be characters!')
    # if not lname.isaplha():
    #   errors.append('Last name must be characters!')
    if not len(email):
      errors.append('email is required!')
    # if not EMAIL_REGEX.match(email):
    #   errors.append('email is invalid!')
    # # query = 'SELECT * FROM users WHERE email = :email'
    # # data = {
    # #   'email': email
    # # }
    # # email = mysql.query_db(query, data)
    # if email:
    #   errors.append('email must be unique!')
    if len(password) < 8:
      errors.append('password must be 8 characters long!')
    if not password == password_confirmation:
      errors.append('password must match')
    
    print errors
    # did we pass validations 

    if errors:
      for error in errors:
         flash (error)
      return redirect('/')
    #if false
    else:
      print ' passed vlidations'
      #hash password
      encrypted_password = md5.new(password).hexdigest()
      #create an user
      query = 'INSERT INTO users (first_name, last_name, email, hwpassword, created_at, updated_at) VALUES(:first_name, :last_name, :email, :hwpassword, NOW(), NOW())'
      data = {
        'first_name':fname,
        'last_name':lname,
        'email': email,
        'hwpassword': encrypted_password
      }
      user_id = mysql.query_db(query, data)
      print user_id
      # store user info in seesion
      session['user_id'] = user_id
      #redirect to success page
      return redirect('/wall')

@app.route('/login', methods=['POST'])
def login():
  #find a user with form email
  query = 'SELECT * FROM users WHERE email = :email'
  data = {
    'email': request.form['email']
  }
  user = mysql.query_db(query, data)
  #if user
  if user:
    #hashed pw from the form
    encrypted_password = md5.new(request.form['password]']).hexdigest()
    #do the passwords match
    if encrypted_password == user[0]['password']:
    #if true
      #store user info in seesion
      session['user_id'] = user[0]['id']
      #redirect to success page
      return redirect('/wall')
    #else false
    else:
      #send error to client
      flash('email is invalid')
      #redirect to index
      return redirect('/')


@app.route('/message', methods = ['POST'])
def message():
  message = request.form['message']
  user_id = session['user_id']
  query = 'INSERT INTO messages (message, created_at, updated_at, user_id) VALUES(:message, NOW(), NOW(), :user_id)'
  data = {
    'message':message,
    'user_id':user_id
  }
  # sends info to database
  mysql.query_db(query, data)
  return redirect('/wall')

@app.route('/comment/<messages_id>', methods = ['POST'])
def comment(messages_id):
  print "you made it to comment route!"
  comment = request.form['comment']
  print "test"
  user_id = session['user_id']
  messIDtoDB = int(messages_id)
  query = 'INSERT INTO comments (comment, created_at, updated_at, user_id, message_id) VALUES(:comment, NOW(), NOW(), :user_id, :messIDtoDB)'
  data = {
    'comment':comment,
    'user_id':user_id,
    'messIDtoDB':messages_id
  }
  # sends info to database
  mysql.query_db(query, data)
  return redirect('/wall')

@app.route('/wall')
def wall():
  if 'user_id' in session:
    #query to pull info from db
    query = 'SELECT messages.id, messages.message, users.first_name, users.last_name, messages.user_id, DATE_FORMAT(messages.created_At, "%M %D %T") AS time FROM messages JOIN users ON users.id = messages.user_id;'
    messages = mysql.query_db(query)

    ### this needs to be fixed
    # query1 = 'SELECT comments.id, comments.message, users.first_name, users.last_name, comments.user_id, DATE_FORMAT(comments.created_At, "%M %D %T") AS time FROM comments JOIN users ON users.id = comments.user_id;'

    #comments = mysql.query_db(query1)
    return render_template('wall.html', messageToWall = messages)
  else:
    return redirect('/')

@app.route('/logout', methods = ['POST'])
def logout():
  session.clear()
  return redirect('/')

app.run(debug = True)