from bs4 import BeautifulSoup
import requests
import csv
import pandas as pd

def request_soup(link):
    soup = BeautifulSoup(requests.get(link, headers={'User-Agent': 'Edge'}).text, "html.parser")
    return soup

def scrap_image(soup, images_path, movieTitle):
    try:
        # soup = BeautifulSoup(requests.get(link, headers={'User-Agent': 'Edge'}).text, "html.parser")
        image_link = soup.find("div", {"class": "ipc-media"}).img["src"]
        image_data = requests.get(image_link).content
        image_format = "." + str(image_link.split(".")[-1])
        with open(images_path+"scrap\\"+movieTitle.replace("'", "&quot;")+image_format, "wb+") as handler:
            handler.write(image_data)
    except:
        print("error scraping", movieTitle)
        with open(images_path + "failed_images_scraps.txt", "a+") as writer:
            failed_scraps = [movieTitle.strip() for movieTitle in writer.readlines()]
            print(failed_scraps)
            if movieTitle not in failed_scraps:
                writer.write(movieTitle+"\n")
        return "ERROR_IMAGE"


def scrape_and_create_movie_csv(path,soup,movieTitle):
    # Scrape director name
    director_element = soup.find('a', class_='ipc-metadata-list-item__list-content-item ipc-metadata-list-item__list-content-item--link')
    director_name = director_element.text.strip() if director_element else f"Director name not found on the page for {movieTitle}."

    # Scrape synopsis
    synopsis_element = soup.find('span', attrs={'data-testid': 'plot-xs_to_m'})
    synopsis = synopsis_element.text.strip() if synopsis_element else f"Synopsis not found on the page for {movieTitle}."

    # Scrape additional information
    extracted_texts = []
    informations = soup.find_all('div', class_='sc-52d569c6-0 kNzJA-D')
    if informations:
        for element in informations:
            li_element = element.find_all('li', class_='ipc-inline-list__item')
            for item in li_element:
                extracted_texts.append(item.text.strip())
    else:
        extracted_texts = [f"Informations not found on the page for {movieTitle}."]

    df = pd.DataFrame({
        "title": [movieTitle],
        "director": [director_name],
        "synopsis": [synopsis],
        "informations": [", ".join(extracted_texts)]
    })
    df.to_csv(path, mode='a', index=False, header=False)
    print("done")
    return df

def informations_movies (movieTitle, df_movie_info):
    try:
        informations_movieDate = df_movie_info.loc[df_movie_info['title'] == movieTitle, 'informations'].str.split(",").str.get(0).str.strip().values[0]
        informations_movieTime =  df_movie_info.loc[df_movie_info['title'] == movieTitle, 'informations'].str.split(",").str.get(-1).str.strip().values[0]
        informations_movieSynopsis =  df_movie_info.loc[df_movie_info['title'] == movieTitle, 'synopsis'].values[0]
        informations_movieDirector = df_movie_info.loc[df_movie_info['title'] == movieTitle, 'director'].values[0]
    except:
        informations_movieDate = ""
        informations_movieTime =  ""
        informations_movieSynopsis =  ""
        informations_movieDirector = ""
    return informations_movieDate, informations_movieTime, informations_movieSynopsis, informations_movieDirector