
# Import required libraries
from surprise import Dataset
from surprise.model_selection import train_test_split
from surprise import accuracy
import pandas as pd
from surprise import SVD
from surprise import Reader
from surprise.model_selection import cross_validate
import re



user_id = 4

# Load data
movie_list_user = []
unrating_userid_movie = []
ratings = pd.read_csv('ratings.csv')
movies = pd.read_csv('movies.csv', index_col=[0])
reader = Reader(rating_scale=(1, 5))
data = Dataset.load_from_df(ratings[['userId', 'movieId', 'rating']], reader)


def clean_title(title):
    title = re.sub("[^a-zA-Z0-9 ]", "", title)
    return title


# Faire une colonne en plus contenant les nouveaux titres clean
movies["clean title"] = movies["title"].apply(clean_title)

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


algo = SVD()
cross_validate(algo, data, measures=['RMSE', 'MAE'], cv=5, verbose=True)
trainset = data.build_full_trainset()
algo.fit(trainset)

predictions = algo.test(testset)

accuracy.rmse(predictions)
accuracy.mae(predictions)


# Permet d'avoir top N movie recommendations pour un user
def get_top_n_movies(user_id, n=30):
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
top_n_movies = get_top_n_movies(user_id)
print(f"Top {len(top_n_movies)} recommendations for user {user_id}:")
for i, recommendation in enumerate(top_n_movies):
    # print("Voici les id_recomm", recommendation.est)
    unrating_userid_movie.append(movies.loc[recommendation.iid]['title'])
    print(f"{i+1}. Movie ID: {movies.loc[recommendation.iid]['title']},"
          f" estimation du rating:{round(recommendation.est,2)}")

rating_userid_movie = ratings[ratings["userId"] == user_id]["movieId"].tolist()


def rating_film_user(rating_userid_movie):
    film = 0
    for MovieIdToMovie in rating_userid_movie:
        film += 1
        print(f"\nfilm n°{film} :", movies.loc[MovieIdToMovie]['clean title'])
        print("rating du film : ", ratings.loc[MovieIdToMovie]['rating'])

# ============================================================================
# TODO :  Il faut revoir les années de distribution,
# TODO : essayer de faire un test avec un user test
# TODO : Commencer à faire le site
# ============================================================================