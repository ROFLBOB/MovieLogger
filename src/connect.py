import requests

#This class connects to the OMDB API and collects information about the movies or errors
class Connect():
    def __init__(self, URL, API_KEY):
        self.URL = URL
        self.API_KEY = API_KEY

    #connect to the api and search for a movie. 
    def search(self, title):
        params = {"apikey":self.API_KEY, "s":title}
        response = requests.get(self.URL, params = params)
        #check if successful
        if response.status_code == 200:
            data = response.json()
            print(data)
        else:
            #unsuccessful connection
            print(f"connection unsuccessful. {response.status_code}")
        
        


    #if the connection was successful, format the json query into usable data
    def format(self):
        pass


connection = Connect("http://www.omdbapi.com/", "CODE HERE")
connection.search("Back to the Future")