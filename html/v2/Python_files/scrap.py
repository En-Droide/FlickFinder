from bs4 import BeautifulSoup
import requests

def scrap_image(link, path):
    soup = BeautifulSoup(requests.get(link, headers={'User-Agent': 'Edge'}).text, "html.parser")
    image_link = soup.find("div", {"class": "ipc-media"}).img["src"]
    image_data = requests.get(image_link).content
    image_format = "." + str(image_link.split(".")[-1])
    with open(path+image_format, "wb+") as handler:
        handler.write(image_data)
