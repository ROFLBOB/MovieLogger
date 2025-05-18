import requests
from movie import Movie
from dotenv import load_dotenv
import os

#This class connects to the OMDB API and collects information about the movies or errors
class Connect():
    def __init__(self, URL):
        load_dotenv()
        try:
            self.__API_KEY = os.getenv("API_KEY", default = "demo_key")
            if self.__API_KEY == "demo_key":
                return
        except Exception:
            print("error loading API key from environment file. Does it exist?")
            self.__API_KEY = ""
        self.URL = URL

    #connect to the api and search for a movie. Returns an array with either movie objects or an error message
    def search(self, title):
        params = {"apikey":self.__API_KEY, "s":title}
        response = requests.get(self.URL, params = params)
        #check if successful
        if response.status_code == 200:
            data = response.json()
            #print(data)
            return self.format(data)
        else:
            #unsuccessful connection. Set error message and return it in a list
            error = True
            error_message = f"Connection unsuccessful. Response code {response.status_code}"
            print(f"connection unsuccessful. {response.status_code}")
            return [error_message, error]

    #if the connection was successful, format the json query into usable data. returns a list of movies
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
            #for each in movie_list:
            #    print(each.get_title())
            return movie_list
        #Title isn't in the response so it must be an individual movie lookup
        else:
            movie_lookup_result = Movie(data)
            return movie_lookup_result


        
    def lookup(self, id):
        params = {"apikey":self.__API_KEY, "i":id}
        response = requests.get(self.URL, params = params)
        #check if successful
        if response.status_code == 200:
            data = response.json()
            return self.format(data)
        
