
"""
Columbia's COMS W4111.001 Introduction to Databases
Example Webserver
To run locally:
    python server.py
Go to http://localhost:8111 in your browser.
A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""
import os
  # accessible as a variable in index.html:
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response, session, flash

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)


#
# The following is a dummy URI that does not connect to a valid database. You will need to modify it to connect to your Part 2 database in order to use the data.
#
# XXX: The URI should be in the format of: 
#
#     postgresql://USER:PASSWORD@35.243.220.243/proj1part2
#
# For example, if you had username gravano and password foobar, then the following line would be:
#
#     DATABASEURI = "postgresql://gravano:foobar@35.243.220.243/proj1part2"
#
DATABASEURI = "postgresql://do2330:5822@35.231.103.173/proj1part2"


#
# This line creates a database engine that knows how to connect to the URI above.
#
engine = create_engine(DATABASEURI)

#
# Example of running queries in your database
# Note that this will probably not work if you already have a table named 'test' in your database, containing meaningful data. This is only an example showing you how to run queries in your database using SQLAlchemy.
#
engine.execute("""CREATE TABLE IF NOT EXISTS test (
  id serial,
  name text
);""")
engine.execute("""INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace');""")


@app.before_request
def before_request():
  """
  This function is run at the beginning of every web request 
  (every time you enter an address in the web browser).
  We use it to setup a database connection that can be used throughout the request.

  The variable g is globally accessible.
  """
  try:
    g.conn = engine.connect()
  except:
    print("uh oh, problem connecting to database")
    import traceback; traceback.print_exc()
    g.conn = None


  username = session.get('username')

  if username is None:
    g.user = None
  else:
    query = "SELECT * FROM userr WHERE username = '{}'".format(username)
    g.user = g.conn.execute(query).fetchone()

@app.teardown_request
def teardown_request(exception):
  """
  At the end of the web request, this makes sure to close the database connection.
  If you don't, the database could run out of memory!
  """
  try:
    g.conn.close()
  except Exception as e:
    pass


#
# @app.route is a decorator around index() that means:
#   run index() whenever the user tries to access the "/" path using a GET request
#
# If you wanted the user to go to, for example, localhost:8111/foobar/ with POST or GET then you could use:
#
#       @app.route("/foobar/", methods=["POST", "GET"])
#
# PROTIP: (the trailing / in the path is important)
# 
# see for routing: http://flask.pocoo.org/docs/0.10/quickstart/#routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
#
@app.route('/')
def index():
  """
  request is a special object that Flask provides to access web request information:

  request.method:   "GET" or "POST"
  request.form:     if the browser submitted a form, this contains the data in the form
  request.args:     dictionary of URL arguments, e.g., {a:1, b:2} for http://localhost?a=1&b=2

  See its API: http://flask.pocoo.org/docs/0.10/api/#incoming-request-data
  """

  # DEBUG: this is debugging code to see what request looks like
  print(request.args)


  #
  # example of a database query
  #
  cursor = g.conn.execute("SELECT * FROM movie")
  movies = []
  for result in cursor:
    movies.append(result['title'])  # can also be accessed using result[0]
  cursor.close()

  #
  # Flask uses Jinja templates, which is an extension to HTML where you can
  # pass data to a template and dynamically generate HTML based on the data
  # (you can think of it as simple PHP)
  # documentation: https://realpython.com/blog/python/primer-on-jinja-templating/
  #
  # You can see an example template in templates/index.html
  #
  # context are the variables that are passed to the template.
  # for example, "data" key in the context variable defined below will be 
  # accessible as a variable in index.html:
  #
  #     # will print: [u'grace hopper', u'alan turing', u'ada lovelace']
  #     <div>{{data}}</div>
  #     
  #     # creates a <div> tag for each element in data
  #     # will print: 
  #     #
  #     #   <div>grace hopper</div>
  #     #   <div>alan turing</div>
  #     #   <div>ada lovelace</div>
  #     #
  #     {% for n in data %}
  #     <div>{{n}}</div>
  #     {% endfor %}
  #
  context = dict(data = movies)


  #
  # render_template looks in the templates/ folder for files.
  # for example, the below file reads template/index.html
  #
  return render_template("index.html", **context)

#
# This is an example of a different path.  You can see it at:
# 
#     localhost:8111/another
#
# Notice that the function name is another() rather than index()
# The functions for each app.route need to have different names
#
@app.route('/movies')
def movies():
  cursor = g.conn.execute("SELECT * FROM movie ORDER BY movie.title")
  movies = []
  for result in cursor:
    movies.append(result['title'])  # can also be accessed using result[0]
  cursor.close()

  context = dict(data = movies)
  return render_template("movies.html", **context)

@app.route('/directors')
def directors():
    cursor = g.conn.execute("SELECT * FROM director ORDER BY director.name")
    directors = []
    for result in cursor:
        directors.append(result['name'])
    cursor.close()

    context = dict(data = directors)
    return render_template("directors.html", **context)

@app.route('/genres')
def genres():
    cursor = g.conn.execute("SELECT * FROM genre ORDER BY genre.genre_name")
    genres = []
    for result in cursor:
        genres.append(result['genre_name'])
    cursor.close()

    context = dict(data = genres)
    return render_template("genres.html", **context)

