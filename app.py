from flask import Flask, render_template, request, redirect, flash, session, url_for
import pyodbc
from imdb import IMDb

app = Flask(__name__)
app.secret_key = "qwroiqwkdnkas"
ia = IMDb()

def conn():
    server = 'imovies.database.windows.net'
    db = 'imoviesdb'
    username = 'imovies'
    password = 'COP4710!'
    return pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+db+';UID='+username+';PWD='+password)


@app.route('/')
def home():
    if 'logged' in session:
       return render_template('home.html', usr=session['username'] if 'username' in session else "null", is_log=session['logged'] if 'logged' in session else False)
    else:
       return render_template('home.html', usr="null", is_log=False)

@app.route('/login')
def login():
    return render_template('login.html', usr=session['username'] if 'username' in session else "null", is_log=session['logged'] if 'logged' in session else False)

@app.route('/home')
def homeuser():
    return redirect(url_for('.home') )

@app.route('/postlogin', methods = ['POST'])
def postlogin():
    c = conn().cursor()
    username = request.form['username']
    password = request.form['password']

    c.execute("SELECT Username, Password FROM Users, Logins WHERE Users.Username = ? AND Logins.Password = ?", (username, password))
    data = c.fetchone()

    if data:
        session['logged'] = True
        session['username'] = data[0]
        flash("Successfully logged in")
        return redirect('/home')
    else:
        flash("Username or password is incorrect.")


    c.close()
    return render_template('login.html', usr=session['username'] if 'username' in session else "null", is_log=session['logged'] if 'logged' in session else False)

@app.route('/postmoviesearch', methods = ['POST', 'GET'])
def postmoviesearch():
    name = request.form['searchmovie']
    movies = ia.search_movie(name)
   
    if movies:
        namelist = []
        yearlist = []
        directorlist = []
        genrelist = []
        actorlist = []
        rolelist = []
        ratinglist = []
        imageurl = []

        for movie in movies:
            namelist.append(movie['title'])
            imageurl.append(movie['cover url'])
            movieID = movie.movieID
            movie = ia.get_movie(movieID)
            year = movie['year']
            yearlist.append(year)
            try:
                dlst = []
                for director in movie['directors']:
                    dlst.append(director['name'])

                tuple_list = tuple(dlst)
                directorlist.append(tuple(dlst))  

            except:
                directorlist.append("N/A")
            try:
                glst = []
                for genre in movie['genres']:
                    glst.append(genre)
                tuple_list = tuple(glst)
                genrelist.append(tuple_list)

            except:
                genrelist.append("N/A")
            try:
                actor = movie['cast'][0]
                main_actor = actor['name']
                actorlist.append(main_actor)
                role = actor.currentRole
                rolelist.append(role)
            except:
                actorlist.append("N/A")
                rolelist.append("N/A")
            
            try:
                rating = movie.data['rating']
                ratinglist.append(rating)
            except:
                ratinglist.append("N/A")

        movie_list = list(zip(namelist, yearlist, directorlist, genrelist, actorlist, rolelist, ratinglist, imageurl))
 
    else:
        flash("No movie with that name")
        movie_list = []

    return render_template('postsearch.html', rows = movie_list, usr=session['username'] if 'username' in session else "null", is_log=session['logged'] if 'logged' in session else False)


@app.route('/register')
def register():
    return render_template('register.html', usr=session['username'] if 'username' in session else "null", is_log=session['logged'] if 'logged' in session else False)

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
    return render_template('register.html', usr=session['username'] if 'username' in session else "null", is_log=session['logged'] if 'logged' in session else False)

@app.route('/logout')
def logout():
    session.pop('logged', None)
    session.pop('username', None)
    message = "Successfully Logged Out"
    return render_template('msg.html', msg = message, usr=session['username'] if 'username' in session else "null", is_log=session['logged'] if 'logged' in session else False)

@app.route('/mygroup', methods = ['POST', 'GET'])
def mygroup():
    c = conn().cursor()
    # username = 
    c.close()

if __name__ == '__main__':
    app.run()