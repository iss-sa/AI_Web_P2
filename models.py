from flask_sqlalchemy import SQLAlchemy
from flask_user import UserMixin

db = SQLAlchemy()


# Define the User data-model.
# NB: Make sure to add flask_user UserMixin as this adds additional fields and properties required by Flask-User
class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    active = db.Column('is_active', db.Boolean(), nullable=False, server_default='1')

    # User authentication information. The collation='NOCASE' is required
    # to search case insensitively when USER_IFIND_MODE is 'nocase_collation'.
    username = db.Column(db.String(100, collation='NOCASE'), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False, server_default='')
    email_confirmed_at = db.Column(db.DateTime())

    # User information
    first_name = db.Column(db.String(100, collation='NOCASE'), nullable=False, server_default='')
    last_name = db.Column(db.String(100, collation='NOCASE'), nullable=False, server_default='')

class Movie(db.Model):
    __tablename__ = 'movies'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100, collation='NOCASE'), nullable=False, unique=True)
    genres = db.relationship('MovieGenre', backref='movie', lazy=True)
    tags = db.relationship('MovieTags', backref='movie', lazy=True)
    links = db.relationship('MovieLinks', backref='movie', lazy=True)
    ratings = db.relationship('MovieRatings', backref='movie', lazy=True)


class MovieGenre(db.Model):
    __tablename__ = 'movie_genres'
    id = db.Column(db.Integer, primary_key=True)
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.id'), nullable=False)
    genre = db.Column(db.String(255), nullable=False, server_default='')


#added tags, links and ratings same as in genre and movies

class MovieTags(db.Model):
    __tablename__ = 'movie_tags'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.id'), nullable=False)
    tag = db.Column(db.String(255), nullable=False, server_default='')
    timestamp = db.Column(db.Integer)

class MovieLinks(db.Model):
    __tablename__ = 'movie_links'
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.id'), nullable=False, primary_key=True)
    imdb_id = db.Column(db.Integer)
    tmdb_id = db.Column(db.String)

class MovieRatings(db.Model):
    __tablename__ = 'movie_ratings'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.id'), nullable=False)
    rating = db.Column(db.Integer)
    timestamp = db.Column(db.Integer)