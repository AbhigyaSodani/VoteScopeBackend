import flask
from flask import request, jsonify
import sqlite3
import hashlib
from flask_cors import CORS
from flask_bcrypt import generate_password_hash, check_password_hash
import mysql.connector
import jwt
from datetime import datetime, timedelta
from random import randint


SECRET_KEY="8947357943789907843098489284HFVH94-7FG-GVVG-"
app = flask.Flask(__name__)
app.config["DEBUG"] = True
cors = CORS(app)
db = mysql.connector.connect(user='databse', password='sgbat2001',
                                host='34.132.108.122',
                                database='polls')
cursor = db.cursor(buffered=True)
def tokenize(user_data: dict) -> str:
    return jwt.encode(
        {
            'user_id': user_data[0],
            'email': user_data[1],
            'password': user_data[2],
            'type': user_data[3],
            'exp': datetime.utcnow() + timedelta(days=365)
        },
        SECRET_KEY,
        algorithm="HS256")

def user_helper(user) -> dict:
    print(user)
    return {
        "id": str(user[0]["id"]),
        "email": str(user[0]["email"]),
        "password": str(user[0]["password"]),
        "type":str(user[0]["type"])
    }

def authenticate_user(username: str, password: str) -> dict:
    cursor.execute("select * from polls.users where email = 'abhigyasodani@gmail.com'")
    email=None
    password_real=None
    type_real=None
    id_real = None
    for (id, email_temp, password_temp, type) in cursor:
        email=email_temp
        password_real=password_temp
        type_real=type
        id_real = id
    try:
        if email and check_password_hash(password_real,
                                                password):
            return (id_real,username,password_real,type_real)
        else:
            return None
    except:
        return None



@app.route('/signup', methods=['POST'])
def api_signup():
    if(request.method=='POST'):
        data = request.json
        
        print(data)

        message = 'success'

        # make sure no fields are blank
    
        if data['email'] == '':
            message = "No email given. Try again"
        elif data['password'] == '':
            message = "No password given. Try again"

        if message != 'success':
            print(message)
            return {"status": 403, "message" : message}

        # make sure username is not a duplicate

        duplicate = cursor.execute("SELECT * FROM users WHERE email = %(email)s", {"email":data['email']})
        print(duplicate)
        if duplicate is not None:
            message = "Email already exists. Pick another one."

        if message != 'success':
            print(message)
            return {"status": 403, "message" : message}

        # hash the password before storing it

        read = cursor.execute("INSERT INTO users(email,password,type) VALUES('"+str(data['email'])+"','"+str(generate_password_hash(str(data['password'])).decode('utf8'))+"','"+str(data['type'])+"')")
        cursor.close()
        db.commit()
        db.close()
        return { "status" : 200 }

@app.route('/login', methods=['GET', 'POST'])
def api_login():
    if request.method == 'POST':
      data = request.json
      print(request)
      auth_user = authenticate_user(data['email'], str(data['password']))
      if auth_user:
            token = tokenize(auth_user)
            if type(token) is bytes:
                token=token[2:-1]
            return {"status": 200, "access_token": str(token), "token_type": "bearer"}
      else:
          return {"status": 403, "message": "Wrong credentials!"}
app.run()
