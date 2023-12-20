from scipy import spatial
import numpy as np
import pandas as pd
import csv

data_rat = pd.read_csv('data/ratings.csv')
user_rat = pd.DataFrame({"user_ID":data_rat["userId"].unique()})

#for userid in user_rat["user_ID"]:
for userid in range(1,3):
    mask = data_rat["userId"].isin([user_rat["user_ID"][userid]])
    new_df = data_rat[mask]

    for movie, rat in zip(new_df["movieId"], new_df["rating"]):
        if movie not in user_rat.columns:
            for user_id in user_rat["user_ID"]:
                if user_id == userid:
                    user_rat.at[user_id,movie]= rat
                else:
                    user_rat.at[user_id,movie] = 0

#print(data_rat)
print(user_rat)
#print(new_df)
"""
with open('data/ratings.csv', newline='', encoding='utf8') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            count = 0
            for row in reader:
                if count > 0: 
                
                    user_id = row[0]
                    movie_id = row[1]
                    rating = row[2]

                    np.vstack
                        
                count += 1
                if count % 100 == 0:
                    print(count, " user added read")"""