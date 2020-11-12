from flask import Flask, render_template, request, redirect, flash, session, url_for
import pyodbc

app = Flask(__name__)
app.secret_key = "qwroiqwkdnkas"

def conn():
    server = 'imovies.database.windows.net'
    db = 'imoviesdb'
    username = 'imovies'
    password = 'COP4710!'
    return pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+db+';UID='+username+';PWD='+password)


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/postregister', methods = ['POST'])
def postregister():
    c = conn().cursor()
    username = request.form['username']
    location = request.form['location']
    fname = request.form['fname']
    lname = request.form['lname']
    email = request.form['email']
    password = request.form['password']
    cpassword = request.form['cpassword']

    if password == cpassword:
        try:
            c.execute("INSERT INTO Users (Username, firstname, lastname, Locations) VALUES (?, ?, ?, ?)", username, fname, lname, location)
            c.execute("INSERT INTO Logins (Email, Password) VALUES (?, ?)", email, password)
            flash('Successfully registered')
            c.commit()
        except:
            flash('User or/and email address already exists')
            c.rollback()
    else:
        flash('Password does not meet confirm password')

    c.close()
    return render_template('register.html')

if __name__ == '__main__':
    app.run()