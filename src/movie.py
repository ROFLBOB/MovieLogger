class Movie():
    #movie is a dictionary containing information about the movie
    #{"title":"jaws","year":1979,"id"="1235td"}
    def __init__(self, movie = {"Title":"N/A", "Year":"N/A", "imdbID":"N/A", "Type":"N/A", "Poster":"N/A"}):
        self._movie_data = movie
        self._title = movie.get("Title", "N/A")
        self._year = movie.get("Year", "N/A")
        self._id = movie.get("imdbID", "N/A")
        self._type = movie.get("Type", "N/A")
        self._thumbnail_url = movie.get("Poster", "N/A")
        self._rating = movie.get("Rated", "N/A")
        self._released = movie.get("Released", "N/A")
        self._runtime = movie.get("Runtime", "N/A")
        self._genre = movie.get("Genre", "N/A")
        self._director = movie.get("Director", "N/A")
        self._actors = movie.get("Actors", "N/A")
        self._plot = movie.get("Plot", "N/A")
        self._boxoffice = movie.get("BoxOffice", "N/A")
        self._poster_image = None
        self._review_score = movie.get("review_score", None)
        self._text_review = movie.get("review_text", None)
        self._runtime = None
    
    def __str__(self):
        return f"Movie(Title: {self._title}, Year: {self._year}, IMDBID: {self._id}, Type: {self._type}, Thumbnail URL: {self._thumbnail_url})\nReview Score: {self.get_review_score()}"
    
    def __repr__(self):
        return f"Movie(Title: {self._title}, Year: {self._year}, IMDBID: {self._id}, Type: {self._type}, Thumbnail URL: {self._thumbnail_url})\nReview Score: {self.get_review_score()}"
    
    def __eq__(self, other):
        isMovie = isinstance(other,self.__class__)
        if not isMovie:
            return False
        if self.get_id() == other.get_id():
            return True
        else:
            return False
    
    def get_title(self):
        return self._title
    
    def get_year(self):
        return self._year
    
    def get_id(self):
        return self._id
    
    def get_thumbnail_url(self):
        return self._thumbnail_url
    
    def get_rating(self):
        return self._rating
    
    def get_released(self):
        return self._released

    def get_runtime(self):
        return self.runtime
    
    def get_genre(self):
        return self._genre
    
    def get_director(self):
        return self._director
    
    def get_actors(self):
        return self._actors
    
    def get_plot(self):
        return self._plot
    
    def get_boxoffice(self):
        return self._boxoffice
    
    def set_poster_image(self, image):
        self._poster_image = image
    
    def get_poster_image(self):
        return self._poster_image
    
    def get_review_score(self):
        return self._review_score
    
    def set_review_score(self, score):
        self._review_score = score
        print(f"Set {self.get_title()}'s review score to {score}.")

    def get_review_text(self):
        return self._text_review
    
    def set_review_text(self, text):
        self._text_review = text
        print(f"Set {self.get_title()}'s text review to:\n{text}")

    #convert movie review to dictionary
    def review_to_dictionary(self):
        return{
            "imdbID": self.get_id(),
            "Review Score": self.get_review_score(),
            "Review": self.get_review_text()
        }
    
    #convert movie to dictionary
    def to_dictionary(self):
        return{
            "imdbID":self.get_id(),
            "Title":self.get_title(),
            "Year":self.get_year(),
            "Poster":self.get_thumbnail_url(),
            "review_text":self.get_review_text(),
            "review_score":self.get_review_score()
        }
    
    @staticmethod
    def load_from_dictionary(data):
        return Movie({
            "Title":data["Title"],
            "Year":data["Year"],
            "Poster":data["Poster"],
            "imdbID":data["imdbID"],
            "review_text":data["review_text"],
            "review_score":data["review_score"]
        })