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

    c.execute("SELECT Username, Password FROM Users WHERE Username = ? AND Password = ?", (username, password))
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
        movieidlist = []

        for movie in movies:
            namelist.append(movie['title'])
            imageurl.append(movie['cover url'])
            movieID = movie.movieID
            movieidlist.append(movieID)
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

        movie_list = list(zip(namelist, yearlist, directorlist, genrelist, actorlist, rolelist, ratinglist, imageurl, movieidlist))
 
    else:
        flash("No movie with that name")
        movie_list = []

    return render_template('postsearch.html', rows = movie_list, usr=session['username'] if 'username' in session else "null", is_log=session['logged'] if 'logged' in session else False)


@app.route("/addMovie", methods = ['GET', 'POST'])
def addmovie():
    if 'logged' in session:
        movie_list = []
        title = request.form['title']
        year = request.form['year']
        directors = request.form['directors']
        genres = request.form['genres']
        actor = request.form['actor']
        role = request.form['role']
        rating = request.form['rating']
        url = request.form['url']
        id = request.form['id']
        movie_list.append(title)
        movie_list.append(year)
        movie_list.append(directors)
        movie_list.append(genres)
        movie_list.append(actor)
        movie_list.append(role)
        movie_list.append(rating)
        movie_list.append(url)
        movie_list.append(id)
        return render_template('addmovie.html', row = movie_list, usr=session['username'] if 'username' in session else "null", is_log=session['logged'] if 'logged' in session else False)

    else:
        flash("Login is required")
        return render_template('login.html', usr=session['username'] if 'username' in session else "null", is_log=session['logged'] if 'logged' in session else False)


@app.route("/postadd", methods = ['GET', 'POST'])
def postadd():
    c = conn().cursor()
    title = request.form['title']
    year = request.form['year']
    directors = request.form['directors']
    genres = request.form['genres']
    actor = request.form['actor']
    role = request.form['role']
    rating = request.form['rating']
    url = request.form['url']
    id = request.form['id']
    userrating = request.form['userrating']
    review = request.form['review']
    try:
        c.execute("INSERT INTO Watched_Movies (Username, movieID, movieName, MovieYear, Director_name, Genre, Lead_Actor, roles, Rating, url, UserRating, review) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", session['username'], id, title, int(year), str(directors), str(genres), actor, role, float(rating), url, float(userrating), review)
        c.commit()
        flash("Successfully added to your list")
    except:
        flash("Movie already in your list")
    c.close()
    return render_template('home.html', usr=session['username'] if 'username' in session else "null", is_log=session['logged'] if 'logged' in session else False)

@app.route('/mymovies')
def mymovies():
    c = conn().cursor()
    try:
        c.execute("SELECT movieName, MovieYear, Director_name, Genre, Lead_Actor, roles, Rating, review, UserRating, url, movieID FROM Watched_Movies WHERE Username = ?", session['username'])
        data = c.fetchall()
        c.close()
        return render_template('mymovies.html', rows = data, usr=session['username'] if 'username' in session else "null", is_log=session['logged'] if 'logged' in session else False)
    except:
        flash("Nothing found")
        c.close()
        return render_template('mymovies.html', usr=session['username'] if 'username' in session else "null", is_log=session['logged'] if 'logged' in session else False)

    
@app.route('/edit', methods = ['GET', 'POST'])
def edit():
    id = request.form['id']
    return render_template('edit.html', id = id,usr=session['username'] if 'username' in session else "null", is_log=session['logged'] if 'logged' in session else False)

@app.route('/postedit', methods = ['GET', 'POST'])
def postedit():
    c = conn().cursor()
    id = request.form['id']
    password = request.form['password']
    userrating = request.form['userrating']
    review = request.form['review']

    c.execute("SELECT Password FROM Users WHERE Username = ?", session['username'])
    userpassword = c.fetchone()
    print(userpassword)
    if password == userpassword:
        try:
            c.execute("UPDATE Watched_Movies SET UserRating = ?, review = ? WHERE movieID = ?", userrating, review, id)
            c.commit()
            flash("Successfully Updated")
            return redirect('/mymovies')
        except:
            flash("Unable to edit")
            return redirect('/mymovies')
    else:
        flash("Password incorrect")
        return redirect('/mymovies')

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
    password = request.form['password']
    cpassword = request.form['cpassword']

    if password == cpassword:
        try:
            c.execute("INSERT INTO Users (Username, firstname, lastname, Locations, Password) VALUES (?, ?, ?, ?, ?)", username, fname, lname, location, password)
            flash('Successfully registered')
            c.commit()
        except:
            flash('User already exists')
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
    if 'logged' in session:
        c = conn().cursor()
        currentUser = session['username']
    
        c.execute("SELECT * FROM Watched_Movies WHERE Username = '?'", currentUser)
        c.commit()
        c.close()
    
    else:
        flash("Login is required")
        return render_template('login.html', usr=session['username'] if 'username' in session else "null", is_log=session['logged'] if 'logged' in session else False)


if __name__ == '__main__':
    app.run()