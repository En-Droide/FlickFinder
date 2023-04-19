import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse import csr_matrix
from surprise import Reader, Dataset, SVD


csv_file = pd.read_csv('csv_files/tmdb_5000_movies.csv')

# stop_words='english' permet lors de l'utilisation de la methode tfidf
# d'enlever des mots que l'on ne veut pas dans le texte avant de créer les
# vecteurs en utilisant 'english', on fait appel à une liste par défaut
# enlevant alors tous les mots du style : "the", "and", "a", etc."

tfidf = TfidfVectorizer(stop_words='english')

# En utilisant chat-GPT j'ai trouvé la méthode fillna (de Panda)
# qui permet de remplacer tous les NaN que j'ai pu avoir par ""
csv_file['overview'] = csv_file['overview'].fillna('')
tfidf_matrix = tfidf.fit_transform(csv_file['overview'])
print(tfidf_matrix)
#Csr_matrix permet de réduire la matrice 
tfidf_matrix = csr_matrix(tfidf_matrix)
print(tfidf_matrix)

# On utilise la méthode de la similarité cosinus
similarity_overview = cosine_similarity(tfidf_matrix)


def get_similar_movies(movie_title):
    movie_indices = []
    movie_index = csv_file[csv_file['title'] == movie_title].index[0]
    # print(movie_index)
    list_similar_movies = list(enumerate(similarity_overview[movie_index]))

    # key=lambda x: x[1] permet de sorted en fonction de la deuxième valeur,
    # étant celle que l'on veut
    list_similar_movies = sorted(list_similar_movies, key=lambda x: x[1],
                                 reverse=True)
    list_similar_movies = list_similar_movies[1:15]
    # print(list_similar_movies)

    for each_film in list_similar_movies:
        movie_indices.append(each_film[0])

    similar_movies = csv_file.iloc[movie_indices][['id', 'vote_average',
                                                   'title']]
    return similar_movies


# Test the functions with some examples
print(get_similar_movies('Harry Potter and the Goblet of Fire'))
