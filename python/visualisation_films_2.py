# -*- coding: utf-8 -*-
"""
Created on Tue Mar 21 11:12:34 2023

@author: MatyG
"""

# Import required libraries
from surprise import Dataset
from surprise import Reader
from surprise import KNNWithMeans
from surprise.model_selection import train_test_split
from surprise import accuracy
import pandas as pd

# Load data
ratings = pd.read_csv('ratings.csv')
movies = pd.read_csv('movies.csv', index_col=[0])
reader = Reader(rating_scale=(1, 5))
data = Dataset.load_from_df(ratings[['userId', 'movieId', 'rating']], reader)

# test_size = 0.2 pour 20% test and 80 training
trainset, testset = train_test_split(data, test_size=0.2)

# =============================================================================
# Utilisation de la méthode similarité cosinus
# On peut utiliser similarité cosinus, un coefficient de corrélation de Pearson
# ou encore Mean Squared Difference (MSD)
# User_based ==> permet de savoir si l'algo doit faire des similarités entre
# les utilisateurs ou alors les items (pour nous les films)
#
# J'ai vu aussi qu'on pouvait utiliser ça "user_sample" ou "skip_train"
# pour accelerer les process mais j'ai pas plus regardé
# =============================================================================
sim_options = {'name': 'cosine', 'user_based': True}
algo = KNNWithMeans(sim_options=sim_options)


# =============================================================================
# J'utilise KNN mais à voir si SVD est mieux ou pas
# algo = SVD()
# cross_validate(algo, data, measures=['RMSE', 'MAE'], cv=5, verbose=True)
# trainset = data.build_full_trainset()
# algo.fit(trainset) 
# =============================================================================

algo.fit(trainset)
# Predictions
predictions = algo.test(testset)

# Calcule accuracy measures
accuracy.rmse(predictions)
accuracy.mae(predictions)

# Permet d'avoir top N movie recommendations pour un user
def get_top_n_movies(user_id, n=10):
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
user_id = 13
top_n_movies = get_top_n_movies(user_id)
print(f"Top {len(top_n_movies)} recommendations for user {user_id}:")
for i, recommendation in enumerate(top_n_movies):
    #print("Voici les id_recomm", recommendation.est)
    print(f"{i+1}. Movie ID: {movies.loc[recommendation.iid]['title']},"
          f" estimation du rating:{recommendation.est}")
