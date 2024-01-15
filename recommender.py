# Contains parts from: https://flask-user.readthedocs.io/en/latest/quickstart_app.html

from flask import Flask, render_template, request
from flask_user import login_required, UserManager, current_user

from models import db, User, Movie, MovieGenre, MovieLinks, MovieTags, MovieRatings
from read_data import check_and_read_data, database_pd_matrix
from colab_filter import collab_filter


# Class-based application configuration
class ConfigClass(object):
    """ Flask application config """

    # Flask settings
    SECRET_KEY = 'This is an INSECURE secret!! DO NOT use this in production!!'

    # Flask-SQLAlchemy settings
    SQLALCHEMY_DATABASE_URI = 'sqlite:///movie_recommender.sqlite'  # File-based SQL database
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Avoids SQLAlchemy warning

    # Flask-User settings
    USER_APP_NAME = "Movie Recommender"  # Shown in and email templates and page footers
    USER_ENABLE_EMAIL = False  # Disable email authentication
    USER_ENABLE_USERNAME = True  # Enable username authentication
    USER_REQUIRE_RETYPE_PASSWORD = True  # Simplify register form

# Create Flask app
app = Flask(__name__)
app.config.from_object(__name__ + '.ConfigClass')  # configuration
app.app_context().push()  # create an app context before initializing db
db.init_app(app)  # initialize database
db.create_all()  # create database if necessary
user_manager = UserManager(app, db, User)  # initialize Flask-User management


@app.cli.command('initdb')
def initdb_command():
    global db
    """Creates the database tables."""
    check_and_read_data(db)
    print('Initialized the database.')

# The Home page is accessible to anyone
@app.route('/')
def home_page():
    # render home.html template
    return render_template("home.html")

@app.route('/recommender')
@login_required  # User must be authenticated
def recommender_page():
    
    genres = db.session.query(MovieGenre.genre).distinct().all()
    genres.pop()

    return render_template("recommender.html", genres=genres) 

# The Members page is only accessible to authenticated users via the @login_required decorator
@app.route('/movies')
@login_required  # User must be authenticated
def movies_page():
    # String-based templates

    # first 10 movies
    movies = Movie.query.limit(10).all()
    URLs = []
    for m in movies:
        for l in m.links:
            num = l.tmdb_id
            URLs.append("https://www.themoviedb.org/movie/"+num)

    mov_url = zip(movies, URLs)

    #links = MovieLinks.query.limit(10).all()

    # only Romance movies
    # movies = Movie.query.filter(Movie.genres.any(MovieGenre.genre == 'Romance')).limit(10).all()

    # only Romance AND Horror movies
    # movies = Movie.query\
    #     .filter(Movie.genres.any(MovieGenre.genre == 'Romance')) \
    #     .filter(Movie.genres.any(MovieGenre.genre == 'Horror')) \
    #     .limit(10).all()

    return render_template("movies.html", movies=mov_url) 

@app.route('/recMovies')
@login_required  # User must be authenticated
def recommended_movies():
    # matrix for collab_filter
    data_m = database_pd_matrix(db)
    picked_user = 1
    df_movies = collab_filter(picked_userid=picked_user, n=10, user_similarity_threshold=0.3, m=10, p_corr=True, matrix=data_m)
    list_movie_ids = df_movies["movie"][:10]
    movies = []
    for m_id in list_movie_ids:
        movies.append(Movie.query.filter_by(id = m_id).all())
    print(movies)
    """    URLs = []
    for m in movies:
        for l in m.links:
            num = l.tmdb_id
            URLs.append("https://www.themoviedb.org/movie/"+num)"""

    #mov_url = zip(movies, URLs)
    return render_template("rec_movies.html", list_movies=movies)

@app.route('/rate', methods=['POST'])
@login_required  # User must be authenticated
def rate():
    #id = 
    movieid = request.form.get('movieid')
    rating = request.form.get('rating')
    userid = current_user.id
    db.session.add(MovieRatings(user_id=userid, movie_id=movieid, rating=rating))
    db.session.commit()
    print("Rate {} for {} by {}".format(rating, movieid, userid))
    return render_template("rated.html", rating=rating)

# Start development web server
if __name__ == '__main__':
    app.run(port=5000, debug=True)


#flask --app .\recommender.py initdb