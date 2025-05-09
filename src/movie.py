class Movie():
    #movie is a dictionary containing information about the movie
    #{"title":"jaws","year":1979,"id"="1235td"}
    def __init__(self, movie = {"Title":"N/A", "Year":"N/A", "imdbID":"N/A", "Type":"N/A", "Poster":"N/A"}):
        self._title = movie["Title"]
        self._year = movie["Year"]
        self._id = movie["imdbID"]
        self._type = movie["Type"]
        self._thumbnail_url = movie["Poster"]
    
    def __str__(self):
        return f"Movie(Title: {self._title}, Year: {self._year}, IMDBID: {self._id}, Type: {self._type}, Thumbnail URL: {self._thumbnail_url})\n"
    
    def __repr__(self):
        return f"Movie(Title: {self._title}, Year: {self._year}, IMDBID: {self._id}, Type: {self._type}, Thumbnail URL: {self._thumbnail_url})\n"
    
    def get_title(self):
        return self._title
    
    def get_year(self):
        return self._year
    
    def get_id(self):
        return self._id
    
    def get_thumbnail_url(self):
        return self._thumbnail_url