@app.route('/actors')
def actors():
    cursor = g.conn.execute("SELECT * FROM actor ORDER BY actor.name")
    actors = []
    for result in cursor:
        actors.append(result['name'])
    cursor.close()

    context = dict(data = actors)
    return render_template("actors.html", **context)

@app.route('/movies/<title>')
def movie(title):
  query = "SElECT * FROM movie INNER JOIN directs ON directs.movie_id=movie.id WHERE movie.title = '{0}'".format(title)
  cursor = g.conn.execute(query)
  movieTitle = ""
  moviePopularity = 0
  movieLength = 0
  movieYear = 0
  movieDirector = ""
  actors = []

  for result in cursor:
    movieTitle = result['title']
    moviePopularity = result['popularity']
    movieLength = result['length']
    movieYear = result['year']
    movieDirector = result['director_name']
  cursor.close()

  actors = []
  query = "SELECT actor.name FROM actor INNER JOIN plays_in ON actor.id=plays_in.actor_id INNER JOIN movie ON plays_in.movie_id=movie.id WHERE movie.title = '{0}'".format(title)
  cursor = g.conn.execute(query)
  for result in cursor:
      actors.append(result[0])
  cursor.close()
  
  awards = []
  query = "SELECT won.award_name FROM won INNER JOIN movie ON movie.id=won.id WHERE movie.title = '{0}'".format(title)
  cursor = g.conn.execute(query)
  for result in cursor:
      awards.append(result[0])
  cursor.close()
  
  return render_template("movie.html", title=movieTitle, popularity=moviePopularity, length=movieLength, year=movieYear, director=movieDirector, actors=actors, awards=awards)

@app.route('/directors/<name>')
def director(name):
    query = "SELECT * FROM director WHERE director.name = '{0}'".format(name)
    cursor = g.conn.execute(query)
    for result in cursor:
        name = result['name']
        studio = result['studio']
    cursor.close()
    
    movies = []
    query = "SELECT movie.title FROM movie INNER JOIN directs ON movie.id = directs.movie_id WHERE directs.director_name = '{0}'".format(name)
    cursor = g.conn.execute(query)
    for result in cursor:
         movies.append(result['title'])
    cursor.close()


    return render_template("director.html", name=name, studio=studio, movies=movies)

@app.route('/genres/<genre_name>')
def genre(genre_name):
    query = "SELECT * FROM genre WHERE genre.genre_name = '{0}'".format(genre_name)
    cursor = g.conn.execute(query)
    for result in cursor:
        genre_name = result['genre_name']
    cursor.close()

    movies = []
    query = "SELECT movie.title FROM movie INNER JOIN is_a ON movie.id = is_a.id WHERE is_a.genre_name = '{0}'".format(genre_name)
    cursor = g.conn.execute(query)
    for result in cursor:
        movies.append(result['title'])
    cursor.close()

    return render_template("genre.html", genre_name=genre_name, movies=movies)

@app.route('/actors/<name>')
def actor(name):
    query = "SELECT * FROM actor WHERE actor.name = '{0}'".format(name)
    cursor = g.conn.execute(query)
    for result in cursor:
        name = result['name']
        sag_number = result['sag_number']
        actor_id = result['id']
        #print(actor_id) ## something wrong here
    cursor.close()

    movies = []
    query = "SELECT movie.title FROM movie INNER JOIN plays_in ON movie.id = plays_in.movie_id WHERE plays_in.actor_id = {0}".format(actor_id)
    cursor = g.conn.execute(query) 
    for result in cursor:
        movies.append(result['title'])
    cursor.close()

    return render_template("actor.html", name=name, sag_number=sag_number, movies=movies)

# Example of adding new data to the database
@app.route('/add', methods=['POST'])
def add():
  name = request.form['name']
  g.conn.execute('INSERT INTO test(name) VALUES (%s)', name)
  return redirect('/')

@app.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None
        query = "SELECT * FROM userr WHERE username = '{}'".format(username)
        user = g.conn.execute(query).fetchone()

        if user is None:
            error = 'Incorrect username.'
        elif user['password'] != password:
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['username'] = user['username']
            return redirect('/')

        flash(error)

    return render_template("login.html")

@app.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        error = None

        query = "SELECT username FROM userr WHERE username = '{0}'".format(username)
        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        elif not email:
            error = 'Email is required.'
        elif g.conn.execute(query).fetchone() is not None:
            error = 'User {} is already registered.'.format(username)

        if error is None:
            query = "INSERT INTO userr (username, password, dob, email) VALUES ('{0}', '{1}', NULL, '{2}')".format(username, password, email)
            g.conn.execute(query)
            #db.commit()
            return redirect('/login')

        flash(error)

    return render_template("register.html")

@app.route('/logout', methods=('GET', 'POST'))
def logout():
    session.clear()
    return redirect('/')

if __name__ == "__main__":
  import click

  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0') # external IP address of VM instance: 35.185.56.218
  @click.argument('PORT', default=8111, type=int)
  def run(debug, threaded, host, port):
    """
    This function handles command line parameters.
    Run the server using:

        python server.py

    Show the help text using:

        python server.py --help

    """

    HOST, PORT = host, port 
    print("running on %s:%d" % (HOST, PORT))
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)

  run()
