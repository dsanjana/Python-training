import jwt
import json
from functools import wraps
from flask_cors import CORS
from datetime import datetime
from flask_bcrypt import Bcrypt
from flask_mysqldb import MySQL
from flask_jwt_extended import JWTManager
from flask import Flask, request, jsonify
from flask_jwt_extended import (create_access_token)

app = Flask(__name__)

# DB config
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '19961120@dsH'
app.config['MYSQL_DB'] = 'test_app'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
app.config['JWT_SECRET_KEY'] = 'secret'

mysql = MySQL(app)
bcrypt = Bcrypt(app)
_jwt = JWTManager(app)

CORS(app)

def check_for_token(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        token = request.json['token']
        if not token:
            return jsonify({"message": "Missing token"}), 403
        try:
            data = jwt.decode(token, app.config['JWT_SECRET_KEY'])
            print(data['username'])    
        except:
            return jsonify({"message": "Invalid token"}), 403
        return func(*args, **kwargs)
    return wrapped                

@app.route("/user/register", methods=['POST'])
def register():
    # try:

    firstname = request.json['firstname']
    lastname = request.json['lastname']
    email = request.json['email']
    username = request.json['username']
    password = bcrypt.generate_password_hash(request.json['password']).decode('utf-8')

    cur = mysql.connection.cursor()
    cur.execute(
        "INSERT INTO users (firstName, lastName, email, username, password, dateCreated) VALUES (%s, %s, %s, %s, %s, %s)", (firstname, lastname, email, username, password, datetime.utcnow()))
    mysql.connection.commit()
    return jsonify({"message": "User Registed Succesfully"})

    # except Exception as e:
	# 	print(e)
	# finally:
	# 	cur.close() 
	# 	mysql.connection.close()  

@app.route("/user/login", methods=['POST'])
def login():

    username = request.json['username']
    password = request.json['password']
    result = ""

    cur = mysql.connection.cursor()
    cur.execute("""SELECT * FROM users WHERE username = %s""", (username,))
    data = cur.fetchone()

    if bcrypt.check_password_hash(data['password'], password):
        access_token = create_access_token(identity = {'username': data['username'], 'email': data['email']})
        result = jsonify({"token": access_token})
    else:
        result = jsonify({"error": "Invalid username or password"})    

    return result    

@app.route("/post/create", methods=['POST'])
@check_for_token
def create():

    title = request.json['title']
    description = request.json['description']
    comment = request.json['comment']

    cur = mysql.connection.cursor()
    cur.execute(
        "INSERT INTO posts (title, description, comment, dateCreated) VALUES (%s, %s, %s, %s)", (title, description, comment, datetime.utcnow()))
    mysql.connection.commit()
    return jsonify({"message": "Post Created Succesfully"})    

@app.route("/posts/get", methods=['GET'])
def getAll():

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM posts")

    data = cur.fetchall()
    cur.close()
    return jsonify(data)

@app.route("/post/get/<int:id>", methods=['GET'])
def getPost(id):

    cur = mysql.connection.cursor()
    cur.execute("""SELECT * FROM posts WHERE id = %s""", (id,))

    data = cur.fetchone()   
    cur.close()
    return jsonify(data)    

@app.route("/post/update", methods=['PUT'])    
@check_for_token
def updatePost():

    id = request.json['id']
    title = request.json['title']
    description = request.json['description']
    comment = request.json['comment']

    cur = mysql.connection.cursor()
    cur.execute("""UPDATE posts SET title = %s, description = %s, comment = %s WHERE id = %s""", (title, description, comment, id))

    mysql.connection.commit()
    return jsonify({"message": "Post Updated Succesfully"})  

@app.route("/post/delete/<int:id>", methods=['DELETE'])    
@check_for_token
def deletePost(id):

    cur = mysql.connection.cursor()
    cur.execute("""DELETE FROM posts WHERE id = %s""", (id,))

    mysql.connection.commit()
    return jsonify({"message": "Post Deleted Succesfully"})     

@app.route("/comment/add", methods=['POST'])    
def addComment():

    id = request.json['id']
    comment = request.json['comment']

    cur = mysql.connection.cursor()
    cur.execute("""UPDATE posts SET comment = %s WHERE id = %s""", (comment, id))

    mysql.connection.commit()
    return jsonify({"message": "Comment Added Succesfully"})  


application = app    
