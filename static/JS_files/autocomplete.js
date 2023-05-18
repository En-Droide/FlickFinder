$(function () {
  // Fetch the movie titles from the server
  $.getJSON("./static/JS_files/movieList.json", function(json) {
    var movieTitles = json; // this will show the info it in firebug console
    alert("test")
    return movieTitles;
});

  // $.getJSON(
  //   "https://raw.githubusercontent.com/privacy-tech-lab/gretel-demo/main/ml-latest-small/movies.json",
  //   function (data) {
  //     $.each(data, function (index, movie) {
  //       movieTitles.push(movie.title);
  //     });
  //   }
  // );

  // Define a custom search function to return the top 10 best matches
  $.ui.autocomplete.filter = function (array, term) {
    var matcher = new RegExp($.ui.autocomplete.escapeRegex(term), "i");
    return $.grep(array, function (value) {
      return matcher.test(value);
    })
      .sort(function (a, b) {
        // Sort the matches by the index of the match in the title string
        var aIndex = a.toLowerCase().indexOf(term.toLowerCase());
        var bIndex = b.toLowerCase().indexOf(term.toLowerCase());
        return aIndex - bIndex;
      })
      .slice(0, 5);
  };

  // Initialize the autocomplete widget with the movie titles and custom search function
  $("#tags").autocomplete({
    source: movieTitles,
    minLength: 2,
    autoFocus: true,
    delay: 500,
  });
});
