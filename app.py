# -----------------------
# Flask + MongoDB App
# -----------------------

# Import essential libraries
from flask import Flask, render_template, request, redirect, url_for, session
from pymongo import MongoClient
from bson.objectid import ObjectId
from dotenv import load_dotenv
import os

# Load environment variables from .env (Mongo URI, admin creds)
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "devsecret")

#Connect to MongoDB Atlas
client = MongoClient(os.getenv("MONGO_URI"))
db = client["College"]
students = db["Students"]

# Admin credentials
ADMIN_USER = os.getenv("ADMIN_USER", "admin")
ADMIN_PASS = os.getenv("ADMIN_PASS", "admin123")

# Home Page with dark mode + options
@app.route('/')
def home():
    return render_template("home.html")

#Adding new Student
@app.route('/form', methods=['GET', 'POST'])
def form():
    if request.method == 'POST':
        data = {
            "name": request.form['name'],
            "address": request.form['address'],
            "email": request.form['email'],
            "subjects": {
                "name": request.form['sub_name'],
                "author": request.form['author'],
                "description": request.form['description']
            }
        }
        students.insert_one(data)
        return redirect('/view')
    return render_template("form.html")


# View all students
@app.route('/view')
def view():
    all_students = list(students.find())
    return render_template("view.html", students=all_students, is_admin=session.get('is_admin', False))

# Update student (POST update)
@app.route('/edit/<id>', methods=['GET', 'POST'])
def edit(id):
    if not session.get('is_admin'):
        return redirect(url_for('login'))
    student = students.find_one({"_id": ObjectId(id)})
    if request.method == 'POST':
        updated_data = {
            "name": request.form['name'],
            "address": request.form['address'],
            "email": request.form['email'],
            "subjects": {
                "name": request.form['sub_name'],
                "author": request.form['author'],
                "description": request.form['description']
            }
        }
        students.update_one({"_id": ObjectId(id)}, {"$set": updated_data})
        return redirect('/view')
    return render_template("edit.html", student=student)


# Delete student
@app.route('/delete/<id>')
def delete(id):
    if not session.get('is_admin'):
        return redirect(url_for('login'))
    students.delete_one({"_id": ObjectId(id)})
    return redirect('/view')


# Admin Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == ADMIN_USER and password == ADMIN_PASS:
            session['is_admin'] = True
            return redirect('/view')
    return render_template('login.html')


# Admin Logout
@app.route('/logout')
def logout():
    session.pop('is_admin', None)
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
