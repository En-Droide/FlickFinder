jQuery(function () {
  // Fetch the movie titles from the server
  jQuery.getJSON("./static/JS_files/movieList.json", function (json) {
    var movieTitles = json; // Store the movie titles

    // Define a custom search function to return the top 10 best matches
    jQuery.ui.autocomplete.filter = function (array, term) {
      var matcher = new RegExp(jQuery.ui.autocomplete.escapeRegex(term), "i");
      return jQuery.grep(array, function (value) {
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
    jQuery("#tags").autocomplete({
      source: movieTitles,
      minLength: 2,
      autoFocus: true,
      delay: 500,
    });
  });
});

