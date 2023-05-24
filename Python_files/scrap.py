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


# def scrap_director(soup, movieTitle):
#     # soup = BeautifulSoup((requests.get(link, headers={'User-Agent': 'Edge'})).text, 'html.parser')
#     director_element = soup.find('a', class_='ipc-metadata-list-item__list-content-item ipc-metadata-list-item__list-content-item--link')
#     if director_element:
#         director_name = director_element.text.strip()
#         return director_name
#     else:
#         return f"Director name not found on the page for {movieTitle}."
    
# def scrap_synopsis(soup, movieTitle):
#     # soup = BeautifulSoup((requests.get(link, headers={'User-Agent': 'Edge'})).text, 'html.parser')
#     synopsis_element = soup.find('div', class_='ipc-html-content-inner-div')
#     if synopsis_element:
#         synopsis = synopsis_element.text.strip()
#         return synopsis
#     else:
#         return f"Synopsis not found on the page for {movieTitle}."

# def scrap_infos(soup, movieTitle):
#     extracted_texts=[]
#     informations = soup.find_all('div', class_='sc-52d569c6-0 kNzJA-D')
#     if informations:
#         for element in informations:
#             li_element = element.find_all('li', class_='ipc-inline-list__item')
#         for item in li_element:
#             extracted_texts.append(item.text.strip())
#         return extracted_texts
#     else :
#          return f"Informations not found on the page for {movieTitle}."



# def create_movie_json(movieTitle, director_name, synopsis, informations):
#     movie_data = {
#         "title": movieTitle,
#         "director": director_name,
#         "synopsis": synopsis,
#         "informations": informations
#     }

#     with open("C:\\Users\\MatyG\\Documents\\Annee_2022_2023\\Projet_films\\FlickFinder\\static\\movie_informations.json", "w") as json_file:
#         json.dump(movie_data, json_file)

def scrape_and_create_movie_json(soup, movieTitle):
    # Scrape director name
    director_element = soup.find('a', class_='ipc-metadata-list-item__list-content-item ipc-metadata-list-item__list-content-item--link')
    director_name = director_element.text.strip() if director_element else f"Director name not found on the page for {movieTitle}."

    # Scrape synopsis
    synopsis_element = soup.find('div', class_='ipc-html-content-inner-div')
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
    df.to_csv('C:\\Users\\MatyG\\Documents\\Annee_2022_2023\\Projet_films\\FlickFinder\\static\\Csv_files\\movies_informations.csv', mode='a', index=False, header=False)
    print("done")
    return df
