# Contains parts from: https://flask-user.readthedocs.io/en/latest/quickstart_app.html

from flask import Flask, render_template, request, send_from_directory
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

@app.route('/recommender', methods=["GET", "POST"])
@login_required  # User must be authenticated
def recommender_page():
    
    genres = db.session.query(MovieGenre.genre).distinct().all()
    genres.pop()
    genres = [genre[0] for genre in genres]
    
    #checked_genres = request.form.get('checked')
    #print("checked genres = ", checked_genres)
    
    return render_template("recommender.html", genres=genres)

# The Members page is only accessible to authenticated users via the @login_required decorator
@app.route('/movies')
@login_required  # User must be authenticated
def movies_page():
    # String-based templates

    # first 10 movies
    #movies = Movie.query.limit(10).all()
    
    pairs = request.query_string.split(b"&")
    split_pairs = {kv[0]: kv[1].decode() for pair in pairs if len(kv := pair.split(b"=", 2)) == 2}

    movie_filter = Movie.query
    if (selected_genres := split_pairs.get(b"genres")):
        selected_genres = selected_genres.split(",")

        for genre in selected_genres:
            movie_filter = movie_filter.filter(Movie.genres.any(genre = genre))

    # first 20 movies
    movies = movie_filter.limit(20).all()

    URLs = []
    for m in movies:
        for l in m.links:
            num = l.tmdb_id
            URLs.append("https://www.themoviedb.org/movie/"+num)

    mov_url = zip(movies, URLs)

    return render_template("movies.html", movies=mov_url) 

@app.route('/recMovies')
@login_required  # User must be authenticated
def recommended_movies():
    user_ratings = (
        db.session.query(MovieRatings)
        .filter(MovieRatings.user_id == current_user.id)
        .all()
    )
    # check if the user has rated movies already
    if len(user_ratings)> 0: 
        # matrix for collab_filter
        data_m = database_pd_matrix(db)
        picked_user = current_user.id
        df_movies = collab_filter(picked_userid=picked_user, n=10, user_similarity_threshold=0.3, m=10, p_corr=True, matrix=data_m)
        list_movie_ids = df_movies["movie"][:10]
        movies = []
        for m_id in list_movie_ids:
            movies.append(Movie.query.get(m_id))
            #movies.append(Movie.query.filter(Movie.id == m_id).one())
    else:
        movies = Movie.query.limit(10).all()
        
    URLs = []
    for m in movies:
        for l in m.links:
            num = l.tmdb_id
            URLs.append("https://www.themoviedb.org/movie/"+num)

    mov_url = zip(movies, URLs)
    return render_template("movies.html", movies=mov_url)

@app.route('/rate', methods=['POST'])
@login_required  # User must be authenticated
def rate():
    movieid = request.form.get('movieid')
    rating = request.form.get('rating')
    userid = current_user.id
    db.session.add(MovieRatings(user_id=userid, movie_id=movieid, rating=rating))
    db.session.commit()
    print("Rate {} for {} by {}".format(rating, movieid, userid))
    return render_template("rated.html", rating=rating)

@app.route('/static/<path:path>')
def send_report(path):
    return send_from_directory('static', path)

# Start development web server
if __name__ == '__main__':
    app.run(port=5000, debug=True)

#flask --app .\recommender.py initdb