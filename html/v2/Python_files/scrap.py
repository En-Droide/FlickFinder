from bs4 import BeautifulSoup
import requests

def scrap_image(link, images_path, movieTitle):
    try:
        soup = BeautifulSoup(requests.get(link, headers={'User-Agent': 'Edge'}).text, "html.parser")
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
        
    
