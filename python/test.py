import pandas as pd
from imdb import IMDb

# Load the TMDB movies CSV file
movies_df = pd.read_csv('csv_files/tmdb_5000_movies.csv')

# Create a new column for IMDB ratings
movies_df['imdb_rating'] = ''

# Create an instance of the IMDb class
ia = IMDb()

# Iterate over each row in the movies dataframe
i=0
for index, row in movies_df.iterrows():
    i+=1
    print(i)
    # Get the movie title
    title = row['title']
    
    # Search for the movie on IMDB
    search_results = ia.search_movie(title)
    
    # Get the top search result
    movie_id = search_results[0].getID()
    movie = ia.get_movie(movie_id)
    
    # Get the IMDB rating for the movie
    imdb_rating = movie.get('rating')
    
    # Add the IMDB rating to the movies dataframe
    movies_df.at[index, 'imdb_rating'] = imdb_rating
    
    if index == 19:
        break
    
# Save the updated movies dataframe to a CSV file
movies_df.to_csv('csv_files/tmdb_5000_movies_with_imdb_ratings.csv', index=False)


