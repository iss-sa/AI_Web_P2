# Data processing
import pandas as pd
import numpy as np
import scipy.stats

# Similarity
from sklearn.metrics.pairwise import cosine_similarity

#read in ratings and movies
ratings = pd.read_csv('data/ratings.csv')
movies = pd.read_csv('data/movies.csv')

#merge ratings and movie datasets
df = pd.merge(ratings, movies, on = 'movieId', how = 'inner')

#can change movieId to title thats why movies are read in the beginning
matrix = df.pivot_table(index = 'userId', columns = 'movieId', values = 'rating')
print(matrix)

def collab_filter(picked_userid=1, n=10, user_similarity_threshold=0.3, m=10, p_corr=True, matrix=matrix):
  """generates movie recommendations for a given user
  
      picked_userid : the user who receives the recommendations
      n : number of similar users to generate recommendation from
      user_similarity_threshold : similarity threshold for similar users
      m : how many movie recommendations
      p_corr : pearson correlation if True, else cosine similarity is used
      """

  print(matrix)
  #we can normalize ratings 
  # Normalize user-item matrix
  matrix = matrix.subtract(matrix.mean(axis=1), axis = 'rows')

  if p_corr == True:
    #user similarity matrix using Pearson correlation
    user_similarity = matrix.T.corr()
  else:
    #if we want to use cosine similarrity 
    user_similarity = cosine_similarity(matrix.fillna(0))


  #example on how to find similar user
  # Remove picked user ID from the candidate list
  user_similarity.drop(index=picked_userid, inplace=True)

  # Get top n similar users
  similar_users = user_similarity[user_similarity[picked_userid]>user_similarity_threshold][picked_userid].sort_values(ascending=False)[:n]


  #remove movies watched by the target user, keep movies watched by similar users

  # Movies that the target user has watched
  picked_userid_watched = matrix[matrix.index == picked_userid].dropna(axis=1, how='all')


  # Movies that similar users watched. Remove movies that none of the similar users have watched
  similar_user_movies = matrix[matrix.index.isin(similar_users.index)].dropna(axis=1, how='all')


  # Remove the watched movie from the movie list
  similar_user_movies.drop(picked_userid_watched.columns,axis=1, inplace=True, errors='ignore')


  item_score = {}
  # Loop through items
  for i in similar_user_movies.columns:
    # Get the ratings for movie i
    movie_rating = similar_user_movies[i]
    # Create a variable to store the score
    total = 0
    # Create a variable to store the number of scores
    count = 0
    # Loop through similar users
    for u in similar_users.index:
      # If the movie has rating
      if pd.isna(movie_rating[u]) == False:
        # Score is the sum of user similarity score multiply by the movie rating
        score = similar_users[u] * movie_rating[u]
        # Add the score to the total score for the movie so far
        total += score
        # Add 1 to the count
        count +=1
    # Get the average score for the item
    item_score[i] = total / count
  # Convert dictionary to pandas dataframe
  item_score = pd.DataFrame(item_score.items(), columns=['movie', 'movie_score'])
      
  # Sort the movies by score
  ranked_item_score = item_score.sort_values(by='movie_score', ascending=False)

  print("top {m} movies for user {user}".format(m=m, user=picked_userid))
  print(ranked_item_score.head(m))

  return ranked_item_score

#collab_filter()