from flask import Flask, render_template, request, redirect, flash, session, url_for
import pyodbc
from imdb import IMDb
from collections import Counter

app = Flask(__name__)
app.secret_key = "qwroiqwkdnkas"
ia = IMDb()

def conn():
    server = 'new-movieate.database.windows.net'
    db = 'new-movieate'
    username = 'newCOP4710AdminLogin'
    password = 'newCOP4710Password'
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
    userrating = float(request.form['userrating'])
    review = request.form['review']
    if userrating > 10:
        userrating = 10
    elif userrating < 0:
        userrating = 0

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
    userrating = float(request.form['userrating'])
    review = request.form['review']

    if userrating > 10:
        userrating = 10
    elif userrating < 0:
        userrating = 0

    c.execute("SELECT Password FROM Users WHERE Username = ?", session['username'])
    userpassword = c.fetchone()
    print(userpassword)
    if password == userpassword[0]:
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

@app.route('/remove', methods = ['GET', 'POST'])
def remove():
    c = conn().cursor()
    id = request.form['id']
    c.execute("DELETE FROM Watched_Movies WHERE movieID = ?", id)
    c.commit()
    c.close()
    return redirect("/mymovies")

@app.route('/profile')
def profile():
    if 'logged' in session:
        user = session['username']
        c = conn().cursor()
        c.execute("SELECT FirstName, LastName, FavoriteGenre FROM Users WHERE Username = ?", user)
        data = c.fetchone()
        c.close()

        fname = data[0]
        lname = data[1]
        favoritegenre = data[2]
        return render_template('profile.html', name = user, firstname = fname, lastname = lname, favoritegenre = favoritegenre, usr=session['username'] if 'username' in session else "null", is_log=session['logged'] if 'logged' in session else False)
    else:
        return redirect('/login')

#Update First Name
@app.route('/FUP', methods = ['Get', 'Post'])
def FUP():
    return render_template("FUP.html" , usr=session['username'] if 'username' in session else "null", is_log=session['logged'] if 'logged' in session else False)

@app.route('/FirstUP', methods = ['GET', 'POST'])
def FirstUP():
    c = conn().cursor()
    fname = request.form['fname']
    password = request.form['password']
    c.execute("SELECT Password FROM Users WHERE Username = ?", session['username'])
    data = c.fetchone()

    if password == data[0]:
        c.execute("UPDATE Users SET firstname = ? WHERE Username = ?", fname , session['username'])
        c.commit()
        flash("First Name Updated!")
        return redirect('/profile')
    else:
        flash("Incorrect password")
        return render_template("FUP.html", usr=session['username'] if 'username' in session else "null", is_log=session['logged'] if 'logged' in session else False)
    c.close()

#Update Last Name
@app.route('/LUP', methods = ['Get', 'Post'])
def LUP():
    return render_template("LUP.html" , usr=session['username'] if 'username' in session else "null", is_log=session['logged'] if 'logged' in session else False)

@app.route('/LastUP', methods = ['GET', 'POST'])
def LastUP():
    c = conn().cursor()
    lname = request.form['lname']
    password = request.form['password']
    c.execute("SELECT Password FROM Users WHERE username = ?", session['username'])
    data = c.fetchone()

    if password == data[0]:
        c.execute("UPDATE Users SET lastname = ? WHERE Username = ?", lname , session['username'])
        c.commit()
        flash("Last Name Updated!")
        return redirect('/profile')
    else:
        flash("Incorrect password")
        return render_template("LUP.html", usr=session['username'] if 'username' in session else "null", is_log=session['logged'] if 'logged' in session else False)
    c.close()

#Update Password
@app.route('/PUP', methods = ['Get', 'Post'])
def PUP():
    return render_template("PUP.html" , usr=session['username'] if 'username' in session else "null", is_log=session['logged'] if 'logged' in session else False)

@app.route('/PasswordUP', methods = ['GET', 'POST'])
def PasswordUP():
    c = conn().cursor()
    password = request.form['password']
    npassword = request.form['npassword']
    cnpassword = request.form['cnpassword']
    c.execute("SELECT Password FROM Users WHERE username = ?", session['username'])
    data = c.fetchone()

    if npassword == cnpassword:
        if password == data[0]:
            c.execute("UPDATE Users SET Password = ? WHERE Username = ?", npassword , session['username'])
            c.commit()
            flash("Password Updated!")
            return redirect('/profile')
        else:
            flash("Incorrect password")
            return render_template("PUP.html", usr=session['username'] if 'username' in session else "null", is_log=session['logged'] if 'logged' in session else False)
    else:
        flash("New password does not meet confirm password")
        return render_template("PUP.html", usr=session['username'] if 'username' in session else "null", is_log=session['logged'] if 'logged' in session else False)

    c.close()

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

        # group by same movie name, and only the movies that the user highly rated
        try:
            c.execute("SELECT Username, movieName FROM Watched_Movies WHERE Username <> ? AND UserRating > 5 AND movieName IN(SELECT movieName FROM Watched_Movies WHERE Username = ? AND UserRating > 5)", session['username'], session['username'])
            gMNData = c.fetchall()
        except:
            gMNData = " "
        
        # group by same location
        try:
            c.execute("SELECT DISTINCT Username FROM Users WHERE Username <> ? AND Locations = (SELECT Locations FROM Users WHERE Username = ?)", session['username'], session['username'])
            gLocData = c.fetchall()
        except:
            gLocData = " "

        # group by same genre (will this work? probs not)
        # GOAL: Given a string of multiple genres, determine which genre the user likes the most,
        # and find other users that also like that genre
        
        try:
            c.execute("SELECT Genre FROM Watched_Movies WHERE Username = ? AND UserRating > 5", session['username'])
            userGenreList = c.fetchall() #this list is a list of string, use double for loop
            allUserGenresList = []
            for eachStr in userGenreList:
                theString = eachStr[0]
                stripEachStr = theString[1:-1]
                eachStr_split = stripEachStr.split(', ')
                for x in eachStr_split:
                    allUserGenresList.append(x)
                
            def most_frequent(allUserGenresList):
                occurance_count = Counter(allUserGenresList)
                return occurance_count.most_common(1)[0][0]

            favGenre = most_frequent(allUserGenresList)
            favGenre = favGenre[1:-1]
            c.execute("UPDATE Users SET FavoriteGenre = ? WHERE Username = ?", favGenre, session['username'])
            c.commit()
            c.execute("SELECT DISTINCT Username, FavoriteGenre FROM Users WHERE Username <> ? AND FavoriteGenre = (SELECT FavoriteGenre FROM Users WHERE Username = ?)", session['username'], session['username'])
            genData = c.fetchall()
        except:
            userGenreList = " "
            favGenre = "Nothing"
            genData = " "
            c.execute("UPDATE Users SET FavoriteGenre = ? WHERE Username = ?", favGenre, session['username'])
            c.commit()


        return render_template('mygroup.html', mNrows = gMNData, Locrows = gLocData, Genrows = genData, userGenre = favGenre, usr=session['username'] if 'username' in session else "null", is_log=session['logged'] if 'logged' in session else False)
        c.close()
    else:
        return render_template('login.html', usr=session['username'] if 'username' in session else "null", is_log=session['logged'] if 'logged' in session else False)


if __name__ == '__main__':
    app.run()