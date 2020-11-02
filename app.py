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


if __name__ == '__main__':
    app.run()