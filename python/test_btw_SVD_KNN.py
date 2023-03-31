# -*- coding: utf-8 -*-
"""
Created on Tue Mar 21 23:28:11 2023

@author: MatyG
"""


# Import required libraries
from surprise import Dataset
from surprise import KNNWithMeans
from surprise.model_selection import train_test_split
from surprise import accuracy
import pandas as pd
from surprise import SVD
from surprise import Reader
from surprise.model_selection import cross_validate


# Load data
movie_list_user = []
unrating_userid_movie = []
unrating_userid_movie_KNN = []

unrating_userid_movie_KNN_rating = []
unrating_userid_movie_rating = []

ratings = pd.read_csv('ratings.csv')
movies = pd.read_csv('movies.csv', index_col=[0])
reader = Reader(rating_scale=(1, 5))
data = Dataset.load_from_df(ratings[['userId', 'movieId', 'rating']], reader)

# test_size = 0.2 pour 20% test and 80 training
trainset, testset = train_test_split(data, test_size=0.2)

# =============================================================================
# J'utilise KNN mais à voir si SVD est mieux ou pas
algo = SVD()
cross_validate(algo, data, measures=['RMSE', 'MAE'], cv=5, verbose=True)
trainset = data.build_full_trainset()
algo.fit(trainset)
# =============================================================================

# Predictions
predictions = algo.test(testset)

# Calcule accuracy measures
accuracy.rmse(predictions)
accuracy.mae(predictions)


# Permet d'avoir top N movie recommendations pour un user
def get_top_n_movies(user_id, n=500):
    # Normalement prends tous les films que le user a noté
    rated_movies = ratings.loc[ratings['userId'] == user_id]['movieId']
    # Normalement prends tous les films que le user n'a pas noté
    unrated_movies = set(ratings['movieId']) - set(rated_movies)
    # Prediction pour les films non noté
    unrated_movies_predictions = [algo.predict(user_id, movie_id)
                                  for movie_id in unrated_movies]
    # print(unrated_movies_predictions)

    # Trie les movies
    top_n_movies = sorted(unrated_movies_predictions, key=lambda x: x.est,
                          reverse=True)[:n]

    return top_n_movies


# Example usage
user_id = 1
top_n_movies = get_top_n_movies(user_id)
print(f"Top {len(top_n_movies)} recommendations for user {user_id}:")
for i, recommendation in enumerate(top_n_movies):
    # print("Voici les id_recomm", recommendation.est)
    unrating_userid_movie.append(movies.loc[recommendation.iid]['title'])
    unrating_userid_movie_rating.append(recommendation.est)

rating_userid_movie = ratings[ratings["userId"] == 13]["movieId"].tolist()

for MovieIdToMovie in rating_userid_movie:
    movie_list_user.append(movies.loc[MovieIdToMovie]['title'])
# print(movie_list_user)


# Load data
ratings = pd.read_csv('ratings.csv')
movies = pd.read_csv('movies.csv', index_col=[0])
reader = Reader(rating_scale=(1, 5))
data = Dataset.load_from_df(ratings[['userId', 'movieId', 'rating']], reader)

# test_size = 0.2 pour 20% test and 80 training
trainset, testset = train_test_split(data, test_size=0.2)

sim_options = {'name': 'cosine', 'user_based': True}
algo = KNNWithMeans(sim_options=sim_options)

algo.fit(trainset)
# Predictions
predictions = algo.test(testset)

# Calcule accuracy measures
accuracy.rmse(predictions)
accuracy.mae(predictions)


# Permet d'avoir top N movie recommendations pour un user
def get_top_n_movies_KNN(user_id, n=500):
    # Normalement prends tous les films que le user a noté
    rated_movies = ratings.loc[ratings['userId'] == user_id]['movieId']

    # Normalement prends tous les films que le user n'a pas noté
    unrated_movies = set(ratings['movieId']) - set(rated_movies)

    # Prediction pour les films non noté
    unrated_movies_predictions = [algo.predict(user_id, movie_id)
                                  for movie_id in unrated_movies]
    # print(unrated_movies_predictions)

    # Trie les movies
    top_n_movies = sorted(unrated_movies_predictions, key=lambda x: x.est,
                          reverse=True)[:n]

    return top_n_movies


# Example usage


def example_usage(user_id):
    top_n_movies = get_top_n_movies_KNN(user_id)
    # print(f"Top {len(top_n_movies)} recommendations for user {user_id}:")
    for i, recommendation in enumerate(top_n_movies):
        unrating_userid_movie_KNN.append
        (movies.loc[recommendation.iid]['title'])
        unrating_userid_movie_KNN_rating.append(recommendation.est)
    i = 0
    for r in range(len(unrating_userid_movie_KNN)):
        for g in range(len(unrating_userid_movie)):
            if unrating_userid_movie_KNN[r] == unrating_userid_movie[g]:
                i += 1
                print("Name movie: ", unrating_userid_movie_KNN[r],
                      " difference rating movie : ",
                      float(unrating_userid_movie_KNN_rating[r])
                      - float(unrating_userid_movie_rating[g]))
                print("Difference level: ", int(r)-int(g))


print("exemple usage " , example_usage(1))
