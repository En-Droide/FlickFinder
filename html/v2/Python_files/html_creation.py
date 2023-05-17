from airium import Airium
import os
from math import *

# file_path ='C:\\Users\\MatyG\\Documents\\Annee_2022_2023\\Projet_films\\FlickFinder\\html\\v2\\HTML_files\\output.html'
# movies = ["The Shawshank Redemption","The Godfather","The Dark Knight","Pulp Fiction","Fight Club","Goodfellas","Inception","The Matrix","Interstellar","Forrest Gump"]


def NumberOfGrid(movies):
    return ceil(len(movies)/4)



def PageCreation(movies,file_path):
    air = Airium()

    air('<!DOCTYPE html>')
    with air.html(lang="en"):
        with air.head():
            air.meta(charset="utf-8")
            air.meta(name="viewport", content="width=device-width, initial-scale=1")

            air.link(rel="stylesheet", href="https://use.fontawesome.com/releases/v5.12.1/css/all.css", crossorigin="anonymous")
            air.link(rel="stylesheet", href="{{ url_for('static',filename='CSS_files/stylesheet_main.css') }}")
            air.link(rel="stylesheet", href="//code.jquery.com/ui/1.13.2/themes/base/jquery-ui.css")

            air.script(src="https://code.jquery.com/jquery-3.7.0.js", integrity="sha256-JlqSTELeR4TLqP0OG9dxM7yDPqX1ox/HfgiSLBj8+kM=", crossorigin="anonymous")
            air.script(src="https://code.jquery.com/ui/1.13.2/jquery-ui.js")
            air.script(src="{{ url_for('static',filename='JS_files/autocomplete.js') }}")
        air.append("<!-- Top navigation bar -->") 
        with air.header():
            with air.div(klass="topnav"):
                with air.a(href="main.html"):
                    air("Home")
                with air.a(href="about.html"):
                    air("About")
                with air.div(klass="Flickfinder"):
                    air("FlickFinder")
                with air.a(href="account.html", klass="right"):
                    air("Account")
        
        with air.body():
            air.append("<!-- Search bar -->")
            with air.div(klass="search-container"):
                air.input(id="tags", type="text", name="searchText", placeholder="Search for a movie...")
                air.button(_t="Search", klass="searchFilm", id="search-btn", type="submit")
                with air.script():
                    air.append("""
                        $(document).ready(function () {
                        $(".searchFilm").click(function () {
                            const message = $("[name=searchText]").val();
                            var formData = {
                            myMessage: message,
                            };

                            if (message == "") {
                            } else {
                            $.ajax({
                                url: "/_postExemple",
                                type: "POST",
                                crossDomain: true,
                                data: formData,
                                dataType: "text",
                                // success: function (data) {
                                //   alert(data);
                                // },
                            });
                            }
                        });
                        });
                    """)
            imgLeft= len(movies)
            for grids in range(NumberOfGrid(movies)):
                with air.div(klass="movie-grid"):
                    if imgLeft >= 4:
                        for img_grid in range(4):
                            with air.div():
                                with air.a(href="movie_page.html"):
                                    
                                    air.img(src=f"{{{{ url_for('static', filename='PNG/{movies[(grids*4)+img_grid]}.webp') }}}}", alt=f"Movie: {movies[(grids*4)+img_grid]}")
                                air.h3(_t="Title")
                                air.h6(_t="Genre")
                                air.p(_t="Synopsys")
                    else : 
                        for img_grid in range(imgLeft):
                            with air.div():
                                with air.a(href="movie_page.html"):
                                    air.img(src=f"{{{{ url_for('static', filename='PNG/{movies[(grids*4)+img_grid]}.webp') }}}}", alt=f"Movie: {movies[(grids*4)+img_grid]}")
                                air.h3(_t="Title")
                                air.h6(_t="Genre")
                                air.p(_t="Synopsys")
                imgLeft-=4

            air.append("<!-- Pagination links -->")
            with air.div(klass="pagination"):
                air.a(_t="1", href="#", klass="active")
                air.a(_t="2", href="#")
                air.a(_t="3", href="#")
                air.a(_t="4", href="#")
                air.a(_t="5", href="#")
        with air.footer():
            with air.div(klass="container"):
                air.h3(_t="About Us, The Recommendation website")
                air.break_source_line()
                air.img(src="{{ url_for('static',filename='PNG/ESME.jpg') }}", alt="Me", klass="w3-image", style="display: block; margin: auto", width="100", height="100")
                air.h4(_t="<b>hello</b>")
                air.h6(_t="<i>By Matteo Gentili and Robin Lotode</i>")
                with air.ul():
                    with air.li():
                        with air.a(href="#"):
                            air.i(klass="fab fa-facebook",**{"aria-hidden": "true"})
                    with air.li():
                        with air.a(href="#"):
                            air.i(klass="fab fa-twitter",**{"aria-hidden": "true"})
                    with air.li():
                        with air.a(href="#"):
                            air.i(klass="fab fa-google-plus-g",**{"aria-hidden": "true"})
                    with air.li():
                        with air.a(href="#"):
                            air.i(klass="fab fa-linkedin",**{"aria-hidden": "true"})
                    with air.li():
                        with air.a(href="#"):
                            air.i(klass="fab fa-instagram",**{"aria-hidden": "true"})

        

    html = str(air)  # casting to string extracts the value
    # or directly to UTF-8 encoded bytes:
    html_bytes = bytes(air)  # casting to bytes is a shortcut to str(a).encode('utf-8')

    with open(file_path, 'w') as file:
        file.write(html)

    print("HTML page created successfully.")



def delete_file(file_path):
    try:
        os.remove(file_path)
        print("File deleted successfully.")
    except OSError as e:
        print(f"Error deleting the file: {e}")
# PageCreation()
#delete_file(file_path)