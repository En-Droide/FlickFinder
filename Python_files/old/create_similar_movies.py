from airium import Airium
import os
from math import *

ROW_SIZE = 4


def NumberOfGrid(movies):
    return ceil(len(movies)/4)


def SimilarPageCreation(tfidf_movies, similarity_movies, file_path, images_path, row_size = ROW_SIZE):
    delete_file(file_path)
    air = Airium()

    air('<!DOCTYPE html>')
    with air.html(lang="en"):
        with air.head():
            air.meta(charset="utf-8")
            air.meta(name="viewport", content="width=device-width, initial-scale=1")
            with air.title():
                air("FlickFinder")

            air.link(rel="stylesheet", href="https://use.fontawesome.com/releases/v5.12.1/css/all.css", crossorigin="anonymous")
            air.link(rel="stylesheet", href="{{ url_for('static',filename='CSS_files/stylesheet_main.css') }}")
            air.link(rel="stylesheet", href="//code.jquery.com/ui/1.13.2/themes/base/jquery-ui.css")

            air.script(src="https://code.jquery.com/jquery-3.7.0.js", integrity="sha256-JlqSTELeR4TLqP0OG9dxM7yDPqX1ox/HfgiSLBj8+kM=", crossorigin="anonymous")
            air.script(src="https://code.jquery.com/ui/1.13.2/jquery-ui.js")
            air.script(src="{{ url_for('static',filename='JS_files/autocomplete.js') }}")
        air.append("<!-- Top navigation bar -->") 
        with air.header():
            with air.div(klass="topnav"):
                with air.a(href="/main.html"):
                    air("Home")
                with air.a(href="/about.html"):
                    air("About")
                with air.div(klass="Flickfinder"):
                    air("FlickFinder")
                air.append("{% if currentUserId %}")
                with air.div(klass="right"):
                    with air.a(href="/myratings.html"):
                        air("My Ratings")
                    with air.button(klass="disconnectButton", type="submit"):
                        air("Disconnect (connected as {{ currentUserId }})")
                air.append("{% else %}")
                with air.a(href="/account.html", klass="right"):
                    air("Account")
                air.append("{% endif %}")
            with air.script():
                air.append("""
        $(document).ready(function () {
        $(".disconnectButton").click(function () {
            $.ajax({
                url: "/_disconnect",
                type: "POST",
                crossDomain: true,
                success: function () {
                    window.location.href = "/main.html"; 
                },
            });
        });
        });
        """)
        
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
            searchText: message,
            };

            if (message == "") {
            } else {
            $.ajax({
                url: "/_tfidf",
                type: "POST",
                crossDomain: true,
                data: formData,
                dataType: "text",
                    success: function (data) {
                    // alert(data);
                    window.location.href = "/similar_movies.html"; 
                },
            });
            }
        });
        });
        """)
            
            air.append('<h3 class="Titlegrid">Recommendation based on the content (TFIDF) :</h3>')
            for i in range(len(tfidf_movies)):
                movieTitle = tfidf_movies[i].replace("'", "&quot;")
                if(os.path.exists(images_path+'scrap\\'+movieTitle+'.jpg')):
                    imPath = f'Images/scrap/{movieTitle}.jpg'
                else:
                    imPath = 'Images/placeholder.png'
                if(i % row_size == 0):
                    air.append('<div class="movie-grid">')
                # with air.div(klass="movie-grid"):
                with air.div(klass="moviecontainer"):
                    with air.a(href=f"/_movie/{movieTitle}", id=f"{movieTitle}"):
                        air.img(src=f"{{{{ url_for('static', filename='{imPath}') }}}}", alt=f"Movie: {movieTitle}")
                    with air.script():
                        air.append("""
        $(document).ready(function() {{
            $("a[href='/_movie/{movieTitle}']").click(function(event) {{
                event.preventDefault();
                // alert("yes");
                window.location.href = "/_movie/{movieTitle}";
            }});
        }});
                        """.format(movieTitle=movieTitle))
                    air.h3(_t=movieTitle)
                    air.h6(_t="Genre")
                    air.p(_t="Synopsys")
                if(i%row_size == row_size-1 or i == len(tfidf_movies)-1): air.append('</div>')

        air.append('<h3 class="Titlegrid">Recommendation based on the movie similarities (Correlation) :</h3>')
        for i in range(len(similarity_movies)):
            movieTitle = similarity_movies[i].replace("'", "&quot;")
            if(os.path.exists(images_path+'scrap\\'+movieTitle+'.jpg')):
                imPath = f'Images/scrap/{movieTitle}.jpg'
            else:
                imPath = 'Images/placeholder.png'
            if(i % row_size == 0):
                air.append('<div class="movie-grid">')
            # with air.div(klass="movie-grid"):
            with air.div(klass="moviecontainer"):
                with air.a(href=f"/_movie/{movieTitle}", id=f"{movieTitle}"):
                    air.img(src=f"{{{{ url_for('static', filename='{imPath}') }}}}", alt=f"Movie: {movieTitle}")
                with air.script():
                    air.append("""
    $(document).ready(function() {{
        $("a[href='/_movie/{movieTitle}']").click(function(event) {{
            event.preventDefault();
            // alert("yes");
            window.location.href = "/_movie/{movieTitle}";
        }});
    }});
                    """.format(movieTitle=movieTitle))
                air.h3(_t=movieTitle)
                air.h6(_t="Genre")
                air.p(_t="Synopsys")
            if(i%row_size == row_size-1 or i == len(similarity_movies)-1): air.append('</div>')

        with air.footer():
            with air.div(klass="container"):
                air.h3(_t="The Recommendation website")
                air.break_source_line()
                air.img(src="{{ url_for('static',filename='Images/ESME.jpg') }}", alt="Me", klass="w3-image", style="display: block; margin: auto", width="100", height="100")
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

    with open(file_path, 'w', encoding="utf-8") as file:
        file.write(html)

    print("HTML page created successfully.")



def delete_file(file_path):
    try:
        os.remove(file_path)
        print("File deleted successfully.")
    except OSError as e:
        print(f"Error deleting the file: {e}")
