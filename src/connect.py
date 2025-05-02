#This class connects to the OMDB API and collects information about the movies or errors
class Connect():
    def __init__(self, URL, API_KEY):
        self.URL = URL
        self.API_KEY = API_KEY

    #connect to the api and format the json. 
    def query(self):
        pass

    #if the connection was successful, format the json query into usable data
    def format(self):
        pass