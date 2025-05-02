class Movie():
    #movie is a dictionary containing information about the movie
    #{"title":"jaws","year":1979,"id"="1235td"}
    def __init__(self, movie):
        self._title = movie["title"]
        self._year = movie["year"]
        self._id = movie["id"]
    
    def get_title(self):
        return self._title
    
    def get_year(self):
        return self._year
    
    def get_id(self):
        return self._id