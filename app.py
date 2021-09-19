import pythontest
import os
import shutil
import Model_SVM
import sqlite3 as lite
from pathlib import Path
from pythontest import construct
from Model_SVM import main
from flask import Flask, render_template, request, redirect, url_for, jsonify
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///result.db'
db = SQLAlchemy(app)


class User(db.Model):
   """ Create user table"""
   id = db.Column(db.Integer, primary_key=True)
   email = db.Column(db.String(80), unique=True)
   password = db.Column(db.String(80))

   def __init__(self, email, password):
      self.email = email
      self.password = password

@app.route('/')
def home():
   return render_template('home.html')


@app.route('/results')
def results():
	return render_template('results.html')
	
@app.route('/uploader', methods = ['GET', 'POST'])
def upload_file():
   if request.method == 'POST':
      target =Path("./imagetotest1")
      if target.is_dir():
         # shutil.rmtree("./imagetotest1")
         valuereturn = "Server is Busy try after few minutes"
         return jsonify(valuereturn)
      else:
         os.makedirs('./imagetotest1/To_Check')
         for file in request.files.getlist('file'):
            # file = request.files['file']
            filename = secure_filename(file.filename)
            # IMG_PATH = "./imagetotest/To_Check/" + filename
            IMG_PATH = "./imagetotest1/To_Check/" + filename
            file.save(IMG_PATH)
         # testvar = (pythontest.construct())
         # print(testvar)
         valuereturn = Model_SVM.main()
         print(valuereturn)
         shutil.rmtree('./imagetotest1')
         return valuereturn
         # return redirect(url_for('results'))

@app.route('/login', methods = ['GET', 'POST'])
def login():
   if request.method == 'POST':
      # name = request.form['email']
      # passw = request.form['pass']
      try:
         data = User.query.filter_by(email=request.form['email'], password=request.form['pass']).first()
         if data is not None:
            return jsonify('found')
            # return redirect(url_for('home'))
         else:
            print('Incorrect')
            return jsonify('Incorrect')
      except:
         print('Incorrect')
         return jsonify('Incorrect')

@app.route('/signup', methods = ['GET', 'POST'])
def signup():
   if request.method == 'POST':
      data = User.query.filter_by(email=request.form['email']).first()
      if data is not None:
         return jsonify('found')
      else:
         new_user = User(email=request.form['email'], password=request.form['pass'])
         db.session.add(new_user)
         db.session.commit()
         return jsonify('created')
   return jsonify('Error')
   #    return render_template('login.html')
   # return render_template('register.html')





if __name__ == '__main__':
   app.run(debug = True)
   # app.run(debug = True, host='0.0.0.0', port= '5000')