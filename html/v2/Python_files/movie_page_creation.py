from airium import Airium
import os


air = Airium()
def open_movie_page(file_path, movieTitle, listgenre, listcast, meanRating):
    air('<!DOCTYPE html>')
    with air.html(lang="en"):
        with air.head():
            air.meta(charset="utf-8")
            air.meta(name="viewport", content="width=device-width, initial-scale=1")

            air.link(rel="stylesheet", href="{{ url_for('static',filename='CSS_files/stylesheet_click_film.css') }}")
        
        air.append("<!-- Top navigation bar -->") 
        with air.header():
            with air.div(klass="topnav"):
                with air.a(href="/main.html"):
                    air("Home")
                with air.a(href="/about.html"):
                    air("About")
                with air.div(klass="Flickfinder"):
                    air("FlickFinder")
                with air.a(href="/account.html", klass="right"):
                    air("Account")
        with air.body():
            with air.div(class_="container"):
                with air.div(class_="img-container"):
                    air.img(src="{{ url_for('static', filename='Images/Themenu.webp') }}", alt="Movie Title")
                with air.div(class_="synopsis-container"):
                    air.h1(_t=f"{movieTitle}")
                    for genre in listgenre:
                        air.span(_t=f"{genre}", class_=f"tag_{genre}")
                    air.p(_t="2022&emsp;-&emsp;1h47m")
                    air.p(_t="A young couple travels to a remote island to eat at an exclusive restaurant where the chef has prepared a lavish menu, with some shocking surprises.")
                    air.hr()
                    air.p(_t="Director :")
                    air.hr()
                    cast_output = "Cast:&emsp;| "
                    for cast in listcast:
                        cast_output += f" {cast} |"
                    air.p(_t=cast_output)
                    # air.p(_t=f"Cast:&emsp; {listcast[0]} | {listcast[1]} | {listcast[2]}")
                    air.h3(_t=f"Rating :&ensp;{meanRating}&ensp;", class_="stars_rating")
                    
                    with air.div(class_="rate"):
                        air.p("Your rating:", class_="rating-label")
                        air.input(type="radio", id="star1", name="rate", value="1")
                        air.label("1 star", for_="star1", title="text")
                        air.input(type="radio", id="star2", name="rate", value="2")
                        air.label("2 stars", for_="star2", title="text")
                        air.input(type="radio", id="star3", name="rate", value="3")
                        air.label("3 stars", for_="star3", title="text")
                        air.input(type="radio", id="star4", name="rate", value="4")
                        air.label("4 stars", for_="star4", title="text")
                        air.input(type="radio", id="star5", name="rate", value="5")
                        air.label("5 stars", for_="star5", title="text")

                    # air.button("Watchlist&ensp;+", class_="buttonwatchlist")  # Commented out as per your example
                    
            with air.div(class_="additional-text"):
                air.p(_t="Additional text goes here...")

    html = str(air)  # casting to string extracts the value
    # or directly to UTF-8 encoded bytes:
    html_bytes = bytes(air)  # casting to bytes is a shortcut to str(a).encode('utf-8')

    with open(file_path, 'w', encoding="utf-8") as file:
        file.write(html)

    print("HTML page created successfully.")