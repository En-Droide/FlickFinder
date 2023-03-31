

import pandas as pd

from surprise import SVD
from surprise import Dataset
from surprise import Reader
from surprise import accuracy
from surprise.model_selection import train_test_split

from surprise.model_selection import cross_validate

import warnings
warnings.filterwarnings("ignore")

movies_df = pd.read_csv("movies.csv")
rating_df = pd.read_csv("ratings.csv")

# print("head= ", movies_df.head())
print("info= ", rating_df.columns.values)

# Permet de savoir combien d'éléments il y a différent dans une colonne
# print(movies_df.groupby("genres")["movieId"].nunique())
# print(movies_df.genres.value_counts())


df = pd.read_csv('ratings.csv')

# =============================================================================
# # Création de l'objet Reader pour les notes entre 1 et 5
# reader = Reader(rating_scale=(1, 5))
# # Chargement des données
# data = Dataset.load_from_df(df[['userId', 'movieId', 'rating']], reader)
# # Division des données en ensemble de formation/test
# trainset, testset = train_test_split(data, test_size=0.25)
# model = SVD()
# # Entrainement
# fit_model = model.fit(trainset)
# # Prédiction des notes pour l'ensemble de test
# predictions = model.test(testset)
# # Calcul de la RMSE (Root Mean Square Error) = en gros ça permet d'évaluer la
# # performance d'un modèle de recommandation.
# accuracy.rmse(predictions)
# =============================================================================

reader = Reader(rating_scale=(1, 5))
data = Dataset.load_from_df(df[['userId', 'movieId', 'rating']],
                                    reader=reader)

# Use the famous SVD algorithm.
algo = SVD()

# Run 5-fold cross-validation and print results.
cross_validate(algo, data, measures=['RMSE', 'MAE'], cv=5, verbose=True)





