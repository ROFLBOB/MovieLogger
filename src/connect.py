import requests
from movie import Movie
from dotenv import load_dotenv
import os

#This class connects to the OMDB API and collects information about the movies or errors
class Connect():
    def __init__(self, URL):
        self.URL = URL
        self.total_results = 0
        self.load_api_key()


    def load_api_key(self):
        load_dotenv(override=True)
        self.api_key=os.getenv("API_KEY", default="demo_key")

    def set_api_key(self, new_key):
        self.api_key = new_key

    #connect to the api and search for a movie. Returns an array with either movie objects or an error message
    def search(self, title, page = 1):
        params = {"apikey":self.api_key, "s":title, "page":page}
        response = requests.get(self.URL, params = params)
        #check if successful
        if response.status_code == 200:
            data = response.json()
            #check if response contains any movies
            print(f'data.get("Response"): {data.get("Response")}')
            if data.get("Response") == "False":
                return "No movies found."
            print(f"Data: {data}")
            self.total_results = str(data.get("totalResults", "0"))
            return self.format(data)

        else:
            #unsuccessful connection. Set error message and return it in a list
            error = True
            error_message = f"Connection unsuccessful. Response code {response.status_code}"
            print(f"connection unsuccessful. {response.status_code}")
            return "Error"

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
        params = {"apikey":self.api_key, "i":id}
        response = requests.get(self.URL, params = params)
        #check if successful
        if response.status_code == 200:
            data = response.json()
            return self.format(data)
        else:
            return None
        
