import pandas as pd
from imdb import IMDb

# Load the TMDB movies CSV file
movies_df = pd.read_csv('csv_files/tmdb_5000_movies.csv')

# Create a new column for IMDB ratings
movies_df['imdb_rating'] = ''

# Create an instance of the IMDb class
ia = IMDb()

# Iterate over each row in the movies dataframe
start = 0 
end = 10
for i in range (start, end):
    index =i
# for index, row in movies_df.iterrows():
    print("i = ", index)
    # print(row)
    row = movies_df.iloc[index]
    # print(row)
        # Get the movie title
    title = row['title']
    print(title)
    
    # Search for the movie on IMDB
    search_results = ia.search_movie(title)
    
    # Get the top search result
    movie_id = search_results[0].getID()
    movie = ia.get_movie(movie_id)
    
    # Get the IMDB rating for the movie
    imdb_rating = movie.get('rating')
    print(imdb_rating)
    
    # Add the IMDB rating to the movies dataframe
    movies_df.at[index, 'imdb_rating'] = imdb_rating
    
# Save the updated movies dataframe to a CSV file
movies_df.to_csv('csv_files/tmdb_500_movies_with_imdb_ratings.csv', 
                 index=False)


