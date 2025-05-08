import requests
from movie import Movie

#This class connects to the OMDB API and collects information about the movies or errors
class Connect():
    def __init__(self, URL, API_KEY):
        self.URL = URL
        self.API_KEY = API_KEY

    #connect to the api and search for a movie. Returns an array with either movie objects or an error message
    def search(self, title):
        params = {"apikey":self.API_KEY, "s":title}
        response = requests.get(self.URL, params = params)
        #check if successful
        if response.status_code == 200:
            data = response.json()
            #print(data)
            self.format(data)
        else:
            #unsuccessful connection. Set error message and return it in a list
            error_message = f"Connection unsuccessful. Response code {response.status_code}"
            print(f"connection unsuccessful. {response.status_code}")
            return [error_message]

    #if the connection was successful, format the json query into usable data
    def format(self, data):
        movie_list = []
        print(data)
        #data should be a dictionary
        #check if "Search" key exists
        if "Search" in data:
            #in the value is a list of dictionaries. Each dictionary has the movie information
            #in the following keys: Title, Year, imdbID, Type, Poster (url)
            for movie in data["Search"]:
                search_result_movie = Movie(movie)
                movie_list.append(search_result_movie)
            for each in movie_list:
                print(each.get_title())


connection = Connect("http://www.omdbapi.com/", "9cda324")
connection.search("Back to the Future")