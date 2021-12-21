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
import json


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

@app.route('/', methods=['POST'])
def test():
    return "test"
  
@app.route('/get_polls_many_checked', methods=['POST'])
def return_top_polls():
    data = request.json
    cursor.execute("SELECT * FROM polls WHERE poll_date < %(poll_date_end)s AND poll_date > %(poll_date_start)s AND checked=1", {"poll_date_start":data['poll_date_start'],"poll_date_end":data['poll_date_end']})
    rv=cursor.fetchall()
    if not rv:
        return json.dumps({"return":0})
    row_headers=[x[0] for x in cursor.description]
    try:
        json_data=[]
        for result in rv:
            json_data.append(dict(zip(row_headers,result)))
            


    except Exception as e:
        print(e)
    
    return json.dumps(json_data,default=str)

@app.route('/get_polls_many_all', methods=['POST'])
def return_top_polls_all():
    data = request.json
    cursor.execute("SELECT * FROM polls WHERE poll_date < %(poll_date_end)s AND poll_date > %(poll_date_start)s", {"poll_date_start":data['poll_date_start'],"poll_date_end":data['poll_date_end']})
    rv=cursor.fetchall()
    if not rv:
        return json.dumps({"return":0})
    row_headers=[x[0] for x in cursor.description]
    try:
        json_data=[]
        for result in rv:
            json_data.append(dict(zip(row_headers,result)))
            


    except Exception as e:
        print(e)
    
    return json.dumps(json_data,default=str)

@app.route('/get_poll', methods=['POST'])
def return_poll_by_id():
    data = request.json
    cursor.execute("SELECT * FROM polls WHERE id = %(poll_id)s AND checked=1", {"poll_id":data['poll_id']})
    rv=cursor.fetchall()
    if not rv:
        return json.dumps({"return":0})
    row_headers=[x[0] for x in cursor.description]
    try:
        json_data=[]
        for result in rv:
            json_data.append(dict(zip(row_headers,result)))
            return json.dumps(json_data[0],default=str)
            


    except Exception as e:
        print(e)
    
    
@app.route('/edit_poll', methods=['POST'])
def edit():
    data = request.json
    try:
        cursor.execute("UPDATE polls SET question=%(question)s WHERE id=%(poll_id)s", {"poll_id":data['poll_id'],"question":data['question']})
        db.commit()
        return json.dumps({"return":100})
    except Exception as e:
        print(e)
        return json.dumps({"return":0})


@app.route('/get_polls_singular', methods=['POST'])
def return_singular_polls():
    cursor.execute("SELECT * FROM polls.polls WHERE checked=1 ORDER BY poll_date desc")
    rv=cursor.fetchall()
    if not rv:
        return json.dumps({"return":0})
    row_headers=[x[0] for x in cursor.description]
    try:
        json_data=[]
        for result in rv:
            json_data.append(dict(zip(row_headers,result)))
            return json.dumps(json_data[0],default=str)


    except Exception as e:
        print(e)
     
   

@app.route('/get_poll_date', methods=['POST'])
def return_date_polls():
    data = request.json
    cursor.execute("SELECT * FROM polls WHERE poll_date = %(poll_date)s AND checked=1", {"poll_date":data['poll_date']})
    rv=cursor.fetchall()
    if not rv:
        return json.dumps({"return":0})
    row_headers=[x[0] for x in cursor.description]
    try:
        json_data=[]
        for result in rv:
            json_data.append(dict(zip(row_headers,result)))
            
            


    except Exception as e:
        print(e)
    
    return json.dumps(json_data,default=str)

@app.route('/add_polls', methods=['POST'])
def add_polls():
     data = request.json
     insert_question = {'question':data['question'] , 'approve':0, 'no_opinion':0, 'disapprove':0, 'poll_date':datetime.now().strftime('%Y-%m-%d'), 'checked':1}
     try:
        
        cursor.execute("INSERT INTO polls (question, approve, no_opinion, disapprove, poll_date, checked) VALUES (%(question)s, %(approve)s, %(no_opinion)s, %(disapprove)s, %(poll_date)s,%(checked)s)",insert_question)
        db.commit()
        return json.dumps({"return":100})
     except Exception as e:
        print(e)

        return json.dumps({"return":0})

@app.route('/get_result_of_poll', methods=['POST'])
def return_results():
    data = request.json
    cursor.execute("SELECT approve,no_opinion,disapprove FROM polls WHERE id= %(poll_id)s", {"poll_id":data['poll_id']})
    rv=cursor.fetchall()
    if not rv:
        return json.dumps({"return":0})
    row_headers=[x[0] for x in cursor.description]
    try:
        json_data=[]
        for result in rv:
            json_data.append(dict(zip(row_headers,result)))
            return json.dumps(json_data[0],default=str)
    except:
        return json.dumps({"return":0})

@app.route('/set_checked', methods=['POST'])
def set_checked():
    data = request.json
    try:
        cursor.execute("UPDATE polls SET checked=1 WHERE id=%(poll_id)s", {"poll_id":data['poll_id']})
        db.commit()
        return json.dumps({"return":100})
    except:
        return json.dumps({"return":0})

@app.route('/set_unchecked', methods=['POST'])
def set_unchecked():
    data = request.json
    try:
        cursor.execute("UPDATE polls SET checked=0 WHERE id=%(poll_id)s", {"poll_id":data['poll_id']})
        db.commit()
        return json.dumps({"return":100})
    except:
        return json.dumps({"return":0})


    
    


@app.route('/set_result_of_poll', methods=['POST'])
def return_set_results():
    data = request.json
    try:
        if(data['answer']=="approve"):
            cursor.execute("UPDATE polls SET approve=approve+1 WHERE id= %(poll_id)s", {"poll_id":data['poll_id']})
        if(data['answer']=="disapprove"):
            cursor.execute("UPDATE polls SET disapprove=disapprove+1 WHERE id= %(poll_id)s", {"poll_id":data['poll_id']})
        if(data['answer']=="no_opinion"):
            cursor.execute("UPDATE polls SET no_opinion=no_opinion+1 WHERE id= %(poll_id)s", {"poll_id":data['poll_id']})
        db.commit()
        return json.dumps({"return":100})
    except:
        return json.dumps({"return":0})

@app.route('/signup', methods=['POST'])
def api_signup():
    if(request.method=='POST'):
        data = request.json
        
        print(data)

        message = 'success'

        # make sure no fields are blank
    
        if data['email'] == '':
            message = "No email given. Try again"
            return {"return": 0, "message" : message}
        elif data['password'] == '':
            message = "No password given. Try again"
            return {"return": 0, "message" : message}

       

        # make sure username is not a duplicate

        duplicate = cursor.execute("SELECT * FROM users WHERE email = %(email)s", {"email":data['email']})
        rv=cursor.fetchall()
        if rv:
            message = "Email already exists. Pick another one."
            return {"return": 0, "message" : message}

       
            
            

        # hash the password before storing it

        read = cursor.execute("INSERT INTO users(email,password,type) VALUES('"+str(data['email'])+"','"+str(generate_password_hash(str(data['password'])).decode('utf8'))+"','"+str(data['type'])+"')")
        cursor.close()
        db.commit()
        db.close()
        return {"return": 100, "message" : message}

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
            return {"return": 100, "access_token": str(token), "token_type": "bearer"}
      else:
          return {"return": 0, "message": "Wrong credentials!"}
app.run()
