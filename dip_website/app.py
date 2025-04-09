from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_pymongo import PyMongo
from flask_bcrypt import Bcrypt
import threading
import time

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb+srv://satya288:hellomini@spnweb.2nt6szt.mongodb.net/test?retryWrites=true&w=majority&appName=spnweb"
app.secret_key = 'supersecretkey'

mongo = PyMongo(app)
bcrypt = Bcrypt(app)

@app.route('/')
def home():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        users = mongo.db.husermodels
        user = users.find_one({"h_ID": int(request.form['username'])})

        if user and user['password'] == request.form['password']:
            session['user'] = request.form['username']
            return redirect(url_for('dashboard'))
        return "Invalid Credentials", 401

    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))

    hospital_id = int(session['user'])
    hospital = mongo.db.hospitals.find_one({"hospitalID": hospital_id})
    return render_template('dashboard.html', hospital=hospital)

@app.route('/update-beds', methods=['POST'])
def update_beds():
    if 'user' not in session:
        return redirect(url_for('login'))

    hospital_id = int(session['user'])
    new_beds = int(request.form['available_beds'])

    mongo.db.hospitals.update_one(
        {"hospitalID": hospital_id},
        {"$set": {"no_of_available_beds": new_beds}}
    )
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

@app.route('/get-alert')
def get_alert():
    if 'user' not in session:
        return jsonify({"show": False})
    
    hID = int(session['user'])
    alert = mongo.db.hospitalstatuses.find_one({"status": True, "hID": str(hID)})

    if alert:
        return jsonify({"show": True, "hID": alert['hID'], "noOfBeds": alert['nofBeds']})
    return jsonify({"show": False})


@app.route('/resolve-alert', methods=['POST'])
def resolve_alert():
    data = request.json
    hID = int(data['hID'])
    nofBeds = int(data['noOfBeds'])

    hospital = mongo.db.hospitals.find_one({"hospitalID": hID})
    if hospital:
        updated_beds = hospital['no_of_available_beds'] - nofBeds
        mongo.db.hospitals.update_one({"hospitalID": hID}, {"$set": {"no_of_available_beds": updated_beds}})
    
    mongo.db.hospitalstatuses.update_one({"hID": str(hID)}, {"$set": {"status": False}})
    return jsonify({"success": True})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
