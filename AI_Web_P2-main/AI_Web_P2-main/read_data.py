import csv
from sqlalchemy.exc import IntegrityError
from models import Movie, MovieGenre, MovieLinks, MovieTags, MovieRatings, User

import pandas as pd

def check_and_read_data(db):
    # check if we have movies in the database
    # read data if database is empty
    if Movie.query.count() == 0:

        # read movies from csv
        with open('data/movies.csv', newline='', encoding='utf8') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            count = 0
            for row in reader:
                if count > 0:
                    try:
                        id = row[0]
                        title = row[1]
                        movie = Movie(id=id, title=title)
                        db.session.add(movie)

                        genres = row[2].split('|')  # genres is a list of genres
                        for genre in genres:  # add each genre to the movie_genre table
                            movie_genre = MovieGenre(movie_id=id, genre=genre)
                            db.session.add(movie_genre)
                        db.session.commit()  # save data to database

                    except IntegrityError:
                        print("Ignoring duplicate movie: " + title)
                        db.session.rollback()
                        pass
                count += 1
                if count % 100 == 0:
                    print(count, " movies read")
        
        # read tags from csv
        with open('data/tags.csv', newline='', encoding='utf8') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            count = 0
            for row in reader:
                if count > 0:
                    try:
                        id = count
                        user_id = row[0]
                        movie_id = row[1]
                        tag = row[2]
                        timestamp = row[3]
                        tags = MovieTags(id = id, user_id=user_id, movie_id=movie_id, tag=tag, timestamp=timestamp)
                        db.session.add(tags)
                        db.session.commit() # save data to database

                    except IntegrityError:
                        print("Ignoring duplicate movie: " + title)
                        db.session.rollback()
                        pass
                count += 1
                if count % 100 == 0:
                    print(count, " tags read")

        # read links from csv
        with open('data/links.csv', newline='', encoding='utf8') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            count = 0
            for row in reader:
                if count > 0:
                    try:
                        movie_id = row[0]
                        imdb_id = row[1]
                        tmdb_id = row[2]
                        links = MovieLinks(movie_id=movie_id, imdb_id=imdb_id, tmdb_id=tmdb_id)
                        db.session.add(links)
                        db.session.commit()  # save data to database
                    
                    except IntegrityError:
                        print("Ignoring duplicate movie: " + title)
                        db.session.rollback()
                        pass
                count += 1
                if count % 100 == 0:
                    print(count, " links read")

        # read ratings from csv
        with open('data/ratings.csv', newline='', encoding='utf8') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            count = 0
            for row in reader:
                if count > 0: 
                    try:
                        id = count
                        user_id = row[0]
                        movie_id = row[1]
                        rating = row[2]
                        timestamp = row[3]
                        ratings = MovieRatings(id = id, user_id=user_id, movie_id=movie_id, rating=rating, timestamp=timestamp)
                        db.session.add(ratings)
                        db.session.commit() # save data to database

                        add_rating_user(db.session, user_id=row[0])

                    except IntegrityError:
                        print("Ignoring duplicate movie: " + title)
                        db.session.rollback()
                        pass
                count += 1
                if count % 100 == 0:
                    print(count, " ratings read")

def add_rating_user(session, user_id):
    """ Adds the users from the ratings.csv file. """

    added_user = User(id=user_id, username="User"+str(user_id))
    session.add(added_user)
    session.commit()

def database_pd_matrix(db):
    data_r = ( db.session.query(MovieRatings.user_id, MovieRatings.movie_id, MovieRatings.rating, MovieRatings.timestamp)
        .all()
    )
    
    data_m = ( db.session.query(Movie.id, Movie.title)
        .all()
    )

    # convert to Pandas DataFrame
    df_ratings = pd.DataFrame(data_r, columns=['userId', 'movieId', 'rating', 'timestamp'])
    df_movies = pd.DataFrame(data_m, columns=['movieId', 'title'])

    df = pd.merge(df_ratings, df_movies, on = 'movieId', how = 'inner')

    # create user-movie matrix with missing values = 0
    user_movie_matrix = df.pivot_table(index='userId', columns='movieId', values='rating')
    return user_movie_matrix