from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import tensorflow as tf
import MySQLdb.cursors
import numpy as np
import cv2
import re
import os
 
#Programs
from programs.reshapeImage import reshapeImage

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'INCOMING/'
#Loading models
# CNN
cnnWithoutPreprocess = tf.keras.models.load_model('models/cnn/without-preprocessing1.h5')
cnnWithSharpening = tf.keras.models.load_model('models/cnn/with-sharpening.h5')
cnnWithNormalization = tf.keras.models.load_model('models/cnn/with-normalization.h5')
#Resnet
resnetWithoutPreprocess = tf.keras.models.load_model('models/resnet/without-preprocessing1.h5')
resnetWithSharpening = tf.keras.models.load_model('models/resnet/with-sharpening.h5')
resnetWithNormalization = tf.keras.models.load_model('models/resnet/with-normalization.h5')
#Other Model
combined_model = tf.keras.models.load_model('models/imagesTextCombined.h5')


app.static_folder = 'static'
 
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'admin'
app.config['MYSQL_DB'] = 'skincancer'

mysql = MySQL(app)
 
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/predict')
def predict():
    prediction = ''
    return render_template('predict.html', pred=prediction)

@app.route('/login', methods =['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = % s AND password = % s', (username, password, ))
        account = cursor.fetchone()
        if account:
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            msg = 'Logged in successfully !'
            return render_template('index.html', msg = msg)
        else:
            msg = 'Incorrect username / password !'
    return render_template('login.html', msg = msg)
 
@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login'))
 
@app.route('/register', methods =['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form :
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = % s', (username, ))
        account = cursor.fetchone()
        if account:
            msg = 'Account already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address !'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers !'
        elif not username or not password or not email:
            msg = 'Please fill out the form !'
        else:
            cursor.execute('INSERT INTO accounts VALUES (NULL, % s, % s)', (username, password, ))
            mysql.connection.commit()
            msg = 'You have successfully registered !'
    elif request.method == 'POST':
        msg = 'Please fill out the form !'
    return render_template('register.html', msg = msg)

@app.route('/result', methods= ['POST', 'GET'])
def result():
    if request.method == 'POST':
        image = request.files['rawImage']
        path = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
        image.save(path)

        image = cv2.imread(path)
        image = reshapeImage(image)

        preprocessMethod = request.form['preprocess']
        modelType = request.form['model']

        if modelType == 'cnn':
            if preprocessMethod == 'na':
                model = cnnWithoutPreprocess
            elif preprocessMethod == 'sharpening':
                model = cnnWithSharpening
            elif preprocessMethod == 'normalization':
                model = cnnWithNormalization

        elif modelType == 'resnet':
            if preprocessMethod == 'na':
                model = resnetWithoutPreprocess
            elif preprocessMethod == 'sharpening':
                model = resnetWithSharpening
            elif preprocessMethod == 'normalization':
                model = resnetWithNormalization

        pred = model.predict(image, verbose=0)[0]
        if int(pred) == 0:
            prediction = 'benign'
        elif int(pred) == 1:
            prediction = 'malignant'

        return render_template('predict.html',pred=prediction)

app.run(debug=True)

