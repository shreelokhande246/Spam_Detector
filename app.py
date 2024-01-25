from flask import Flask,render_template,request,jsonify
import pandas as pd
import numpy as np 
import joblib


import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
cred = credentials.Certificate("./service_account.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

def abc(type, message):
  data = {
    u'Message': f'{message}',
    u'timestamp': firestore.SERVER_TIMESTAMP
  }
 # data = {"name": "Los Angeles", "state": "CA", "country": "USA"}
# Add a new doc in collection 'cities' with ID 'LA'
  #await db.collection("cities").document("LA").set(data)
  doc_ref = db.collection(type).document()
  doc_ref.set(data)

app = Flask(__name__)

model = joblib.load('spam_model.pkl')

@app.route('/',methods=['GET', 'POST'])
def index():
  if request.method == 'POST':
    message = request.form.get('message')
    output = model.predict([message])
    if output == [0]:
      abc("Important" , message)
      result = "This Message is Not a SPAM Message."
    else:
      result = "This Message is a SPAM Message." 
      abc("Spam" , message)
    return render_template('index.html', result=result,message=message)      
 
  else:
    return render_template('index.html')  
    
@app.route('/About.html',methods=['GET']) 
def home():
  if request.method == 'GET':
    return render_template('About.html')

@app.route('/Spam.html',methods=['GET']) 
def spam():
  if request.method == 'GET':
    docs = db.collection(u'Spam')
    newdoc= docs.order_by(u'timestamp', direction = firestore.Query.DESCENDING)
    results = newdoc.stream()
    items = []
    for doc in results:
      document = doc.to_dict()["Message"]
      items.append(document)
      print(document)  
    return render_template('Spam.html', doc=items) 

@app.route('/Important.html',methods=['GET']) 
def important():
  if request.method == 'GET':
    docs = db.collection(u'Important')
    newdoc= docs.order_by(u'timestamp', direction = firestore.Query.DESCENDING)
    results = newdoc.stream()
    items = []
    for doc in results:
      document = doc.to_dict()["Message"]
      items.append(document)
      print(document)  
    return render_template('Important.html', doc=items) 

if __name__ == '__main__':
    app.run(debug=True)